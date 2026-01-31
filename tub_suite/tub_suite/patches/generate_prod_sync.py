"""
DIRECT DATABASE SYNC: Copy DEV Config to PROD
==============================================

Run this ON DEV (site: tub) to generate a patch that syncs PROD (site: tub.x-desk.tech).

Usage:
    bench --site tub execute tub_suite.patches.generate_prod_sync.generate_python_patch
"""

import frappe
import json
from datetime import datetime


def generate_python_patch():
    """
    Generate a Python patch file that syncs PROD to match DEV.
    Run this ON DEV ENVIRONMENT (site: tub).
    """

    config = {
        "custom_fields": {},
        "property_setters": {},
        "docfields": {},
        "workflow_states": [],
        "workflow_transitions": [],
        "client_scripts": {},
        "server_scripts": {}
    }

    print("Collecting Custom Fields...")
    for cf in frappe.get_all("Custom Field",
                             filters={"dt": "Asset Repair"},
                             fields=["*"]):
        config["custom_fields"][cf['name']] = {
            "depends_on": cf.get('depends_on'),
            "mandatory_depends_on": cf.get('mandatory_depends_on'),
            "read_only_depends_on": cf.get('read_only_depends_on'),
            "hidden": cf.get('hidden'),
            "read_only": cf.get('read_only'),
            "reqd": cf.get('reqd'),
            "in_list_view": cf.get('in_list_view'),
            "in_standard_filter": cf.get('in_standard_filter'),
            "columns": cf.get('columns'),
            "default": cf.get('default'),
            "options": cf.get('options'),
            "fetch_from": cf.get('fetch_from'),
            "insert_after": cf.get('insert_after'),
        }

    print("Collecting Property Setters...")
    for ps in frappe.get_all("Property Setter",
                             filters={"doc_type": "Asset Repair"},
                             fields=["*"]):
        config["property_setters"][ps['name']] = {
            "doc_type": ps.get('doc_type'),
            "doctype_or_field": ps.get('doctype_or_field'),
            "field_name": ps.get('field_name'),
            "property": ps.get('property'),
            "property_type": ps.get('property_type'),
            "value": ps.get('value')
        }

    print("Collecting DocFields...")
    child_tables = ["Repair Spare Part", "Parts Inserted Item", "Parts Removed Item", "Engineering Todo Item"]
    for dt in child_tables:
        if not frappe.db.exists("DocType", dt):
            continue

        for df in frappe.get_all("DocField",
                                 filters={"parent": dt},
                                 fields=["parent", "fieldname", "in_list_view", "columns", "read_only", "hidden"]):
            key = f"{df['parent']}.{df['fieldname']}"
            config["docfields"][key] = {
                "parent": df['parent'],
                "fieldname": df['fieldname'],
                "in_list_view": df.get('in_list_view'),
                "columns": df.get('columns'),
                "read_only": df.get('read_only'),
                "hidden": df.get('hidden')
            }

    print("Collecting Workflow States...")
    for ws in frappe.db.sql("""
        SELECT wds.state, wds.allow_edit, wds.doc_status, wds.update_field, wds.update_value, w.name as parent
        FROM `tabWorkflow Document State` wds
        JOIN `tabWorkflow` w ON wds.parent = w.name
        WHERE w.document_type = 'Asset Repair'
    """, as_dict=True):
        config["workflow_states"].append({
            "parent": ws['parent'],
            "state": ws['state'],
            "allow_edit": ws.get('allow_edit', ''),
            "doc_status": ws.get('doc_status'),
            "update_field": ws.get('update_field'),
            "update_value": ws.get('update_value')
        })

    print("Collecting Workflow Transitions...")
    for wt in frappe.db.sql("""
        SELECT wt.state, wt.action, wt.next_state, wt.allowed, wt.allow_self_approval, wt.condition, w.name as parent
        FROM `tabWorkflow Transition` wt
        JOIN `tabWorkflow` w ON wt.parent = w.name
        WHERE w.document_type = 'Asset Repair'
    """, as_dict=True):
        config["workflow_transitions"].append({
            "parent": wt['parent'],
            "state": wt['state'],
            "action": wt['action'],
            "next_state": wt['next_state'],
            "allowed": wt.get('allowed', ''),
            "allow_self_approval": wt.get('allow_self_approval'),
            "condition": wt.get('condition', '')
        })

    print("Collecting Client Scripts...")
    for cs in frappe.get_all("Client Script", filters={"dt": "Asset Repair"}, fields=["name", "script", "enabled"]):
        config["client_scripts"][cs['name']] = {
            "script": cs.get('script', ''),
            "enabled": cs.get('enabled', 0)
        }

    print("Collecting Server Scripts...")
    for ss in frappe.get_all("Server Script", filters={"reference_doctype": "Asset Repair"}, fields=["name", "script", "disabled"]):
        config["server_scripts"][ss['name']] = {
            "script": ss.get('script', ''),
            "disabled": ss.get('disabled', 0)
        }

    # Generate the patch file
    patch_template = '''"""
Asset Repair Configuration Mega-Sync
====================================
Generated from DEV (site: tub): {timestamp}
Target: PROD (site: tub.x-desk.tech)

This patch syncs ALL Asset Repair configuration to match DEV.

Usage:
    1. Copy this file to: ~/frappe-bench/apps/tub_suite/tub_suite/patches/mega_sync_dev_to_prod.py
    2. Add to patches.txt: tub_suite.patches.mega_sync_dev_to_prod
    3. Run: bench --site tub.x-desk.tech migrate
    4. Clear cache: bench --site tub.x-desk.tech clear-cache
"""

import frappe
import json

# Configuration data exported from DEV
CONFIG = {config_json}


def execute():
    """Sync all configuration from DEV to PROD."""

    print("=" * 60)
    print("MEGA-SYNC: Applying DEV configuration to PROD")
    print("Site: tub.x-desk.tech")
    print("=" * 60)

    # 1. Custom Fields
    print("\\n[1/7] Syncing Custom Fields...")
    for cf_name, values in CONFIG["custom_fields"].items():
        try:
            if frappe.db.exists("Custom Field", cf_name):
                for field, value in values.items():
                    frappe.db.set_value("Custom Field", cf_name, field, value, update_modified=False)
                print(f"  ✓ {{cf_name}}")
        except Exception as e:
            print(f"  ✗ {{cf_name}}: {{e}}")

    # 2. Property Setters
    print("\\n[2/7] Syncing Property Setters...")
    for ps_name, values in CONFIG["property_setters"].items():
        try:
            if frappe.db.exists("Property Setter", ps_name):
                for field, value in values.items():
                    frappe.db.set_value("Property Setter", ps_name, field, value, update_modified=False)
                print(f"  ✓ {{ps_name}}")
            else:
                # Create new Property Setter
                ps = frappe.new_doc("Property Setter")
                ps.update(values)
                ps.name = ps_name
                ps.insert(ignore_permissions=True)
                print(f"  + Created: {{ps_name}}")
        except Exception as e:
            print(f"  ✗ {{ps_name}}: {{e}}")

    # 3. DocFields (grid columns)
    print("\\n[3/7] Syncing DocFields (grid columns)...")
    for key, values in CONFIG["docfields"].items():
        try:
            frappe.db.sql("""
                UPDATE `tabDocField`
                SET in_list_view = %s, columns = %s, read_only = %s, hidden = %s
                WHERE parent = %s AND fieldname = %s
            """, (values["in_list_view"], values["columns"], values["read_only"],
                  values["hidden"], values["parent"], values["fieldname"]))
            print(f"  ✓ {{key}}")
        except Exception as e:
            print(f"  ✗ {{key}}: {{e}}")

    # 4. Workflow States
    print("\\n[4/7] Syncing Workflow States...")
    for ws in CONFIG["workflow_states"]:
        try:
            frappe.db.sql("""
                UPDATE `tabWorkflow Document State`
                SET allow_edit = %s, doc_status = %s, update_field = %s, update_value = %s
                WHERE parent = %s AND state = %s
            """, (ws["allow_edit"], ws.get("doc_status"), ws.get("update_field"),
                  ws.get("update_value"), ws["parent"], ws["state"]))
            print(f"  ✓ {{ws['state']}}")
        except Exception as e:
            print(f"  ✗ {{ws['state']}}: {{e}}")

    # 5. Workflow Transitions
    print("\\n[5/7] Syncing Workflow Transitions...")
    for wt in CONFIG["workflow_transitions"]:
        try:
            frappe.db.sql("""
                UPDATE `tabWorkflow Transition`
                SET allowed = %s, `condition` = %s, allow_self_approval = %s
                WHERE parent = %s AND state = %s AND action = %s AND next_state = %s
            """, (wt["allowed"], wt["condition"], wt.get("allow_self_approval"),
                  wt["parent"], wt["state"], wt["action"], wt["next_state"]))
            print(f"  ✓ {{wt['state']}} -> {{wt['next_state']}}")
        except Exception as e:
            print(f"  ✗ {{wt['state']}}: {{e}}")

    # 6. Client Scripts
    print("\\n[6/7] Syncing Client Scripts...")
    for cs_name, values in CONFIG["client_scripts"].items():
        try:
            if frappe.db.exists("Client Script", cs_name):
                frappe.db.set_value("Client Script", cs_name, "script", values["script"], update_modified=False)
                frappe.db.set_value("Client Script", cs_name, "enabled", values["enabled"], update_modified=False)
                print(f"  ✓ {{cs_name}}")
        except Exception as e:
            print(f"  ✗ {{cs_name}}: {{e}}")

    # 7. Server Scripts
    print("\\n[7/7] Syncing Server Scripts...")
    for ss_name, values in CONFIG["server_scripts"].items():
        try:
            if frappe.db.exists("Server Script", ss_name):
                frappe.db.set_value("Server Script", ss_name, "script", values["script"], update_modified=False)
                frappe.db.set_value("Server Script", ss_name, "disabled", values["disabled"], update_modified=False)
                print(f"  ✓ {{ss_name}}")
        except Exception as e:
            print(f"  ✗ {{ss_name}}: {{e}}")

    # Commit and clear cache
    print("\\n" + "=" * 60)
    frappe.db.commit()
    frappe.clear_cache()

    print("✅ MEGA-SYNC COMPLETE!")
    print("=" * 60)
    print("\\n⚠️  IMPORTANT: Clear browser cache and hard refresh (Ctrl+Shift+R)")
'''

    config_json = json.dumps(config, indent=4, default=str)

    patch_content = patch_template.format(
        timestamp=datetime.now().isoformat(),
        config_json=config_json
    )

    output_file = f"/tmp/mega_sync_patch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    with open(output_file, 'w') as f:
        f.write(patch_content)

    print(f"\n{'='*60}")
    print(f"✅ Python patch generated: {output_file}")
    print(f"{'='*60}")
    print(f"\nTo apply to production:")
    print(f"  1. Copy to: ~/frappe-bench/apps/tub_suite/tub_suite/patches/mega_sync_dev_to_prod.py")
    print(f"  2. Add to patches.txt: tub_suite.patches.mega_sync_dev_to_prod")
    print(f"  3. Run: bench --site tub.x-desk.tech migrate")
    print(f"  4. Clear cache: bench --site tub.x-desk.tech clear-cache")

    return output_file
