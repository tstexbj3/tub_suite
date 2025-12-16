"""
Clean up duplicate approval fields from Asset Repair
Removes unused fields from old approval API system
"""

import frappe

def remove_duplicate_approval_fields():
    """
    Remove duplicate approval fields that are not being used

    REMOVES (System B - Unused):
    - approval_time (duplicate of approval_timestamp)
    - approved_by (not used in current workflow)
    - approval_status (not used in current workflow)

    KEEPS (System A - Active):
    - approval_timestamp (used by asset_repair_override.py)
    - approval_notes (manager editable)
    - approval_signature (manager editable)
    - approval_section (UI section break)
    - engineer_signature (required field)
    """

    # List of duplicate/unused fields to remove
    fields_to_remove = [
        "Asset Repair-approval_time",
        "Asset Repair-approved_by",
        "Asset Repair-approval_status"
    ]

    removed = []
    not_found = []
    errors = []

    for field_name in fields_to_remove:
        try:
            if frappe.db.exists("Custom Field", field_name):
                # Get field details before deletion
                field = frappe.get_doc("Custom Field", field_name)
                field_label = field.label

                # Delete the field
                frappe.delete_doc("Custom Field", field_name, force=True)
                removed.append(f"{field_label} ({field.fieldname})")
                print(f"✓ Deleted: {field_label} ({field.fieldname})")
            else:
                not_found.append(field_name)
                print(f"⚠ Not found: {field_name}")
        except Exception as e:
            errors.append(f"{field_name}: {str(e)}")
            print(f"✗ Error deleting {field_name}: {str(e)}")

    # Commit changes
    frappe.db.commit()

    # Clear cache to reload meta
    frappe.clear_cache(doctype="Asset Repair")

    print("\n" + "="*60)
    print("CLEANUP SUMMARY")
    print("="*60)
    print(f"Fields removed: {len(removed)}")
    print(f"Fields not found: {len(not_found)}")
    print(f"Errors: {len(errors)}")
    print("="*60)

    if removed:
        print("\n✓ REMOVED FIELDS:")
        for field in removed:
            print(f"  - {field}")

    if not_found:
        print("\n⚠ NOT FOUND (already deleted or never existed):")
        for field in not_found:
            print(f"  - {field}")

    if errors:
        print("\n✗ ERRORS:")
        for error in errors:
            print(f"  - {error}")

    return {
        "success": len(errors) == 0,
        "removed": removed,
        "not_found": not_found,
        "errors": errors,
        "message": f"Removed {len(removed)} duplicate field(s)"
    }


def verify_remaining_fields():
    """
    Verify that the correct approval fields remain after cleanup
    """

    expected_fields = [
        "approval_timestamp",
        "approval_notes",
        "approval_signature",
        "approval_section",
        "engineer_signature"
    ]

    print("\n" + "="*60)
    print("VERIFICATION - Expected Approval Fields")
    print("="*60)

    all_present = True

    for fieldname in expected_fields:
        exists = frappe.db.exists("Custom Field", f"Asset Repair-{fieldname}")
        status = "✓ Present" if exists else "✗ MISSING"
        print(f"{status}: {fieldname}")
        if not exists:
            all_present = False

    print("="*60)

    if all_present:
        print("✓ All expected fields are present!")
    else:
        print("✗ WARNING: Some expected fields are missing!")

    return all_present


def run_cleanup_with_verification():
    """
    Run cleanup and verify results
    """
    print("Starting duplicate field cleanup...\n")

    # Run cleanup
    result = remove_duplicate_approval_fields()

    # Verify remaining fields
    verified = verify_remaining_fields()

    result["verified"] = verified

    if result["success"] and verified:
        print("\n🎉 Cleanup completed successfully!")
    elif result["success"] and not verified:
        print("\n⚠️ Cleanup completed but verification failed - check missing fields")
    else:
        print("\n❌ Cleanup completed with errors")

    return result
