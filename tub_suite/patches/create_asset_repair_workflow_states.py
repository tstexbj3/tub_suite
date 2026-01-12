"""
Create workflow states for Asset Repair workflow
This patch ensures all required workflow states exist before the workflow is used
"""

import frappe


def execute():
    """Create all workflow states needed for Asset Repair workflow"""

    workflow_states = [
        "Draft",
        "Pending Reporter Confirmation",
        "Pending Reporter Supervisor Verification",
        "Pending GM Approval Section 1",
        "Pending Engineering Assessment",
        "Pending Engineering Supervisor Review",
        "Pending GM Final Approval",
        "Approved for Repair",
        "Repair In Progress",
        "Finished",
        "Rejected",
        "Cancelled"
    ]

    for state_name in workflow_states:
        if not frappe.db.exists('Workflow State', state_name):
            doc = frappe.get_doc({
                'doctype': 'Workflow State',
                'workflow_state_name': state_name,
                'style': 'Primary'
            })
            doc.insert(ignore_permissions=True)
            print(f"Created Workflow State: {state_name}")
        else:
            print(f"Workflow State already exists: {state_name}")

    frappe.db.commit()
