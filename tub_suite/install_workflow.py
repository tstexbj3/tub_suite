"""Install Asset Repair Workflow from fixture"""
import frappe
import json
import os

def install():
    """Import Asset Repair Workflow from workflow.json fixture"""

    fixture_path = os.path.join(
        frappe.get_app_path('tub_suite'),
        'fixtures',
        'workflow.json'
    )

    print(f"Loading workflow from: {fixture_path}")

    with open(fixture_path, 'r', encoding='utf-8') as f:
        workflows = json.load(f)

    print(f"Found {len(workflows)} workflow(s) in file")

    # Delete existing workflow if any
    if frappe.db.exists('Workflow', 'Asset Repair Workflow FM-EN-04'):
        print("Deleting existing workflow...")
        frappe.delete_doc('Workflow', 'Asset Repair Workflow FM-EN-04', force=1)
        frappe.db.commit()

    # Import the workflow
    for wf_data in workflows:
        if wf_data.get('name') == 'Asset Repair Workflow FM-EN-04':
            print(f"Importing workflow: {wf_data['name']}")

            # Create workflow states first
            for state in wf_data.get('states', []):
                state_name = state.get('state')
                if state_name and not frappe.db.exists('Workflow State', state_name):
                    print(f"  Creating state: {state_name}")
                    frappe.get_doc({
                        'doctype': 'Workflow State',
                        'workflow_state_name': state_name,
                        'style': 'Primary'
                    }).insert(ignore_permissions=True)

            # Now create the workflow
            wf = frappe.get_doc(wf_data)
            wf.insert(ignore_permissions=True)
            print(f"✅ Workflow imported: {wf.name}")
            break

    frappe.db.commit()
    print("✅ Done! Workflow installation complete.")
