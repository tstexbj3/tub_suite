"""
Final fix for Asset Repair form - proper field ordering
"""
import frappe

def fix():
    """Fix Asset Repair form field ordering completely"""

    print("🔧 Applying final fixes to Asset Repair form...")

    # STEP 1: Hide the standard "Repair Details" section break that's breaking Section 1
    if not frappe.db.exists('Property Setter', {
        'doc_type': 'Asset Repair',
        'field_name': 'repair_details_section',
        'property': 'hidden'
    }):
        frappe.get_doc({
            'doctype': 'Property Setter',
            'doc_type': 'Asset Repair',
            'field_name': 'repair_details_section',
            'property': 'hidden',
            'value': '1',
            'property_type': 'Check'
        }).insert(ignore_permissions=True)
        print("🙈 Hidden: repair_details_section")

    # STEP 2: Hide standard fields we don't need in Section 1
    standard_fields_to_hide = [
        ('failure_date', 'hidden', '1'),  # Will use it elsewhere
        ('issue_severity', 'hidden', '1'),  # Not in FM-EN-04
        ('repair_status', 'hidden', '0'),  # Keep visible but move later
    ]

    for field, prop, value in standard_fields_to_hide:
        prop_name = f'{field}-{prop}'
        if not frappe.db.exists('Property Setter', {
            'doc_type': 'Asset Repair',
            'field_name': field,
            'property': prop
        }):
            frappe.get_doc({
                'doctype': 'Property Setter',
                'doc_type': 'Asset Repair',
                'field_name': field,
                'property': prop,
                'value': value,
                'property_type': 'Check'
            }).insert(ignore_permissions=True)
            print(f"🙈 Set {field}.{prop} = {value}")

    # STEP 3: Fix Section 1 field order - make them consecutive
    section1_fields = [
        ('repair_type', 'section_1_break'),
        ('repair_source', 'repair_type'),
        ('repair_subject', 'repair_source'),
        ('description', 'repair_subject'),  # Standard field - use Property Setter
        ('issue_photos', 'description'),
        ('reported_by', 'issue_photos'),
        ('reporter_department', 'reported_by'),
        ('reporter_signature', 'reporter_department'),
    ]

    for fieldname, insert_after in section1_fields:
        # Check if custom field
        if frappe.db.exists('Custom Field', f'Asset Repair-{fieldname}'):
            doc = frappe.get_doc('Custom Field', f'Asset Repair-{fieldname}')
            doc.insert_after = insert_after
            doc.save(ignore_permissions=True)
            print(f"📌 Section 1: {fieldname} → after {insert_after}")
        else:
            # Standard field - use Property Setter
            if not frappe.db.exists('Property Setter', {
                'doc_type': 'Asset Repair',
                'field_name': fieldname,
                'property': 'insert_after'
            }):
                frappe.get_doc({
                    'doctype': 'Property Setter',
                    'doc_type': 'Asset Repair',
                    'field_name': fieldname,
                    'property': 'insert_after',
                    'value': insert_after,
                    'property_type': 'Data'
                }).insert(ignore_permissions=True)
                print(f"📌 Section 1 (standard): {fieldname} → after {insert_after}")

    # STEP 4: Hide duplicate "Section 5" and old sections
    duplicate_sections = [
        'section_5_break',  # Duplicate
        'final_remarks_section',  # Old section
    ]

    for section in duplicate_sections:
        if frappe.db.exists('Custom Field', f'Asset Repair-{section}'):
            doc = frappe.get_doc('Custom Field', f'Asset Repair-{section}')
            doc.hidden = 1
            doc.save(ignore_permissions=True)
            print(f"🙈 Hidden section: {section}")

    # STEP 5: Fix "Section 5" fields - they should be in Section 3
    # supervisor_verification_notes and supervisor_signature are correct in Section 3
    # Move them if they're wrongly positioned

    # STEP 6: Ensure Section 2 fields are in correct order
    section2_fields = [
        ('action_type', 'section_2_break'),
        ('engineering_todo_items', 'action_type'),
        ('spare_parts_used', 'engineering_todo_items'),
        ('expected_duration_days', 'spare_parts_used'),
        ('repair_start_date', 'expected_duration_days'),
        ('repair_end_date', 'repair_start_date'),
        ('engineering_operator_signature', 'repair_end_date'),
    ]

    for fieldname, insert_after in section2_fields:
        if frappe.db.exists('Custom Field', f'Asset Repair-{fieldname}'):
            doc = frappe.get_doc('Custom Field', f'Asset Repair-{fieldname}')
            doc.insert_after = insert_after
            doc.save(ignore_permissions=True)
            print(f"📌 Section 2: {fieldname} → after {insert_after}")

    # STEP 7: Hide old "Section 2: Spare Parts Used" and "Section 4: Hygiene & Safety"
    old_sections = [
        'section_2_spare_parts',
        'section_4_hygiene',
    ]

    for section in old_sections:
        if frappe.db.exists('Custom Field', f'Asset Repair-{section}'):
            doc = frappe.get_doc('Custom Field', f'Asset Repair-{section}')
            doc.hidden = 1
            doc.save(ignore_permissions=True)
            print(f"🙈 Hidden old section: {section}")

    frappe.db.commit()

    print()
    print("=" * 60)
    print("✅ Final fixes applied!")
    print()
    print("🔄 Run: bench --site tub clear-cache")
    print("🔄 Then: bench --site tub reload-doctype Asset\\ Repair")
    print("🔄 Then refresh browser")
    print("=" * 60)
