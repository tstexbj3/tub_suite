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
        """Auto-fill approval timestamp - NO super() call"""
        before_save_asset_repair(self, None)

    def before_submit(self):
        """Validate engineer signature"""
        super(CustomAssetRepair, self).before_submit()
        before_submit_asset_repair(self, None)

    def on_update_after_submit(self):
        """Handle workflow transitions after submit - CRITICAL for asset status management"""
        # Note: Parent class may not have this method, so we don't call super()

        # Check if workflow state or verification changed
        if not self.is_new():
            old_doc = frappe.db.get_value("Asset Repair", self.name,
                ["workflow_state", "verification_status"], as_dict=True)

            if old_doc:
                old_workflow = old_doc.get("workflow_state")
                new_workflow = self.get("workflow_state")
                old_verification = old_doc.get("verification_status")
                new_verification = self.get("verification_status")

                # Handle Approved → Set asset Out of Order (if Major)
                if old_workflow != new_workflow and new_workflow == "Approved":
                    update_asset_status_on_approval(self)

                # Handle Job Finished → Auto-fill completion date + Notify reporter
                if old_workflow != new_workflow and new_workflow == "Finished":
                    # Set completion date when engineer finishes job
                    if not self.get("completion_date"):
                        frappe.db.set_value("Asset Repair", self.name, "completion_date", frappe.utils.now())
                        frappe.db.set_value("Asset Repair", self.name, "repair_status", "Completed")
                        frappe.db.commit()
                    notify_reporter_to_verify(self)

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

    # Get user roles
    user_roles = frappe.get_roles()
    manager_roles = ["Maintenance Manager", "Quality Manager"]
    inspector_roles = ["Maintenance User"]
    engineer_roles = ["Engineering Team"]
    is_manager = any(role in user_roles for role in manager_roles)
    is_inspector = any(role in user_roles for role in inspector_roles)
    is_engineer = any(role in user_roles for role in engineer_roles)

    # Allow free editing in Draft state ONLY for engineers and managers
    if not workflow_state or workflow_state == "Draft":
        # Maintenance Users should NOT access ERPNext desk at all
        # They only use mobile portal
        return

    # After Draft: Lock ALL fields for engineers
    if not is_manager:
        # Engineers cannot edit anything after submitting for approval
        if not doc.is_new():
            old_doc = frappe.db.get_value("Asset Repair", doc.name, "*", as_dict=True)
            if old_doc:
                # Check if any field changed (except system fields)
                ignored_fields = ["_user_tags", "_comments", "_assign", "_liked_by", "modified", "modified_by",
                                 "docstatus", "workflow_state", "repair_status", "completion_date"]
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
    """Auto-fill approval timestamp and handle asset status based on severity"""
    if not doc.is_new():
        old_doc = frappe.db.get_value("Asset Repair", doc.name,
            ["approval_notes", "approval_signature", "approval_timestamp", "issue_severity", "workflow_state"], as_dict=True)

        if old_doc:
            notes_changed = str(old_doc.get("approval_notes") or "") != str(doc.get("approval_notes") or "")
            signature_changed = str(old_doc.get("approval_signature") or "") != str(doc.get("approval_signature") or "")

            if (notes_changed or signature_changed) and not doc.get("approval_timestamp"):
                doc.approval_timestamp = now()

            # Handle asset status change when workflow changes
            workflow_changed = str(old_doc.get("workflow_state") or "") != str(doc.get("workflow_state") or "")

            if workflow_changed:
                if doc.get("workflow_state") == "Approved":
                    update_asset_status_on_approval(doc)
                elif doc.get("workflow_state") == "Finished":
                    restore_asset_status_on_finish(doc)


def before_submit_asset_repair(doc, method):
    """Validate engineer signature before submission"""
    if not doc.get("engineer_signature"):
        frappe.throw(_("Engineer Signature is required before submission"), frappe.MandatoryError)


def on_update_after_submit_asset_repair(doc, method):
    """Handle workflow transitions after submit (Approved → Finished)"""
    # Set flag to bypass validation during workflow transitions
    doc.flags.ignore_validate_update_after_submit = True

    print(f"\n🔄 ON_UPDATE_AFTER_SUBMIT CALLED:")
    print(f"   Repair: {doc.name}")
    print(f"   Current workflow_state: {doc.get('workflow_state')}")

    # Check if workflow state is Finished - restore asset
    if doc.get("workflow_state") == "Finished":
        print(f"   ✅ State is Finished - restoring asset")
        restore_asset_status_on_finish(doc)
    else:
        print(f"   ⏭️  State is {doc.get('workflow_state')} - no restore")


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
