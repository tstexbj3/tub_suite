"""
Fix section visibility conditions - correct logic this time
"""
import frappe

def fix():
    """Fix the visibility conditions with correct logic"""

    print("🔧 Fixing section visibility with CORRECT conditions...")

    # Section 3A (Reporter Confirmation) - only show in "Pending Reporter Confirmation" state
    section3a_fields = [
        'section_3a_break',
        'reporter_confirmed',
        'reporter_confirmation_photos',
        'reporter_confirmation_notes',
        'reporter_satisfaction',
    ]

    section3a_condition = 'eval:doc.workflow_state=="Pending Reporter Confirmation"'

    for fieldname in section3a_fields:
        if frappe.db.exists('Custom Field', f'Asset Repair-{fieldname}'):
            field = frappe.get_doc('Custom Field', f'Asset Repair-{fieldname}')
            field.depends_on = section3a_condition
            field.save(ignore_permissions=True)
            print(f"✅ Section 3A: {fieldname}")

    # Section 2D (Repair Completion) - only show after repair starts
    section2d_fields = [
        'section_2d_break',
        'actions_performed',
        'completion_date',
    ]

    section2d_condition = 'eval:["Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state) && doc.reporter_confirmed==1'

    for fieldname in section2d_fields:
        if frappe.db.exists('Custom Field', f'Asset Repair-{fieldname}'):
            field = frappe.get_doc('Custom Field', f'Asset Repair-{fieldname}')
            field.depends_on = section2d_condition
            field.save(ignore_permissions=True)
            print(f"✅ Section 2D: {fieldname}")

    # Section 4 (Final Remarks) - show only at end
    if frappe.db.exists('Custom Field', 'Asset Repair-section_4_break'):
        field = frappe.get_doc('Custom Field', 'Asset Repair-section_4_break')
        field.depends_on = 'eval:doc.workflow_state=="Finished"'
        field.save(ignore_permissions=True)
        print(f"✅ Section 4 break")

    if frappe.db.exists('Custom Field', 'Asset Repair-final_remarks'):
        field = frappe.get_doc('Custom Field', 'Asset Repair-final_remarks')
        field.depends_on = 'eval:doc.workflow_state=="Finished"'
        field.save(ignore_permissions=True)
        print(f"✅ final_remarks")

    # Fix standard fields in DocType
    doc = frappe.get_doc('DocType', 'Asset Repair')
    for field in doc.fields:
        if field.fieldname == 'repair_details_section':
            field.hidden = 1
        elif field.fieldname == 'issue_severity':
            field.depends_on = 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'

    doc.save(ignore_permissions=True)
    print(f"✅ Fixed standard fields")

    frappe.db.commit()
    frappe.clear_cache(doctype='Asset Repair')

    print()
    print("=" * 60)
    print("✅ Section visibility fixed with CORRECT logic!")
    print()
    print("📋 Visibility in 'Pending Reporter Supervisor Verification' (first time):")
    print("   ✅ Section 1")
    print("   ✅ Section 1B (Supervisor Verification)")
    print("   ❌ Section 3A (Reporter Confirmation) - HIDDEN")
    print("   ❌ Repair Completion - HIDDEN")
    print("   ❌ Final Remarks - HIDDEN")
    print()
    print("🔄 Clear cache and reload:")
    print("   bench --site tub clear-cache")
    print("   Refresh browser (hard refresh: Ctrl+Shift+R)")
    print("=" * 60)
