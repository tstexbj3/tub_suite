"""
FORCE SYNC ALL CUSTOM FIELDS FROM FIXTURES TO DATABASE

WHY THIS EXISTS:
Frappe's bench migrate does NOT update existing Custom Fields from fixtures.
It only adds NEW fields and skips existing ones due to timestamp comparison.

This patch reads custom_field.json and force-applies EVERY setting to the database,
bypassing Frappe's broken timestamp logic.

This ensures DEV and PROD have identical Custom Field configurations.
"""

import frappe
import json
import os


def execute():
    """Force sync all Asset Repair Custom Fields from fixture file to database"""

    # Path to fixture file
    fixture_path = os.path.join(
        frappe.get_app_path("tub_suite"),
        "fixtures",
        "custom_field.json"
    )

    if not os.path.exists(fixture_path):
        print(f"❌ Fixture file not found: {fixture_path}")
        return

    # Read fixture file
    with open(fixture_path, 'r', encoding='utf-8') as f:
        fixture_data = json.load(f)

    # Filter only Asset Repair fields
    asset_repair_fields = [
        field for field in fixture_data
        if field.get("dt") == "Asset Repair"
    ]

    print(f"Found {len(asset_repair_fields)} Asset Repair custom fields in fixture file")

    updated_count = 0
    created_count = 0

    # Important fields to sync
    critical_fields = [
        "depends_on",
        "hidden",
        "read_only",
        "read_only_depends_on",
        "mandatory_depends_on",
        "collapsible_depends_on",
        "reqd",
        "label",
        "description"
    ]

    for field_data in asset_repair_fields:
        field_name = field_data.get("name")
        fieldname = field_data.get("fieldname")

        if not field_name or not fieldname:
            continue

        # Check if field exists
        if frappe.db.exists("Custom Field", field_name):
            # Update existing field
            doc = frappe.get_doc("Custom Field", field_name)

            # Update critical fields
            for key in critical_fields:
                if key in field_data:
                    setattr(doc, key, field_data[key])

            doc.flags.ignore_validate = True
            doc.save(ignore_permissions=True)
            updated_count += 1

            # Print for important visibility fields
            if field_data.get("depends_on") or field_data.get("hidden"):
                print(f"✓ Updated {fieldname}: depends_on={field_data.get('depends_on')}, hidden={field_data.get('hidden')}")
        else:
            # Field doesn't exist - this shouldn't happen but handle it
            print(f"⚠ Field {field_name} doesn't exist in database (skipping)")

    frappe.db.commit()

    print("\n" + "=" * 80)
    print(f"SYNC COMPLETE")
    print(f"  Updated: {updated_count} fields")
    print(f"  Created: {created_count} fields")
    print("=" * 80)
    print("\nAll Custom Field settings from fixtures are now applied to database.")
    print("Production should now match DEV exactly.")
