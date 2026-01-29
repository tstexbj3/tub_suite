"""
Patch: Update Asset Repair field visibility to match DEV database

This patch updates depends_on conditions for Custom Fields that were not syncing
via fixtures due to timestamp conflicts.

Fields updated:
- final_remarks: Only show in Finished state
- section_3b_break: Show in Pending Supervisor Verification and Finished states
"""

import frappe


def execute():
    """Update Custom Field depends_on values"""

    updates = [
        {
            "name": "Asset Repair-final_remarks",
            "depends_on": 'eval:doc.workflow_state=="Finished"',
            "label": "final_remarks"
        },
        {
            "name": "Asset Repair-section_3b_break",
            "depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"',
            "label": "section_3b_break"
        }
    ]

    for field_data in updates:
        if frappe.db.exists("Custom Field", field_data["name"]):
            doc = frappe.get_doc("Custom Field", field_data["name"])
            doc.depends_on = field_data["depends_on"]
            doc.flags.ignore_validate = True
            doc.save(ignore_permissions=True)
            print(f"✓ Updated {field_data['label']}")
        else:
            print(f"⚠ Custom Field {field_data['name']} not found")

    frappe.db.commit()
    print("✓ Asset Repair field visibility updated successfully")
