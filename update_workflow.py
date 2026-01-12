#!/usr/bin/env python3
import json

# Read existing workflow.json
with open('tub_suite/fixtures/workflow.json', 'r', encoding='utf-8') as f:
    workflows = json.load(f)

# Find Asset Repair workflow index
asset_repair_idx = None
for i, wf in enumerate(workflows):
    if wf.get('document_type') == 'Asset Repair':
        asset_repair_idx = i
        break

if asset_repair_idx is None:
    print('ERROR: Asset Repair workflow not found')
    exit(1)

print(f'Found Asset Repair workflow at index {asset_repair_idx}')

# Create new FM-EN-04 workflow with 11 states
new_workflow = {
    'docstatus': 0,
    'doctype': 'Workflow',
    'document_type': 'Asset Repair',
    'is_active': 1,
    'modified': '2026-01-08 20:00:00.000000',
    'name': 'Repair Approval WorkFlow',
    'override_status': 0,
    'send_email_alert': 0,
    'states': [
        {
            'allow_edit': 'All',
            'avoid_status_override': 0,
            'doc_status': '0',
            'is_optional_state': 0,
            'message': None,
            'next_action_email_template': None,
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'states',
            'parenttype': 'Workflow',
            'send_email': 1,
            'state': 'Draft',
            'update_field': 'repair_status',
            'update_value': 'Pending',
            'workflow_builder_id': None
        },
        {
            'allow_edit': 'Supervisor',
            'avoid_status_override': 0,
            'doc_status': '0',
            'is_optional_state': 0,
            'message': None,
            'next_action_email_template': None,
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'states',
            'parenttype': 'Workflow',
            'send_email': 1,
            'state': 'Pending Reporter Supervisor Approval',
            'update_field': 'repair_status',
            'update_value': 'Pending',
            'workflow_builder_id': None
        },
        {
            'allow_edit': 'Maintenance Manager',
            'avoid_status_override': 0,
            'doc_status': '0',
            'is_optional_state': 0,
            'message': None,
            'next_action_email_template': None,
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'states',
            'parenttype': 'Workflow',
            'send_email': 1,
            'state': 'Pending GM Approval Section 1',
            'update_field': 'repair_status',
            'update_value': 'Pending',
            'workflow_builder_id': None
        },
        {
            'allow_edit': 'Engineering Team',
            'avoid_status_override': 0,
            'doc_status': '0',
            'is_optional_state': 0,
            'message': None,
            'next_action_email_template': None,
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'states',
            'parenttype': 'Workflow',
            'send_email': 1,
            'state': 'Pending Engineering Assessment',
            'update_field': 'repair_status',
            'update_value': 'Pending',
            'workflow_builder_id': None
        },
        {
            'allow_edit': 'Engineering Supervisor',
            'avoid_status_override': 0,
            'doc_status': '0',
            'is_optional_state': 0,
            'message': None,
            'next_action_email_template': None,
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'states',
            'parenttype': 'Workflow',
            'send_email': 1,
            'state': 'Pending Engineering Supervisor Review',
            'update_field': 'repair_status',
            'update_value': 'Pending',
            'workflow_builder_id': None
        },
        {
            'allow_edit': 'Maintenance Manager',
            'avoid_status_override': 0,
            'doc_status': '0',
            'is_optional_state': 0,
            'message': None,
            'next_action_email_template': None,
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'states',
            'parenttype': 'Workflow',
            'send_email': 1,
            'state': 'Pending GM Final Approval',
            'update_field': 'repair_status',
            'update_value': 'Pending',
            'workflow_builder_id': None
        },
        {
            'allow_edit': 'Engineering Team',
            'avoid_status_override': 0,
            'doc_status': '0',
            'is_optional_state': 0,
            'message': None,
            'next_action_email_template': None,
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'states',
            'parenttype': 'Workflow',
            'send_email': 1,
            'state': 'Approved for Repair',
            'update_field': 'repair_status',
            'update_value': 'Under Repair',
            'workflow_builder_id': None
        },
        {
            'allow_edit': 'Engineering Team',
            'avoid_status_override': 0,
            'doc_status': '0',
            'is_optional_state': 0,
            'message': None,
            'next_action_email_template': None,
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'states',
            'parenttype': 'Workflow',
            'send_email': 1,
            'state': 'Repair In Progress',
            'update_field': 'repair_status',
            'update_value': 'Under Repair',
            'workflow_builder_id': None
        },
        {
            'allow_edit': 'Supervisor',
            'avoid_status_override': 0,
            'doc_status': '0',
            'is_optional_state': 0,
            'message': None,
            'next_action_email_template': None,
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'states',
            'parenttype': 'Workflow',
            'send_email': 1,
            'state': 'Pending Reporter Supervisor Verification',
            'update_field': 'repair_status',
            'update_value': 'Under Repair',
            'workflow_builder_id': None
        },
        {
            'allow_edit': 'All',
            'avoid_status_override': 0,
            'doc_status': '0',
            'is_optional_state': 0,
            'message': None,
            'next_action_email_template': None,
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'states',
            'parenttype': 'Workflow',
            'send_email': 1,
            'state': 'Pending Reporter Confirmation',
            'update_field': 'repair_status',
            'update_value': 'Under Repair',
            'workflow_builder_id': None
        },
        {
            'allow_edit': 'Maintenance Manager',
            'avoid_status_override': 0,
            'doc_status': '1',
            'is_optional_state': 0,
            'message': None,
            'next_action_email_template': None,
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'states',
            'parenttype': 'Workflow',
            'send_email': 1,
            'state': 'Finished',
            'update_field': 'repair_status',
            'update_value': 'Completed',
            'workflow_builder_id': None
        },
        {
            'allow_edit': 'Maintenance Manager',
            'avoid_status_override': 0,
            'doc_status': '0',
            'is_optional_state': 0,
            'message': None,
            'next_action_email_template': None,
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'states',
            'parenttype': 'Workflow',
            'send_email': 1,
            'state': 'Rejected',
            'update_field': 'repair_status',
            'update_value': 'Pending',
            'workflow_builder_id': None
        },
        {
            'allow_edit': 'System Manager',
            'avoid_status_override': 0,
            'doc_status': '2',
            'is_optional_state': 0,
            'message': None,
            'next_action_email_template': None,
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'states',
            'parenttype': 'Workflow',
            'send_email': 1,
            'state': 'Cancelled',
            'update_field': 'repair_status',
            'update_value': 'Cancelled',
            'workflow_builder_id': None
        }
    ],
    'transitions': [
        # Draft -> Reporter Supervisor Approval
        {
            'action': 'Submit',
            'allow_self_approval': 0,
            'allowed': 'All',
            'condition': None,
            'next_state': 'Pending Reporter Supervisor Approval',
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'transitions',
            'parenttype': 'Workflow',
            'send_email_to_creator': 0,
            'state': 'Draft',
            'workflow_builder_id': None
        },
        # Reporter Supervisor -> GM Section 1 Approval
        {
            'action': 'Supervisor Approve',
            'allow_self_approval': 0,
            'allowed': 'Supervisor',
            'condition': None,
            'next_state': 'Pending GM Approval Section 1',
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'transitions',
            'parenttype': 'Workflow',
            'send_email_to_creator': 0,
            'state': 'Pending Reporter Supervisor Approval',
            'workflow_builder_id': None
        },
        # Reporter Supervisor -> Rejected
        {
            'action': 'Supervisor Reject',
            'allow_self_approval': 0,
            'allowed': 'Supervisor',
            'condition': None,
            'next_state': 'Rejected',
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'transitions',
            'parenttype': 'Workflow',
            'send_email_to_creator': 0,
            'state': 'Pending Reporter Supervisor Approval',
            'workflow_builder_id': None
        },
        # GM Section 1 -> Engineering Assessment
        {
            'action': 'GM Approve Section 1',
            'allow_self_approval': 0,
            'allowed': 'Maintenance Manager',
            'condition': None,
            'next_state': 'Pending Engineering Assessment',
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'transitions',
            'parenttype': 'Workflow',
            'send_email_to_creator': 0,
            'state': 'Pending GM Approval Section 1',
            'workflow_builder_id': None
        },
        # GM Section 1 -> Rejected
        {
            'action': 'GM Reject',
            'allow_self_approval': 0,
            'allowed': 'Maintenance Manager',
            'condition': None,
            'next_state': 'Rejected',
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'transitions',
            'parenttype': 'Workflow',
            'send_email_to_creator': 0,
            'state': 'Pending GM Approval Section 1',
            'workflow_builder_id': None
        },
        # Engineering Assessment -> Engineering Supervisor Review
        {
            'action': 'Engineering Assessment Complete',
            'allow_self_approval': 0,
            'allowed': 'Engineering Team',
            'condition': None,
            'next_state': 'Pending Engineering Supervisor Review',
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'transitions',
            'parenttype': 'Workflow',
            'send_email_to_creator': 0,
            'state': 'Pending Engineering Assessment',
            'workflow_builder_id': None
        },
        # Engineering Supervisor Review -> GM Final Approval
        {
            'action': 'Supervisor Review Complete',
            'allow_self_approval': 0,
            'allowed': 'Engineering Supervisor',
            'condition': None,
            'next_state': 'Pending GM Final Approval',
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'transitions',
            'parenttype': 'Workflow',
            'send_email_to_creator': 0,
            'state': 'Pending Engineering Supervisor Review',
            'workflow_builder_id': None
        },
        # GM Final Approval -> Approved for Repair
        {
            'action': 'GM Final Approve',
            'allow_self_approval': 0,
            'allowed': 'Maintenance Manager',
            'condition': None,
            'next_state': 'Approved for Repair',
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'transitions',
            'parenttype': 'Workflow',
            'send_email_to_creator': 0,
            'state': 'Pending GM Final Approval',
            'workflow_builder_id': None
        },
        # GM Final Approval -> Rejected
        {
            'action': 'GM Final Reject',
            'allow_self_approval': 0,
            'allowed': 'Maintenance Manager',
            'condition': None,
            'next_state': 'Rejected',
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'transitions',
            'parenttype': 'Workflow',
            'send_email_to_creator': 0,
            'state': 'Pending GM Final Approval',
            'workflow_builder_id': None
        },
        # Approved for Repair -> Repair In Progress
        {
            'action': 'Start Repair',
            'allow_self_approval': 0,
            'allowed': 'Engineering Team',
            'condition': None,
            'next_state': 'Repair In Progress',
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'transitions',
            'parenttype': 'Workflow',
            'send_email_to_creator': 0,
            'state': 'Approved for Repair',
            'workflow_builder_id': None
        },
        # Repair In Progress -> Reporter Supervisor Verification
        {
            'action': 'Repair Complete',
            'allow_self_approval': 0,
            'allowed': 'Engineering Supervisor',
            'condition': None,
            'next_state': 'Pending Reporter Supervisor Verification',
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'transitions',
            'parenttype': 'Workflow',
            'send_email_to_creator': 0,
            'state': 'Repair In Progress',
            'workflow_builder_id': None
        },
        # Reporter Supervisor Verification -> Reporter Confirmation
        {
            'action': 'Supervisor Verify',
            'allow_self_approval': 0,
            'allowed': 'Supervisor',
            'condition': None,
            'next_state': 'Pending Reporter Confirmation',
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'transitions',
            'parenttype': 'Workflow',
            'send_email_to_creator': 0,
            'state': 'Pending Reporter Supervisor Verification',
            'workflow_builder_id': None
        },
        # Reporter Confirmation -> Finished (via portal/API)
        {
            'action': 'Reporter Confirm',
            'allow_self_approval': 0,
            'allowed': 'All',
            'condition': None,
            'next_state': 'Finished',
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'transitions',
            'parenttype': 'Workflow',
            'send_email_to_creator': 0,
            'state': 'Pending Reporter Confirmation',
            'workflow_builder_id': None
        },
        # Cancel from Finished (System Manager only)
        {
            'action': 'Cancel',
            'allow_self_approval': 1,
            'allowed': 'System Manager',
            'condition': None,
            'next_state': 'Cancelled',
            'parent': 'Repair Approval WorkFlow',
            'parentfield': 'transitions',
            'parenttype': 'Workflow',
            'send_email_to_creator': 0,
            'state': 'Finished',
            'workflow_builder_id': None
        }
    ],
    'workflow_data': None,
    'workflow_name': 'Repair Approval WorkFlow',
    'workflow_state_field': 'workflow_state'
}

# Replace the Asset Repair workflow
workflows[asset_repair_idx] = new_workflow

# Write back
with open('tub_suite/fixtures/workflow.json', 'w', encoding='utf-8') as f:
    json.dump(workflows, f, indent=1, ensure_ascii=False)

print('Successfully updated Asset Repair workflow with 13 states and 14 transitions')
print('\nWorkflow States:')
for i, state in enumerate(new_workflow['states'], 1):
    print(f'{i}. {state["state"]} (allow_edit: {state["allow_edit"]})')
