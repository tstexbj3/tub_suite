#!/usr/bin/env python3
"""
One-time setup script to install Asset Repair approval fields
Run this via: bench --site tub.x-desk.tech execute tub_suite.install_approval_fields.install
"""
import frappe

def install():
    """Install approval fields for Asset Repair"""
    print("\n" + "="*60)
    print("Installing Asset Repair Approval Fields...")
    print("="*60 + "\n")

    custom_fields = [
        {
            "dt": "Asset Repair",
            "fieldname": "repair_type",
            "fieldtype": "Select",
            "label": "Repair Type",
            "options": "Repair\nPreventive Maintenance\nBreakdown\nInspection\nReplacement",
            "insert_after": "description",
            "allow_on_submit": 0
        },
        {
            "dt": "Asset Repair",
            "fieldname": "approval_section",
            "fieldtype": "Section Break",
            "label": "Approval Details",
            "insert_after": "repair_status",
            "collapsible": 0
        },
        {
            "dt": "Asset Repair",
            "fieldname": "approval_status",
            "fieldtype": "Select",
            "label": "Approval Status",
            "options": "Pending\nApproved\nRejected",
            "default": "Pending",
            "insert_after": "approval_section",
            "in_list_view": 1,
            "in_standard_filter": 1,
            "read_only": 0,
            "allow_on_submit": 1
        },
        {
            "dt": "Asset Repair",
            "fieldname": "approval_column",
            "fieldtype": "Column Break",
            "insert_after": "approval_status"
        },
        {
            "dt": "Asset Repair",
            "fieldname": "approved_by",
            "fieldtype": "Link",
            "label": "Approved By",
            "options": "User",
            "insert_after": "approval_column",
            "read_only": 1,
            "allow_on_submit": 1
        },
        {
            "dt": "Asset Repair",
            "fieldname": "approval_time",
            "fieldtype": "Datetime",
            "label": "Approval Date & Time",
            "insert_after": "approved_by",
            "read_only": 1,
            "allow_on_submit": 1,
            "description": "Server timestamp - cannot be modified"
        },
        {
            "dt": "Asset Repair",
            "fieldname": "approval_notes_break",
            "fieldtype": "Section Break",
            "insert_after": "approval_time"
        },
        {
            "dt": "Asset Repair",
            "fieldname": "approval_notes",
            "fieldtype": "Small Text",
            "label": "Approval Notes",
            "insert_after": "approval_notes_break",
            "allow_on_submit": 1,
            "description": "Manager can add notes when approving/rejecting"
        },
        {
            "dt": "Asset Repair",
            "fieldname": "approval_signature_break",
            "fieldtype": "Column Break",
            "insert_after": "approval_notes"
        },
        {
            "dt": "Asset Repair",
            "fieldname": "approval_signature",
            "fieldtype": "Signature",
            "label": "Manager Signature",
            "insert_after": "approval_signature_break",
            "allow_on_submit": 1
        }
    ]

    created = 0
    updated = 0
    skipped = 0

    for field in custom_fields:
        existing = frappe.db.exists("Custom Field", {
            "dt": field["dt"],
            "fieldname": field["fieldname"]
        })

        if existing:
            try:
                doc = frappe.get_doc("Custom Field", existing)
                doc.update(field)
                doc.save()
                updated += 1
                print(f"✓ Updated: {field['fieldname']}")
            except Exception as e:
                print(f"⚠ Skipped {field['fieldname']}: {str(e)}")
                skipped += 1
        else:
            try:
                custom_field = frappe.get_doc({
                    "doctype": "Custom Field",
                    **field
                })
                custom_field.insert()
                created += 1
                print(f"✓ Created: {field['fieldname']}")
            except Exception as e:
                print(f"⚠ Failed {field['fieldname']}: {str(e)}")
                skipped += 1

    frappe.db.commit()
    frappe.clear_cache(doctype="Asset Repair")

    print("\n" + "="*60)
    print(f"✅ Setup Complete!")
    print(f"   Created: {created} fields")
    print(f"   Updated: {updated} fields")
    if skipped > 0:
        print(f"   Skipped: {skipped} fields")
    print("="*60 + "\n")
    print("Next: Open an Asset Repair document and reload the page.")
    print("You should see the new 'Approval Details' section.\n")

    return {
        "success": True,
        "created": created,
        "updated": updated,
        "skipped": skipped
    }
