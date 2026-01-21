#!/usr/bin/env python3
"""Add 'Pending Reporter Confirmation' state to Asset Repair workflow"""

import frappe
import os
os.chdir('/home/user/frappe-bench/sites')
frappe.init(site='tub')
frappe.connect()

# First, create the workflow action if it doesn't exist
if not frappe.db.exists('Workflow Action Master', 'Reporter Confirm'):
    action = frappe.get_doc({
        'doctype': 'Workflow Action Master',
        'workflow_action_name': 'Reporter Confirm'
    })
    action.insert()
    frappe.db.commit()
    print("✅ Created Workflow Action: Reporter Confirm")
else:
    print("⚠️  Workflow Action 'Reporter Confirm' already exists")

# Get the workflow
workflow = frappe.get_doc('Workflow', 'Asset Repair Workflow - Supervisor Only')

# Check if state already exists
existing_states = [s.state for s in workflow.states]
if 'Pending Reporter Confirmation' in existing_states:
    print("⚠️  State 'Pending Reporter Confirmation' already exists")
else:
    # Add new state after Pending Supervisor Verification
    # Find position to insert (after Pending Supervisor Verification)
    insert_pos = None
    for i, state in enumerate(workflow.states):
        if state.state == 'Pending Supervisor Verification':
            insert_pos = i + 1
            break
    
    new_state = workflow.append('states', {})
    new_state.state = 'Pending Reporter Confirmation'
    new_state.doc_status = '1'
    new_state.allow_edit = 'Supervisor'
    new_state.is_optional_state = 0
    new_state.message = 'Awaiting reporter confirmation from portal'
    
    print("✅ Added 'Pending Reporter Confirmation' state")

# Update transition: Pending Supervisor Verification → Pending Reporter Confirmation
for transition in workflow.transitions:
    if transition.state == 'Pending Supervisor Verification' and transition.action == 'Supervisor Verify':
        old_next = transition.next_state
        transition.next_state = 'Pending Reporter Confirmation'
        print(f"✅ Updated transition: Supervisor Verify now goes to 'Pending Reporter Confirmation' (was {old_next})")

# Add new transition: Pending Reporter Confirmation → Finished
existing_transitions = [(t.state, t.action, t.next_state) for t in workflow.transitions]
if ('Pending Reporter Confirmation', 'Reporter Confirm', 'Finished') not in existing_transitions:
    new_transition = workflow.append('transitions', {})
    new_transition.state = 'Pending Reporter Confirmation'
    new_transition.action = 'Reporter Confirm'
    new_transition.next_state = 'Finished'
    new_transition.allowed = 'Supervisor'
    new_transition.allow_self_approval = 0
    print("✅ Added transition: Reporter Confirm (Pending Reporter Confirmation → Finished)")

# Save workflow
workflow.save()
frappe.db.commit()

print("\n✅ Workflow updated successfully!")
print("New flow: Pending Supervisor Verification → Supervisor Verify → Pending Reporter Confirmation → Reporter Confirm → Finished")
