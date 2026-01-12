"""
Data Migration Script: Renamed Thai Fields to English
Version: 2.1.0
Date: 2026-01-09

This script migrates data from old Thai fieldnames to new English fieldnames
Run ONCE after deploying v2.1.0 to production
"""

import frappe


def execute():
    """Main migration function"""
    migrate_renamed_fields()


def migrate_renamed_fields():
    """Migrate data from old Thai fieldnames to new English fieldnames"""

    field_mapping = {
        "custom_ฝายวศวกรรม": "custom_engineering_section",
        "custom_คาใชจาย": "custom_cost_type",
        "custom_การดำเนินการ": "custom_engineering_todo_items",
        "custom_สาเหต": "custom_cause_category",
        "custom_ระบสาเหต": "custom_cause_description",
        "custom_ใบสงของเลขท": "custom_purchase_order_no"
    }

    print("\n" + "="*60)
    print("DATA MIGRATION: Thai Fieldnames → English Fieldnames")
    print("="*60)

    # Get all Asset Repair records
    repairs = frappe.get_all("Asset Repair", fields=["name", "creation"], order_by="creation desc")

    if not repairs:
        print("⏭️  No Asset Repair records found - skipping migration")
        return

    print(f"\n📊 Found {len(repairs)} Asset Repair records")

    migrated_count = 0
    skipped_count = 0

    for repair in repairs:
        try:
            doc = frappe.get_doc("Asset Repair", repair.name)
            updated = False
            field_updates = {}

            for old_field, new_field in field_mapping.items():
                # Check if old field exists and has data
                if hasattr(doc, old_field):
                    old_value = doc.get(old_field)

                    if old_value:
                        # Check if new field is empty or not set
                        new_value = doc.get(new_field)

                        if not new_value:
                            # Copy data to new field
                            field_updates[new_field] = old_value
                            updated = True
                            print(f"   ✅ {repair.name}: {old_field} → {new_field}")
                        else:
                            # New field already has data, skip
                            print(f"   ⏭️  {repair.name}: {new_field} already set")

            # Batch update all fields for this document
            if field_updates:
                for field, value in field_updates.items():
                    frappe.db.set_value("Asset Repair", doc.name, field, value, update_modified=False)
                migrated_count += 1
            else:
                skipped_count += 1

        except Exception as e:
            print(f"   ❌ Error migrating {repair.name}: {str(e)}")
            continue

    frappe.db.commit()

    print("\n" + "="*60)
    print(f"✅ Migration Complete")
    print(f"   - Records migrated: {migrated_count}")
    print(f"   - Records skipped: {skipped_count}")
    print(f"   - Total processed: {len(repairs)}")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Run when called directly
    migrate_renamed_fields()
