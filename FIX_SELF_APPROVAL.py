import frappe
import os
os.chdir('/home/user/frappe-bench/sites')
frappe.init(site='tub')
frappe.connect()

# Get the workflow
workflow = frappe.get_doc('Workflow', 'Asset Repair Workflow - Supervisor Only')

# Find the Reporter Confirm transition
for transition in workflow.transitions:
    if transition.state == 'Pending Reporter Confirmation' and transition.action == 'Reporter Confirm':
        print(f"Current allow_self_approval: {transition.allow_self_approval}")
        transition.allow_self_approval = 1  # Allow self-approval
        print(f"Updated to: {transition.allow_self_approval}")

workflow.save()
frappe.db.commit()

print("✅ Updated Reporter Confirm transition to allow self-approval")
