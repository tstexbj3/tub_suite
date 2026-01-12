"""
Set up conditional field visibility based on workflow state
This makes sections appear/disappear based on where the repair is in the workflow
"""
import frappe

def setup():
    """Configure depends_on for all sections based on workflow state"""

    print("👁️  Setting up conditional visibility for Asset Repair sections...")

    # Define visibility rules for each section
    visibility_rules = [
        # SECTION 1: Always visible (Draft and first approvals)
        ('section_1_break', None),  # Always show

        # SECTION 1B: Supervisor Verification - only in "Pending Reporter Supervisor Verification" state
        ('section_1b_break', 'eval:doc.workflow_state=="Pending Reporter Supervisor Verification" && !doc.__islocal'),
        ('supervisor_section1_notes', 'eval:doc.workflow_state=="Pending Reporter Supervisor Verification"'),
        ('supervisor_section1_signature', 'eval:doc.workflow_state=="Pending Reporter Supervisor Verification"'),

        # SECTION 1C: GM Approval Section 1
        ('section_1c_break', 'eval:doc.workflow_state=="Pending GM Approval Section 1" && !doc.__islocal'),
        ('gm_section1_notes', 'eval:doc.workflow_state=="Pending GM Approval Section 1"'),
        ('gm_section1_signature', 'eval:doc.workflow_state=="Pending GM Approval Section 1"'),

        # SECTION 2: Engineering Department - show after GM approves Section 1
        ('section_2_break', 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'),
        ('action_type', 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'),
        ('engineering_todo_items', 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'),
        ('spare_parts_used', 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'),
        ('expected_duration_days', 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'),
        ('repair_start_date', 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'),
        ('repair_end_date', 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'),
        ('engineering_operator_signature', 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'),

        # SECTION 2B: Engineering Supervisor Review
        ('section_2b_break', 'eval:["Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'),
        ('eng_supervisor_signature', 'eval:["Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'),
        ('eng_supervisor_reviewed_by', 'eval:["Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'),
        ('eng_supervisor_review_date', 'eval:["Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'),

        # SECTION 2C: GM Final Approval
        ('section_2c_break', 'eval:["Pending GM Final Approval","Approved for Repair","Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'),
        ('gm_final_notes', 'eval:["Pending GM Final Approval","Approved for Repair","Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'),
        ('gm_final_signature', 'eval:["Pending GM Final Approval","Approved for Repair","Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'),

        # SECTION 2D: Repair Completion
        ('section_2d_break', 'eval:["Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'),
        ('actions_performed', 'eval:["Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'),
        ('completion_date', 'eval:["Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'),

        # SECTION 3A: Reporter Confirmation - show after repair complete
        ('section_3a_break', 'eval:["Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'),
        ('reporter_confirmed', 'eval:["Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'),
        ('reporter_confirmation_photos', 'eval:["Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'),
        ('reporter_confirmation_notes', 'eval:["Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'),
        ('reporter_satisfaction', 'eval:["Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'),

        # SECTION 3B: Hygiene & Safety - only in last supervisor verification
        ('section_3b_break', 'eval:doc.workflow_state=="Pending Reporter Supervisor Verification" || doc.workflow_state=="Finished"'),
        ('hygiene_status', 'eval:doc.workflow_state=="Pending Reporter Supervisor Verification" || doc.workflow_state=="Finished"'),
        ('cleanliness_before_machine', 'eval:doc.workflow_state=="Pending Reporter Supervisor Verification" || doc.workflow_state=="Finished"'),
        ('cleanliness_after_machine', 'eval:doc.workflow_state=="Pending Reporter Supervisor Verification" || doc.workflow_state=="Finished"'),
        ('cleanliness_before_area', 'eval:doc.workflow_state=="Pending Reporter Supervisor Verification" || doc.workflow_state=="Finished"'),
        ('cleanliness_after_area', 'eval:doc.workflow_state=="Pending Reporter Supervisor Verification" || doc.workflow_state=="Finished"'),
        ('parts_inserted', 'eval:doc.workflow_state=="Pending Reporter Supervisor Verification" || doc.workflow_state=="Finished"'),
        ('parts_removed', 'eval:doc.workflow_state=="Pending Reporter Supervisor Verification" || doc.workflow_state=="Finished"'),
        ('supervisor_verification_notes', 'eval:doc.workflow_state=="Pending Reporter Supervisor Verification" || doc.workflow_state=="Finished"'),
        ('supervisor_signature', 'eval:doc.workflow_state=="Pending Reporter Supervisor Verification" || doc.workflow_state=="Finished"'),

        # SECTION 4: Final Remarks - always visible
        ('section_4_break', None),
        ('final_remarks', None),
    ]

    updated_count = 0
    not_found = []

    for fieldname, depends_on in visibility_rules:
        if frappe.db.exists('Custom Field', f'Asset Repair-{fieldname}'):
            doc = frappe.get_doc('Custom Field', f'Asset Repair-{fieldname}')

            if depends_on:
                doc.depends_on = depends_on
                print(f"👁️  {fieldname}: Show when {depends_on}")
            else:
                doc.depends_on = None
                print(f"👁️  {fieldname}: Always visible")

            doc.save(ignore_permissions=True)
            updated_count += 1
        else:
            not_found.append(fieldname)

    frappe.db.commit()

    print()
    print("=" * 60)
    print(f"✅ Conditional visibility configured!")
    print(f"   Updated: {updated_count} fields")
    if not_found:
        print(f"   ⚠️  Not found: {len(not_found)} fields")
        print(f"   Fields: {', '.join(not_found)}")
    print()
    print("📋 Now sections will show/hide based on workflow state:")
    print("   • Draft: Show Section 1 only")
    print("   • Pending Supervisor: Show Section 1 + approval fields")
    print("   • Pending GM Section 1: Show Section 1 + GM approval")
    print("   • Engineering states: Show Section 1 + Section 2")
    print("   • After repair: Show Section 3 (Reporter confirmation + Hygiene)")
    print()
    print("🔄 Run: bench --site tub clear-cache")
    print("🔄 Then refresh browser and test each workflow state!")
    print("=" * 60)
