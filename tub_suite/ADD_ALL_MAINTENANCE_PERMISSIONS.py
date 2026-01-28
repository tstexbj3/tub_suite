#!/usr/bin/env python3
"""
Add all missing permissions for maintenance roles on DEV
Run with: bench --site tub execute tub_suite.ADD_ALL_MAINTENANCE_PERMISSIONS.add_all_permissions
"""

import frappe

def add_all_permissions():
    """Add comprehensive permissions for all maintenance roles"""

    print("=" * 80)
    print("ADDING MAINTENANCE ROLE PERMISSIONS")
    print("=" * 80)

    # Define comprehensive permissions for each role
    role_permissions = {
        "Maintenance User": {
            "Asset": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Asset Repair": {"read": 1, "write": 1, "create": 1, "delete": 0, "submit": 0, "cancel": 0},
            "Asset Maintenance": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Asset Maintenance Log": {"read": 1, "write": 1, "create": 1, "delete": 0, "submit": 0, "cancel": 0},
            "Asset Maintenance Task": {"read": 1, "write": 1, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Location": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Asset Category": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Item": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
        },
        "Supervisor": {
            "Asset": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Asset Repair": {"read": 1, "write": 1, "create": 0, "delete": 0, "submit": 1, "cancel": 0},
            "Asset Maintenance": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Asset Maintenance Log": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Asset Maintenance Task": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Location": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Asset Category": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Item": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
        },
        "Maintenance Supervisor": {
            "Asset": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Asset Repair": {"read": 1, "write": 1, "create": 0, "delete": 0, "submit": 1, "cancel": 0},
            "Asset Maintenance": {"read": 1, "write": 1, "create": 1, "delete": 0, "submit": 0, "cancel": 0},
            "Asset Maintenance Log": {"read": 1, "write": 1, "create": 1, "delete": 0, "submit": 0, "cancel": 0},
            "Asset Maintenance Task": {"read": 1, "write": 1, "create": 1, "delete": 0, "submit": 0, "cancel": 0},
            "Location": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Asset Category": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Item": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
        },
        "Maintenance Manager": {
            "Asset": {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0},
            "Asset Repair": {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1},
            "Asset Maintenance": {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0},
            "Asset Maintenance Log": {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0},
            "Asset Maintenance Task": {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0},
            "Location": {"read": 1, "write": 1, "create": 1, "delete": 0, "submit": 0, "cancel": 0},
            "Asset Category": {"read": 1, "write": 1, "create": 1, "delete": 0, "submit": 0, "cancel": 0},
            "Item": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
        },
        "Engineering Supervisor": {
            "Asset": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Asset Repair": {"read": 1, "write": 1, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Asset Maintenance": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Asset Maintenance Log": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Asset Maintenance Task": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Location": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Asset Category": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Item": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
        },
        "Engineering Team": {
            "Asset": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Asset Repair": {"read": 1, "write": 1, "create": 1, "delete": 0, "submit": 0, "cancel": 0},
            "Asset Maintenance": {"read": 1, "write": 1, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Asset Maintenance Log": {"read": 1, "write": 1, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Asset Maintenance Task": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Location": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Asset Category": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "Item": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
        }
    }

    added_count = 0
    updated_count = 0
    skipped_count = 0

    for role, doctypes in role_permissions.items():
        print(f"\n{'='*80}")
        print(f"Processing role: {role}")
        print(f"{'='*80}")

        # Verify role exists
        if not frappe.db.exists("Role", role):
            print(f"  ⚠️  Role '{role}' does not exist! Skipping...")
            continue

        for doctype, perms in doctypes.items():
            # Verify doctype exists
            if not frappe.db.exists("DocType", doctype):
                print(f"  ⏭️  DocType '{doctype}' does not exist, skipping")
                continue

            # Check if Custom DocPerm already exists
            existing = frappe.db.get_value("Custom DocPerm",
                {"parent": doctype, "role": role, "permlevel": 0},
                ["name", "read", "write", "create", "delete", "submit", "cancel"],
                as_dict=True
            )

            if existing:
                # Check if permissions match
                needs_update = False
                for perm_type in ["read", "write", "create", "delete", "submit", "cancel"]:
                    if existing.get(perm_type) != perms.get(perm_type):
                        needs_update = True
                        break

                if needs_update:
                    # Update existing permission
                    doc = frappe.get_doc("Custom DocPerm", existing.name)
                    for perm_type in ["read", "write", "create", "delete", "submit", "cancel"]:
                        setattr(doc, perm_type, perms.get(perm_type, 0))
                    doc.save(ignore_permissions=True)
                    updated_count += 1

                    perm_str = "".join([
                        "R" if perms["read"] else "",
                        "W" if perms["write"] else "",
                        "C" if perms["create"] else "",
                        "D" if perms["delete"] else "",
                        "S" if perms["submit"] else "",
                        "X" if perms["cancel"] else ""
                    ])
                    print(f"  🔄 {doctype:<30} {perm_str:<10} (updated)")
                else:
                    skipped_count += 1
                    print(f"  ⏭️  {doctype:<30} (already correct)")
            else:
                # Create new Custom DocPerm
                perm_doc = frappe.get_doc({
                    "doctype": "Custom DocPerm",
                    "parent": doctype,
                    "parenttype": "DocType",
                    "parentfield": "permissions",
                    "role": role,
                    "permlevel": 0,
                    "read": perms.get("read", 0),
                    "write": perms.get("write", 0),
                    "create": perms.get("create", 0),
                    "delete": perms.get("delete", 0),
                    "submit": perms.get("submit", 0),
                    "cancel": perms.get("cancel", 0),
                    "amend": 0,
                    "report": 1 if perms.get("read") else 0,
                    "export": 1 if perms.get("read") else 0,
                    "import": 0,
                    "share": 1 if perms.get("read") else 0,
                    "print": 1 if perms.get("read") else 0,
                    "email": 1 if perms.get("read") else 0
                })
                perm_doc.insert(ignore_permissions=True)
                added_count += 1

                perm_str = "".join([
                    "R" if perms["read"] else "",
                    "W" if perms["write"] else "",
                    "C" if perms["create"] else "",
                    "D" if perms["delete"] else "",
                    "S" if perms["submit"] else "",
                    "X" if perms["cancel"] else ""
                ])
                print(f"  ✅ {doctype:<30} {perm_str:<10} (added)")

    # Commit changes
    frappe.db.commit()

    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"  ✅ Added: {added_count} permissions")
    print(f"  🔄 Updated: {updated_count} permissions")
    print(f"  ⏭️  Skipped: {skipped_count} permissions (already correct)")
    print(f"  📊 Total: {added_count + updated_count + skipped_count} permissions processed")

    # Clear cache
    print(f"\n{'='*80}")
    print("CLEARING CACHE")
    print(f"{'='*80}")
    frappe.clear_cache()
    print("  ✅ Cache cleared")

    print(f"\n{'='*80}")
    print("✅ ALL PERMISSIONS ADDED SUCCESSFULLY!")
    print(f"{'='*80}")
    print("\nNext steps:")
    print("1. Export Custom DocPerm fixtures: bench --site tub export-fixtures")
    print("2. Commit changes and tag v2.1.3")
    print("3. Deploy to production")

    return f"Added {added_count}, Updated {updated_count}, Skipped {skipped_count} permissions"

if __name__ == "__main__":
    add_all_permissions()
