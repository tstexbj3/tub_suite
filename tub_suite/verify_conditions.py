"""
Verify what conditions are actually saved on the problematic sections
"""
import frappe

def verify():
    """Check what's actually in the database"""

    print("=" * 60)
    print("Verifying saved conditions")
    print("=" * 60)

    # Check the problematic sections
    problem_fields = [
        'section_3a_break',
        'reporter_confirmed',
        'reporter_confirmation_photos',
        'section_2d_break',
        'section_4_break',
        'final_remarks',
    ]

    print("\n📋 Checking field conditions:\n")
    for fieldname in problem_fields:
        if frappe.db.exists('Custom Field', f'Asset Repair-{fieldname}'):
            field = frappe.get_doc('Custom Field', f'Asset Repair-{fieldname}')
            print(f"{fieldname}:")
            print(f"   hidden: {field.hidden}")
            print(f"   depends_on: {field.depends_on or 'None'}")
            print()

    # Check standard fields in DocType
    print("\n📋 Checking standard fields:\n")
    doc = frappe.get_doc('DocType', 'Asset Repair')
    for field in doc.fields:
        if field.fieldname in ['repair_details_section', 'issue_severity']:
            print(f"{field.fieldname}:")
            print(f"   hidden: {field.hidden}")
            print(f"   depends_on: {field.depends_on or 'None'}")
            print()

    print("=" * 60)
