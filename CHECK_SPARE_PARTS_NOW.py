#!/usr/bin/env python3
"""
Check Repair Spare Part DocType current state
"""
import frappe

frappe.init(site='tub')
frappe.connect()

print("=" * 80)
print("CHECKING REPAIR SPARE PART DOCTYPE")
print("=" * 80)

# Check DocField table
fields = frappe.db.sql("""
    SELECT fieldname, label, fieldtype, in_list_view, columns, idx
    FROM `tabDocField`
    WHERE parent = 'Repair Spare Part'
    ORDER BY idx
""", as_dict=True)

print("\n📋 Fields in database (tabDocField):\n")
for field in fields:
    list_view = "✓" if field.in_list_view else "✗"
    print(f"{field.idx:2}. {field.fieldname:20} ({field.fieldtype:15}) {field.label:30} [List: {list_view}, Cols: {field.columns}]")

# Also check Custom Field table in case there are customizations
custom_fields = frappe.db.sql("""
    SELECT fieldname, label, fieldtype, in_list_view, columns
    FROM `tabCustom Field`
    WHERE dt = 'Repair Spare Part'
    ORDER BY idx
""", as_dict=True)

if custom_fields:
    print("\n📝 Custom Fields:\n")
    for field in custom_fields:
        list_view = "✓" if field.in_list_view else "✗"
        print(f"  {field.fieldname:20} ({field.fieldtype:15}) {field.label:30} [List: {list_view}, Cols: {field.columns}]")
else:
    print("\n(No custom fields)")

print("\n" + "=" * 80)
