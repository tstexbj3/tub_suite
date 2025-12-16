"""
Audit all Client and Server Scripts for Asset Repair
"""

import frappe

def audit_asset_repair_scripts():
    """List all scripts related to Asset Repair"""

    print("="*70)
    print("ASSET REPAIR - SCRIPT AUDIT")
    print("="*70)

    # Server Scripts
    server_scripts = frappe.db.sql("""
        SELECT name, script_type, reference_doctype, disabled
        FROM `tabServer Script`
        WHERE reference_doctype = 'Asset Repair'
        ORDER BY name
    """, as_dict=True)

    print(f"\n📋 SERVER SCRIPTS: {len(server_scripts)}")
    print("-"*70)
    for script in server_scripts:
        status = "❌ DISABLED" if script.disabled else "✅ ACTIVE"
        print(f"{status} | {script.name}")
        print(f"  Type: {script.script_type}")
        print()

    # Client Scripts
    client_scripts = frappe.db.sql("""
        SELECT name, dt, disabled
        FROM `tabClient Script`
        WHERE dt = 'Asset Repair'
        ORDER BY name
    """, as_dict=True)

    print(f"\n💻 CLIENT SCRIPTS: {len(client_scripts)}")
    print("-"*70)
    for script in client_scripts:
        status = "❌ DISABLED" if script.disabled else "✅ ACTIVE"
        print(f"{status} | {script.name}")
        print()

    # Check if we can consolidate
    print("\n"+"="*70)
    print("OPTIMIZATION RECOMMENDATIONS")
    print("="*70)

    # Check for Python overrides
    print("\n🐍 PYTHON OVERRIDES (asset_repair_override.py):")
    print("  - validate_asset_repair()")
    print("  - before_save_asset_repair()")
    print("  - before_submit_asset_repair()")
    print("  - update_asset_status_based_on_severity()")

    total_scripts = len(server_scripts) + len(client_scripts)

    print(f"\n📊 TOTAL SCRIPTS: {total_scripts}")
    print(f"   Server Scripts: {len(server_scripts)}")
    print(f"   Client Scripts: {len(client_scripts)}")
    print(f"   Python Overrides: 1 file (4 functions)")

    print("\n💡 RECOMMENDATION:")
    if total_scripts > 2:
        print("   ⚠️  Multiple scripts detected - consider consolidation")
        print("   Ideally use: 1 Server Script OR Python override (not both)")
        print("   Ideally use: 1 Client Script for all UI behavior")
    else:
        print("   ✅ Script count is reasonable")

    return {
        "server_scripts": len(server_scripts),
        "client_scripts": len(client_scripts),
        "total": total_scripts
    }
