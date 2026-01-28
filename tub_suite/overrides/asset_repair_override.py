"""
Custom Asset Repair Controller Override
Role-based field editing permissions for workflow-based documents
"""

import frappe
from frappe import _
from frappe.utils import now
from erpnext.assets.doctype.asset_repair.asset_repair import AssetRepair


class CustomAssetRepair(AssetRepair):
    """Custom Asset Repair with role-based field permissions"""

    def validate(self):
        """Enforce manager field restrictions"""
        super(CustomAssetRepair, self).validate()

        # Set flag to ignore validation if workflow is changing
        if not self.is_new():
            old_workflow = frappe.db.get_value("Asset Repair", self.name, "workflow_state")
            if old_workflow != self.workflow_state:
                self.flags.ignore_validate_update_after_submit = True

        validate_asset_repair(self, None)

    def update_status(self):
        """
        OVERRIDE ERPNext's update_status() to prevent automatic asset status change

        ERPNext default behavior:
        - Sets asset to "Out of Order" when repair_status = "Pending"

        TUB Suite behavior:
        - Asset status ONLY changes when manager APPROVES Major severity repair
        - Controlled by workflow state + issue_severity field
        - Handled in before_save_asset_repair() hook
        """
        # DO NOTHING - asset status is managed by our workflow
        # See before_save_asset_repair() and update_asset_status_on_approval()
        pass

    def before_save(self):
        """Auto-fill approval timestamp + Store old workflow state for transition detection"""
        # Store current workflow state BEFORE save for transition detection
        if not self.is_new():
            old_doc = frappe.db.get_value("Asset Repair", self.name,
                ["workflow_state", "verification_status"], as_dict=True)
            if old_doc:
                self._old_workflow_state = old_doc.get("workflow_state")
                self._old_verification_status = old_doc.get("verification_status")

        before_save_asset_repair(self, None)

    def check_repair_status(self):
        """Override ERPNext's check_repair_status to bypass repair_status validation
        We use workflow_state instead of repair_status for tracking"""
        # Skip ERPNext's repair_status validation - we manage this via workflow_state
        pass

    def before_submit(self):
        """Validate engineer signature"""
        super(CustomAssetRepair, self).before_submit()
        before_submit_asset_repair(self, None)

    def before_workflow_action(self, workflow_state_field, workflow_action):
        """Auto-update repair_status before workflow transitions"""
        # When supervisor verifies (Pending Supervisor Verification → Finished), set repair_status to Completed
        if self.workflow_state == "Pending Supervisor Verification" and workflow_action == "Supervisor Verify":
            self.repair_status = "Completed"
        # When reporter confirms (Pending Reporter Confirmation → Finished), set repair_status to Completed
        if self.workflow_state == "Pending Reporter Confirmation" and workflow_action == "Reporter Confirm":
            self.repair_status = "Completed"

    def on_update_after_submit(self):
        """Handle workflow transitions after submit - CRITICAL for asset status management"""
        # Note: Parent class may not have this method, so we don't call super()

        # Get old workflow state stored in before_save()
        old_workflow = getattr(self, '_old_workflow_state', None)
        old_verification = getattr(self, '_old_verification_status', None)

        new_workflow = self.get("workflow_state")
        new_verification = self.get("verification_status")

        print(f"\n🔄 ON_UPDATE_AFTER_SUBMIT:")
        print(f"   Doc: {self.name}")
        print(f"   Old workflow: {old_workflow}")
        print(f"   New workflow: {new_workflow}")

        # Handle workflow state transitions
        if old_workflow != new_workflow and new_workflow:
            print(f"   🔄 WORKFLOW TRANSITION DETECTED: {old_workflow} → {new_workflow}")

            # Pending Approval → Notify managers
            if new_workflow == "Pending Approval":
                print(f"   📧 Notifying managers...")
                notify_manager_on_submit(self)

            # Approved → Update asset status + Notify engineer
            elif new_workflow == "Approved":
                print(f"   ✅ Approved - updating asset + notifying engineer")
                update_asset_status_on_approval(self)
                notify_engineer_on_approval(self)

            # Rejected → Update maintenance log + Notify engineer
            elif new_workflow == "Rejected":
                print(f"   ❌ Rejected - updating maintenance log + notifying engineer")
                update_maintenance_log_on_rejection(self)
                notify_engineer_on_rejection(self)

            # Approved for Repair → Pending Supervisor Verification (Finish Repair)
            elif old_workflow == "Approved for Repair" and new_workflow == "Pending Supervisor Verification":
                print(f"   ✅ Finish Repair - setting completion handover date")
                if not self.get("completion_handover_date"):
                    frappe.db.set_value("Asset Repair", self.name, "completion_handover_date", frappe.utils.today())
                    frappe.db.commit()

            # Finished → Auto-fill completion date + Notify reporter
            elif new_workflow == "Finished":
                print(f"   ✅ Finished - setting completion date + notifying reporter")
                # Set completion date when engineer finishes job
                if not self.get("completion_date"):
                    frappe.db.set_value("Asset Repair", self.name, "completion_date", frappe.utils.now())
                    frappe.db.set_value("Asset Repair", self.name, "repair_status", "Completed")
                    frappe.db.commit()
                notify_reporter_to_verify(self)
        else:
            print(f"   ⏭️  No workflow change detected")

        # Handle Inspector Verification → Restore asset to Submitted
        # This happens when original reporter verifies after engineer finishes
        if old_verification != new_verification and new_verification == "Verified - Passed":
            restore_asset_status_on_verification(self)


# Event Functions (also called by doc_events hooks)
def validate_asset_repair(doc, method):
    """Validate manager field restrictions and engineer signature"""

    # Check engineer signature before workflow transition to Pending Approval
    workflow_state = doc.get("workflow_state")
    if workflow_state == "Pending Approval" and not doc.get("engineer_signature"):
        frappe.throw(
            _("Engineer Signature is required before submitting for approval"),
            frappe.MandatoryError
        )

    # For workflow transitions, check OLD state to validate who can perform the action
    old_workflow_state = None
    if not doc.is_new():
        old_workflow_state = frappe.db.get_value("Asset Repair", doc.name, "workflow_state")

    # Use old state for permission checks if it exists (during transitions)
    check_state = workflow_state  # FIXED 2026-01-27

    # Get user roles
    user_roles = frappe.get_roles()
    manager_roles = ["Maintenance Manager", "Quality Manager"]
    inspector_roles = ["Maintenance User"]
    engineer_roles = ["Engineering Team"]
    eng_supervisor_roles = ["Engineering Supervisor"]
    is_manager = any(role in user_roles for role in manager_roles)
    is_inspector = any(role in user_roles for role in inspector_roles)
    is_engineer = any(role in user_roles for role in engineer_roles)
    is_eng_supervisor = any(role in user_roles for role in eng_supervisor_roles)
    is_regular_supervisor = "Supervisor" in user_roles
    is_maintenance_supervisor = "Maintenance Supervisor" in user_roles
    is_any_supervisor = is_regular_supervisor or is_maintenance_supervisor

    # Get repair source to check if Regular Supervisor can edit PM repairs
    repair_source = doc.get("repair_source")
    is_pm_repair = repair_source == "Planned Maintenance (ตามแผน)"

    # CRITICAL: Allow Draft/new documents - block ONLY Regular Supervisor from PM repairs
    if not check_state or check_state == "Draft" or check_state == "Approved for Repair":
        # Block Regular Supervisor (not Maintenance Supervisor) from editing PM repairs
        if is_regular_supervisor and not is_maintenance_supervisor and is_pm_repair:
            frappe.throw(_("Only Maintenance Supervisor can edit PM repairs"))
        return  # Allow everyone else

    # Special case: Pending Supervisor Verification - only reporter OR managers OR supervisors can edit
    if check_state == "Pending Supervisor Verification":
        current_user = frappe.session.user
        is_original_reporter = (doc.get("reported_by") == current_user)

                # Check supervisor permissions based on repair source
        if is_regular_supervisor and not is_maintenance_supervisor:
            # Regular Supervisor can ONLY edit Portal repairs
            if repair_source == "Portal (แจ้งผ่านระบบ)":
                return
            else:
                frappe.throw(_("Regular Supervisor can only verify Portal repairs."))
        
        if is_maintenance_supervisor:
            # Maintenance Supervisor can ONLY edit PM repairs
            if repair_source == "Planned Maintenance (ตามแผน)":
                return
            else:
                frappe.throw(_("Maintenance Supervisor can only verify Planned Maintenance repairs."))
        
        if is_original_reporter or is_manager:
            return  # Allow reporter and managers for all repair sources

        # Block everyone else
        frappe.throw(_("You do not have permission to edit this repair."))

    # Special case: Pending Reporter Confirmation - only reporter OR managers OR supervisors can edit
    if check_state == "Pending Reporter Confirmation":
        current_user = frappe.session.user
        is_original_reporter = (doc.get("reported_by") == current_user)
        if is_original_reporter or is_manager or is_any_supervisor:
            return  # Allow editing (reporter confirms via portal)
        else:
            frappe.throw(_("Only the original reporter or supervisor can edit in Pending Reporter Confirmation state"))

    # State-specific permission checks
    # Pending Engineering Assessment - ONLY Engineering Team can edit
    if check_state == "Pending Engineering Assessment":
        if is_engineer:
            return  # Allow Engineering Team ONLY
        else:
            frappe.throw(_("Only Engineering Team can edit in Pending Engineering Assessment state"))

    # Pending Engineering Supervisor Review - ONLY Engineering Supervisor can edit
    if check_state == "Pending Engineering Supervisor Review":
        if is_eng_supervisor:
            return  # Allow Engineering Supervisor ONLY
        else:
            frappe.throw(_("Only Engineering Supervisor can edit in Pending Engineering Supervisor Review state"))

    # Pending GM Final Approval - ONLY GM/Managers can edit
    if check_state == "Pending GM Final Approval":
        # Check if this is a workflow transition (old state was different)
        if old_workflow_state and old_workflow_state != check_state:
            # Workflow transition - allow Eng Supervisor transitioning FROM their review state
            if is_eng_supervisor and old_workflow_state == "Pending Engineering Supervisor Review":
                return  # Allow transition to GM Final Approval

        # Normal editing (not transition) - only managers allowed
        if is_manager:
            return  # Allow Managers only
        else:
            frappe.throw(_("Only GM/Maintenance Manager can edit in Pending GM Final Approval state"))

    # After Draft: Lock ALL fields for engineers
    if not is_manager:
        # Engineers cannot edit anything after submitting for approval
        if not doc.is_new():
            old_doc = frappe.db.get_value("Asset Repair", doc.name, "*", as_dict=True)
            if old_doc:
                # Check if any field changed (except system fields)
                ignored_fields = ["_user_tags", "_comments", "_assign", "_liked_by", "modified", "modified_by",
                                 "docstatus", "workflow_state", "repair_status", "completion_date"]

                # CRITICAL: Block engineers from editing manager approval fields
                manager_approval_fields = ["approval_notes", "approval_signature", "approval_timestamp"]
                for field in manager_approval_fields:
                    if doc.get(field) != old_doc.get(field):
                        frappe.throw(
                            _("Engineers cannot edit Manager Approval fields. This is restricted to Maintenance Managers only."),
                            frappe.PermissionError
                        )

                meta = frappe.get_meta("Asset Repair")
                for field in meta.fields:
                    if field.fieldname in ignored_fields:
                        continue
                    if field.fieldtype in ["Table", "Table MultiSelect", "Attach", "Attach Image"]:
                        continue
                    if doc.get(field.fieldname) != old_doc.get(field.fieldname):
                        frappe.throw(
                            _("Engineers cannot edit fields after submitting for approval. Changed field: {0}").format(field.label or field.fieldname),
                            frappe.ValidationError
                        )
        return

    # For managers: Restrict editing based on state
    if workflow_state == "Pending Approval":
        # In Pending Approval: Managers can ONLY edit approval fields
        pass  # Continue to validation below
    elif workflow_state in ["Approved", "Finished"]:
        # After Approved/Finished: Managers can ONLY edit approval notes (for corrections)
        # Lock everything else
        pass  # Continue to validation below
    else:
        # Rejected/Cancelled: Allow editing for resubmission
        return
    
    if doc.is_new():
        return
        
    old_doc = frappe.db.get_value("Asset Repair", doc.name, "*", as_dict=True)
    if not old_doc:
        return
    
    # Fields that managers can edit
    manager_editable_fields = ["approval_notes", "approval_signature", "approval_timestamp"]
    workflow_fields = ["workflow_state", "repair_status", "completion_date"]
    ignored_fields = ["_user_tags", "_comments", "_assign", "_liked_by", "modified", "modified_by", "docstatus"]
    
    # Check what fields changed
    changed_fields = []
    meta = frappe.get_meta("Asset Repair")
    
    for field in meta.fields:
        fieldname = field.fieldname
        
        if fieldname in manager_editable_fields or fieldname in workflow_fields or fieldname in ignored_fields:
            continue
        
        # Skip child tables and attachments
        if field.fieldtype in ["Table", "Table MultiSelect", "Attach", "Attach Image"]:
            continue
        
        old_value = old_doc.get(fieldname)
        new_value = doc.get(fieldname)
        
        if str(old_value or "") != str(new_value or ""):
            changed_fields.append(fieldname)
    
    # Block managers from editing non-approval fields
    if changed_fields:
        field_labels = [meta.get_label(f) or f for f in changed_fields[:3]]
        frappe.throw(
            _("Managers can only edit Approval Notes and Manager Signature.<br>Cannot modify: {0}").format(", ".join(field_labels)),
            frappe.ValidationError
        )


def before_save_asset_repair(doc, method):
    """Auto-fill all signature timestamps and handle asset status based on severity"""
    if not doc.is_new():
        old_doc = frappe.db.get_value("Asset Repair", doc.name,
            ["approval_notes", "approval_signature", "approval_timestamp", "issue_severity", "workflow_state",
             "supervisor_section1_signature", "supervisor_section1_date",
             "custom_gm_signature", "gm_section1_signature", "gm_section1_approval_date",
             "engineering_operator_signature", "engineering_operator_sign_date",
             "eng_supervisor_signature", "eng_supervisor_review_date",
             "approval_signature", "gm_final_approval_date",
             "supervisor_signature", "supervisor_verification_date",
             "reporter_signature", "reporter_confirmation_date"], as_dict=True)

        if old_doc:
            # Section 1B - Supervisor signature in Draft state
            if doc.get("supervisor_section1_signature") and not old_doc.get("supervisor_section1_signature"):
                if not doc.get("supervisor_section1_date"):
                    doc.supervisor_section1_date = now()

            # GM Section 1 - GM signature in Pending GM Approval Section 1
            # Check for custom_gm_signature (newer field)
            if doc.get("custom_gm_signature") and not old_doc.get("custom_gm_signature"):
                if not doc.get("gm_section1_approval_date"):
                    doc.gm_section1_approval_date = now()
            if doc.get("gm_section1_signature") and not old_doc.get("gm_section1_signature"):
                if not doc.get("gm_section1_approval_date"):
                    doc.gm_section1_approval_date = now()

            # Engineering Section - Operator signature in Pending Engineering Assessment
            if doc.get("engineering_operator_signature") and not old_doc.get("engineering_operator_signature"):
                if not doc.get("engineering_operator_sign_date"):
                    doc.engineering_operator_sign_date = now()

            # Engineering Section - Supervisor signature in Pending Engineering Supervisor Review
            if doc.get("eng_supervisor_signature") and not old_doc.get("eng_supervisor_signature"):
                if not doc.get("eng_supervisor_review_date"):
                    doc.eng_supervisor_review_date = now()

            # Engineering Section - GM signature in Pending GM Final Approval
            if doc.get("approval_signature") and not old_doc.get("approval_signature"):
                if not doc.get("gm_final_approval_date"):
                    doc.gm_final_approval_date = now()

            # Section 3B - Supervisor signature in Pending Supervisor Verification
            if doc.get("supervisor_signature") and not old_doc.get("supervisor_signature"):
                if not doc.get("supervisor_verification_date"):
                    doc.supervisor_verification_date = now()

            # Reporter confirmation - Portal signature in Finished state
            if doc.get("reporter_signature") and not old_doc.get("reporter_signature"):
                if not doc.get("reporter_confirmation_date"):
                    doc.reporter_confirmation_date = now()

            # Legacy approval_timestamp field
            notes_changed = str(old_doc.get("approval_notes") or "") != str(doc.get("approval_notes") or "")
            signature_changed = str(old_doc.get("approval_signature") or "") != str(doc.get("approval_signature") or "")

            if (notes_changed or signature_changed) and not doc.get("approval_timestamp"):
                doc.approval_timestamp = now()

            # Handle asset status change when workflow changes
            old_workflow = old_doc.get("workflow_state")
            new_workflow = doc.get("workflow_state")
            workflow_changed = str(old_workflow or "") != str(new_workflow or "")

            if workflow_changed:
                # Validate manager signature for approval/rejection
                if new_workflow in ["Approved", "Rejected"] and old_workflow == "Pending Approval":
                    if not doc.get("approval_signature"):
                        frappe.throw(_("Manager Signature is required for approval or rejection"), frappe.MandatoryError)
                    if not doc.get("approval_notes"):
                        frappe.throw(_("Approval Notes are required for approval or rejection"), frappe.MandatoryError)

                # Prevent duplicate notifications if before_save is called multiple times
                notification_key = f"notified_{doc.name}_{old_workflow}_to_{new_workflow}"

                if not frappe.flags.get(notification_key):
                    print(f"\n🔄 WORKFLOW CHANGE DETECTED IN BEFORE_SAVE:")
                    print(f"   {old_workflow} → {new_workflow}")

                    if new_workflow == "Pending Approval":
                        print(f"   📧 Notifying managers...")
                        # Track who submitted for approval (engineer) in cache
                        engineer_submitter = doc.get("modified_by") or frappe.session.user
                        frappe.cache().set_value(f"engineer_submitter_{doc.name}", engineer_submitter, expires_in_sec=86400)
                        print(f"   📝 Stored engineer submitter in cache: {engineer_submitter}")
                        notify_manager_on_submit(doc)

                    elif new_workflow == "Approved":
                        print(f"   ✅ Approved - updating asset + notifying engineer")
                        update_asset_status_on_approval(doc)
                        notify_engineer_on_approval(doc)

                    elif new_workflow == "Rejected":
                        print(f"   ❌ Rejected - updating maintenance log + notifying engineer")
                        update_maintenance_log_on_rejection(doc)
                        notify_engineer_on_rejection(doc)

                    elif new_workflow == "Finished":
                        print(f"   ✅ Finished - restoring asset + notifying reporter")
                        restore_asset_status_on_finish(doc)
                        notify_reporter_to_verify(doc)

                    # Set flag to prevent duplicate notifications in same request
                    frappe.flags[notification_key] = True
                else:
                    print(f"   ⏭️  Skipping duplicate notification (already sent)")


def before_submit_asset_repair(doc, method):
    """Validate engineer signature before submission"""
    # Only check engineer_signature if this is the initial submit (docstatus changing from 0 to 1)
    # Not for workflow transitions (which happen after submit when docstatus is already 1)
    if doc.docstatus == 0 and not doc.get("engineer_signature"):
        frappe.throw(_("Engineer Signature is required before submission"), frappe.MandatoryError)


def on_update_after_submit_asset_repair(doc, method):
    """Handle workflow transitions after submit - notifications + asset status"""
    # Set flag to bypass validation during workflow transitions
    doc.flags.ignore_validate_update_after_submit = True

    print(f"\n🔄 ON_UPDATE_AFTER_SUBMIT CALLED:")
    print(f"   Repair: {doc.name}")
    print(f"   Current workflow_state: {doc.get('workflow_state')}")

    # Get old workflow state from doc_before_save (cached in memory before DB update)
    old_workflow = None
    if hasattr(doc, '_doc_before_save') and doc._doc_before_save:
        old_workflow = doc._doc_before_save.get('workflow_state')

    new_workflow = doc.get("workflow_state")

    print(f"   Workflow transition: {old_workflow} → {new_workflow}")

    # Handle state transitions with notifications
    if old_workflow != new_workflow:
        # Pending Approval → Manager needs to review
        if new_workflow == "Pending Approval":
            print(f"   📧 Notifying managers...")
            notify_manager_on_submit(doc)

        # Approved → Notify engineer
        elif new_workflow == "Approved":
            print(f"   ✅ Approved - notifying engineer")
            update_asset_status_on_approval(doc)
            notify_engineer_on_approval(doc)

        # Rejected → Update maintenance log + Notify engineer
        elif new_workflow == "Rejected":
            print(f"   ❌ Rejected - updating maintenance log + notifying engineer")
            update_maintenance_log_on_rejection(doc)
            notify_engineer_on_rejection(doc)

        # Finished → Restore asset + notify reporter
        elif new_workflow == "Finished":
            print(f"   ✅ Finished - restoring asset + notifying reporter")
            restore_asset_status_on_finish(doc)
            notify_reporter_to_verify(doc)
    else:
        print(f"   ⏭️  No workflow state change - skipping notifications")


def update_asset_status_on_approval(doc):
    """
    Update asset status when manager APPROVES repair
    - Major issue approved: Asset stops (Out of Order)
    - Minor issue approved: Asset stays operational (or restore if no other major issues)

    This ensures asset only goes Out of Order when manager confirms it's necessary
    """
    print(f"\n🔧 ASSET STATUS UPDATE CALLED")
    print(f"   Repair: {doc.name}")
    print(f"   Asset: {doc.asset}")
    print(f"   Workflow State: {doc.get('workflow_state')}")
    print(f"   Severity: {doc.get('issue_severity')}")

    if not doc.asset:
        print(f"   ⏭️  No asset - skipping")
        return

    severity = doc.get("issue_severity")
    workflow_state = doc.get("workflow_state")

    # Only update status if repair is approved
    if workflow_state != "Approved":
        print(f"   ⏭️  Not Approved - skipping (state: {workflow_state})")
        return

    asset_doc = frappe.get_doc("Asset", doc.asset)
    print(f"   Current asset status: {asset_doc.status}")

    if severity == "Major - Asset Must Stop":
        # Manager approved Major issue - mark asset Out of Order
        if asset_doc.status != "Out of Order":
            asset_doc.status = "Out of Order"
            asset_doc.add_comment("Comment",
                f"Asset marked Out of Order - Manager approved Major severity repair: {doc.description}")
            asset_doc.save(ignore_permissions=True)
            frappe.logger().info(f"Asset {doc.asset} status changed to Out of Order (Major approved by manager)")

    elif severity == "Minor - Asset Operational":
        # For minor issues, restore asset to In Service ONLY if no other Major repairs exist
        if asset_doc.status == "Out of Order":
            # Check if there are OTHER Major severity repairs still open
            # Use workflow_state instead of repair_status for consistency
            other_major_repairs = frappe.db.count("Asset Repair", {
                "asset": doc.asset,
                "name": ["!=", doc.name],
                "issue_severity": "Major - Asset Must Stop",
                "workflow_state": ["not in", ["Finished", "Cancelled", "Rejected"]]
            })

            if other_major_repairs == 0:
                # No other major issues - safe to restore
                asset_doc.status = "Submitted"
                asset_doc.add_comment("Comment",
                    f"Asset restored to service - Minor severity issue, no other major repairs: {doc.description}")
                asset_doc.save(ignore_permissions=True)
                frappe.logger().info(f"Asset {doc.asset} restored to Submitted (Minor severity, no major repairs)")
            else:
                frappe.logger().info(f"Asset {doc.asset} remains Out of Order - {other_major_repairs} major repair(s) still open")
        else:
            frappe.logger().info(f"Asset {doc.asset} remains operational (Minor severity)")


def restore_asset_status_on_verification(doc):
    """
    Restore asset status when inspector VERIFIES repair completion
    - Check if there are other open Major repairs
    - If none, restore asset to Submitted (operational)
    - If other Major repairs exist, keep asset Out of Order
    """
    print(f"\n🔧 ASSET RESTORE ON VERIFICATION")
    print(f"   Repair: {doc.name}")
    print(f"   Asset: {doc.asset}")
    print(f"   Verification Status: {doc.get('verification_status')}")

    if not doc.asset:
        print(f"   ⏭️  No asset - skipping")
        return

    # Only restore if verification passed
    if doc.get("verification_status") != "Verified - Passed":
        print(f"   ⏭️  Verification not passed - skipping")
        return

    asset_doc = frappe.get_doc("Asset", doc.asset)
    print(f"   Current asset status: {asset_doc.status}")

    # Check if there are OTHER open Major repairs for this asset
    other_major_repairs = frappe.db.count("Asset Repair", {
        "asset": doc.asset,
        "name": ["!=", doc.name],
        "issue_severity": "Major - Asset Must Stop",
        "workflow_state": ["not in", ["Finished", "Cancelled", "Rejected"]]
    })

    print(f"   Other open Major repairs: {other_major_repairs}")

    if other_major_repairs == 0:
        # No other major issues - safe to restore asset to operational
        if asset_doc.status == "Out of Order":
            asset_doc.status = "Submitted"
            asset_doc.add_comment("Comment",
                f"Asset restored to service - Inspector verified repair completion: {doc.description}")
            asset_doc.save(ignore_permissions=True)
            print(f"   ✅ Asset restored to Submitted")
            frappe.logger().info(f"Asset {doc.asset} restored to Submitted (inspector verified, no other major issues)")
        else:
            print(f"   ℹ️  Asset already operational")
    else:
        print(f"   ⚠️  Asset stays Out of Order - {other_major_repairs} major repair(s) still open")
        frappe.logger().info(f"Asset {doc.asset} remains Out of Order - {other_major_repairs} major repair(s) still open")


def restore_asset_status_on_finish(doc):
    """
    Restore asset status when repair is marked as Finished
    - Check if there are other open Major repairs
    - If none, restore asset to Submitted (operational)
    - If other Major repairs exist, keep asset Out of Order
    """
    print(f"\n🔧 ASSET RESTORE CALLED (Finished)")
    print(f"   Repair: {doc.name}")
    print(f"   Asset: {doc.asset}")
    print(f"   Severity: {doc.get('issue_severity')}")

    if not doc.asset:
        print(f"   ⏭️  No asset - skipping")
        return

    asset_doc = frappe.get_doc("Asset", doc.asset)
    print(f"   Current asset status: {asset_doc.status}")

    # Check if there are OTHER open Major repairs for this asset
    other_major_repairs = frappe.db.count("Asset Repair", {
        "asset": doc.asset,
        "name": ["!=", doc.name],
        "issue_severity": "Major - Asset Must Stop",
        "workflow_state": ["not in", ["Finished", "Cancelled", "Rejected"]]
    })

    print(f"   Other open Major repairs: {other_major_repairs}")

    if other_major_repairs == 0:
        # No other major issues - safe to restore asset to operational
        if asset_doc.status == "Out of Order":
            asset_doc.status = "Submitted"
            asset_doc.add_comment("Comment",
                f"Asset restored to service - Repair completed: {doc.description}")
            asset_doc.save(ignore_permissions=True)
            print(f"   ✅ Asset restored to Submitted")
            frappe.logger().info(f"Asset {doc.asset} restored to Submitted (repair finished, no other major issues)")
        else:
            print(f"   ℹ️  Asset already operational")
    else:
        print(f"   ⚠️  Asset stays Out of Order - {other_major_repairs} major repair(s) still open")
        frappe.logger().info(f"Asset {doc.asset} remains Out of Order - {other_major_repairs} major repair(s) still open")


def update_maintenance_log_on_rejection(doc):
    """
    Update Asset Maintenance Log when repair is rejected

    When manager rejects a repair, it means the issue was invalid/false alarm
    Update the corresponding maintenance log from "Planned" to "Completed"
    """
    print(f"\n🔄 UPDATE_MAINTENANCE_LOG_ON_REJECTION:")
    print(f"   Repair: {doc.name}")
    print(f"   Maintenance Task: {doc.get('maintenance_task')}")

    if not doc.get("maintenance_task"):
        print(f"   ⚠️  No maintenance_task linked to this repair, skipping log update")
        return

    # Find the maintenance log created when this issue was reported
    # Match by: asset + task name + status "Planned" + created around same time as repair
    logs = frappe.get_all("Asset Maintenance Log",
        filters={
            "asset_name": doc.asset,
            "maintenance_status": "Planned"
        },
        fields=["name", "task", "task_name", "creation"],
        order_by="creation desc",
        limit=10
    )

    # Find log that matches this repair's task
    matching_log = None
    for log in logs:
        task_field = log.get("task") or log.get("task_name") or ""
        if doc.get("maintenance_task") in task_field or task_field in doc.get("maintenance_task", ""):
            # Found matching log
            matching_log = log
            break

    if not matching_log:
        print(f"   ⚠️  No matching maintenance log found with status 'Planned'")
        return

    # Update log to "Completed" (issue was false alarm/rejected)
    print(f"   📝 Updating log {matching_log['name']} from Planned → Completed")
    frappe.db.set_value("Asset Maintenance Log", matching_log["name"], {
        "maintenance_status": "Completed",
        "completion_date": frappe.utils.nowdate()
    })
    frappe.db.commit()
    print(f"   ✅ Maintenance log updated successfully")


def notify_engineer_on_new_issue(doc):
    """Notify ONLY engineers when new issue is reported (NOT managers)"""
    asset_name = frappe.db.get_value("Asset", doc.asset, "asset_name") if doc.asset else "Unknown Asset"
    reporter = doc.get("reported_by") or "Unknown"

    # Get all users with Engineering Team role
    engineers = frappe.get_all("Has Role",
        filters={"role": "Engineering Team", "parenttype": "User"},
        fields=["parent"],
        pluck="parent"
    )

    # Get all manager users to EXCLUDE them
    managers = frappe.get_all("Has Role",
        filters={"role": ["in", ["Maintenance Manager", "Quality Manager"]], "parenttype": "User"},
        fields=["parent"],
        pluck="parent"
    )

    # Remove managers from engineer list (managers should NOT get engineer notifications)
    engineers = list(set(engineers) - set(managers))

    if not engineers:
        print(f"   ⚠️  No engineers found (excluding managers)")
        return

    print(f"   👥 Found {len(engineers)} engineer(s) (excluding managers): {engineers}")

    for engineer_email in engineers:
        # Check if notification already exists for this user and document
        existing = frappe.db.exists("Notification Log", {
            "for_user": engineer_email,
            "document_type": "Asset Repair",
            "document_name": doc.name,
            "subject": f"🔧 New Issue Reported: {asset_name}"
        })

        if existing:
            print(f"   ⏭️  Notification already exists for {engineer_email}, skipping")
            continue

        notification = frappe.new_doc("Notification Log")
        notification.subject = f"🔧 New Issue Reported: {asset_name}"
        notification.email_content = f"""
        <h3>New maintenance issue requires attention</h3>
        <p><strong>Asset:</strong> {asset_name}</p>
        <p><strong>Reported By:</strong> {reporter}</p>
        <p><strong>Issue:</strong> {doc.description or "No description"}</p>
        <p><strong>Date:</strong> {doc.failure_date}</p>
        <hr>
        <p><a href="/app/asset-repair/{doc.name}">View Issue</a></p>
        """
        notification.for_user = engineer_email
        notification.document_type = "Asset Repair"
        notification.document_name = doc.name
        notification.type = "Alert"
        notification.insert(ignore_permissions=True)

    print(f"   📧 New issue notification sent to {len(engineers)} engineer(s)")


def notify_manager_on_submit(doc):
    """Notify managers when engineer submits repair for approval"""
    asset_name = frappe.db.get_value("Asset", doc.asset, "asset_name") if doc.asset else "Unknown Asset"
    engineer = doc.get("owner") or "Unknown"

    # Get all users with Maintenance Manager role ONLY
    managers = frappe.get_all("Has Role",
        filters={"role": "Maintenance Manager", "parenttype": "User"},
        fields=["parent"],
        pluck="parent"
    )

    if not managers:
        print(f"   ⚠️  No managers found with 'Maintenance Manager' role")
        return

    managers = list(set(managers))  # Remove duplicates
    print(f"   👥 Found {len(managers)} Maintenance Manager(s): {managers}")

    notifications_sent = 0
    for manager_email in managers:
        print(f"   🔍 Checking notification for: {manager_email}")

        # Check if notification already exists for this user and document
        existing = frappe.db.exists("Notification Log", {
            "for_user": manager_email,
            "document_type": "Asset Repair",
            "document_name": doc.name,
            "subject": f"⏳ Repair Approval Needed: {asset_name}"
        })

        if existing:
            print(f"   ⏭️  Notification already exists for {manager_email} (ID: {existing}), skipping")
            continue

        print(f"   ✉️  Creating notification for {manager_email}...")
        notification = frappe.new_doc("Notification Log")
        notification.subject = f"⏳ Repair Approval Needed: {asset_name}"
        notification.email_content = f"""
        <h3>New repair request awaiting approval</h3>
        <p><strong>Asset:</strong> {asset_name}</p>
        <p><strong>Submitted By:</strong> {engineer}</p>
        <p><strong>Issue:</strong> {doc.description or "No description"}</p>
        <p><strong>Severity:</strong> {doc.get("issue_severity") or "Not specified"}</p>
        <hr>
        <p><a href="/app/asset-repair/{doc.name}">Review Request</a></p>
        """
        notification.for_user = manager_email
        notification.document_type = "Asset Repair"
        notification.document_name = doc.name
        notification.type = "Alert"
        notification.insert(ignore_permissions=True)
        notifications_sent += 1
        print(f"   ✅ Notification created: {notification.name}")

    print(f"   📧 Sent {notifications_sent} new notifications to managers")


def notify_engineer_on_approval(doc):
    """Notify engineer when manager approves repair

    Engineer = the person who submitted for approval (stored in _engineer_submitter field)
    NOT the document owner (who is the inspector who reported the issue)
    """
    # Get the engineer who submitted this for approval (stored in cache when workflow changed to Pending Approval)
    engineer_email = frappe.cache().get_value(f"engineer_submitter_{doc.name}")

    if not engineer_email:
        print(f"   ⚠️  No engineer_submitter found in cache for repair {doc.name}, trying fallback")
        # Fallback: Try to use owner if it's an engineer
        engineer_email = doc.get("owner")

        if not engineer_email or engineer_email == doc.get("reported_by"):
            # Get any user with Engineering Team role (excluding managers)
            engineers = frappe.get_all("Has Role",
                filters={"role": "Engineering Team", "parenttype": "User"},
                fields=["parent"],
                pluck="parent"
            )
            managers = frappe.get_all("Has Role",
                filters={"role": ["in", ["Maintenance Manager", "Quality Manager"]], "parenttype": "User"},
                fields=["parent"],
                pluck="parent"
            )
            engineers = list(set(engineers) - set(managers))

            if engineers:
                engineer_email = engineers[0]  # Pick first engineer as fallback
                print(f"   📧 Using fallback engineer: {engineer_email}")
            else:
                print(f"   ⚠️  No engineers found to notify")
                return
    else:
        print(f"   📧 Retrieved engineer submitter: {engineer_email}")

    asset_name = frappe.db.get_value("Asset", doc.asset, "asset_name") if doc.asset else "Unknown Asset"

    # Check if notification already exists
    existing = frappe.db.exists("Notification Log", {
        "for_user": engineer_email,
        "document_type": "Asset Repair",
        "document_name": doc.name,
        "subject": f"✅ Repair APPROVED: {asset_name}"
    })

    if existing:
        print(f"   ⏭️  Approval notification already exists for {engineer_email}, skipping")
        return

    notification = frappe.new_doc("Notification Log")
    notification.subject = f"✅ Repair APPROVED: {asset_name}"
    notification.email_content = f"""
    <h3 style="color: green;">Your repair request has been approved</h3>
    <p><strong>Asset:</strong> {asset_name}</p>
    <p><strong>Issue:</strong> {doc.description or "No description"}</p>
    <p><strong>Manager's Notes:</strong> {doc.get("approval_notes") or "No notes"}</p>
    <hr>
    <p>Please proceed with the repair. Mark as "Finished" when complete.</p>
    <p><a href="/app/asset-repair/{doc.name}">Open Repair</a></p>
    """
    notification.for_user = engineer_email
    notification.document_type = "Asset Repair"
    notification.document_name = doc.name
    notification.type = "Alert"
    notification.insert(ignore_permissions=True)

    print(f"   📧 Approval notification sent to {engineer_email}")


def notify_engineer_on_rejection(doc):
    """Notify engineer when manager rejects repair

    Engineer = the person who submitted for approval (stored in _engineer_submitter field)
    NOT the document owner (who is the inspector who reported the issue)
    """
    # Get the engineer who submitted this for approval (stored in cache when workflow changed to Pending Approval)
    engineer_email = frappe.cache().get_value(f"engineer_submitter_{doc.name}")

    if not engineer_email:
        print(f"   ⚠️  No engineer_submitter found in cache for repair {doc.name}, trying fallback")
        # Fallback: Try to use owner if it's an engineer
        engineer_email = doc.get("owner")

        if not engineer_email or engineer_email == doc.get("reported_by"):
            # Get any user with Engineering Team role (excluding managers)
            engineers = frappe.get_all("Has Role",
                filters={"role": "Engineering Team", "parenttype": "User"},
                fields=["parent"],
                pluck="parent"
            )
            managers = frappe.get_all("Has Role",
                filters={"role": ["in", ["Maintenance Manager", "Quality Manager"]], "parenttype": "User"},
                fields=["parent"],
                pluck="parent"
            )
            engineers = list(set(engineers) - set(managers))

            if engineers:
                engineer_email = engineers[0]  # Pick first engineer as fallback
                print(f"   📧 Using fallback engineer: {engineer_email}")
            else:
                print(f"   ⚠️  No engineers found to notify")
                return
    else:
        print(f"   📧 Retrieved engineer submitter: {engineer_email}")

    asset_name = frappe.db.get_value("Asset", doc.asset, "asset_name") if doc.asset else "Unknown Asset"

    # Check if notification already exists
    existing = frappe.db.exists("Notification Log", {
        "for_user": engineer_email,
        "document_type": "Asset Repair",
        "document_name": doc.name,
        "subject": f"❌ Repair REJECTED: {asset_name}"
    })

    if existing:
        print(f"   ⏭️  Rejection notification already exists for {engineer_email}, skipping")
        return

    notification = frappe.new_doc("Notification Log")
    notification.subject = f"❌ Repair REJECTED: {asset_name}"
    notification.email_content = f"""
    <h3 style="color: red;">Your repair request has been rejected</h3>
    <p><strong>Asset:</strong> {asset_name}</p>
    <p><strong>Issue:</strong> {doc.description or "No description"}</p>
    <p><strong>Manager's Reason:</strong> {doc.get("approval_notes") or "No reason provided"}</p>
    <hr>
    <p>Please review and resubmit if necessary.</p>
    <p><a href="/app/asset-repair/{doc.name}">Open Repair</a></p>
    """
    notification.for_user = engineer_email
    notification.document_type = "Asset Repair"
    notification.document_name = doc.name
    notification.type = "Alert"
    notification.insert(ignore_permissions=True)

    print(f"   📧 Rejection notification sent to {engineer_email}")


def notify_reporter_to_verify(doc):
    """
    Send notification to original reporter when repair is finished
    Reporter needs to scan asset QR and verify the fix is complete
    """
    if not doc.get("reported_by"):
        return

    reporter_email = doc.get("reported_by")
    asset_name = frappe.db.get_value("Asset", doc.asset, "asset_name") if doc.asset else "Unknown Asset"

    # Create notification
    notification = frappe.new_doc("Notification Log")
    notification.subject = f"Please verify repair completion: {asset_name}"
    notification.email_content = f"""
    <p>The repair you reported has been completed by the engineer.</p>
    <p><strong>Asset:</strong> {asset_name} ({doc.asset})</p>
    <p><strong>Issue:</strong> {doc.description or "No description"}</p>
    <p><strong>Action Required:</strong> Please scan the asset QR code and verify that the repair is satisfactory.</p>
    <p>Go to the Maintenance Portal and verify the repair.</p>
    """
    notification.for_user = reporter_email
    notification.document_type = "Asset Repair"
    notification.document_name = doc.name
    notification.type = "Alert"
    notification.insert(ignore_permissions=True)

    frappe.logger().info(f"Notified {reporter_email} to verify repair {doc.name}")
    print(f"   📧 Notification sent to {reporter_email}")
