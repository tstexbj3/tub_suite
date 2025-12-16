#!/usr/bin/env python3
"""
Debug today's repairs to see why badge turns green
Run: bench --site tub execute tub_suite.utils.debug_today_repairs.check_today
"""

import frappe
from frappe.utils import nowdate

def check_today():
    """Check today's repairs and the query results"""

    today = nowdate()

    print("\n" + "="*80)
    print(f"DEBUG: Today's Repairs (date = {today})")
    print("="*80)

    # Get ALL repairs created today
    all_today = frappe.get_all("Asset Repair",
        filters={"failure_date": today},
        fields=["name", "asset", "workflow_state", "repair_status", "issue_severity", "docstatus"],
        order_by="creation desc"
    )

    print(f"\n1. ALL Repairs with failure_date = {today}: {len(all_today)}")
    for r in all_today:
        print(f"   {r.name}")
        print(f"     Asset: {r.asset}")
        print(f"     Workflow State: '{r.workflow_state}'")
        print(f"     Repair Status: '{r.repair_status}'")
        print(f"     Issue Severity: {r.issue_severity}")
        print(f"     Docstatus: {r.docstatus}")

    # Test OLD query (broken)
    print(f"\n2. OLD QUERY (repair_status):")
    old_query = frappe.get_all("Asset Repair",
        filters={
            "failure_date": today,
            "repair_status": ["in", ["Pending", "In Progress"]]
        },
        fields=["name", "workflow_state", "repair_status"]
    )
    print(f"   Found: {len(old_query)} repairs")
    for r in old_query:
        print(f"   - {r.name}: workflow={r.workflow_state}, status={r.repair_status}")

    # Test NEW query (should work)
    print(f"\n3. NEW QUERY (workflow_state NOT IN Finished/Cancelled/Rejected):")
    new_query = frappe.get_all("Asset Repair",
        filters={
            "failure_date": today,
            "workflow_state": ["not in", ["Finished", "Cancelled", "Rejected"]]
        },
        fields=["name", "workflow_state", "repair_status"]
    )
    print(f"   Found: {len(new_query)} repairs")
    for r in new_query:
        print(f"   - {r.name}: workflow={r.workflow_state}, status={r.repair_status}")

    # Check if workflow_state is None/empty
    print(f"\n4. REPAIRS WITH EMPTY workflow_state:")
    empty_workflow = frappe.get_all("Asset Repair",
        filters={
            "failure_date": today,
            "workflow_state": ["in", [None, ""]]
        },
        fields=["name", "workflow_state", "repair_status"]
    )
    print(f"   Found: {len(empty_workflow)} repairs")
    for r in empty_workflow:
        print(f"   - {r.name}: workflow={r.workflow_state}, status={r.repair_status}")

    # Now check what get_asset_tasks would return
    print(f"\n5. SIMULATING get_asset_tasks API:")
    if all_today:
        test_asset = all_today[0].asset
        print(f"   Testing asset: {test_asset}")

        # Get maintenance tasks for this asset
        asset_doc = frappe.get_doc("Asset", test_asset)
        if asset_doc.asset_maintenance:
            tasks = frappe.get_all("Asset Maintenance Task",
                filters={"parent": asset_doc.asset_maintenance},
                fields=["name", "maintenance_task", "last_completion_date"]
            )

            print(f"   Tasks for this asset: {len(tasks)}")
            for task in tasks:
                print(f"\n   Task: {task.maintenance_task}")
                print(f"     Last completed: {task.last_completion_date}")

                if task.last_completion_date == today:
                    # Run the actual query from maintenance.py
                    open_repairs = frappe.get_all("Asset Repair", filters={
                        "asset": test_asset,
                        "failure_date": today,
                        "workflow_state": ["not in", ["Finished", "Cancelled", "Rejected"]]
                    }, fields=["name", "workflow_state", "repair_status"])

                    has_open_issue = 1 if len(open_repairs) > 0 else 0

                    print(f"     Query found: {len(open_repairs)} open repairs")
                    for r in open_repairs:
                        print(f"       - {r.name}: workflow={r.workflow_state}")
                    print(f"     has_open_issue = {has_open_issue}")

                    if has_open_issue == 0:
                        print(f"     ❌ BUG: Should be 1 but is 0!")
                    else:
                        print(f"     ✅ Correct!")

    print("\n" + "="*80 + "\n")
