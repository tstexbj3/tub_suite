"""
Fix workflow actions - add condition to Supervisor Verify so it only shows at the end
"""
import frappe

def fix():
    """Add condition to Supervisor Verify transition"""

    print("🔧 Fixing workflow action buttons...")

    # Get the workflow
    workflow = frappe.get_doc('Workflow', 'Repair Approval WorkFlow')

    # Find the "Supervisor Verify" transition and add condition
    for transition in workflow.transitions:
        if transition.action == "Supervisor Verify" and transition.state == "Pending Reporter Supervisor Verification":
            # Add condition: only show when reporter has confirmed
            transition.condition = "doc.reporter_confirmed == 1"
            print(f"✅ Added condition to 'Supervisor Verify':")
            print(f"   Condition: doc.reporter_confirmed == 1")
            print(f"   This action will only show after reporter confirms")

    # Save the workflow
    workflow.save(ignore_permissions=True)
    frappe.db.commit()

    print()
    print("=" * 60)
    print("✅ Workflow actions fixed!")
    print()
    print("📋 Now in 'Pending Reporter Supervisor Verification':")
    print()
    print("   FIRST TIME (after Draft, reporter_confirmed=0):")
    print("      • Supervisor Approve → Goes to GM")
    print("      • Supervisor Reject → Rejected")
    print()
    print("   SECOND TIME (after repair, reporter_confirmed=1):")
    print("      • Supervisor Verify → Finished")
    print()
    print("🔄 Run: bench --site tub clear-cache")
    print("🔄 Then refresh browser")
    print("=" * 60)
