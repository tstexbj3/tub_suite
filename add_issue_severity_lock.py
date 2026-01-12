#!/usr/bin/env python3
"""
Add Property Setter to lock issue_severity after Pending Engineering Assessment
Editable ONLY at: Pending Engineering Assessment
Read-only at: All other states
"""
import frappe

frappe.init(site='tub')
frappe.connect()

# Check if Property Setter exists
existing = frappe.db.exists("Property Setter", {
    "doc_type": "Asset Repair",
    "field_name": "issue_severity",
    "property": "read_only_depends_on"
})

if existing:
    print(f"⚠️  Property Setter already exists: {existing}")
    print("Updating...")
    frappe.db.sql("""
        UPDATE `tabProperty Setter`
        SET value = %s
        WHERE name = %s
    """, ('eval:doc.workflow_state!="Pending Engineering Assessment"', existing))
else:
    print("Creating new Property Setter...")
    frappe.db.sql("""
        INSERT INTO `tabProperty Setter`
        (name, creation, modified, modified_by, owner, docstatus, idx,
         doc_type, doctype_or_field, field_name, property, value, property_type,
         default_value, row_name, is_system_generated)
        VALUES
        (%s, NOW(), NOW(), 'Administrator', 'Administrator', 0, 0,
         'Asset Repair', 'DocField', 'issue_severity', 'read_only_depends_on',
         %s, 'Data', NULL, NULL, 0)
    """, (
        'Asset Repair-issue_severity-read_only_depends_on',
        'eval:doc.workflow_state!="Pending Engineering Assessment"'
    ))

frappe.db.commit()

print("\n✅ issue_severity will now be:")
print("   - HIDDEN in Draft")
print("   - VISIBLE AND EDITABLE at Pending Engineering Assessment")
print("   - VISIBLE BUT READ-ONLY at all other states")
print("\nRun: bench --site tub clear-cache")
