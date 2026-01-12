"""
Implement the CORRECT workflow:
Draft → Supervisor Verify → Pending GM Approval Section 1
"""
import frappe

def implement():
    """Fix workflow to correct flow"""

    print("🔧 Implementing correct workflow...")

    workflow_name = 'Repair Approval WorkFlow'
    workflow = frappe.get_doc('Workflow', workflow_name)

    # 1. Remove "Submit" action from Draft
    # 2. Add "Supervisor Verify" action from Draft → GM Approval

    transitions_to_remove = []

    for trans in workflow.transitions:
        # Remove old "Submit" action
        if trans.state == "Draft" and trans.action == "Submit":
            transitions_to_remove.append(trans)
            print(f"🗑️  Removing: Draft → Submit")

        # Remove ALL transitions from "Pending Reporter Supervisor Verification" (first occurrence)
        if trans.state == "Pending Reporter Supervisor Verification" and trans.next_state in ["Pending GM Approval Section 1", "Rejected"]:
            transitions_to_remove.append(trans)
            print(f"🗑️  Removing: {trans.action} from Pending Reporter Supervisor Verification (first occurrence)")

    # Remove the transitions
    for trans in transitions_to_remove:
        workflow.transitions.remove(trans)

    # Add new transition: Draft → Supervisor Verify → GM Approval
    workflow.append('transitions', {
        'state': 'Draft',
        'action': 'Supervisor Verify',
        'next_state': 'Pending GM Approval Section 1',
        'allowed': 'Supervisor',
        'allow_self_approval': 0,
        'condition': None
    })
    print(f"✅ Added: Draft → Supervisor Verify → Pending GM Approval Section 1")

    # Update Draft state to allow Supervisor to edit
    for state in workflow.states:
        if state.state == "Draft":
            state.allow_edit = "Supervisor"
            print(f"✅ Updated Draft state: allow_edit = Supervisor")

    # Save workflow
    workflow.save(ignore_permissions=True)

    # Update Section 1B fields to show in Draft state
    if frappe.db.exists('Custom Field', 'Asset Repair-section_1b_break'):
        field = frappe.get_doc('Custom Field', 'Asset Repair-section_1b_break')
        field.depends_on = 'eval:doc.workflow_state=="Draft" && !doc.__islocal'
        field.hidden = 0
        field.save(ignore_permissions=True)
        print(f"✅ Section 1B visible in Draft state")

    if frappe.db.exists('Custom Field', 'Asset Repair-supervisor_section1_notes'):
        field = frappe.get_doc('Custom Field', 'Asset Repair-supervisor_section1_notes')
        field.depends_on = 'eval:doc.workflow_state=="Draft"'
        field.hidden = 0
        field.save(ignore_permissions=True)

    if frappe.db.exists('Custom Field', 'Asset Repair-supervisor_section1_signature'):
        field = frappe.get_doc('Custom Field', 'Asset Repair-supervisor_section1_signature')
        field.depends_on = 'eval:doc.workflow_state=="Draft"'
        field.hidden = 0
        field.save(ignore_permissions=True)

    frappe.db.commit()

    print()
    print("=" * 80)
    print("✅ CORRECT WORKFLOW IMPLEMENTED!")
    print()
    print("📋 WORKFLOW:")
    print("   1. Draft")
    print("      → Operator creates via portal")
    print("      → Supervisor opens, fills Section 1B, signs")
    print("      → Action: Supervisor Verify")
    print()
    print("   2. Pending GM Approval Section 1")
    print("      → GM Approve / GM Reject")
    print()
    print("   3. Pending Engineering Assessment → ...")
    print()
    print("🔄 MUST RUN:")
    print("   bench --site tub clear-cache")
    print("   Refresh browser")
    print("=" * 80)
