"""
Final cleanup - hide remaining problem sections and fix supervisor visibility
"""
import frappe

def cleanup():
    """Final form cleanup"""

    print("🧹 Final form cleanup...")

    # STEP 1: Hide "Repair Details" section via DocType modification
    doc = frappe.get_doc('DocType', 'Asset Repair')

    for field in doc.fields:
        if field.fieldname == 'repair_details_section':
            field.hidden = 1
            print("🙈 Hidden: repair_details_section")
        elif field.fieldname == 'issue_severity':
            # Move it after section_2_break
            field.insert_after = 'section_2_break'
            field.depends_on = 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'
            print("📌 Moved: issue_severity to Section 2")

    doc.save(ignore_permissions=True)

    # STEP 2: Hide old "Section 2: Spare Parts" and "Engineer Signature"
    if frappe.db.exists('Custom Field', 'Asset Repair-spare_parts_section_break'):
        field = frappe.get_doc('Custom Field', 'Asset Repair-spare_parts_section_break')
        field.hidden = 1
        field.save(ignore_permissions=True)
        print("🙈 Hidden: spare_parts_section_break")

    if frappe.db.exists('Custom Field', 'Asset Repair-engineer_signature'):
        field = frappe.get_doc('Custom Field', 'Asset Repair-engineer_signature')
        field.hidden = 1
        field.save(ignore_permissions=True)
        print("🙈 Hidden: engineer_signature")

    # STEP 3: Fix Section 1B visibility - simplify the depends_on
    if frappe.db.exists('Custom Field', 'Asset Repair-section_1b_break'):
        field = frappe.get_doc('Custom Field', 'Asset Repair-section_1b_break')
        # Show in first Pending Reporter Supervisor Verification state only
        # Use a simpler condition
        field.depends_on = 'eval:doc.workflow_state=="Pending Reporter Supervisor Verification"'
        field.collapsible = 0  # Don't collapse
        field.save(ignore_permissions=True)
        print("👁️  Fixed: section_1b_break visibility")

    if frappe.db.exists('Custom Field', 'Asset Repair-supervisor_section1_notes'):
        field = frappe.get_doc('Custom Field', 'Asset Repair-supervisor_section1_notes')
        field.depends_on = 'eval:doc.workflow_state=="Pending Reporter Supervisor Verification"'
        field.save(ignore_permissions=True)

    if frappe.db.exists('Custom Field', 'Asset Repair-supervisor_section1_signature'):
        field = frappe.get_doc('Custom Field', 'Asset Repair-supervisor_section1_signature')
        field.depends_on = 'eval:doc.workflow_state=="Pending Reporter Supervisor Verification"'
        field.save(ignore_permissions=True)

    # STEP 4: Move Final Remarks to end
    if frappe.db.exists('Custom Field', 'Asset Repair-final_remarks'):
        field = frappe.get_doc('Custom Field', 'Asset Repair-final_remarks')
        # Find the last section's last field - supervisor_signature in Section 3
        field.insert_after = 'supervisor_signature'
        field.depends_on = None  # Always show
        field.save(ignore_permissions=True)
        print("📌 Moved: final_remarks to end")

    if frappe.db.exists('Custom Field', 'Asset Repair-section_4_break'):
        field = frappe.get_doc('Custom Field', 'Asset Repair-section_4_break')
        field.insert_after = 'supervisor_signature'
        field.depends_on = None  # Always show
        field.save(ignore_permissions=True)
        print("📌 Moved: Final Remarks section to end")

    frappe.db.commit()
    frappe.clear_cache(doctype='Asset Repair')

    print()
    print("=" * 60)
    print("✅ Final cleanup complete!")
    print()
    print("📋 What was fixed:")
    print("   • Hidden: Repair Details section")
    print("   • Hidden: Old Section 2 Spare Parts")
    print("   • Hidden: engineer_signature")
    print("   • Fixed: Supervisor Verification section visibility")
    print("   • Moved: issue_severity to Section 2")
    print("   • Moved: Final Remarks to end")
    print()
    print("🔄 Run: bench --site tub clear-cache")
    print("🔄 Then refresh browser")
    print()
    print("📝 Note: Supervisor Verification section will ONLY show when:")
    print("   workflow_state = 'Pending Reporter Supervisor Verification'")
    print("=" * 60)
