"""
PERMANENT FIX for Custom Field visibility on Asset Repair.

This patch sets the correct visibility rules for Custom Fields and should be
re-run on EVERY migration to ensure values don't get overwritten by bad fixtures.

Background:
- custom_field.json fixture had wrong/null values for depends_on
- Fixture import was overwriting correct database values
- Solution: Remove Custom Field from fixtures, use this patch instead
- This patch is IDEMPOTENT - safe to run multiple times

Fields fixed (ALL 13 differences found by compare_dev_prod.py):
- received_by, received_date: Always hidden
- final_remarks: Visible only in "Finished"
- cleanliness fields: Visible in "Pending Supervisor Verification" and "Finished"
- parts_inserted, parts_removed: Visible in verification states
- spare_parts_used: Visible in engineering states
- repair_type, repair_source: Read-only rules
"""

import frappe


def execute():
    """Set correct visibility for Asset Repair custom fields."""

    # Configuration: {field_name: {property: value}}
    # Based on comprehensive comparison with DEV (13 differences found)
    custom_field_config = {
        # Hidden fields (signature auto-fills these)
        "Asset Repair-received_by": {
            "hidden": 1,
            "depends_on": None
        },
        "Asset Repair-received_date": {
            "hidden": 1,
            "depends_on": None
        },

        # Final remarks - only in Finished state
        "Asset Repair-final_remarks": {
            "hidden": 0,
            "depends_on": 'eval:doc.workflow_state=="Finished"'
        },

        # Cleanliness fields - visible in verification states
        "Asset Repair-cleanliness_after_area": {
            "depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'
        },
        "Asset Repair-cleanliness_after_machine": {
            "depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'
        },
        "Asset Repair-cleanliness_before_area": {
            "depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'
        },
        "Asset Repair-cleanliness_before_machine": {
            "depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'
        },

        # Parts tables - visible in verification states
        "Asset Repair-parts_inserted": {
            "depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'
        },
        "Asset Repair-parts_removed": {
            "depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'
        },

        # Spare parts - visible in engineering states
        "Asset Repair-spare_parts_used": {
            "depends_on": 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)'
        },

        # Repair type/source - read-only rules
        "Asset Repair-repair_type": {
            "depends_on": 'eval:doc.workflow_state!="Pending Reporter Confirmation"',
            "read_only_depends_on": 'eval:doc.workflow_state!="Draft"'
        },
        "Asset Repair-repair_source": {
            "read_only_depends_on": 'eval:doc.workflow_state!="Draft"'
        },

        # Section breaks
        "Asset Repair-section_3b_break": {
            "hidden": 0,
            "depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'
        },
        "Asset Repair-fm_en_04_section_5": {
            "hidden": 0,
            "depends_on": 'eval:doc.workflow_state=="Finished"'
        }
    }

    updated_count = 0

    for field_name, properties in custom_field_config.items():
        if not frappe.db.exists("Custom Field", field_name):
            print(f"Custom Field {field_name} not found, skipping...")
            continue

        # Get the Custom Field document
        doc = frappe.get_doc("Custom Field", field_name)

        # Track if anything changed
        changed = False

        # Update properties
        for prop, value in properties.items():
            current_value = getattr(doc, prop, None)
            if current_value != value:
                setattr(doc, prop, value)
                changed = True
                print(f"Updated {field_name}.{prop}: {current_value} → {value}")

        # Save if changed
        if changed:
            doc.save()
            updated_count += 1

    # Commit changes
    if updated_count > 0:
        frappe.db.commit()
        print(f"Successfully updated {updated_count} Custom Fields")

        # Clear cache
        frappe.clear_cache(doctype="Asset Repair")
    else:
        print("No Custom Fields needed updating - all values already correct")
