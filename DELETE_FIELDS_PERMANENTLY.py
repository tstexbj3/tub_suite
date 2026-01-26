#!/usr/bin/env python3
"""
PERMANENTLY delete fields from database and prevent them from coming back
Run: bench --site tub console < DELETE_FIELDS_PERMANENTLY.py
"""

import frappe
import json
frappe.init(site='tub')
frappe.connect()

print('=== STEP 1: DELETE FROM DATABASE ===\n')

# Fields to delete
fields_to_delete = [
    'custom_supervisor_notes_หมายเหตหวหนา',  # Supervisor Notes (หมายเหตุหัวหน้า)
]

for fieldname in fields_to_delete:
    # Try to delete from database
    cf_name = f'Asset Repair-{fieldname}'
    if frappe.db.exists('Custom Field', cf_name):
        frappe.db.sql("DELETE FROM `tabCustom Field` WHERE name = %s", cf_name)
        print(f'✅ Deleted from DB: {fieldname}')
    else:
        print(f'⚠️  Not in DB: {fieldname}')

frappe.db.commit()

print('\n=== STEP 2: REMOVE FROM FIXTURE FILE ===\n')

fixture_path = '/home/user/frappe-bench/apps/tub_suite/tub_suite/fixtures/custom_field.json'

try:
    with open(fixture_path, 'r', encoding='utf-8') as f:
        custom_fields = json.load(f)

    print(f'Original: {len(custom_fields)} fields in fixture')

    # Remove fields
    filtered_fields = []
    removed_count = 0

    for cf in custom_fields:
        fieldname = cf.get('fieldname', '')
        # Keep field if it's NOT in delete list
        if fieldname not in fields_to_delete:
            filtered_fields.append(cf)
        else:
            print(f'  Removing: {fieldname}')
            removed_count += 1

    # Also remove any fields that reference stock_consumption_details_section
    final_fields = []
    for cf in filtered_fields:
        insert_after = cf.get('insert_after', '')
        if 'stock_consumption' not in insert_after:
            final_fields.append(cf)
        else:
            print(f'  Removing (references stock): {cf.get("fieldname")}')
            removed_count += 1

    print(f'\nRemoved: {removed_count} fields')
    print(f'Remaining: {len(final_fields)} fields')

    # Write back to file
    with open(fixture_path, 'w', encoding='utf-8') as f:
        json.dump(final_fields, f, indent=1, ensure_ascii=False)

    print('\n✅ Fixture file updated')

except Exception as e:
    print(f'❌ Error updating fixture: {e}')

print('\n=== STEP 3: CLEAR CACHE ===')
frappe.clear_cache()
print('✅ Cache cleared')

print('\n=== DONE ===')
print('Fields permanently deleted!')
print('\nNext time you run "bench migrate", these fields will NOT come back.')
print('\nNow commit the updated fixture:')
print('  git add tub_suite/fixtures/custom_field.json')
print('  git commit -m "refactor: Remove unwanted fields from Asset Repair"')
