"""
Rebuild Asset Repair form from scratch using direct DocType customization
This is more reliable than Property Setters
"""
import frappe
from frappe.custom.doctype.customize_form.customize_form import customize_form

def rebuild():
    """Rebuild Asset Repair form with proper field ordering"""

    print("🔨 Rebuilding Asset Repair form structure...")

    # Get the doctype meta
    doc = frappe.get_doc('DocType', 'Asset Repair')

    print(f"📋 Current field count: {len(doc.fields)}")

    # Find problematic standard fields and update them
    for field in doc.fields:
        # Hide "Repair Details" section
        if field.fieldname == 'repair_details_section':
            field.hidden = 1
            print(f"🙈 Hidden: {field.fieldname}")

        # Move failure_date to after repair_source
        elif field.fieldname == 'failure_date':
            field.insert_after = 'repair_source'
            field.hidden = 0
            print(f"📌 Moved: failure_date → after repair_source")

        # Move issue_severity to Section 2 area and make conditional
        elif field.fieldname == 'issue_severity':
            field.depends_on = 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Repair In Progress","Pending Reporter Confirmation","Pending Reporter Supervisor Verification","Finished"].includes(doc.workflow_state)'
            field.hidden = 0
            print(f"👁️  Conditional: issue_severity (engineering states only)")

        # Make repair_status read-only and move to top
        elif field.fieldname == 'repair_status':
            field.read_only = 1
            field.insert_after = 'asset_name'
            print(f"🔒 Made read-only: repair_status")

        # Move description to Section 1 (after repair_subject)
        elif field.fieldname == 'description':
            field.insert_after = 'repair_subject'
            print(f"📌 Moved: description → after repair_subject")

    # Save the modified doctype
    doc.save(ignore_permissions=True)

    print()
    print("🔄 Clearing cache and reloading...")

    # Clear cache
    frappe.clear_cache(doctype='Asset Repair')

    # Reload the doctype
    frappe.reload_doctype('Asset Repair', force=True)

    frappe.db.commit()

    print()
    print("=" * 60)
    print("✅ Asset Repair form rebuilt!")
    print()
    print("📋 Standard fields updated:")
    print("   • Repair Details section → Hidden")
    print("   • failure_date → Moved to Section 1")
    print("   • description → Moved to Section 1")
    print("   • issue_severity → Conditional (engineering only)")
    print("   • repair_status → Read-only, moved to top")
    print()
    print("⚠️  You MUST restart bench for changes to take effect:")
    print("   Ctrl+C to stop bench")
    print("   Then: bench start")
    print("=" * 60)
