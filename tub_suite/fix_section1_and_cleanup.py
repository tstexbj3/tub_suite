"""
Fix Section 1 - remove reporter signature, hide old sections, move final remarks to end
"""
import frappe

def fix():
    """Fix remaining issues with Asset Repair form"""

    print("🔧 Fixing Section 1 and cleaning up old fields...")

    # STEP 1: Hide reporter_signature from Section 1 (they sign in Section 3A when confirming)
    if frappe.db.exists('Custom Field', 'Asset Repair-reporter_signature'):
        doc = frappe.get_doc('Custom Field', 'Asset Repair-reporter_signature')
        doc.hidden = 1
        doc.save(ignore_permissions=True)
        print("🙈 Hidden: reporter_signature (they sign in Section 3A, not Section 1)")

    # STEP 2: Hide old "Section 2: Spare Parts Used" section break
    old_section2_names = [
        'section_2_spare_parts',
        'spare_parts_section',
        'section_break_spare_parts',
    ]

    for field in old_section2_names:
        if frappe.db.exists('Custom Field', f'Asset Repair-{field}'):
            doc = frappe.get_doc('Custom Field', f'Asset Repair-{field}')
            doc.hidden = 1
            doc.save(ignore_permissions=True)
            print(f"🙈 Hidden old section: {field}")

    # STEP 3: Hide "engineer_signature" field (old/duplicate)
    if frappe.db.exists('Custom Field', 'Asset Repair-engineer_signature'):
        doc = frappe.get_doc('Custom Field', 'Asset Repair-engineer_signature')
        doc.hidden = 1
        doc.save(ignore_permissions=True)
        print("🙈 Hidden: engineer_signature (old field)")

    # STEP 4: Move "Final Remarks" section to the very end
    # First, find all sections to determine the last one
    # Final Remarks should be after supervisor_signature (last field in Section 3B)

    if frappe.db.exists('Custom Field', 'Asset Repair-section_4_break'):
        doc = frappe.get_doc('Custom Field', 'Asset Repair-section_4_break')
        doc.insert_after = 'supervisor_signature'
        doc.collapsible = 0  # Don't collapse final remarks
        doc.save(ignore_permissions=True)
        print("📌 Moved: Final Remarks section to end (after Section 3)")

    if frappe.db.exists('Custom Field', 'Asset Repair-final_remarks'):
        doc = frappe.get_doc('Custom Field', 'Asset Repair-final_remarks')
        doc.insert_after = 'section_4_break'
        doc.save(ignore_permissions=True)
        print("📌 Moved: final_remarks field to end")

    # STEP 5: Hide duplicate "Final Remarks" sections if they exist
    duplicate_final_sections = [
        'final_remarks_section',
        'section_5_break',
        'final_remarks_break',
    ]

    for field in duplicate_final_sections:
        if frappe.db.exists('Custom Field', f'Asset Repair-{field}'):
            doc = frappe.get_doc('Custom Field', f'Asset Repair-{field}')
            doc.hidden = 1
            doc.save(ignore_permissions=True)
            print(f"🙈 Hidden duplicate section: {field}")

    # STEP 6: Ensure "Repair Details" section is still hidden
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
        print("🙈 Hidden: Repair Details section (standard ERPNext)")

    # STEP 7: Add a reporter_confirmation_signature field in Section 3A
    # (For when reporter confirms the repair is done)
    if not frappe.db.exists('Custom Field', 'Asset Repair-reporter_confirmation_signature'):
        frappe.get_doc({
            'doctype': 'Custom Field',
            'dt': 'Asset Repair',
            'fieldname': 'reporter_confirmation_signature',
            'label': 'Reporter Signature (ลายเซ็นผู้แจ้งยืนยัน)',
            'fieldtype': 'Signature',
            'insert_after': 'reporter_satisfaction',
            'depends_on': 'eval:["Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)',
            'description': 'Reporter signs here to confirm repair completion'
        }).insert(ignore_permissions=True)
        print("✅ Created: reporter_confirmation_signature in Section 3A")

    frappe.db.commit()

    print()
    print("=" * 60)
    print("✅ Section 1 and cleanup complete!")
    print()
    print("📋 Changes:")
    print("   • Removed reporter signature from Section 1")
    print("   • Added reporter signature to Section 3A (confirmation)")
    print("   • Moved Final Remarks to end of form")
    print("   • Hidden old 'Section 2: Spare Parts' duplicate")
    print("   • Hidden old 'engineer_signature' field")
    print()
    print("📝 Section 1 now only has:")
    print("   - repair_type, repair_source, failure_date")
    print("   - repair_subject, description, issue_photos")
    print("   - reported_by, reporter_department")
    print("   (No signature - reporter signs later in Section 3A)")
    print()
    print("🔄 Run: bench --site tub clear-cache")
    print("🔄 Then refresh browser")
    print("=" * 60)
