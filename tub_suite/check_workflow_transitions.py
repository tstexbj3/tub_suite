"""Check what workflow transitions are actually in the database"""
import frappe

def check():
    workflow = frappe.get_doc('Workflow', 'Repair Approval WorkFlow')
    print('=' * 60)
    print('Transitions from "Pending Reporter Supervisor Verification":')
    print('=' * 60)
    for t in workflow.transitions:
        if t.state == 'Pending Reporter Supervisor Verification':
            print(f'\nAction: {t.action}')
            print(f'  Next State: {t.next_state}')
            print(f'  Condition: {t.condition or "None"}')
            print(f'  Allowed: {t.allowed}')
    print('=' * 60)
