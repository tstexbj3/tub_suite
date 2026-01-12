"""
Change workflow - Supervisor only verifies, GM/Manager approves/rejects
"""
import frappe

def change():
    """Update workflow transitions"""

    print("🔧 Changing Supervisor role to verify-only...")

    workflow_name = 'Repair Approval WorkFlow'

    # Find and update transitions from "Pending Reporter Supervisor Verification"
    transitions = frappe.get_all('Workflow Transition',
        filters={
            'parent': workflow_name,
            'state': 'Pending Reporter Supervisor Verification'
        },
        fields=['name', 'action', 'next_state', 'allowed'])

    print(f"\n📋 Current transitions from 'Pending Reporter Supervisor Verification':")
    for t in transitions:
        print(f"   • {t.action} → {t.next_state} (Allowed: {t.allowed})")

    # Delete Supervisor Approve and Supervisor Reject
    # Keep only Supervisor Verify → but make it go to GM Approval
    for t in transitions:
        doc = frappe.get_doc('Workflow Transition', t.name)

        if doc.action == "Supervisor Approve":
            # Change this to "Supervisor Verify" going to GM
            doc.action = "Supervisor Verify"
            doc.next_state = "Pending GM Approval Section 1"
            doc.condition = None  # No condition for first verification
            doc.save(ignore_permissions=True)
            print(f"\n✅ Changed 'Supervisor Approve' to 'Supervisor Verify'")
            print(f"   Next State: Pending GM Approval Section 1")

        elif doc.action == "Supervisor Reject":
            # Delete this transition
            doc.delete(ignore_permissions=True)
            print(f"\n🗑️  Deleted 'Supervisor Reject' (GM will reject, not supervisor)")

        elif doc.action == "Supervisor Verify" and doc.next_state == "Finished":
            # This is the SECOND supervisor verify (at the end)
            # Add condition so it only shows when reporter confirmed
            doc.condition = "doc.reporter_confirmed == 1"
            doc.save(ignore_permissions=True)
            print(f"\n✅ Updated second 'Supervisor Verify' (to Finished)")
            print(f"   Condition: doc.reporter_confirmed == 1")

    frappe.db.commit()

    print()
    print("=" * 60)
    print("✅ Workflow updated!")
    print()
    print("📋 New flow:")
    print("   1. Draft → Submit")
    print("   2. Pending Reporter Supervisor Verification")
    print("      → Supervisor Verify → Pending GM Approval Section 1")
    print("   3. Pending GM Approval Section 1")
    print("      → GM Approve / GM Reject (Maintenance Manager role)")
    print()
    print("🔄 Run: bench --site tub clear-cache")
    print("🔄 Then refresh browser")
    print("=" * 60)
