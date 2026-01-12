#!/usr/bin/env python3
"""
DELETE fields with Thai characters in fieldnames
These are invalid and should not exist
"""
import frappe

frappe.init(site='tub')
frappe.connect()

print("=" * 80)
print("DELETING FIELDS WITH THAI CHARACTERS IN FIELDNAME")
print("=" * 80)

# Get all Asset Repair custom fields
fields = frappe.get_all("Custom Field",
    filters={"dt": "Asset Repair"},
    fields=["name", "fieldname", "label", "fieldtype"]
)

deleted = []

for field in fields:
    fieldname = field.fieldname
    # Check if fieldname contains non-ASCII (Thai) characters
    if any(ord(c) > 127 for c in fieldname):
        print(f"\n❌ DELETING: {fieldname}")
        print(f"   Label: {field.label}")
        print(f"   Type: {field.fieldtype}")

        # Delete from database
        frappe.db.sql("""
            DELETE FROM `tabCustom Field`
            WHERE name = %s
        """, (field.name,))

        deleted.append(fieldname)

if deleted:
    frappe.db.commit()
    print("\n" + "=" * 80)
    print(f"✅ DELETED {len(deleted)} fields with Thai in fieldnames:")
    for fn in deleted:
        print(f"   - {fn}")
    print("=" * 80)
    print("\nNow run: bench --site tub clear-cache")
else:
    print("\n✅ No fields with Thai characters in fieldnames found")
    print("=" * 80)
