#!/usr/bin/env python3
"""Find actual fieldnames for Thai labels"""
import frappe

frappe.init(site='tub')
frappe.connect()

# Find all custom fields for Asset Repair
fields = frappe.db.sql("""
    SELECT fieldname, label, fieldtype, depends_on, hidden
    FROM `tabCustom Field`
    WHERE dt = 'Asset Repair'
    AND (
        label LIKE '%สาเหตุ%'
        OR label LIKE '%การดำเนิน%'
        OR label LIKE '%Reporter%'
        OR label LIKE '%Inspector%'
        OR label LIKE '%Severity%'
        OR label LIKE '%Completion Date%'
        OR label LIKE '%Purchase%'
    )
    ORDER BY label
""", as_dict=True)

print("Found fields:")
for f in fields:
    print(f"\n{f.fieldname}:")
    print(f"  Label: {f.label}")
    print(f"  Type: {f.fieldtype}")
    print(f"  Hidden: {f.hidden}")
    print(f"  Depends on: {f.depends_on or '(none)'}")
