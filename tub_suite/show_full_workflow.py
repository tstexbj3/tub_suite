"""
Show the complete current workflow with all states and transitions
"""
import frappe

def show():
    """Display the complete workflow"""

    workflow = frappe.get_doc('Workflow', 'Repair Approval WorkFlow')

    print("=" * 80)
    print(f"WORKFLOW: {workflow.name}")
    print(f"Document Type: {workflow.document_type}")
    print(f"Active: {workflow.is_active}")
    print("=" * 80)

    # Show all states
    print("\n📋 WORKFLOW STATES:")
    print("-" * 80)
    for i, state in enumerate(workflow.states, 1):
        print(f"{i:2}. {state.state:50} | Allow Edit: {state.allow_edit:25} | Docstatus: {state.doc_status}")

    # Show all transitions grouped by state
    print("\n\n🔄 WORKFLOW TRANSITIONS:")
    print("-" * 80)

    # Group transitions by state
    from collections import defaultdict
    transitions_by_state = defaultdict(list)

    for trans in workflow.transitions:
        transitions_by_state[trans.state].append(trans)

    # Show in order of states
    for state in workflow.states:
        state_name = state.state
        if state_name in transitions_by_state:
            print(f"\n📍 FROM: {state_name}")

            for trans in transitions_by_state[state_name]:
                condition = f" (IF: {trans.condition})" if trans.condition else ""
                print(f"   ✅ {trans.action:35} → {trans.next_state:40} | Allowed: {trans.allowed}{condition}")

    print("\n" + "=" * 80)
    print("\n📊 SUMMARY:")
    print(f"   Total States: {len(workflow.states)}")
    print(f"   Total Transitions: {len(workflow.transitions)}")
    print("=" * 80)
