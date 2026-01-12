"""
Update the Supervisor Verify transition row with condition
"""
import frappe

def update():
    """Find and update the Supervisor Verify transition"""

    print("🔧 Updating Supervisor Verify transition...")

    # Get workflow directly from database
    workflow_name = 'Repair Approval WorkFlow'

    # Get all workflow transitions
    transitions = frappe.get_all('Workflow Transition',
        filters={
            'parent': workflow_name,
            'state': 'Pending Reporter Supervisor Verification',
            'action': 'Supervisor Verify'
        },
        fields=['name', 'action', 'state', 'next_state', 'condition'])

    if transitions:
        for trans in transitions:
            print(f"Found transition: {trans.name}")
            print(f"  Action: {trans.action}")
            print(f"  State: {trans.state}")
            print(f"  Next State: {trans.next_state}")
            print(f"  Current Condition: {trans.condition or 'None'}")

            # Update it
            doc = frappe.get_doc('Workflow Transition', trans.name)
            doc.condition = 'doc.reporter_confirmed == 1'
            doc.save(ignore_permissions=True)
            print(f"  ✅ Updated condition to: doc.reporter_confirmed == 1")
    else:
        print("❌ Supervisor Verify transition not found!")
        print("\nSearching all transitions from 'Pending Reporter Supervisor Verification':")

        all_trans = frappe.get_all('Workflow Transition',
            filters={
                'parent': workflow_name,
                'state': 'Pending Reporter Supervisor Verification'
            },
            fields=['name', 'action', 'next_state', 'condition'])

        for t in all_trans:
            print(f"  • {t.action} → {t.next_state} (condition: {t.condition or 'None'})")

    frappe.db.commit()

    print()
    print("=" * 60)
    print("✅ Workflow transition updated!")
    print("🔄 Run: bench --site tub clear-cache")
    print("🔄 Then refresh browser")
    print("=" * 60)
