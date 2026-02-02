import frappe

def execute():
    """
    v2.1.24: Remove duplicate workflow transitions from Pending Supervisor Verification

    Issue: All 4 action buttons showing (Supervisor Verify, Supervisor Reject, PM Supervisor Verify, PM Supervisor Reject)
    Expected: Only PM buttons should show for PM repairs, only regular buttons for non-PM repairs

    Root Cause: Duplicate transitions without conditions allow Maintenance Supervisor to use
    regular "Supervisor Verify" and "Supervisor Reject" on ALL repairs including PM ones.

    Fix: Remove the unconditional duplicate transitions for Maintenance Supervisor role.
    """

    workflow = frappe.get_doc('Workflow', 'Asset Repair Workflow - Supervisor Only')

    # Find duplicate transitions to remove
    transitions_to_remove = []

    for i, transition in enumerate(workflow.transitions):
        if (transition.state == 'Pending Supervisor Verification' and
            transition.allowed == 'Maintenance Supervisor' and
            transition.action in ['Supervisor Verify', 'Supervisor Reject'] and
            not transition.condition):
            # This is a duplicate without condition - mark for removal
            transitions_to_remove.append(i)
            print(f'Found duplicate to remove: Action="{transition.action}", Allowed="Maintenance Supervisor", Condition=None')

    # Remove in reverse order to maintain indices
    for i in reversed(transitions_to_remove):
        removed = workflow.transitions.pop(i)
        print(f'Removed: {removed.action} (Maintenance Supervisor, no condition)')

    # Save workflow
    workflow.save(ignore_permissions=True)

    print(f'\nRemoved {len(transitions_to_remove)} duplicate transitions')
    print('\nRemaining transitions from "Pending Supervisor Verification":')

    remaining = [t for t in workflow.transitions if t.state == 'Pending Supervisor Verification']
    for t in remaining:
        print(f'  - {t.action} ({t.allowed}) -> {t.next_state}')
        if t.condition:
            print(f'    Condition: {t.condition}')

    print(f'\nTotal remaining: {len(remaining)}')
    print('\nExpected result:')
    print('  - For PM repairs: Only "PM Supervisor Verify" and "PM Supervisor Reject" buttons')
    print('  - For non-PM repairs: Only "Supervisor Verify" and "Supervisor Reject" buttons')
