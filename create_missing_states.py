"""Create missing workflow states for Asset Repair workflow"""
import frappe

def create_states():
    """Create all missing workflow states"""

    # List of all workflow states needed
    states_to_create = [
        "Pending GM Approval Section 1",
        "Pending Engineering Assessment",
        "Pending Engineering Supervisor Review",
        "Pending GM Final Approval",
        "Approved for Repair",
        "Repair In Progress",
        "Rejected",
        "Cancelled"
    ]

    created = []
    skipped = []

    for state_name in states_to_create:
        if frappe.db.exists('Workflow State', state_name):
            skipped.append(state_name)
            print(f"⏭️  Skipped (already exists): {state_name}")
        else:
            doc = frappe.get_doc({
                'doctype': 'Workflow State',
                'workflow_state_name': state_name,
                'style': 'Primary'
            })
            doc.insert(ignore_permissions=True)
            created.append(state_name)
            print(f"✅ Created: {state_name}")

    frappe.db.commit()

    print(f"\n📊 Summary:")
    print(f"   Created: {len(created)} states")
    print(f"   Skipped: {len(skipped)} states (already existed)")
    print(f"\n✅ Done! All workflow states are now in the database.")

    return {
        'created': created,
        'skipped': skipped
    }
