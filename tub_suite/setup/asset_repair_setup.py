# Copyright (c) 2024, Tipubon International Co.,Ltd. and contributors
# For license information, please see license.txt

"""
Production Setup Script for Asset Repair Maintenance Portal
Run this ONCE after deploying to production

Usage:
    bench --site your_site execute tub_suite.setup.asset_repair_setup.run_production_setup
"""

import frappe
from frappe import _


def run_production_setup():
    """
    Complete setup for Asset Repair maintenance workflow
    Run this once on production after deployment
    """
    print("\n" + "="*70)
    print("TUB Suite - Asset Repair Production Setup")
    print("="*70 + "\n")

    results = []

    # 1. Fix severity field options
    results.append(fix_severity_field())

    # 2. Set field properties
    results.append(set_field_readonly_properties())

    # 3. Create server script for field locking
    results.append(create_field_locking_server_script())

    # 4. Create client script for UI behavior
    results.append(create_ui_client_script())

    # Commit all changes
    frappe.db.commit()
    frappe.clear_cache()

    print("\n" + "="*70)
    print("Setup Results:")
    print("="*70)
    for result in results:
        print(result)
    print("="*70 + "\n")

    return {
        "success": True,
        "results": results
    }


def fix_severity_field():
    """Remove blank option from severity field"""
    try:
        if frappe.db.exists("Custom Field", {"dt": "Asset Repair", "fieldname": "issue_severity"}):
            cf = frappe.get_doc("Custom Field", {"dt": "Asset Repair", "fieldname": "issue_severity"})
            cf.options = "Minor - Asset Operational\nMajor - Asset Must Stop"
            cf.default = "Minor - Asset Operational"
            cf.save()
            return "✓ Severity field options fixed"
        return "⚠ Severity field not found (custom fields may not be imported yet)"
    except Exception as e:
        return f"✗ Severity field error: {str(e)}"


def set_field_readonly_properties():
    """Set read-only properties on protected fields"""
    try:
        fields_to_lock = [
            'failure_date',
            'description',
            'reported_by'
        ]

        for field in fields_to_lock:
            set_property("Asset Repair", field, "read_only", 1)

        return f"✓ Locked {len(fields_to_lock)} fields (failure_date, description, reported_by)"
    except Exception as e:
        return f"✗ Field properties error: {str(e)}"


def create_field_locking_server_script():
    """Create server-side validation to prevent field editing"""
    try:
        script_name = "Asset Repair - Lock Reporter Fields"

        script_code = """# Lock fields that reporters submitted - prevent engineers from changing
if not doc.is_new():
    old_doc = frappe.get_doc("Asset Repair", doc.name)

    # Fields that cannot be changed after creation
    protected_fields = ['failure_date', 'description', 'reported_by']

    for field in protected_fields:
        old_val = old_doc.get(field)
        new_val = doc.get(field)
        if str(old_val or '') != str(new_val or ''):
            frappe.throw(f"Cannot modify {field.replace('_', ' ').title()} - this field is locked and set by the inspector")
"""

        if frappe.db.exists("Server Script", script_name):
            doc = frappe.get_doc("Server Script", script_name)
            doc.script = script_code
            doc.enabled = 1
            doc.save()
            return "✓ Server Script updated (field locking)"
        else:
            frappe.get_doc({
                "doctype": "Server Script",
                "name": script_name,
                "script_type": "DocType Event",
                "doctype_event": "Before Save",
                "reference_doctype": "Asset Repair",
                "enabled": 1,
                "script": script_code
            }).insert()
            return "✓ Server Script created (field locking)"

    except Exception as e:
        return f"✗ Server Script error: {str(e)}"


def create_ui_client_script():
    """Create client-side script for UI behavior"""
    try:
        script_name = "Asset Repair - Field Locking UI"

        script_code = """// Asset Repair - UI Field Behavior
frappe.ui.form.on('Asset Repair', {
    refresh: function(frm) {
        // Always lock reporter fields in UI
        frm.set_df_property('failure_date', 'read_only', 1);
        frm.set_df_property('description', 'read_only', 1);
        frm.set_df_property('reported_by', 'read_only', 1);

        // Lock completion_date until repair is completed
        if (frm.doc.repair_status !== 'Completed') {
            frm.set_df_property('completion_date', 'read_only', 1);
        }

        // Check user roles
        var user_roles = frappe.user_roles;
        var is_inspector = user_roles.includes('Maintenance User');  // Actual inspector role
        var is_manager = user_roles.includes('Maintenance Manager') || user_roles.includes('Quality Manager');
        var is_engineer = user_roles.includes('Engineering Team');  // Actual engineer role

        // Get workflow state
        var workflow_state = frm.doc.workflow_state || 'Draft';

        // Lock verification fields for non-inspectors
        if (!is_inspector) {
            frm.set_df_property('verification_notes', 'read_only', 1);
            frm.set_df_property('verification_status', 'read_only', 1);
        }

        // ENGINEER FIELD LOCKING
        if (is_engineer && !is_manager) {
            // CRITICAL: Engineers should NEVER edit manager approval fields
            // But they SHOULD see rejection notes when repair is rejected

            if (workflow_state === 'Rejected') {
                // SHOW manager notes (read-only) so engineer can see rejection reason
                frm.set_df_property('approval_section', 'hidden', 0);
                frm.set_df_property('approval_notes', 'hidden', 0);
                frm.set_df_property('approval_notes', 'read_only', 1);
                frm.set_df_property('approval_timestamp', 'hidden', 0);
                frm.set_df_property('approval_timestamp', 'read_only', 1);
                // Keep signature hidden (not needed for engineer to see)
                frm.set_df_property('approval_signature', 'hidden', 1);
                frm.set_df_property('approval_signature', 'read_only', 1);
            } else {
                // HIDE approval section in all other states (Draft, Pending, Approved, Finished)
                frm.set_df_property('approval_section', 'hidden', 1);
                frm.set_df_property('approval_notes', 'hidden', 1);
                frm.set_df_property('approval_notes', 'read_only', 1);
                frm.set_df_property('approval_signature', 'hidden', 1);
                frm.set_df_property('approval_signature', 'read_only', 1);
                frm.set_df_property('approval_timestamp', 'hidden', 1);
                frm.set_df_property('approval_timestamp', 'read_only', 1);
            }

            // After submitting for approval, lock ALL engineer fields
            // But allow editing in Rejected state so engineer can fix and resubmit
            if (workflow_state !== 'Draft' && workflow_state !== 'Rejected') {
                frm.set_df_property('actions_performed', 'read_only', 1);
                frm.set_df_property('engineer_signature', 'read_only', 1);
                frm.set_df_property('issue_severity', 'read_only', 1);
                frm.set_df_property('asset', 'read_only', 1);
                frm.set_df_property('maintenance_task', 'read_only', 1);
            }
        }

        // MANAGER FIELD LOCKING
        if (is_manager) {
            // Show approval section
            frm.set_df_property('approval_section', 'hidden', 0);
            frm.set_df_property('approval_notes', 'hidden', 0);
            frm.set_df_property('approval_signature', 'hidden', 0);
            frm.set_df_property('approval_timestamp', 'hidden', 0);

            // Lock engineer fields in ALL states (managers can't edit engineer work)
            frm.set_df_property('actions_performed', 'read_only', 1);
            frm.set_df_property('engineer_signature', 'read_only', 1);

            // In Pending Approval or after: Lock approval fields if already approved
            if (frm.doc.approval_timestamp) {
                frm.set_df_property('approval_notes', 'read_only', 1);
                frm.set_df_property('approval_signature', 'read_only', 1);
                frm.set_df_property('approval_timestamp', 'read_only', 1);
            }

            // After Approved/Finished: Lock ALL fields except approval notes (for corrections)
            if (workflow_state === 'Approved' || workflow_state === 'Finished') {
                frm.set_df_property('issue_severity', 'read_only', 1);
                frm.set_df_property('asset', 'read_only', 1);
                frm.set_df_property('maintenance_task', 'read_only', 1);
                // Allow editing approval notes if NOT already approved
                if (!frm.doc.approval_timestamp) {
                    frm.set_df_property('approval_notes', 'read_only', 0);
                    frm.set_df_property('approval_signature', 'read_only', 0);
                }
            }
        }

        // Make engineer signature mandatory before workflow submission
        if (frm.doc.docstatus === 0) {
            frm.set_df_property('engineer_signature', 'reqd', 1);
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

        if frappe.db.exists("Client Script", script_name):
            doc = frappe.get_doc("Client Script", script_name)
            doc.script = script_code
            doc.enabled = 1
            doc.save()
            return "✓ Client Script updated (UI behavior)"
        else:
            frappe.get_doc({
                "doctype": "Client Script",
                "name": script_name,
                "dt": "Asset Repair",
                "enabled": 1,
                "script_type": "Form",
                "script": script_code
            }).insert()
            return "✓ Client Script created (UI behavior)"

    except Exception as e:
        return f"✗ Client Script error: {str(e)}"


def set_property(doctype, fieldname, property_name, value):
    """Helper to set field property using Property Setter"""
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
