"""Clean up old duplicate scripts"""

import frappe

def cleanup_old_scripts():
    """Remove old duplicate Client and Server Scripts"""

    # Scripts to delete
    old_client_scripts = [
        "Asset Repair - Field Locking",  # Old version
        "Asset Repair - Lock All Fields Except Approval",  # Old version
        "Asset Repair - Lock Fields After Submit",  # Old version
        "Repair Approval",  # Old version
        "Show Approval Fields - Asset Repair",  # Old version
    ]

    old_server_scripts = [
        "Asset repair approval",  # Old version with no doctype
    ]

    print("="*80)
    print("CLEANING UP OLD SCRIPTS")
    print("="*80)

    deleted_client = []
    deleted_server = []
    not_found = []

    # Delete old Client Scripts
    print("\n🗑️  Deleting OLD CLIENT SCRIPTS...")
    for script_name in old_client_scripts:
        if frappe.db.exists("Client Script", script_name):
            try:
                frappe.delete_doc("Client Script", script_name, force=True)
                deleted_client.append(script_name)
                print(f"   ✓ Deleted: {script_name}")
            except Exception as e:
                print(f"   ✗ Error deleting {script_name}: {str(e)}")
        else:
            not_found.append(script_name)
            print(f"   ⚠ Not found: {script_name}")

    # Delete old Server Scripts
    print("\n🗑️  Deleting OLD SERVER SCRIPTS...")
    for script_name in old_server_scripts:
        if frappe.db.exists("Server Script", script_name):
            try:
                frappe.delete_doc("Server Script", script_name, force=True)
                deleted_server.append(script_name)
                print(f"   ✓ Deleted: {script_name}")
            except Exception as e:
                print(f"   ✗ Error deleting {script_name}: {str(e)}")
        else:
            not_found.append(script_name)
            print(f"   ⚠ Not found: {script_name}")

    frappe.db.commit()

    # Show what's left
    print("\n" + "="*80)
    print("REMAINING SCRIPTS (SHOULD KEEP)")
    print("="*80)

    remaining_server = frappe.db.sql("""
        SELECT name, reference_doctype
        FROM `tabServer Script`
        WHERE reference_doctype = 'Asset Repair'
    """, as_dict=True)

    remaining_client = frappe.db.sql("""
        SELECT name
        FROM `tabClient Script`
        WHERE dt = 'Asset Repair'
    """, as_dict=True)

    print(f"\n✅ Server Scripts for Asset Repair: {len(remaining_server)}")
    for s in remaining_server:
        print(f"   - {s.name}")

    print(f"\n✅ Client Scripts for Asset Repair: {len(remaining_client)}")
    for c in remaining_client:
        print(f"   - {c.name}")

    print("\n" + "="*80)
    print("CLEANUP SUMMARY")
    print("="*80)
    print(f"Client Scripts Deleted: {len(deleted_client)}")
    print(f"Server Scripts Deleted: {len(deleted_server)}")
    print(f"Scripts Not Found: {len(not_found)}")

    if len(deleted_client) + len(deleted_server) > 0:
        print("\n✅ CLEANUP SUCCESSFUL - Refresh your browser!")
        print("   Old conflicting scripts have been removed.")
    else:
        print("\n⚠️  No scripts were deleted (already clean or not found)")

    return {
        "success": True,
        "deleted_client": deleted_client,
        "deleted_server": deleted_server,
        "not_found": not_found,
        "remaining_server": len(remaining_server),
        "remaining_client": len(remaining_client)
    }
