"""
FORCE SYNC ALL FIXTURES FROM JSON TO DATABASE

WHY THIS EXISTS:
Frappe's bench migrate does NOT update existing records from fixtures.
It only adds NEW records and skips existing ones due to timestamp comparison.

This patch reads ALL fixture files and force-applies EVERY setting to the database,
bypassing Frappe's broken timestamp logic.

Syncs: Custom Fields, Property Setters, Workflows, Workflow States, DocPerms
This ensures DEV and PROD have identical configurations.
"""

import frappe
import json
import os


def sync_fixture_file(filename, doctype_name, key_field="name"):
    """Read a fixture file and force-sync all records to database"""

    fixture_path = os.path.join(
        frappe.get_app_path("tub_suite"),
        "fixtures",
        filename
    )

    if not os.path.exists(fixture_path):
        print(f"⚠ Fixture file not found: {filename}")
        return 0

    # Read fixture file
    with open(fixture_path, 'r', encoding='utf-8') as f:
        fixture_data = json.load(f)

    if not isinstance(fixture_data, list):
        fixture_data = [fixture_data]

    updated_count = 0

    for record in fixture_data:
        record_name = record.get(key_field)

        if not record_name:
            continue

        # Check if record exists
        if frappe.db.exists(doctype_name, record_name):
            # Update existing record
            doc = frappe.get_doc(doctype_name, record_name)

            # Update ALL fields from fixture
            for key, value in record.items():
                if key not in ["doctype", "name", "modified", "modified_by", "creation", "owner"]:
                    setattr(doc, key, value)

            doc.flags.ignore_validate = True
            doc.flags.ignore_permissions = True
            doc.save(ignore_permissions=True)
            updated_count += 1

    return updated_count


def execute():
    """Force sync all fixtures from JSON files to database"""

    print("=" * 80)
    print("FORCE SYNCING ALL FIXTURES FROM JSON TO DATABASE")
    print("=" * 80)

    # Sync each fixture file
    fixtures_to_sync = [
        ("custom_field.json", "Custom Field"),
        ("property_setter.json", "Property Setter"),
        ("workflow.json", "Workflow"),
        ("workflow_state.json", "Workflow State"),
        ("workflow_action_master.json", "Workflow Action Master"),
        ("custom_docperm.json", "Custom DocPerm"),
    ]

    total_updated = 0

    for filename, doctype in fixtures_to_sync:
        print(f"\n📁 Syncing {filename}...")
        count = sync_fixture_file(filename, doctype)
        print(f"   ✓ Updated {count} {doctype} records")
        total_updated += count

    frappe.db.commit()

    print("\n" + "=" * 80)
    print(f"SYNC COMPLETE - {total_updated} records updated")
    print("=" * 80)
    print("\nAll fixture settings are now applied to database.")
    print("Production should now match DEV exactly.")
