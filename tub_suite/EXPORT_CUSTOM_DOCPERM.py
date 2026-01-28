#!/usr/bin/env python3
"""
Export all Custom DocPerm for maintenance roles
Run with: bench --site tub execute tub_suite.EXPORT_CUSTOM_DOCPERM.export_custom_docperm
"""

import frappe
import json
import os

def export_custom_docperm():
    """Export Custom DocPerm fixtures for maintenance roles"""

    maintenance_roles = [
        "Maintenance User",
        "Supervisor",
        "Maintenance Supervisor",
        "Maintenance Manager",
        "Engineering Supervisor",
        "Engineering Team"
    ]

    print("=" * 80)
    print("EXPORTING CUSTOM DOCPERM FIXTURES")
    print("=" * 80)

    # Get all Custom DocPerm for maintenance roles
    custom_perms = frappe.get_all(
        "Custom DocPerm",
        filters={"role": ["in", maintenance_roles]},
        fields=["name"]
    )

    print(f"\nFound {len(custom_perms)} Custom DocPerm records to export")

    # Get full documents
    docs = []
    for perm in custom_perms:
        doc = frappe.get_doc("Custom DocPerm", perm.name)
        doc_dict = doc.as_dict()

        # Remove system fields
        for field in ["modified", "modified_by", "creation", "owner", "docstatus", "idx", "name"]:
            doc_dict.pop(field, None)

        docs.append(doc_dict)
        print(f"  ✅ {doc_dict['parent']} - {doc_dict['role']}")

    # Write to fixture file
    fixture_path = os.path.join(
        frappe.get_app_path("tub_suite"),
        "fixtures",
        "custom_docperm.json"
    )

    with open(fixture_path, "w") as f:
        json.dump(docs, f, indent=1, sort_keys=True)

    print(f"\n✅ Exported {len(docs)} Custom DocPerm records to:")
    print(f"   {fixture_path}")

    # Show file size
    file_size = os.path.getsize(fixture_path)
    print(f"   File size: {file_size:,} bytes")

    print("\n" + "=" * 80)
    print("✅ EXPORT COMPLETE!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Verify the fixture file: cat tub_suite/fixtures/custom_docperm.json | head -20")
    print("2. Add to fixtures list in hooks.py")
    print("3. Commit and tag v2.1.3")
    print("4. Deploy to production")

    return f"Exported {len(docs)} Custom DocPerm records"

if __name__ == "__main__":
    export_custom_docperm()
