"""List all Client and Server Scripts in the system"""

import frappe

def list_all_scripts():
    """List all scripts to identify old/unnecessary ones"""

    all_server = frappe.db.sql("""
        SELECT name, reference_doctype, script_type
        FROM `tabServer Script`
        ORDER BY reference_doctype, name
    """, as_dict=True)

    all_client = frappe.db.sql("""
        SELECT name, dt
        FROM `tabClient Script`
        ORDER BY dt, name
    """, as_dict=True)

    print("="*80)
    print(f"SERVER SCRIPTS: {len(all_server)}")
    print("="*80)
    for s in all_server:
        print(f"📋 {s.name}")
        print(f"   DocType: {s.reference_doctype}")
        print(f"   Type: {s.script_type}")
        print()

    print("="*80)
    print(f"CLIENT SCRIPTS: {len(all_client)}")
    print("="*80)
    for c in all_client:
        print(f"💻 {c.name}")
        print(f"   DocType: {c.dt}")
        print()

    return {
        "server_scripts": [s.name for s in all_server],
        "client_scripts": [c.name for c in all_client]
    }
