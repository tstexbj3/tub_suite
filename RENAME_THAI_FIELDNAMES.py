#!/usr/bin/env python3
"""
RENAME fields with Thai characters in fieldnames to valid English names
"""
import frappe
import re

frappe.init(site='tub')
frappe.connect()

print("=" * 80)
print("RENAMING FIELDS WITH THAI CHARACTERS IN FIELDNAME")
print("=" * 80)

# Get all Asset Repair custom fields
fields = frappe.get_all("Custom Field",
    filters={"dt": "Asset Repair"},
    fields=["name", "fieldname", "label", "fieldtype"]
)

# Mapping of Thai fieldnames to English equivalents
rename_map = {
    'custom_สาเหตุ': 'custom_cause_category',
    'custom_การดำเนินการ': 'custom_action_section',
    'custom_การดำเนนการ': 'custom_engineering_action_section',
}

renamed = []

for field in fields:
    fieldname = field.fieldname

    # Check if fieldname contains non-ASCII (Thai) characters
    if any(ord(c) > 127 for c in fieldname):
        # Get new name from map or generate one
        if fieldname in rename_map:
            new_fieldname = rename_map[fieldname]
        else:
            # Generate a new name by removing Thai chars
            new_fieldname = re.sub(r'[^\w]', '', fieldname.encode('ascii', 'ignore').decode('ascii'))
            if not new_fieldname.startswith('custom_'):
                new_fieldname = 'custom_' + new_fieldname

        print(f"\n🔄 RENAMING: {fieldname}")
        print(f"   Label: {field.label}")
        print(f"   Type: {field.fieldtype}")
        print(f"   New name: {new_fieldname}")

        # Check if new name already exists
        exists = frappe.db.exists("Custom Field", {
            "dt": "Asset Repair",
            "fieldname": new_fieldname
        })

        if exists:
            print(f"   ⚠️  Field {new_fieldname} already exists - SKIPPING")
            continue

        # Rename in database
        try:
            frappe.db.sql("""
                UPDATE `tabCustom Field`
                SET fieldname = %s,
                    name = CONCAT('Asset Repair-', %s)
                WHERE name = %s
            """, (new_fieldname, new_fieldname, field.name))

            renamed.append((fieldname, new_fieldname))
        except Exception as e:
            print(f"   ❌ ERROR: {e}")

if renamed:
    frappe.db.commit()
    print("\n" + "=" * 80)
    print(f"✅ RENAMED {len(renamed)} fields:")
    for old, new in renamed:
        print(f"   {old} → {new}")
    print("=" * 80)
    print("\nNow run:")
    print("1. bench --site tub clear-cache")
    print("2. bench --site tub migrate  # To update form layout")
else:
    print("\n✅ No fields with Thai characters in fieldnames found")
    print("=" * 80)
