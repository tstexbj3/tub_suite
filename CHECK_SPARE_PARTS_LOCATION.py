#!/usr/bin/env python3
"""
Check where spare_parts_used field is in Asset Repair
"""
import frappe

frappe.init(site='tub')
frappe.connect()

print("=" * 80)
print("CHECKING SPARE_PARTS_USED FIELD LOCATION")
print("=" * 80)

# Get spare_parts_used field details
field = frappe.db.sql("""
    SELECT fieldname, label, fieldtype, insert_after, depends_on, hidden
    FROM `tabCustom Field`
    WHERE dt = 'Asset Repair'
    AND fieldname = 'spare_parts_used'
""", as_dict=True)

if field:
    f = field[0]
    print(f"\n📋 spare_parts_used field:")
    print(f"   Label: {f.label}")
    print(f"   Type: {f.fieldtype}")
    print(f"   Insert After: {f.insert_after}")
    print(f"   Depends On: {f.depends_on or '(none)'}")
    print(f"   Hidden: {f.hidden}")
else:
    print("\n❌ spare_parts_used field NOT FOUND in Custom Field table!")
    print("   Checking if it exists in standard Asset Repair DocType...")

    # Check if it's in standard DocType
    std_field = frappe.db.sql("""
        SELECT fieldname, label
        FROM `tabDocField`
        WHERE parent = 'Asset Repair'
        AND fieldname = 'spare_parts_used'
    """, as_dict=True)

    if std_field:
        print(f"   ✓ Found in standard DocType: {std_field[0].label}")
    else:
        print("   ✗ NOT FOUND anywhere!")

# Check what comes before and after
print(f"\n📍 Fields around 'custom_engineering_todo_items':")

nearby = frappe.db.sql("""
    SELECT fieldname, label, insert_after
    FROM `tabCustom Field`
    WHERE dt = 'Asset Repair'
    AND (fieldname = 'custom_engineering_todo_items'
         OR insert_after = 'custom_engineering_todo_items')
    ORDER BY fieldname
""", as_dict=True)

for f in nearby:
    print(f"   {f.fieldname}: insert_after = {f.insert_after}")

print("\n" + "=" * 80)
