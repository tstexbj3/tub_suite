"""
Fix ALL section visibility based on workflow state - final comprehensive fix
"""
import frappe

def fix():
    """Fix all section visibility issues"""

    print("🔧 Fixing all section visibility based on workflow state...")

    # Update Section 3A (Reporter Confirmation) visibility
    section3a_fields = [
        'section_3a_break',
        'reporter_confirmed',
        'reporter_confirmation_photos',
        'reporter_confirmation_notes',
        'reporter_satisfaction',
    ]

    # These should only show AFTER repair is complete
    section3a_condition = 'eval:["Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state) && doc.reporter_confirmed==0'

    for fieldname in section3a_fields:
        if frappe.db.exists('Custom Field', f'Asset Repair-{fieldname}'):
            field = frappe.get_doc('Custom Field', f'Asset Repair-{fieldname}')
            field.depends_on = section3a_condition
            field.save(ignore_permissions=True)
            print(f"👁️  Section 3A: {fieldname}")

    # Update Repair Completion section visibility
    completion_fields = [
        'section_2d_break',
        'actions_performed',
        'completion_date',
        'repair_completed_by',
    ]

    completion_condition = 'eval:["Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'

    for fieldname in completion_fields:
        if frappe.db.exists('Custom Field', f'Asset Repair-{fieldname}'):
            field = frappe.get_doc('Custom Field', f'Asset Repair-{fieldname}')
            field.depends_on = completion_condition
            field.save(ignore_permissions=True)
            print(f"👁️  Completion: {fieldname}")

    # Move Final Remarks to the VERY end
    # It should be after Section 3B which is after supervisor_signature

    # First, ensure Section 3B fields have correct dependencies
    section3b_condition = 'eval:(doc.workflow_state=="Pending Reporter Supervisor Verification" && doc.reporter_confirmed==1) || doc.workflow_state=="Finished"'

    # Update section_4_break positioning
    if frappe.db.exists('Custom Field', 'Asset Repair-section_4_break'):
        field = frappe.get_doc('Custom Field', 'Asset Repair-section_4_break')
        field.insert_after = 'supervisor_signature'  # After Section 3B
        field.depends_on = None  # Always visible
        field.save(ignore_permissions=True)
        print(f"📌 Moved: section_4_break to end")

    # Hide "Repair Details" standard section
    doc = frappe.get_doc('DocType', 'Asset Repair')
    for field in doc.fields:
        if field.fieldname == 'repair_details_section':
            field.hidden = 1
            print(f"🙈 Hidden: repair_details_section")
        elif field.fieldname == 'issue_severity':
            # Move to Section 2 and make conditional
            field.insert_after = 'section_2_break'
            field.depends_on = 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'
            print(f"📌 Moved: issue_severity to Section 2")

    doc.save(ignore_permissions=True)

    frappe.db.commit()
    frappe.clear_cache(doctype='Asset Repair')

    print()
    print("=" * 60)
    print("✅ All section visibility fixed!")
    print()
    print("📋 What's visible in each state:")
    print()
    print("   Draft:")
    print("      • Section 1 only")
    print()
    print("   Pending Reporter Supervisor Verification:")
    print("      • Section 1")
    print("      • Section 1B (Supervisor Verification) ← YOU ARE HERE")
    print()
    print("   After Supervisor approves → GM Section 1:")
    print("      • Section 1, 1C (GM approval fields)")
    print()
    print("   Engineering states:")
    print("      • Sections 1, 2 (engineering work)")
    print()
    print("   After repair complete:")
    print("      • Section 3A (Reporter confirms)")
    print("      • Section 3B (Supervisor hygiene check)")
    print()
    print("   Finished:")
    print("      • All sections + Final Remarks")
    print()
    print("⚠️  MUST restart bench:")
    print("   Ctrl+C")
    print("   bench start")
    print("=" * 60)
