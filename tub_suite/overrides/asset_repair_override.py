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

    def before_save(self):
        """Auto-fill approval timestamp - NO super() call"""
        before_save_asset_repair(self, None)

    def before_submit(self):
        """Validate engineer signature"""
        super(CustomAssetRepair, self).before_submit()
        before_submit_asset_repair(self, None)


# Event Functions (also called by doc_events hooks)
def validate_asset_repair(doc, method):
    """Validate manager field restrictions"""
    # Allow free editing in Draft state
    workflow_state = doc.get("workflow_state")
    if not workflow_state or workflow_state == "Draft":
        return
    
    # Get user roles
    user_roles = frappe.get_roles()
    manager_roles = ["Manufacturing Manager", "Quality Manager"]
    is_manager = any(role in user_roles for role in manager_roles)
    
    # If not a manager, allow (engineers can't edit anyway due to permissions)
    if not is_manager:
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
            ["approval_notes", "approval_signature", "issue_severity"], as_dict=True)

        if old_doc:
            notes_changed = str(old_doc.get("approval_notes") or "") != str(doc.get("approval_notes") or "")
            signature_changed = str(old_doc.get("approval_signature") or "") != str(doc.get("approval_signature") or "")

            if (notes_changed or signature_changed) and not doc.get("approval_timestamp"):
                doc.approval_timestamp = now()

            # Handle asset status change when engineer sets severity
            severity_changed = str(old_doc.get("issue_severity") or "") != str(doc.get("issue_severity") or "")
            if severity_changed and doc.get("issue_severity"):
                update_asset_status_based_on_severity(doc)


def before_submit_asset_repair(doc, method):
    """Validate engineer signature before submission"""
    if not doc.get("engineer_signature"):
        frappe.throw(_("Engineer Signature is required before submission"), frappe.MandatoryError)


def on_update_after_submit_asset_repair(doc, method):
    """Allow workflow to update fields after submit"""
    # Set flag to bypass validation during workflow transitions
    doc.flags.ignore_validate_update_after_submit = True


def update_asset_status_based_on_severity(doc):
    """
    Update asset status based on issue severity set by engineer
    - Minor: Asset stays operational (In Service)
    - Major: Asset stops (Out of Order)
    """
    if not doc.asset:
        return

    severity = doc.get("issue_severity")
    asset_doc = frappe.get_doc("Asset", doc.asset)

    if severity == "Major - Asset Must Stop":
        if asset_doc.status != "Out of Order":
            asset_doc.status = "Out of Order"
            asset_doc.add_comment("Comment",
                f"Asset marked Out of Order by engineer due to Major severity issue: {doc.failure_description}")
            asset_doc.save(ignore_permissions=True)
            frappe.logger().info(f"Asset {doc.asset} status changed to Out of Order (Major severity)")

    elif severity == "Minor - Asset Operational":
        # Keep asset operational - do nothing or restore if needed
        # Asset status is NOT changed for minor issues
        frappe.logger().info(f"Asset {doc.asset} remains operational (Minor severity)")
