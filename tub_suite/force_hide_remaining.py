"""
Force hide the remaining visible sections
"""
import frappe

def fix():
    """Force hide Repair Details and Repair Completion sections"""

    print("🔧 Force hiding remaining sections...")

    # Get DocType and modify standard fields
    doc = frappe.get_doc('DocType', 'Asset Repair')

    changes = 0
    for field in doc.fields:
        if field.fieldname == 'repair_details_section':
            if not field.hidden:
                field.hidden = 1
                changes += 1
                print(f"🙈 Hiding: repair_details_section")

    if changes > 0:
        doc.save(ignore_permissions=True)
        print(f"✅ Saved DocType changes")

    # Hide Repair Completion section break
    if frappe.db.exists('Custom Field', 'Asset Repair-section_2d_break'):
        field = frappe.get_doc('Custom Field', 'Asset Repair-section_2d_break')
        field.hidden = 1
        field.save(ignore_permissions=True)
        print(f"🙈 Hidden: section_2d_break (Repair Completion)")

    # Hide GM Final Notes if it's showing outside its section
    if frappe.db.exists('Custom Field', 'Asset Repair-gm_final_notes'):
        field = frappe.get_doc('Custom Field', 'Asset Repair-gm_final_notes')
        field.depends_on = 'eval:["Pending GM Final Approval","Approved for Repair","Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'
        field.save(ignore_permissions=True)
        print(f"👁️  Conditional: gm_final_notes")

    frappe.db.commit()

    # Force clear all caches
    frappe.clear_cache(doctype='Asset Repair')
    from frappe.desk.form.load import get_meta
    get_meta.clear_cache()

    print()
    print("=" * 60)
    print("✅ Forced hiding complete!")
    print()
    print("⚠️  CRITICAL: You MUST do these steps:")
    print("   1. Stop bench (Ctrl+C)")
    print("   2. bench start")
    print("   3. Hard refresh browser (Ctrl+Shift+R)")
    print()
    print("   If still showing after restart, the fields might be")
    print("   hardcoded in the form layout. We may need to use")
    print("   Customize Form UI to manually hide them.")
    print("=" * 60)
