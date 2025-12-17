#!/usr/bin/env python3
"""
Quick script to check Asset Maintenance data
Run: bench --site tub execute tub_suite.check_maintenance_data.check_data
"""

import frappe

def check_data():
    frappe.init(site='tub')
    frappe.connect()

    print("\n" + "="*60)
    print("CHECKING ASSET MAINTENANCE DATA")
    print("="*60)

    # Check Asset Maintenance
    maintenance = frappe.get_all("Asset Maintenance",
        filters={"docstatus": 1},
        fields=["name", "asset_name", "maintenance_status"],
        limit=10
    )

    print(f"\n1. Asset Maintenance records (Submitted): {len(maintenance)}")
    if maintenance:
        for m in maintenance[:5]:
            print(f"   - {m.name}: {m.asset_name} ({m.maintenance_status})")

    # Check Asset Maintenance Tasks
    tasks = frappe.get_all("Asset Maintenance Task",
        fields=["name", "parent", "maintenance_task", "assign_to", "next_due_date"],
        limit=10
    )

    print(f"\n2. Asset Maintenance Tasks: {len(tasks)}")
    if tasks:
        for t in tasks[:5]:
            print(f"   - {t.maintenance_task}")
            print(f"     Parent: {t.parent}")
            print(f"     Assigned to: {t.assign_to or 'Not assigned'}")
            print(f"     Due: {t.next_due_date or 'No due date'}")

    # Check current user
    current_user = frappe.session.user
    print(f"\n3. Current user: {current_user}")

    # Check tasks assigned to current user
    my_tasks = frappe.get_all("Asset Maintenance Task",
        filters={"assign_to": current_user},
        fields=["name", "parent", "maintenance_task", "next_due_date"]
    )

    print(f"\n4. Tasks assigned to {current_user}: {len(my_tasks)}")
    if my_tasks:
        for t in my_tasks:
            print(f"   - {t.maintenance_task} (Due: {t.next_due_date})")
    else:
        print("   NO TASKS ASSIGNED TO THIS USER!")

    # Check all users who have assignments
    assigned_users = frappe.db.sql("""
        SELECT DISTINCT assign_to
        FROM `tabAsset Maintenance Task`
        WHERE assign_to IS NOT NULL AND assign_to != ''
    """, as_dict=True)

    print(f"\n5. Users with assigned tasks: {len(assigned_users)}")
    for u in assigned_users:
        count = frappe.db.count("Asset Maintenance Task", {"assign_to": u.assign_to})
        print(f"   - {u.assign_to}: {count} tasks")

    print("\n" + "="*60)
    print("SUMMARY:")
    if not maintenance:
        print("❌ No Asset Maintenance records found!")
        print("   You need to create Asset Maintenance schedules first.")
    elif not tasks:
        print("❌ No tasks found in Asset Maintenance!")
        print("   Add tasks to your Asset Maintenance records.")
    elif not my_tasks:
        print("❌ No tasks assigned to current user!")
        print(f"   Assign tasks to: {current_user}")
    else:
        print("✅ Data looks good!")
    print("="*60 + "\n")

    frappe.db.close()

if __name__ == "__main__":
    check_data()
