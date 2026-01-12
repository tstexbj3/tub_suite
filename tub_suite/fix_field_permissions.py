"""
Fix field permissions and visibility for proper FM-EN-04 workflow
"""
import frappe

def fix():
    """Fix field permissions and read-only settings"""

    print("🔒 Fixing field permissions and visibility...")

    # STEP 1: Hide "Repair Details" section break (standard ERPNext section)
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
        print("🙈 Hidden: Repair Details section")

    # STEP 2: Move failure_date to Section 1 (after repair_source)
    if not frappe.db.exists('Property Setter', {
        'doc_type': 'Asset Repair',
        'field_name': 'failure_date',
        'property': 'insert_after'
    }):
        frappe.get_doc({
            'doctype': 'Property Setter',
            'doc_type': 'Asset Repair',
            'field_name': 'failure_date',
            'property': 'insert_after',
            'value': 'repair_source',
            'property_type': 'Data'
        }).insert(ignore_permissions=True)
        print("📌 Moved: failure_date to Section 1")

    # Make it visible
    if not frappe.db.exists('Property Setter', {
        'doc_type': 'Asset Repair',
        'field_name': 'failure_date',
        'property': 'hidden'
    }):
        frappe.get_doc({
            'doctype': 'Property Setter',
            'doc_type': 'Asset Repair',
            'field_name': 'failure_date',
            'property': 'hidden',
            'value': '0',
            'property_type': 'Check'
        }).insert(ignore_permissions=True)

    # STEP 3: Move issue_severity to Section 2 (Engineering assessment)
    # And make it visible only during engineering states
    if not frappe.db.exists('Property Setter', {
        'doc_type': 'Asset Repair',
        'field_name': 'issue_severity',
        'property': 'insert_after'
    }):
        frappe.get_doc({
            'doctype': 'Property Setter',
            'doc_type': 'Asset Repair',
            'field_name': 'issue_severity',
            'property': 'insert_after',
            'value': 'section_2_break',
            'property_type': 'Data'
        }).insert(ignore_permissions=True)
        print("📌 Moved: issue_severity to Section 2")

    # Make it conditional - only show in engineering states
    if not frappe.db.exists('Property Setter', {
        'doc_type': 'Asset Repair',
        'field_name': 'issue_severity',
        'property': 'depends_on'
    }):
        frappe.get_doc({
            'doctype': 'Property Setter',
            'doc_type': 'Asset Repair',
            'field_name': 'issue_severity',
            'property': 'depends_on',
            'value': 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)',
            'property_type': 'Data'
        }).insert(ignore_permissions=True)
        print("👁️  issue_severity: Only visible during/after engineering assessment")

    # STEP 4: Make repair_status read-only (auto-updated by workflow)
    if not frappe.db.exists('Property Setter', {
        'doc_type': 'Asset Repair',
        'field_name': 'repair_status',
        'property': 'read_only'
    }):
        frappe.get_doc({
            'doctype': 'Property Setter',
            'doc_type': 'Asset Repair',
            'field_name': 'repair_status',
            'property': 'read_only',
            'value': '1',
            'property_type': 'Check'
        }).insert(ignore_permissions=True)
        print("🔒 Made read-only: repair_status (auto-updated by workflow)")

    # Move repair_status to top (after asset_name)
    if not frappe.db.exists('Property Setter', {
        'doc_type': 'Asset Repair',
        'field_name': 'repair_status',
        'property': 'insert_after'
    }):
        frappe.get_doc({
            'doctype': 'Property Setter',
            'doc_type': 'Asset Repair',
            'field_name': 'repair_status',
            'property': 'insert_after',
            'value': 'asset_name',
            'property_type': 'Data'
        }).insert(ignore_permissions=True)
        print("📌 Moved: repair_status to top (after asset_name)")

    # STEP 5: Make workflow_state visible but read-only (so users can see current state)
    if frappe.db.exists('Custom Field', 'Asset Repair-workflow_state'):
        doc = frappe.get_doc('Custom Field', 'Asset Repair-workflow_state')
        doc.hidden = 0
        doc.read_only = 1
        doc.insert_after = 'repair_status'
        doc.save(ignore_permissions=True)
        print("👁️  workflow_state: Visible and read-only")

    frappe.db.commit()

    print()
    print("=" * 60)
    print("✅ Field permissions fixed!")
    print()
    print("📋 Changes:")
    print("   • failure_date → Moved to Section 1 (reporter fills)")
    print("   • issue_severity → Moved to Section 2 (engineering fills)")
    print("   • repair_status → Read-only, auto-updated by workflow")
    print("   • workflow_state → Visible so users can see current state")
    print()
    print("🔄 Run: bench --site tub clear-cache")
    print("🔄 Then refresh browser")
    print("=" * 60)
