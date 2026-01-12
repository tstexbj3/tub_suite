#!/usr/bin/env python3
"""
Check if spare_parts_used exists in DATABASE (not fixture)
"""
import frappe

frappe.init(site='tub')
frappe.connect()

print("=" * 80)
print("CHECKING DATABASE - NOT FIXTURE FILE")
print("=" * 80)

# Check if field exists in database
field = frappe.db.sql("""
    SELECT fieldname, label, insert_after, depends_on, hidden
    FROM `tabCustom Field`
    WHERE dt = 'Asset Repair'
    AND fieldname = 'spare_parts_used'
""", as_dict=True)

if field:
    f = field[0]
    print(f"\n✓ spare_parts_used EXISTS in database")
    print(f"  Label: {f.label}")
    print(f"  Insert After: {f.insert_after}")
    print(f"  Depends On: {f.depends_on or '(EMPTY - THIS IS THE PROBLEM!)'}")
    print(f"  Hidden: {f.hidden}")
else:
    print("\n❌ spare_parts_used DOES NOT EXIST in database!")
    print("   The field was probably deleted or never migrated")

print("\n" + "=" * 80)
