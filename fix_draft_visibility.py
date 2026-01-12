#!/usr/bin/env python3
"""Fix field visibility in Draft state"""
import frappe

frappe.init(site='tub')
frappe.connect()

# Fields that should NOT show in Draft - hide from Draft, show from Pending Engineering Assessment onwards
hide_from_draft = [
    'expected_completion_date',
    'issue_severity',
    'custom_cause_description',  # ระบุสาเหตุ
    'custom_purchase_order_no'
]

depends_on = 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)'

print("Hiding fields from Draft state...")
for fieldname in hide_from_draft:
    result = frappe.db.sql("""
        UPDATE `tabCustom Field`
        SET depends_on = %s, hidden = 0
        WHERE dt = 'Asset Repair' AND fieldname = %s
    """, (depends_on, fieldname))
    print(f"  Updated {fieldname}")

# Reporter Confirmation - only at Pending Supervisor Verification
reporter_fields = ['reporter_confirmation_date', 'reporter_confirmation_photos', 'reporter_confirmation_notes']
reporter_depends = 'eval:doc.workflow_state=="Pending Supervisor Verification"'

print("\nSetting Reporter Confirmation visibility...")
for fieldname in reporter_fields:
    frappe.db.sql("""
        UPDATE `tabCustom Field`
        SET depends_on = %s, hidden = 0
        WHERE dt = 'Asset Repair' AND fieldname = %s
    """, (reporter_depends, fieldname))
    print(f"  Updated {fieldname}")

# Inspector fields - always hidden
inspector_fields = ['requires_inspector_verification', 'verification_notes', 'verification_status']

print("\nHiding Inspector Verification fields...")
for fieldname in inspector_fields:
    frappe.db.sql("""
        UPDATE `tabCustom Field`
        SET hidden = 1
        WHERE dt = 'Asset Repair' AND fieldname = %s
    """, (fieldname,))
    print(f"  Hidden {fieldname}")

frappe.db.commit()
print("\n✅ Done! Run: bench --site tub clear-cache")
