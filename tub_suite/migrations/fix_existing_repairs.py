"""
Migration script to fix existing Asset Repair documents for v2.1.0 deployment

This script sets safe default values for new custom fields added in v2.0.0
so that existing repairs don't crash the system.

Run this AFTER bench migrate on production deployment.
"""

import frappe
from frappe.utils import nowdate


def execute():
    """
    Update all existing Asset Repair documents with default values for new fields
    """
    frappe.logger().info("Starting Asset Repair migration for v2.1.0...")

    # Get all submitted repairs
    repairs = frappe.get_all("Asset Repair",
        filters={"docstatus": 1},
        fields=["name", "repair_status", "owner", "creation"])

    if not repairs:
        frappe.logger().info("No existing repairs found - skipping migration")
        return

    frappe.logger().info(f"Found {len(repairs)} existing repairs to update")

    updated = 0
    errors = []

    for repair_info in repairs:
        try:
            doc = frappe.get_doc("Asset Repair", repair_info.name)

            # Track if any changes made
            changed = False

            # Set requires_inspector_verification (default: No)
            if not doc.get("requires_inspector_verification"):
                doc.requires_inspector_verification = 0
                changed = True

            # Set verification_status (default: Not Required)
            if not doc.get("verification_status"):
                doc.verification_status = "Not Required"
                changed = True

            # Set issue_severity (default: Minor - Asset Operational)
            # This is CRITICAL - asset status logic depends on this field
            if not doc.get("issue_severity"):
                doc.issue_severity = "Minor - Asset Operational"
                changed = True

            # Set reported_by (default: document owner)
            if not doc.get("reported_by"):
                doc.reported_by = repair_info.owner
                changed = True

            # Set maintenance_task (default: empty)
            # We can't auto-populate this - it would require complex logic
            if not doc.get("maintenance_task"):
                doc.maintenance_task = ""
                changed = True

            # Only save if changes were made
            if changed:
                # Bypass validation for existing records
                doc.flags.ignore_validate_update_after_submit = True
                doc.flags.ignore_mandatory = True
                doc.flags.ignore_permissions = True
                doc.save(ignore_permissions=True)

                updated += 1

                if updated % 10 == 0:
                    frappe.logger().info(f"Updated {updated} repairs...")
                    frappe.db.commit()  # Commit in batches

        except Exception as e:
            error_msg = f"Error updating {repair_info.name}: {str(e)}"
            errors.append(error_msg)
            frappe.logger().error(error_msg)
            # Continue with other repairs even if one fails

    # Final commit
    frappe.db.commit()

    frappe.logger().info(f"✓ Successfully updated {updated} repairs")

    if errors:
        frappe.logger().error(f"✗ Encountered {len(errors)} errors:")
        for err in errors[:10]:  # Log first 10 errors
            frappe.logger().error(f"  {err}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"Asset Repair Migration Summary")
    print(f"{'='*60}")
    print(f"Total repairs found: {len(repairs)}")
    print(f"Successfully updated: {updated}")
    print(f"Errors: {len(errors)}")
    print(f"{'='*60}\n")
