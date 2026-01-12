#!/usr/bin/env python3
"""
Fix Asset Repair Workflow - Final Version
Run: bench --site tub execute tub_suite.fix_workflow_final.fix
"""

import frappe

def fix():
    """Fix workflow transition: Draft → Supervisor Verify → Pending GM Approval Section 1"""

    print("\n🔧 Fixing Asset Repair Workflow...")

    try:
        workflow = frappe.get_doc("Workflow", "Repair Approval WorkFlow")

        # Find and remove the wrong "Submit" transition from Draft
        transitions_to_remove = []
        for idx, transition in enumerate(workflow.transitions):
            if transition.state == "Draft" and transition.action == "Submit":
                print(f"❌ Removing: Draft → Submit → {transition.next_state}")
                transitions_to_remove.append(idx)

        # Remove in reverse order to maintain indices
        for idx in reversed(transitions_to_remove):
            workflow.transitions.pop(idx)

        # Check if "Supervisor Verify" transition already exists
        supervisor_verify_exists = False
        for transition in workflow.transitions:
            if transition.state == "Draft" and transition.action == "Supervisor Verify":
                # Update it to correct next_state
                print(f"✏️  Updating: Draft → Supervisor Verify")
                print(f"   Old next_state: {transition.next_state}")
                transition.next_state = "Pending GM Approval Section 1"
                transition.allowed = "Supervisor"
                print(f"   New next_state: {transition.next_state}")
                supervisor_verify_exists = True
                break

        # Add "Supervisor Verify" transition if it doesn't exist
        if not supervisor_verify_exists:
            print("✅ Adding: Draft → Supervisor Verify → Pending GM Approval Section 1")
            workflow.append("transitions", {
                "state": "Draft",
                "action": "Supervisor Verify",
                "next_state": "Pending GM Approval Section 1",
                "allowed": "Supervisor",
                "allow_self_approval": 0
            })

        # Update Draft state to allow Supervisor to edit
        for state in workflow.states:
            if state.state == "Draft":
                print(f"✅ Updated Draft state: allow_edit = Supervisor")
                state.allow_edit = "Supervisor"
                break

        # Save workflow
        workflow.flags.ignore_links = True  # Ignore validation errors
        workflow.save(ignore_permissions=True)
        frappe.db.commit()

        print("\n✅ Workflow fixed successfully!")
        print("\n📋 Current Draft transitions:")
        workflow.reload()
        for transition in workflow.transitions:
            if transition.state == "Draft":
                print(f"   {transition.action} → {transition.next_state} (Allowed: {transition.allowed})")

        return "Success"

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        frappe.db.rollback()
        return f"Error: {str(e)}"

if __name__ == "__main__":
    fix()
