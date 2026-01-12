"""
Final fix - handle standard ERPNext fields (Repair Details section)
"""
import frappe

def fix():
    """Fix standard fields that can't be modified via Custom Fields"""

    print("🔧 Final fix for standard ERPNext fields...")

    # Get the Asset Repair DocType
    doc = frappe.get_doc('DocType', 'Asset Repair')

    changes_made = 0

    # Modify standard fields directly
    for field in doc.fields:
        # Hide "Repair Details" section break
        if field.fieldname == 'repair_details_section':
            if not field.hidden:
                field.hidden = 1
                changes_made += 1
                print(f"🙈 Hidden: repair_details_section")

        # Move issue_severity to after section_2_break
        elif field.fieldname == 'issue_severity':
            old_position = field.insert_after
            field.insert_after = 'section_2_break'
            if old_position != 'section_2_break':
                changes_made += 1
                print(f"📌 Moved: issue_severity → after section_2_break")

    # Save the doctype
    if changes_made > 0:
        doc.save(ignore_permissions=True)
        print(f"\n✅ Made {changes_made} changes to Asset Repair DocType")

    # Now fix final_remarks positioning
    if frappe.db.exists('Custom Field', 'Asset Repair-final_remarks'):
        remarks = frappe.get_doc('Custom Field', 'Asset Repair-final_remarks')
        # Move to after section_4_break (which should be at the end)
        if remarks.insert_after != 'section_4_break':
            remarks.insert_after = 'section_4_break'
            remarks.save(ignore_permissions=True)
            print("📌 Moved: final_remarks → after section_4_break")

    # Move section_4_break to the end (after supervisor_signature)
    if frappe.db.exists('Custom Field', 'Asset Repair-section_4_break'):
        sec4 = frappe.get_doc('Custom Field', 'Asset Repair-section_4_break')
        if sec4.insert_after != 'supervisor_signature':
            sec4.insert_after = 'supervisor_signature'
            sec4.save(ignore_permissions=True)
            print("📌 Moved: section_4_break → after supervisor_signature (end of form)")

    frappe.db.commit()

    # Clear cache and reload doctype
    frappe.clear_cache(doctype='Asset Repair')
    frappe.reload_doctype('Asset Repair', force=True)

    print()
    print("=" * 60)
    print("✅ Final fixes applied!")
    print()
    print("📋 Changes:")
    print("   • Hidden: Repair Details section")
    print("   • Moved: issue_severity to Section 2")
    print("   • Moved: Final Remarks to end of form")
    print()
    print("⚠️  IMPORTANT: You MUST restart bench for these changes:")
    print()
    print("   1. Press Ctrl+C to stop bench")
    print("   2. Run: bench start")
    print("   3. Refresh browser")
    print()
    print("=" * 60)
