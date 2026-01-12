"""
Fix workflow - remove supervisor verification at beginning
Draft should go DIRECTLY to GM Approval Section 1
"""
import frappe

def fix():
    """Remove supervisor step at beginning, go straight to GM"""

    print("🔧 Removing supervisor verification from Section 1...")

    workflow_name = 'Repair Approval WorkFlow'
    workflow = frappe.get_doc('Workflow', workflow_name)

    # 1. Change "Submit" action to go directly to GM Approval
    for trans in workflow.transitions:
        if trans.state == "Draft" and trans.action == "Submit":
            old_next = trans.next_state
            trans.next_state = "Pending GM Approval Section 1"
            print(f"✅ Changed Submit: Draft → {trans.next_state} (was: {old_next})")

    # 2. Delete ALL transitions from "Pending Reporter Supervisor Verification" (first occurrence)
    to_delete = []
    for trans in workflow.transitions:
        if trans.state == "Pending Reporter Supervisor Verification":
            # Check if this is the FIRST occurrence (going to GM/Rejected)
            # or SECOND occurrence (going to Finished)
            if trans.next_state in ["Pending GM Approval Section 1", "Rejected"]:
                to_delete.append(trans)
                print(f"🗑️  Will delete: {trans.action} (first supervisor verification)")

    # Delete the transitions
    for trans in to_delete:
        workflow.transitions.remove(trans)

    # 3. Keep only the SECOND "Pending Reporter Supervisor Verification"
    # (after reporter confirms, supervisor fills hygiene section)

    # Save workflow
    workflow.save(ignore_permissions=True)

    # 4. Hide Section 1B (supervisor verification section) completely
    if frappe.db.exists('Custom Field', 'Asset Repair-section_1b_break'):
        field = frappe.get_doc('Custom Field', 'Asset Repair-section_1b_break')
        field.hidden = 1
        field.save(ignore_permissions=True)
        print(f"🙈 Hidden: section_1b_break")

    if frappe.db.exists('Custom Field', 'Asset Repair-supervisor_section1_notes'):
        field = frappe.get_doc('Custom Field', 'Asset Repair-supervisor_section1_notes')
        field.hidden = 1
        field.save(ignore_permissions=True)
        print(f"🙈 Hidden: supervisor_section1_notes")

    if frappe.db.exists('Custom Field', 'Asset Repair-supervisor_section1_signature'):
        field = frappe.get_doc('Custom Field', 'Asset Repair-supervisor_section1_signature')
        field.hidden = 1
        field.save(ignore_permissions=True)
        print(f"🙈 Hidden: supervisor_section1_signature")

    frappe.db.commit()

    print()
    print("=" * 80)
    print("✅ Workflow fixed!")
    print()
    print("📋 NEW FLOW:")
    print("   1. Draft → Submit")
    print("   2. Pending GM Approval Section 1")
    print("      → GM Approve / GM Reject (Maintenance Manager)")
    print("   3. Pending Engineering Assessment")
    print("   4. Pending Engineering Supervisor Review")
    print("   5. Pending GM Final Approval")
    print("   6. Approved for Repair")
    print("   7. Repair In Progress")
    print("   8. Pending Reporter Confirmation")
    print("   9. Pending Reporter Supervisor Verification (hygiene check)")
    print("      → Supervisor Verify")
    print("   10. Finished")
    print()
    print("🔄 Run: bench --site tub clear-cache")
    print("🔄 Then refresh browser")
    print("=" * 80)
