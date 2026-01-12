#!/usr/bin/env python3
"""
Check what's ACTUALLY in the database right now
"""
import frappe

frappe.init(site='tub')
frappe.connect()

print("=" * 80)
print("CHECKING DATABASE CURRENT STATE")
print("=" * 80)

# Fields that should be hidden from Draft
fields_to_check = [
    'custom_engineering_section',
    'custom_engineering_todo_items',
    'action_type',
    'issue_severity',
    'expected_completion_date',
    'custom_cause_description',
    'requires_inspector_verification',
    'verification_notes',
    'verification_status',
]

print("\nChecking fields in DATABASE (not fixture file):\n")

for fieldname in fields_to_check:
    try:
        field = frappe.get_doc("Custom Field", {"dt": "Asset Repair", "fieldname": fieldname})
        depends_on = field.depends_on or "(none)"
        if len(depends_on) > 60:
            depends_on = depends_on[:60] + "..."

        print(f"{fieldname}:")
        print(f"  depends_on: {depends_on}")
        print(f"  hidden: {field.hidden}")
        print()
    except Exception as e:
        print(f"{fieldname}: ERROR - {e}\n")

print("=" * 80)
print("If depends_on is (none) or empty, the fixture didn't get imported!")
print("=" * 80)
