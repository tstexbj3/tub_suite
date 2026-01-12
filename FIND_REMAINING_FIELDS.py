#!/usr/bin/env python3
"""
Find ALL fields that are showing in Draft but shouldn't
"""
import frappe

frappe.init(site='tub')
frappe.connect()

print("=" * 80)
print("FINDING FIELDS VISIBLE IN DRAFT (depends_on is null or empty)")
print("=" * 80)

# Get all Asset Repair custom fields
fields = frappe.get_all("Custom Field",
    filters={"dt": "Asset Repair", "hidden": 0},
    fields=["fieldname", "label", "fieldtype", "depends_on"],
    order_by="idx"
)

section1_fields = [
    'repair_type', 'repair_source', 'repair_subject', 'issue_photos', 'issue_photos_2',
    'reported_by', 'reporter_department', 'failure_date', 'description',
    'supervisor_section1_signature', 'asset', 'asset_name', 'repair_status',
    'section_1_break', 'section_1a_break', 'section_0_break', 'column_break_repair_header'
]

print("\nFields that SHOULD NOT show in Draft (no depends_on):\n")

for field in fields:
    if field.fieldname in section1_fields:
        continue  # Skip Section 1 fields - they're supposed to show

    depends_on = field.depends_on
    if not depends_on or depends_on.strip() == '':
        print(f"{field.fieldname} ({field.fieldtype}): {field.label}")
        print(f"  depends_on: EMPTY!")
        print()

print("=" * 80)
