#!/usr/bin/env python3
"""
Fix field visibility after bench migrate overwrote custom field settings
"""
import frappe

def fix_visibility():
    frappe.init(site='tub')
    frappe.connect()

    # Engineering fields that should NOT show in Draft
    engineering_fields = ['expected_completion_date', 'issue_severity', 'custom_สาเหตุ', 'custom_cause_description', 'custom_purchase_order_no']
    depends_on_engineering = 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)'

    for fieldname in engineering_fields:
        frappe.db.sql("""
            UPDATE `tabCustom Field`
            SET depends_on = %s, hidden = 0
            WHERE dt = 'Asset Repair' AND fieldname = %s
        """, (depends_on_engineering, fieldname))
        print(f"✓ Fixed {fieldname}")

    # Reporter Confirmation fields - only show at Pending Supervisor Verification
    reporter_fields = ['reporter_confirmation_date', 'reporter_confirmation_photos', 'reporter_confirmation_notes']
    depends_on_reporter = 'eval:doc.workflow_state=="Pending Supervisor Verification"'

    for fieldname in reporter_fields:
        frappe.db.sql("""
            UPDATE `tabCustom Field`
            SET depends_on = %s, hidden = 0
            WHERE dt = 'Asset Repair' AND fieldname = %s
        """, (depends_on_reporter, fieldname))
        print(f"✓ Fixed {fieldname}")

    # Inspector Verification fields - always hidden
    inspector_fields = ['requires_inspector_verification', 'verification_notes', 'verification_status']

    for fieldname in inspector_fields:
        frappe.db.sql("""
            UPDATE `tabCustom Field`
            SET hidden = 1
            WHERE dt = 'Asset Repair' AND fieldname = %s
        """, (fieldname,))
        print(f"✓ Hidden {fieldname}")

    frappe.db.commit()
    print("\n✅ All field visibility fixed!")

if __name__ == '__main__':
    fix_visibility()
