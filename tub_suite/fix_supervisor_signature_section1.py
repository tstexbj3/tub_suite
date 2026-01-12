"""
Fix Section 1 supervisor signature - supervisor signs to verify the report
"""
import frappe

def fix():
    """Ensure supervisor signature fields exist in Section 1B"""

    print("🔧 Setting up Supervisor signature for Section 1...")

    # STEP 1: Ensure Section 1B break exists (Supervisor Verification)
    if not frappe.db.exists('Custom Field', 'Asset Repair-section_1b_break'):
        frappe.get_doc({
            'doctype': 'Custom Field',
            'dt': 'Asset Repair',
            'fieldname': 'section_1b_break',
            'label': 'Supervisor Verification (หัวหน้าแผนกตรวจสอบ)',
            'fieldtype': 'Section Break',
            'insert_after': 'reporter_department',
            'collapsible': 1,
            'depends_on': 'eval:doc.workflow_state=="Pending Reporter Supervisor Verification" && doc.reporter_confirmed != 1'
        }).insert(ignore_permissions=True)
        print("✅ Created: Section 1B - Supervisor Verification")
    else:
        # Update existing
        doc = frappe.get_doc('Custom Field', 'Asset Repair-section_1b_break')
        doc.insert_after = 'reporter_department'
        doc.depends_on = 'eval:doc.workflow_state=="Pending Reporter Supervisor Verification" && doc.reporter_confirmed != 1'
        doc.label = 'Supervisor Verification (หัวหน้าแผนกตรวจสอบ)'
        doc.save(ignore_permissions=True)
        print("📝 Updated: Section 1B positioning")

    # STEP 2: Create/update supervisor_section1_notes
    if not frappe.db.exists('Custom Field', 'Asset Repair-supervisor_section1_notes'):
        frappe.get_doc({
            'doctype': 'Custom Field',
            'dt': 'Asset Repair',
            'fieldname': 'supervisor_section1_notes',
            'label': 'Supervisor Notes (หมายเหตุหัวหน้า)',
            'fieldtype': 'Small Text',
            'insert_after': 'section_1b_break',
            'depends_on': 'eval:doc.workflow_state=="Pending Reporter Supervisor Verification" && doc.reporter_confirmed != 1'
        }).insert(ignore_permissions=True)
        print("✅ Created: supervisor_section1_notes")
    else:
        doc = frappe.get_doc('Custom Field', 'Asset Repair-supervisor_section1_notes')
        doc.insert_after = 'section_1b_break'
        doc.depends_on = 'eval:doc.workflow_state=="Pending Reporter Supervisor Verification" && doc.reporter_confirmed != 1'
        doc.save(ignore_permissions=True)
        print("📝 Updated: supervisor_section1_notes")

    # STEP 3: Create/update supervisor_section1_signature
    if not frappe.db.exists('Custom Field', 'Asset Repair-supervisor_section1_signature'):
        frappe.get_doc({
            'doctype': 'Custom Field',
            'dt': 'Asset Repair',
            'fieldname': 'supervisor_section1_signature',
            'label': 'Supervisor Signature (ลายเซ็นหัวหน้า)',
            'fieldtype': 'Signature',
            'insert_after': 'supervisor_section1_notes',
            'depends_on': 'eval:doc.workflow_state=="Pending Reporter Supervisor Verification" && doc.reporter_confirmed != 1'
        }).insert(ignore_permissions=True)
        print("✅ Created: supervisor_section1_signature")
    else:
        doc = frappe.get_doc('Custom Field', 'Asset Repair-supervisor_section1_signature')
        doc.insert_after = 'supervisor_section1_notes'
        doc.depends_on = 'eval:doc.workflow_state=="Pending Reporter Supervisor Verification" && doc.reporter_confirmed != 1'
        doc.save(ignore_permissions=True)
        print("📝 Updated: supervisor_section1_signature")

    # STEP 4: Keep reporter_signature hidden (operators don't sign when reporting via portal)
    if frappe.db.exists('Custom Field', 'Asset Repair-reporter_signature'):
        doc = frappe.get_doc('Custom Field', 'Asset Repair-reporter_signature')
        doc.hidden = 1
        doc.save(ignore_permissions=True)
        print("🙈 Kept hidden: reporter_signature (not used in portal workflow)")

    frappe.db.commit()

    print()
    print("=" * 60)
    print("✅ Section 1 Supervisor signature configured!")
    print()
    print("📋 Section 1 flow:")
    print("   1. Operator fills form via portal (no signature)")
    print("   2. Doc goes to 'Pending Reporter Supervisor Verification'")
    print("   3. Supervisor sees Section 1B with:")
    print("      - Supervisor Notes field")
    print("      - Supervisor Signature field")
    print("   4. Supervisor signs and approves → goes to GM")
    print()
    print("🔄 Run: bench --site tub clear-cache")
    print("🔄 Then refresh browser and test!")
    print("=" * 60)
