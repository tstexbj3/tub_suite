"""
Custom Asset Repair Controller Override
This overrides ERPNext's Asset Repair to add field locking security
"""

import frappe
from frappe import _
from erpnext.assets.doctype.asset_repair.asset_repair import AssetRepair


class CustomAssetRepair(AssetRepair):
    """Custom Asset Repair with field locking after submission"""

    def validate_update_after_submit(self):
        """
        Override to lock all fields except approval_status after submission
        This runs when editing submitted documents
        """
        # Call parent validation first
        super(CustomAssetRepair, self).validate_update_after_submit()

        # Get original document from database
        old_doc = frappe.db.get_value("Asset Repair", self.name, "*", as_dict=True)
        if not old_doc:
            return

        # Check if approval status changed
        approval_status_changed = (self.get('approval_status') != old_doc.get('approval_status'))

        # Fields that CANNOT be changed after submission
        protected_fields = [
            'asset', 'asset_name', 'failure_date', 'description',
            'repair_status', 'completion_date', 'repair_cost',
            'actions_performed', 'stock_consumption', 'capitalize_repair_cost',
            'increase_in_asset_life', 'company', 'cost_center',
            'project', 'purchase_invoice', 'total_repair_cost',
            'downtime', 'naming_series'
        ]

        # Check if any protected field was modified
        for field in protected_fields:
            old_value = old_doc.get(field)
            new_value = self.get(field)

            if str(old_value or '') != str(new_value or ''):
                frappe.throw(
                    _("Cannot modify {0} after submission. This repair request is locked.").format(
                        frappe.bold(field.replace('_', ' ').title())
                    ),
                    frappe.PermissionError
                )

        # Auto-fill approval fields when status changes to Approved/Rejected
        if approval_status_changed and self.approval_status in ['Approved', 'Rejected']:
            self.approved_by = frappe.session.user
            self.approval_time = frappe.utils.now()
        else:
            # If approval status didn't change, don't allow manual modification of approval fields
            if self.get('approval_time') != old_doc.get('approval_time'):
                frappe.throw(
                    _("Approval Date & Time is automatically set by the system and cannot be modified manually."),
                    frappe.PermissionError
                )

            if self.get('approved_by') != old_doc.get('approved_by'):
                frappe.throw(
                    _("Approved By is automatically set by the system and cannot be modified manually."),
                    frappe.PermissionError
                )


# Override the default AssetRepair class
def get_asset_repair_class():
    """Return custom Asset Repair class"""
    return CustomAssetRepair
