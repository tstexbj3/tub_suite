# Copyright (c) 2024, Tipubon International Co.,Ltd. and contributors
# For license information, please see license.txt

"""
Asset Repair field configuration and permissions
Run these functions via console to configure Asset Repair doctype
"""

import frappe
from frappe import _


@frappe.whitelist()
def configure_asset_repair_fields():
    """
    Configure Asset Repair fields for proper workflow:
    1. Lock failure_date (read-only, auto-set)
    2. Lock error_description (read-only for engineers)
    3. Lock completion_date initially
    4. Remove blank option from severity field
    5. Lock manager approval fields for engineers

    Run this once after installation or upgrade
    """
    results = []

    # 1. Make failure_date read-only
    try:
        set_field_property("Asset Repair", "failure_date", "read_only", 1)
        results.append("✓ failure_date set to read-only")
    except Exception as e:
        results.append(f"✗ failure_date error: {str(e)}")

    # 2. Make error_description read-only
    try:
        set_field_property("Asset Repair", "error_description", "read_only", 1)
        results.append("✓ error_description set to read-only")
    except Exception as e:
        results.append(f"✗ error_description error: {str(e)}")

    # 3. Check if custom severity field exists, update options
    try:
        if frappe.db.exists("Custom Field", {"dt": "Asset Repair", "fieldname": "issue_severity"}):
            cf = frappe.get_doc("Custom Field", {"dt": "Asset Repair", "fieldname": "issue_severity"})
            cf.options = "Minor\nMajor"  # Remove blank option
            cf.save()
            results.append("✓ issue_severity options updated (removed blank)")
        else:
            results.append("ℹ issue_severity custom field not found")
    except Exception as e:
        results.append(f"✗ issue_severity error: {str(e)}")

    # 4. Create Client Script for dynamic field locking
    try:
        script_name = "Asset Repair - Field Locking"

        script_code = """
// Asset Repair - Dynamic Field Locking
frappe.ui.form.on('Asset Repair', {
    refresh: function(frm) {
        // Always lock these fields (set by backend)
        frm.set_df_property('failure_date', 'read_only', 1);
        frm.set_df_property('error_description', 'read_only', 1);

        // Lock manager fields for non-managers
        const is_manager = frappe.user_roles.includes('Maintenance Manager');
        if (!is_manager) {
            frm.set_df_property('approval_notes', 'read_only', 1);
            frm.set_df_property('approval_signature', 'read_only', 1);
        }

        // Lock completion_date until repair is actually completed
        if (frm.doc.repair_status !== 'Completed') {
            frm.set_df_property('completion_date', 'read_only', 1);
        }
    },

    repair_status: function(frm) {
        // Auto-fill completion_date when status changes to Completed
        if (frm.doc.repair_status === 'Completed' && !frm.doc.completion_date) {
            frm.set_value('completion_date', frappe.datetime.now_date());
        }

        // Unlock completion_date when status is Completed
        if (frm.doc.repair_status === 'Completed') {
            frm.set_df_property('completion_date', 'read_only', 0);
        } else {
            frm.set_df_property('completion_date', 'read_only', 1);
        }
    }
});
"""

        existing = frappe.db.exists("Client Script", {"name": script_name})

        if existing:
            doc = frappe.get_doc("Client Script", script_name)
            doc.script = script_code
            doc.enabled = 1
            doc.save()
            results.append("✓ Client Script updated")
        else:
            doc = frappe.get_doc({
                "doctype": "Client Script",
                "name": script_name,
                "dt": "Asset Repair",
                "enabled": 1,
                "script_type": "Form",
                "script": script_code
            })
            doc.insert()
            results.append("✓ Client Script created")

    except Exception as e:
        results.append(f"✗ Client Script error: {str(e)}")

    frappe.db.commit()
    frappe.clear_cache(doctype="Asset Repair")

    return {
        "success": True,
        "results": results,
        "message": "Asset Repair configuration completed. Please reload any open Asset Repair forms."
    }


def set_field_property(doctype, fieldname, property_name, value):
    """Helper to set field property using Property Setter"""
    property_setter_name = f"{doctype}-{fieldname}-{property_name}"

    existing = frappe.db.exists("Property Setter", {
        "doc_type": doctype,
        "field_name": fieldname,
        "property": property_name
    })

    if existing:
        doc = frappe.get_doc("Property Setter", existing)
        doc.value = str(value)
        doc.save()
    else:
        frappe.get_doc({
            "doctype": "Property Setter",
            "doctype_or_field": "DocField",
            "doc_type": doctype,
            "field_name": fieldname,
            "property": property_name,
            "property_type": "Check" if isinstance(value, int) else "Data",
            "value": str(value)
        }).insert()


@frappe.whitelist()
def test_asset_repair_config():
    """Test function to verify Asset Repair configuration"""
    meta = frappe.get_meta("Asset Repair")

    results = {
        "failure_date_readonly": False,
        "error_description_readonly": False,
        "severity_options": None,
        "client_script_exists": False
    }

    # Check field properties
    for field in meta.fields:
        if field.fieldname == "failure_date":
            results["failure_date_readonly"] = field.read_only
        if field.fieldname == "error_description":
            results["error_description_readonly"] = field.read_only

    # Check custom field
    if frappe.db.exists("Custom Field", {"dt": "Asset Repair", "fieldname": "issue_severity"}):
        cf = frappe.get_doc("Custom Field", {"dt": "Asset Repair", "fieldname": "issue_severity"})
        results["severity_options"] = cf.options

    # Check client script
    results["client_script_exists"] = frappe.db.exists("Client Script", {
        "dt": "Asset Repair",
        "enabled": 1,
        "name": "Asset Repair - Field Locking"
    })

    return results
