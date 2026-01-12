"""
Clean up Asset Repair form - hide duplicates and organize properly
"""
import frappe

def cleanup():
    """Hide duplicate/unnecessary fields and fix ordering"""

    print("🧹 Cleaning up Asset Repair form...")

    # Fields to HIDE (duplicates or old fields)
    fields_to_hide = [
        'custom_repair_type',  # Duplicate of repair_type
        'custom_สาเหต',  # Old Thai field
        'custom_การดำเนนการ',  # Old Thai field
        'requires_inspector_verification',  # Not needed in FM-EN-04
        'verification_status',  # Not needed in FM-EN-04
        'received_by',  # Not in FM-EN-04
        'received_date',  # Not in FM-EN-04
        'expected_completion_date',  # Not in FM-EN-04
        'issue_severity',  # Not in FM-EN-04
        'engineer_signature',  # Duplicate section
        'approval_notes',  # Old field
        'approval_signature',  # Old field
        'approval_section',  # Old section
        'approved_by',  # Old field
        'approval_time',  # Old field
        'approval_timestamp',  # Old field
    ]

    hidden_count = 0
    for fieldname in fields_to_hide:
        if frappe.db.exists('Custom Field', f'Asset Repair-{fieldname}'):
            doc = frappe.get_doc('Custom Field', f'Asset Repair-{fieldname}')
            doc.hidden = 1
            doc.save(ignore_permissions=True)
            hidden_count += 1
            print(f"🙈 Hidden: {fieldname}")

    # Fix field positions that are still wrong
    fixes = [
        # Move description to Section 1
        ('description', 'repair_subject', 'Description (Error Description)'),
        ('issue_photos', 'description', 'Issue Photos (รูปถ่ายปัญหา)'),
        ('reported_by', 'issue_photos', 'Reported By (Inspector)'),
        ('reporter_department', 'reported_by', 'Reporter Department'),
        ('reporter_signature', 'reporter_department', 'Reporter Signature'),
    ]

    fixed_count = 0
    for fieldname, insert_after, label in fixes:
        # Check if it's a custom field
        if frappe.db.exists('Custom Field', f'Asset Repair-{fieldname}'):
            doc = frappe.get_doc('Custom Field', f'Asset Repair-{fieldname}')
            doc.insert_after = insert_after
            if label:
                doc.label = label
            doc.save(ignore_permissions=True)
            fixed_count += 1
            print(f"📌 Fixed position: {fieldname}")

    # Hide standard ERPNext sections we don't need
    standard_sections_to_hide = [
        'repair_details_section',  # "Repair Details" section
        'section_break_10',  # Random section breaks
        'section_break_20',
    ]

    # Note: Can't hide standard fields via Custom Field, need Property Setter
    for section in standard_sections_to_hide:
        if not frappe.db.exists('Property Setter', {
            'doc_type': 'Asset Repair',
            'field_name': section,
            'property': 'hidden'
        }):
            frappe.get_doc({
                'doctype': 'Property Setter',
                'doc_type': 'Asset Repair',
                'field_name': section,
                'property': 'hidden',
                'value': '1',
                'property_type': 'Check'
            }).insert(ignore_permissions=True)
            print(f"🙈 Hidden standard section: {section}")

    frappe.db.commit()

    print()
    print("=" * 60)
    print(f"✅ Cleanup complete!")
    print(f"   Hidden: {hidden_count} duplicate/old fields")
    print(f"   Fixed: {fixed_count} field positions")
    print()
    print("🔄 Run: bench --site tub clear-cache")
    print("🔄 Then refresh browser")
    print("=" * 60)
