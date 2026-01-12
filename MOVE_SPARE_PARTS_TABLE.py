#!/usr/bin/env python3
"""
Move spare_parts_used table to Engineering section
Place it after custom_engineering_todo_items
"""
import frappe

frappe.init(site='tub')
frappe.connect()

print("=" * 80)
print("MOVING SPARE PARTS TABLE TO ENGINEERING SECTION")
print("=" * 80)

# Update the insert_after for spare_parts_used
frappe.db.sql("""
    UPDATE `tabCustom Field`
    SET insert_after = 'custom_engineering_todo_items',
        depends_on = 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)'
    WHERE dt = 'Asset Repair'
    AND fieldname = 'spare_parts_used'
""")

frappe.db.commit()

print("\n✅ spare_parts_used table moved to Engineering Section 1")
print("   Position: After Engineering Todo Items")
print("   Visibility: From Pending Engineering Assessment onwards")
print("\n" + "=" * 80)
print("Run: bench --site tub clear-cache")
print("=" * 80)
