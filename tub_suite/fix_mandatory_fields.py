"""
Fix mandatory fields - make them conditional based on workflow state
"""
import frappe

def fix():
    """Fix mandatory field requirements"""

    print("🔧 Fixing mandatory field requirements...")

    # Fields that should NOT be mandatory in early stages
    # They become mandatory only in their relevant workflow states

    conditional_mandatory = [
        # Engineering fields - mandatory only in engineering states
        ('engineer_signature', 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review"].includes(doc.workflow_state)'),
        ('engineering_operator_signature', 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'),
        ('eng_supervisor_signature', 'eval:["Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'),

        # Supervisor Section 1 - mandatory only in first supervisor verification
        ('supervisor_section1_signature', 'eval:doc.workflow_state=="Pending Reporter Supervisor Verification" && doc.reporter_confirmed != 1'),

        # Section 3 supervisor signature - mandatory only at end
        ('supervisor_signature', 'eval:(doc.workflow_state=="Pending Reporter Supervisor Verification" && doc.reporter_confirmed==1) || doc.workflow_state=="Finished"'),
    ]

    fixed = 0

    for fieldname, mandatory_depends_on in conditional_mandatory:
        if frappe.db.exists('Custom Field', f'Asset Repair-{fieldname}'):
            field = frappe.get_doc('Custom Field', f'Asset Repair-{fieldname}')

            # Remove unconditional mandatory
            if field.reqd:
                field.reqd = 0
                print(f"🔓 Removed mandatory: {fieldname}")

            # Set mandatory_depends_on
            field.mandatory_depends_on = mandatory_depends_on
            field.save(ignore_permissions=True)
            fixed += 1
            print(f"✅ Set conditional mandatory: {fieldname}")

    # Make sure engineer_signature is not mandatory at all (it's old field, should be hidden)
    if frappe.db.exists('Custom Field', 'Asset Repair-engineer_signature'):
        field = frappe.get_doc('Custom Field', 'Asset Repair-engineer_signature')
        field.reqd = 0
        field.mandatory_depends_on = None
        field.hidden = 1  # Hide it completely
        field.save(ignore_permissions=True)
        print(f"🙈 Hidden and removed mandatory: engineer_signature")

    frappe.db.commit()

    print()
    print("=" * 60)
    print(f"✅ Fixed {fixed} mandatory field requirements")
    print()
    print("📋 Now fields are mandatory only when needed:")
    print("   • Draft → No engineering signatures required")
    print("   • Supervisor verifies → supervisor_section1_signature required")
    print("   • Engineering assesses → engineering_operator_signature required")
    print("   • Final supervisor verification → supervisor_signature required")
    print()
    print("🔄 Run: bench --site tub clear-cache")
    print("🔄 Then refresh browser and try Save → Submit again")
    print("=" * 60)
