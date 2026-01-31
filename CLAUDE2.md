# TUB Suite - Asset Repair Deployment Fix

## CRITICAL CONTEXT FOR CLAUDE CODE

### The Problem
DEV environment (site: `tub`) is fully working with all Asset Repair features configured correctly.
PROD environment (site: `tub.x-desk.tech`) has the EXACT SAME CODE but NOTHING WORKS.

**Root Cause:** Frappe fixtures only CREATE new records, they DON'T UPDATE existing ones. PROD database has old/wrong configuration values that fixtures can't fix.

### Sites
- **DEV site:** `tub`
- **PROD site:** `tub.x-desk.tech`
- **App:** `tub_suite`
- **Bench path:** `~/frappe-bench`

### What Needs to Happen
1. Export ALL configuration from DEV database
2. Generate a mega-patch that applies all config to PROD
3. Run the patch on PROD
4. Clear cache and test

---

## STEP 1: Create the diagnostic script

Create file: `~/frappe-bench/apps/tub_suite/tub_suite/patches/diagnose_asset_repair.py`

```python
"""
Asset Repair Configuration Diagnostic
======================================
Run this ON PRODUCTION to identify ALL configuration issues at once.

Usage:
    bench --site tub.x-desk.tech execute tub_suite.patches.diagnose_asset_repair.run_diagnostics
"""

import frappe
from collections import defaultdict


def run_diagnostics():
    """
    Comprehensive diagnostic for Asset Repair configuration.
    Run on PRODUCTION to see all issues.
    """
    
    print("\n" + "=" * 70)
    print("ASSET REPAIR CONFIGURATION DIAGNOSTIC")
    print("=" * 70)
    
    issues = []
    warnings = []
    
    # ==========================================
    # 1. CHECK CUSTOM FIELD VISIBILITY
    # ==========================================
    print("\n[1/7] Checking Custom Field visibility rules...")
    
    custom_fields = frappe.get_all(
        "Custom Field",
        filters={"dt": ["in", ["Asset Repair", "Asset Repair Parts Used", 
                               "Asset Repair Parts Replaced", "Asset Repair Additional Parts"]]},
        fields=["name", "fieldname", "dt", "depends_on", "hidden", "read_only"]
    )
    
    for cf in custom_fields:
        if "section" in cf['fieldname'].lower() and not cf.get('depends_on'):
            issues.append(f"Custom Field '{cf['name']}' has no depends_on (section might show in wrong states)")
    
    print(f"   Found {len(custom_fields)} custom fields")
    
    # ==========================================
    # 2. CHECK CHILD TABLE GRID COLUMNS
    # ==========================================
    print("\n[2/7] Checking child table grid columns (in_list_view)...")
    
    child_tables = ["Asset Repair Parts Used", "Asset Repair Parts Replaced", "Asset Repair Additional Parts"]
    
    for table in child_tables:
        fields = frappe.get_all(
            "DocField",
            filters={"parent": table, "in_list_view": 1},
            fields=["fieldname", "in_list_view", "columns"]
        )
        
        visible_count = len(fields)
        field_names = [f['fieldname'] for f in fields]
        
        if visible_count != 2:
            issues.append(f"{table}: Has {visible_count} grid columns visible (expected 2). Fields: {field_names}")
        else:
            print(f"   ✓ {table}: {visible_count} columns ({', '.join(field_names)})")
    
    # ==========================================
    # 3. CHECK WORKFLOW STATES - allow_edit
    # ==========================================
    print("\n[3/7] Checking Workflow state permissions (allow_edit)...")
    
    workflow = frappe.get_doc("Workflow", {"document_type": "Asset Repair"})
    
    if not workflow:
        issues.append("No workflow found for Asset Repair!")
    else:
        for state in workflow.states:
            allow_edit = state.allow_edit or ""
            roles = [r.strip() for r in allow_edit.split(",") if r.strip()]
            
            if not roles:
                warnings.append(f"State '{state.state}' has no roles in allow_edit (no one can edit)")
            
            if state.state == "Approved for Repair":
                if "Engineering Supervisor" not in roles and "Engineering Team" not in roles:
                    issues.append(f"State 'Approved for Repair' missing Engineering roles. Has: {roles}")
            
            print(f"   {state.state}: {allow_edit or '(none)'}")
    
    # ==========================================
    # 4. CHECK WORKFLOW TRANSITIONS - allowed roles
    # ==========================================
    print("\n[4/7] Checking Workflow transitions (allowed roles)...")
    
    if workflow:
        for trans in workflow.transitions:
            allowed = trans.allowed or ""
            
            if not allowed:
                warnings.append(f"Transition '{trans.state}' -> '{trans.next_state}' has no allowed roles")
            
            print(f"   {trans.state} --[{trans.action}]--> {trans.next_state}: {allowed or '(none)'}")
    
    # ==========================================
    # 5. CHECK CLIENT SCRIPTS
    # ==========================================
    print("\n[5/7] Checking Client Scripts...")
    
    client_scripts = frappe.get_all(
        "Client Script",
        filters={"dt": "Asset Repair"},
        fields=["name", "enabled", "script"]
    )
    
    for cs in client_scripts:
        status = "✓ Enabled" if cs['enabled'] else "✗ Disabled"
        script_len = len(cs.get('script', '') or '')
        print(f"   {status}: {cs['name']} ({script_len} chars)")
        
        if cs.get('script'):
            if "Engineering Supervisor" not in cs['script'] and "field_locking" in cs['name'].lower():
                warnings.append(f"Client Script '{cs['name']}' might be missing Engineering Supervisor logic")
    
    # ==========================================
    # 6. CHECK SERVER SCRIPTS
    # ==========================================
    print("\n[6/7] Checking Server Scripts...")
    
    server_scripts = frappe.get_all(
        "Server Script",
        filters={"reference_doctype": "Asset Repair"},
        fields=["name", "disabled", "script_type", "doctype_event"]
    )
    
    for ss in server_scripts:
        status = "✗ Disabled" if ss['disabled'] else "✓ Enabled"
        print(f"   {status}: {ss['name']} ({ss['script_type']} on {ss['doctype_event']})")
    
    # ==========================================
    # 7. CHECK OVERRIDE CLASS
    # ==========================================
    print("\n[7/7] Checking Override Class registration...")
    
    from frappe import get_hooks
    
    override_doctypes = get_hooks("override_doctype_class", {})
    asset_repair_override = override_doctypes.get("Asset Repair", [])
    
    if asset_repair_override:
        print(f"   Override class: {asset_repair_override}")
        
        try:
            from tub_suite.overrides.asset_repair_override import AssetRepairOverride
            
            if hasattr(AssetRepairOverride, 'has_permission'):
                print(f"   ✓ has_permission method exists")
            else:
                warnings.append("Override class missing has_permission method")
            
            if hasattr(AssetRepairOverride, 'validate'):
                print(f"   ✓ validate method exists")
                
        except ImportError as e:
            issues.append(f"Cannot import override class: {e}")
    else:
        warnings.append("No override class registered for Asset Repair")
    
    # ==========================================
    # SUMMARY
    # ==========================================
    print("\n" + "=" * 70)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 70)
    
    if issues:
        print(f"\n❌ CRITICAL ISSUES ({len(issues)}):")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    else:
        print("\n✅ No critical issues found!")
    
    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")
    
    # ==========================================
    # PERMISSION MATRIX
    # ==========================================
    print("\n" + "=" * 70)
    print("📋 PERMISSION MATRIX (Workflow States vs Roles)")
    print("-" * 70)
    
    if workflow:
        roles = set()
        for state in workflow.states:
            for role in (state.allow_edit or "").split(","):
                if role.strip():
                    roles.add(role.strip())
        
        roles = sorted(roles)
        
        print(f"{'State':<30} | " + " | ".join([r[:12] for r in roles]))
        print("-" * 70)
        
        for state in workflow.states:
            allow_edit_roles = [r.strip() for r in (state.allow_edit or "").split(",")]
            row = f"{state.state:<30} | "
            for role in roles:
                if role in allow_edit_roles:
                    row += f"{'✓':^12} | "
                else:
                    row += f"{'':^12} | "
            print(row)
    
    print("\n" + "=" * 70)
    
    return {"issues": issues, "warnings": warnings}
```

---

## STEP 2: Create the sync generator script

Create file: `~/frappe-bench/apps/tub_suite/tub_suite/patches/generate_prod_sync.py`

```python
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
                             filters={"dt": ["in", ["Asset Repair", "Asset Repair Parts Used", 
                                                    "Asset Repair Parts Replaced", "Asset Repair Additional Parts"]]},
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
                             filters={"doc_type": ["in", ["Asset Repair", "Asset Repair Parts Used",
                                                          "Asset Repair Parts Replaced", "Asset Repair Additional Parts"]]},
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
    for df in frappe.get_all("DocField",
                             filters={"parent": ["in", ["Asset Repair Parts Used",
                                                        "Asset Repair Parts Replaced",
                                                        "Asset Repair Additional Parts"]]},
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
```

---

## STEP 3: Execute the commands

### First, run diagnostic on PROD to see all issues:
```bash
cd ~/frappe-bench
bench --site tub.x-desk.tech execute tub_suite.patches.diagnose_asset_repair.run_diagnostics
```

### Then, generate mega-patch from DEV:
```bash
cd ~/frappe-bench
bench --site tub execute tub_suite.patches.generate_prod_sync.generate_python_patch
```

### Copy the generated patch:
```bash
cp /tmp/mega_sync_patch_*.py ~/frappe-bench/apps/tub_suite/tub_suite/patches/mega_sync_dev_to_prod.py
```

### Register the patch:
```bash
echo "tub_suite.patches.mega_sync_dev_to_prod" >> ~/frappe-bench/apps/tub_suite/tub_suite/patches.txt
```

### Run on PROD:
```bash
bench --site tub.x-desk.tech migrate
bench --site tub.x-desk.tech clear-cache
```

### If patch already executed and needs re-run:
```bash
bench --site tub.x-desk.tech execute frappe.patches.delete_patch_log --args '["tub_suite.patches.mega_sync_dev_to_prod"]'
bench --site tub.x-desk.tech migrate
```

---

## Summary of Tables Being Synced

| Table | What it controls |
|-------|------------------|
| `tabCustom Field` | Field visibility (depends_on), required, hidden |
| `tabProperty Setter` | Property overrides on standard fields |
| `tabDocField` | Child table grid columns (in_list_view) |
| `tabWorkflow Document State` | Who can edit in each state (allow_edit) |
| `tabWorkflow Transition` | Who can transition (allowed) |
| `tabClient Script` | Browser-side validation |
| `tabServer Script` | Server-side validation |

---

## Why This Problem Exists

```
DEV: Configure via UI → Values saved to DEV database
     ↓
Export to fixtures/custom_field.json (often has NULL or old values)
     ↓
PROD: Run migrate
     ↓
Frappe: "Record exists, skipping" (DOESN'T UPDATE!)
     ↓
PROD has OLD values, not DEV values
```

**Solution:** Use patches to UPDATE existing records. Fixtures only CREATE new records.