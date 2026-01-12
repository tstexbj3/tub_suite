#!/usr/bin/env python3
"""
Create spare_parts_used field in database
"""
import frappe

frappe.init(site='tub')
frappe.connect()

print("=" * 80)
print("CREATING SPARE_PARTS_USED FIELD")
print("=" * 80)

# Create the Custom Field
frappe.db.sql("""
    INSERT INTO `tabCustom Field`
    (name, creation, modified, modified_by, owner, docstatus, idx,
     dt, fieldname, fieldtype, label, options, insert_after, depends_on,
     hidden, in_list_view, allow_on_submit, description)
    VALUES
    ('Asset Repair-spare_parts_used', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0,
     'Asset Repair', 'spare_parts_used', 'Table', 'Spare Parts Used (รายการอะไหล่)',
     'Repair Spare Part', 'custom_engineering_todo_items',
     'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)',
     0, 0, 0, 'Spare parts used in repair')
""")

frappe.db.commit()

print("\n✅ spare_parts_used field CREATED!")
print("   Position: After Engineering Todo Items")
print("   Visibility: From Pending Engineering Assessment onwards")
print("   Child DocType: Repair Spare Part")
print("\n" + "=" * 80)
print("Run: bench --site tub clear-cache")
print("=" * 80)
