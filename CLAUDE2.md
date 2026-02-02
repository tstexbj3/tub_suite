# TUB Suite - CORRECTED Deployment Approach

## CRITICAL CONTEXT FOR CLAUDE CODE

### READ THIS FIRST - LESSONS LEARNED THE HARD WAY

**DO NOT** create patches that bake in configuration values and add them to patches.txt.
The v2.1.19 mega_sync_all_config patch did exactly this and CAUSED the problems:
- It ran on migrate with OLD config values
- Every new fix (v2.1.24-v2.1.28) was undone on the next migrate
- This created an infinite loop: fix → migrate → reset → fix → migrate → reset

### Sites
- **DEV site:** `tub` (local WSL)
- **PROD site:** `tub.x-desk.tech` (DigitalOcean VPS)
- **App:** `tub_suite`
- **DEV bench path:** `~/frappe-bench` (WSL)
- **PROD bench path:** `/home/taynaja/frappe-bench` (VPS)
- **Branch:** `v2.1.0`
- **Repo:** `https://github.com/tstexbj3/tub_suite.git`

### CRITICAL: Git Tag vs Branch Ambiguity

**THE PROBLEM**: There is BOTH a tag named `v2.1.0` AND a branch named `v2.1.0` in the repo.

When you run `git pull origin v2.1.0`, git pulls the **TAG** (which points to an old commit), NOT the **BRANCH** (which has all the latest commits).

This is why PROD was stuck on old code even after pushing commits from DEV.

**CORRECT COMMANDS**:

```bash
# ❌ NEVER DO THIS (pulls the tag, not the branch)
git pull origin v2.1.0

# ✅ ALWAYS DO THIS (resets to latest branch commit)
git fetch origin
git reset --hard origin/v2.1.0

# When pushing (already correct)
git push origin refs/heads/v2.1.0
```

**WHY THIS MATTERS**:
- v2.1.24-v2.1.29 commits may have never reached PROD
- PROD was stuck on the old v2.1.0 tag while DEV kept moving forward
- This made debugging impossible - code looked the same but PROD had old version

### The Root Cause
Frappe fixtures ONLY CREATE new records. They DO NOT UPDATE existing records.
When PROD already has a Custom Field, running `migrate` SKIPS the fixture update.
The database values on PROD stay whatever they were before.

---

## RULES - DO NOT BREAK THESE

### Rule 1: NEVER add config-sync patches to patches.txt
Patches in patches.txt run during `bench migrate`. If they contain config snapshots,
they become stale as soon as DEV changes. This is what caused the v2.1.19 disaster.

### Rule 2: NEVER commit from PROD to the repo
All commits should flow DEV → GitHub → PROD. Never the other direction.
PROD should only ever `git pull` or `git reset --hard origin/branch`.

### Rule 3: Config changes need TWO things
1. Update the fixture JSON file (for new installs)
2. Create a ONE-TIME bench execute script (for existing PROD)

### Rule 4: Test on DEV THEN deploy to PROD
Never modify PROD directly unless it's a one-time database fix via `bench console`.

### Rule 5: Read the existing patches.txt before adding anything
Check what patches already exist. Make sure nothing conflicts.

---

## CORRECT WAY TO SYNC DEV → PROD

### Method 1: One-time bench execute (for immediate fixes)

This runs ONCE manually. It does NOT go in patches.txt. It does NOT run on migrate.

```bash
# ON PROD - run manually, one time only
bench --site tub.x-desk.tech execute tub_suite.scripts.sync_config_from_dev
```

The script file goes in `tub_suite/scripts/` (NOT `tub_suite/patches/`).
It is NEVER added to patches.txt.

### Method 2: bench console (for emergency fixes)

```bash
# ON PROD - direct database fix
bench --site tub.x-desk.tech console
```

```python
import frappe
# Fix specific field
frappe.db.set_value("Custom Field", "Asset Repair-my_field", "hidden", 1)
frappe.db.commit()
frappe.clear_cache()
```

### Method 3: Proper fixture export (for new installs)

```bash
# ON DEV after making UI changes
cd ~/frappe-bench
bench --site tub export-fixtures --app tub_suite
# Then commit the updated fixture JSON files
```

This updates the JSON files so NEW installations get correct values.
But it does NOT help existing PROD (because fixtures don't update existing records).

---

## CURRENT STATE (as of v2.1.29)

### What was done:
- v2.1.19: mega_sync_all_config patch created (BAD - caused config reset loop)
- v2.1.24: Remove duplicate workflow transitions
- v2.1.25: Remove section_break_23 and final_remarks from field_order
- v2.1.26: Remove Custom DocPerm from fixtures
- v2.1.27: Set Section 5 Final Remarks fields to hidden in fixture
- v2.1.28: Remove fm_en_04_section_5 from field_order
- v2.1.29: REMOVED mega_sync patch from patches.txt (the fix!)

### What's in patches.txt now (after v2.1.29):
The mega_sync_all_config line was removed. Check current state:
```bash
cat ~/frappe-bench/apps/tub_suite/tub_suite/patches.txt
```

### Known remaining issues on PROD:
- Section 5 (Final Remarks) visibility may still be wrong
- Supervisor signature fields may be affected
- Workflow state permissions may have stale values
- 112 combinations (8 states × 7 roles × 2 repair types) mostly untested

---

## WHAT TO DO NOW

---

## WHAT HAPPENED WITH v2.1.24-v2.1.29 (February 2026)

### The Problem Discovered
After deploying v2.1.19's mega_sync_all_config patch, every subsequent fix (v2.1.24-v2.1.28) was being UNDONE on every `migrate`:

1. **v2.1.24**: Fixed duplicate workflow transitions in workflow.json fixture
2. **v2.1.25**: Removed section_break_23 and final_remarks from field_order in property_setter.json
3. **v2.1.26**: Removed broken Custom DocPerm fixture causing migrate crash
4. **v2.1.27**: Set Section 5 fields (fm_en_04_section_5, final_remarks) to `hidden=1` in custom_field.json
5. **v2.1.28**: Removed fm_en_04_section_5 from field_order in property_setter.json

BUT: Every time `migrate` ran, the mega_sync patch (v2.1.19) ran FIRST and reset everything back to OLD values before fixture sync could apply the new values.

### The Root Cause
The mega_sync_all_config patch:
- Was added to patches.txt in v2.1.19
- **Ran on EVERY migrate** (patches in patches.txt always run)
- Read from fixture files and applied them to PROD database
- BUT it read the fixture files at THE TIME IT WAS CREATED (v2.1.19)
- Even though we updated the fixture files (v2.1.24-v2.1.28), the patch had OLD values baked in
- Result: **Infinite reset loop** - fix → migrate → reset → fix → migrate → reset

### The Fix (v2.1.29)
Removed the mega_sync patch entirely:
```bash
# Removed from patches.txt
sed -i '/mega_sync_all_config/d' tub_suite/patches.txt

# Deleted execution history
frappe.db.sql("DELETE FROM `tabPatch Log` WHERE patch LIKE '%mega_sync_all_config%'")
```

### Why It Took So Long To Find
1. The patch name didn't show up in migrate output (ran silently)
2. We assumed fixtures were the problem (but they were correct in the code)
3. We kept trying to fix PROD database manually (which got reset on next migrate)
4. The mega_sync patch seemed like a good idea initially (sync DEV → PROD)
5. We didn't realize patches.txt patches run EVERY migrate forever

### Lessons Learned
- ❌ **NEVER add config-sync patches to patches.txt**
- ❌ **Patches with baked-in config values become stale immediately**
- ❌ **Patches in patches.txt run on EVERY migrate (not just once)**
- ✅ **Use one-time `bench execute` scripts instead**
- ✅ **Keep config in JSON files, read at runtime**
- ✅ **Fixtures only work for NEW installs, not updates**

---

### Step 1: Create a sync SCRIPT (not a patch)

Create file: `~/frappe-bench/apps/tub_suite/tub_suite/scripts/__init__.py` (empty)
Create file: `~/frappe-bench/apps/tub_suite/tub_suite/scripts/sync_config_from_dev.py`

This script should:
1. Run on DEV first to EXPORT current config to a JSON file
2. That JSON file gets committed to the repo
3. Run on PROD to IMPORT from that JSON file
4. It is NEVER added to patches.txt
5. It reads the JSON at runtime (not baked-in values)

### Step 2: Export from DEV

```bash
bench --site tub execute tub_suite.scripts.sync_config_from_dev.export_dev_config
```

This creates: `~/frappe-bench/apps/tub_suite/tub_suite/config/asset_repair_config.json`

### Step 3: Commit the config JSON

```bash
cd ~/frappe-bench/apps/tub_suite
git add tub_suite/config/asset_repair_config.json
git commit -m "chore: Export current DEV config for PROD sync"
git push origin refs/heads/v2.1.0
```

### Step 4: Pull on PROD and run sync

```bash
# On PROD
cd /home/taynaja/frappe-bench/apps/tub_suite
git fetch origin && git reset --hard origin/v2.1.0

# Run the sync (NOT migrate, just execute)
cd /home/taynaja/frappe-bench
bench --site tub.x-desk.tech execute tub_suite.scripts.sync_config_from_dev.apply_to_prod
bench --site tub.x-desk.tech clear-cache
```

### Step 5: Verify

```bash
bench --site tub.x-desk.tech execute tub_suite.scripts.sync_config_from_dev.verify_sync
```

---

## THE SYNC SCRIPT

Create: `~/frappe-bench/apps/tub_suite/tub_suite/scripts/sync_config_from_dev.py`

```python
"""
Asset Repair Configuration Sync
================================
This is a MANUAL sync script. NOT a patch. NEVER add to patches.txt.

Usage:
    # Step 1: Export from DEV
    bench --site tub execute tub_suite.scripts.sync_config_from_dev.export_dev_config

    # Step 2: Commit the JSON file to git, push, pull on PROD

    # Step 3: Apply to PROD
    bench --site tub.x-desk.tech execute tub_suite.scripts.sync_config_from_dev.apply_to_prod

    # Step 4: Verify
    bench --site tub.x-desk.tech execute tub_suite.scripts.sync_config_from_dev.verify_sync
"""

import frappe
import json
import os
from datetime import datetime


# Path to the config file (relative to app root)
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "asset_repair_config.json")

# DocTypes we care about
ASSET_REPAIR_DOCTYPES = [
    "Asset Repair",
    "Asset Repair Parts Used",
    "Asset Repair Parts Replaced",
    "Asset Repair Additional Parts",
]


def export_dev_config():
    """
    Export ALL Asset Repair configuration from DEV database to a JSON file.
    Run this ON DEV: bench --site tub execute tub_suite.scripts.sync_config_from_dev.export_dev_config
    """

    site = frappe.local.site
    print(f"\n{'='*60}")
    print(f"EXPORTING CONFIG FROM: {site}")
    print(f"{'='*60}")

    config = {
        "_meta": {
            "exported_from": site,
            "exported_at": datetime.now().isoformat(),
            "description": "Asset Repair configuration - DO NOT EDIT MANUALLY"
        },
        "custom_fields": {},
        "property_setters": {},
        "docfields": {},
        "workflow_states": [],
        "workflow_transitions": [],
        "client_scripts": {},
        "server_scripts": {}
    }

    # 1. Custom Fields
    print("\n[1/7] Custom Fields...")
    for cf in frappe.get_all("Custom Field",
                             filters={"dt": ["in", ASSET_REPAIR_DOCTYPES]},
                             fields=["*"]):
        config["custom_fields"][cf["name"]] = {
            "dt": cf.get("dt"),
            "fieldname": cf.get("fieldname"),
            "fieldtype": cf.get("fieldtype"),
            "label": cf.get("label"),
            "insert_after": cf.get("insert_after"),
            "options": cf.get("options"),
            "depends_on": cf.get("depends_on"),
            "mandatory_depends_on": cf.get("mandatory_depends_on"),
            "read_only_depends_on": cf.get("read_only_depends_on"),
            "hidden": cf.get("hidden"),
            "read_only": cf.get("read_only"),
            "reqd": cf.get("reqd"),
            "in_list_view": cf.get("in_list_view"),
            "in_standard_filter": cf.get("in_standard_filter"),
            "columns": cf.get("columns"),
            "default": cf.get("default"),
            "fetch_from": cf.get("fetch_from"),
            "description": cf.get("description"),
        }
    print(f"     {len(config['custom_fields'])} fields exported")

    # 2. Property Setters
    print("[2/7] Property Setters...")
    for ps in frappe.get_all("Property Setter",
                             filters={"doc_type": ["in", ASSET_REPAIR_DOCTYPES]},
                             fields=["*"]):
        config["property_setters"][ps["name"]] = {
            "doc_type": ps.get("doc_type"),
            "doctype_or_field": ps.get("doctype_or_field"),
            "field_name": ps.get("field_name"),
            "property": ps.get("property"),
            "property_type": ps.get("property_type"),
            "value": ps.get("value"),
        }
    print(f"     {len(config['property_setters'])} setters exported")

    # 3. DocFields (child table grid config)
    print("[3/7] DocFields (child tables)...")
    child_tables = [dt for dt in ASSET_REPAIR_DOCTYPES if dt != "Asset Repair"]
    for df in frappe.get_all("DocField",
                             filters={"parent": ["in", child_tables]},
                             fields=["name", "parent", "fieldname", "fieldtype", "label",
                                     "in_list_view", "columns", "read_only", "hidden", "reqd"]):
        key = f"{df['parent']}.{df['fieldname']}"
        config["docfields"][key] = {
            "parent": df["parent"],
            "fieldname": df["fieldname"],
            "in_list_view": df.get("in_list_view"),
            "columns": df.get("columns"),
            "read_only": df.get("read_only"),
            "hidden": df.get("hidden"),
        }
    print(f"     {len(config['docfields'])} fields exported")

    # 4. Workflow States
    print("[4/7] Workflow States...")
    for ws in frappe.db.sql("""
        SELECT wds.state, wds.allow_edit, wds.doc_status, wds.update_field,
               wds.update_value, wds.is_optional_state, w.name as parent
        FROM `tabWorkflow Document State` wds
        JOIN `tabWorkflow` w ON wds.parent = w.name
        WHERE w.document_type = 'Asset Repair'
        ORDER BY wds.idx
    """, as_dict=True):
        config["workflow_states"].append({
            "parent": ws["parent"],
            "state": ws["state"],
            "allow_edit": ws.get("allow_edit", ""),
            "doc_status": ws.get("doc_status"),
            "update_field": ws.get("update_field"),
            "update_value": ws.get("update_value"),
        })
    print(f"     {len(config['workflow_states'])} states exported")

    # 5. Workflow Transitions
    print("[5/7] Workflow Transitions...")
    for wt in frappe.db.sql("""
        SELECT wt.state, wt.action, wt.next_state, wt.allowed,
               wt.allow_self_approval, wt.`condition`, w.name as parent
        FROM `tabWorkflow Transition` wt
        JOIN `tabWorkflow` w ON wt.parent = w.name
        WHERE w.document_type = 'Asset Repair'
        ORDER BY wt.idx
    """, as_dict=True):
        config["workflow_transitions"].append({
            "parent": wt["parent"],
            "state": wt["state"],
            "action": wt["action"],
            "next_state": wt["next_state"],
            "allowed": wt.get("allowed", ""),
            "allow_self_approval": wt.get("allow_self_approval"),
            "condition": wt.get("condition", ""),
        })
    print(f"     {len(config['workflow_transitions'])} transitions exported")

    # 6. Client Scripts
    print("[6/7] Client Scripts...")
    for cs in frappe.get_all("Client Script",
                             filters={"dt": "Asset Repair"},
                             fields=["name", "dt", "view", "enabled", "script"]):
        config["client_scripts"][cs["name"]] = {
            "dt": cs.get("dt"),
            "view": cs.get("view"),
            "enabled": cs.get("enabled"),
            "script": cs.get("script", ""),
        }
    print(f"     {len(config['client_scripts'])} scripts exported")

    # 7. Server Scripts
    print("[7/7] Server Scripts...")
    for ss in frappe.get_all("Server Script",
                             filters={"reference_doctype": "Asset Repair"},
                             fields=["name", "script_type", "reference_doctype",
                                     "doctype_event", "disabled", "script"]):
        config["server_scripts"][ss["name"]] = {
            "script_type": ss.get("script_type"),
            "reference_doctype": ss.get("reference_doctype"),
            "doctype_event": ss.get("doctype_event"),
            "disabled": ss.get("disabled"),
            "script": ss.get("script", ""),
        }
    print(f"     {len(config['server_scripts'])} scripts exported")

    # Write to file
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2, default=str, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"✅ Config exported to: {CONFIG_FILE}")
    print(f"{'='*60}")
    print(f"\nNext steps:")
    print(f"  1. git add tub_suite/config/asset_repair_config.json")
    print(f"  2. git commit -m 'chore: Export DEV config for PROD sync'")
    print(f"  3. git push origin refs/heads/v2.1.0")
    print(f"  4. On PROD: git fetch origin && git reset --hard origin/v2.1.0")
    print(f"  5. On PROD: bench --site tub.x-desk.tech execute tub_suite.scripts.sync_config_from_dev.apply_to_prod")

    return CONFIG_FILE


def apply_to_prod():
    """
    Apply DEV configuration to PROD database.
    Run this ON PROD: bench --site tub.x-desk.tech execute tub_suite.scripts.sync_config_from_dev.apply_to_prod
    """

    site = frappe.local.site
    print(f"\n{'='*60}")
    print(f"APPLYING DEV CONFIG TO: {site}")
    print(f"{'='*60}")

    # Load config from JSON file
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ Config file not found: {CONFIG_FILE}")
        print(f"   Did you export from DEV and pull the latest code?")
        return

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    print(f"Config exported from: {config['_meta']['exported_from']}")
    print(f"Config exported at: {config['_meta']['exported_at']}")

    errors = []
    updated = 0
    skipped = 0

    # 1. Custom Fields
    print("\n[1/7] Syncing Custom Fields...")
    for cf_name, values in config["custom_fields"].items():
        try:
            if frappe.db.exists("Custom Field", cf_name):
                for field, value in values.items():
                    if field in ("dt", "fieldname", "fieldtype", "label"):
                        continue  # Don't update structural fields
                    frappe.db.set_value("Custom Field", cf_name, field, value, update_modified=False)
                updated += 1
                print(f"  ✓ {cf_name}")
            else:
                skipped += 1
                print(f"  ⊘ {cf_name} (not found on PROD)")
        except Exception as e:
            errors.append(f"Custom Field {cf_name}: {e}")
            print(f"  ✗ {cf_name}: {e}")

    # 2. Property Setters
    print("\n[2/7] Syncing Property Setters...")
    for ps_name, values in config["property_setters"].items():
        try:
            if frappe.db.exists("Property Setter", ps_name):
                frappe.db.set_value("Property Setter", ps_name, "value", values.get("value"), update_modified=False)
                updated += 1
                print(f"  ✓ {ps_name}")
            else:
                # Create if doesn't exist
                ps = frappe.new_doc("Property Setter")
                ps.update(values)
                ps.name = ps_name
                ps.insert(ignore_permissions=True)
                updated += 1
                print(f"  + {ps_name} (created)")
        except Exception as e:
            errors.append(f"Property Setter {ps_name}: {e}")
            print(f"  ✗ {ps_name}: {e}")

    # 3. DocFields
    print("\n[3/7] Syncing DocFields...")
    for key, values in config["docfields"].items():
        try:
            result = frappe.db.sql("""
                UPDATE `tabDocField`
                SET in_list_view = %s, columns = %s, read_only = %s, hidden = %s
                WHERE parent = %s AND fieldname = %s
            """, (values["in_list_view"], values["columns"],
                  values["read_only"], values["hidden"],
                  values["parent"], values["fieldname"]))
            updated += 1
            print(f"  ✓ {key}")
        except Exception as e:
            errors.append(f"DocField {key}: {e}")
            print(f"  ✗ {key}: {e}")

    # 4. Workflow States
    print("\n[4/7] Syncing Workflow States...")
    for ws in config["workflow_states"]:
        try:
            frappe.db.sql("""
                UPDATE `tabWorkflow Document State`
                SET allow_edit = %s, doc_status = %s,
                    update_field = %s, update_value = %s
                WHERE parent = %s AND state = %s
            """, (ws["allow_edit"], ws.get("doc_status"),
                  ws.get("update_field"), ws.get("update_value"),
                  ws["parent"], ws["state"]))
            updated += 1
            print(f"  ✓ {ws['state']}: allow_edit={ws['allow_edit']}")
        except Exception as e:
            errors.append(f"Workflow State {ws['state']}: {e}")
            print(f"  ✗ {ws['state']}: {e}")

    # 5. Workflow Transitions
    print("\n[5/7] Syncing Workflow Transitions...")
    for wt in config["workflow_transitions"]:
        try:
            frappe.db.sql("""
                UPDATE `tabWorkflow Transition`
                SET allowed = %s, `condition` = %s, allow_self_approval = %s
                WHERE parent = %s AND state = %s AND action = %s AND next_state = %s
            """, (wt["allowed"], wt["condition"], wt.get("allow_self_approval"),
                  wt["parent"], wt["state"], wt["action"], wt["next_state"]))
            updated += 1
            print(f"  ✓ {wt['state']} --[{wt['action']}]--> {wt['next_state']}")
        except Exception as e:
            errors.append(f"Transition {wt['state']}->{wt['next_state']}: {e}")
            print(f"  ✗ {wt['state']}: {e}")

    # 6. Client Scripts
    print("\n[6/7] Syncing Client Scripts...")
    for cs_name, values in config["client_scripts"].items():
        try:
            if frappe.db.exists("Client Script", cs_name):
                frappe.db.set_value("Client Script", cs_name, {
                    "script": values["script"],
                    "enabled": values["enabled"]
                }, update_modified=False)
                updated += 1
                print(f"  ✓ {cs_name}")
            else:
                skipped += 1
                print(f"  ⊘ {cs_name} (not found)")
        except Exception as e:
            errors.append(f"Client Script {cs_name}: {e}")
            print(f"  ✗ {cs_name}: {e}")

    # 7. Server Scripts
    print("\n[7/7] Syncing Server Scripts...")
    for ss_name, values in config["server_scripts"].items():
        try:
            if frappe.db.exists("Server Script", ss_name):
                frappe.db.set_value("Server Script", ss_name, {
                    "script": values["script"],
                    "disabled": values["disabled"]
                }, update_modified=False)
                updated += 1
                print(f"  ✓ {ss_name}")
            else:
                skipped += 1
                print(f"  ⊘ {ss_name} (not found)")
        except Exception as e:
            errors.append(f"Server Script {ss_name}: {e}")
            print(f"  ✗ {ss_name}: {e}")

    # Commit
    frappe.db.commit()
    frappe.clear_cache()

    print(f"\n{'='*60}")
    print(f"SYNC COMPLETE")
    print(f"  Updated: {updated}")
    print(f"  Skipped: {skipped}")
    print(f"  Errors:  {len(errors)}")
    if errors:
        print(f"\nErrors:")
        for e in errors:
            print(f"  - {e}")
    print(f"{'='*60}")
    print(f"\n⚠️  Clear browser cache and hard refresh (Ctrl+Shift+R)")


def verify_sync():
    """
    Verify PROD configuration matches expected values.
    Run ON PROD: bench --site tub.x-desk.tech execute tub_suite.scripts.sync_config_from_dev.verify_sync
    """

    site = frappe.local.site
    print(f"\n{'='*60}")
    print(f"VERIFYING CONFIG ON: {site}")
    print(f"{'='*60}")

    if not os.path.exists(CONFIG_FILE):
        print(f"❌ Config file not found: {CONFIG_FILE}")
        return

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    mismatches = []

    # Check Custom Fields
    print("\n[1/4] Verifying Custom Fields...")
    for cf_name, expected in config["custom_fields"].items():
        if frappe.db.exists("Custom Field", cf_name):
            actual = frappe.db.get_value("Custom Field", cf_name,
                                         ["depends_on", "hidden", "read_only"],
                                         as_dict=True)
            for field in ["depends_on", "hidden", "read_only"]:
                exp_val = expected.get(field)
                act_val = actual.get(field)
                # Normalize
                if exp_val is None: exp_val = ""
                if act_val is None: act_val = ""
                if str(exp_val) != str(act_val):
                    mismatches.append(f"Custom Field {cf_name}.{field}: expected={exp_val}, actual={act_val}")

    # Check DocFields
    print("[2/4] Verifying DocFields...")
    for key, expected in config["docfields"].items():
        actual = frappe.db.sql("""
            SELECT in_list_view, columns, read_only, hidden
            FROM `tabDocField`
            WHERE parent = %s AND fieldname = %s
        """, (expected["parent"], expected["fieldname"]), as_dict=True)

        if actual:
            actual = actual[0]
            for field in ["in_list_view", "columns"]:
                if str(expected.get(field, 0)) != str(actual.get(field, 0)):
                    mismatches.append(f"DocField {key}.{field}: expected={expected.get(field)}, actual={actual.get(field)}")

    # Check Workflow States
    print("[3/4] Verifying Workflow States...")
    for ws in config["workflow_states"]:
        actual = frappe.db.sql("""
            SELECT allow_edit FROM `tabWorkflow Document State`
            WHERE parent = %s AND state = %s
        """, (ws["parent"], ws["state"]), as_dict=True)

        if actual:
            if (actual[0].get("allow_edit") or "") != (ws.get("allow_edit") or ""):
                mismatches.append(f"Workflow State {ws['state']}.allow_edit: expected={ws['allow_edit']}, actual={actual[0].get('allow_edit')}")

    # Check Workflow Transitions
    print("[4/4] Verifying Workflow Transitions...")
    for wt in config["workflow_transitions"]:
        actual = frappe.db.sql("""
            SELECT allowed, `condition` FROM `tabWorkflow Transition`
            WHERE parent = %s AND state = %s AND action = %s AND next_state = %s
        """, (wt["parent"], wt["state"], wt["action"], wt["next_state"]), as_dict=True)

        if actual:
            if (actual[0].get("allowed") or "") != (wt.get("allowed") or ""):
                mismatches.append(f"Transition {wt['state']}->{wt['next_state']}.allowed: expected={wt['allowed']}, actual={actual[0].get('allowed')}")

    print(f"\n{'='*60}")
    if mismatches:
        print(f"❌ FOUND {len(mismatches)} MISMATCHES:")
        for m in mismatches:
            print(f"  - {m}")
    else:
        print(f"✅ ALL CONFIG MATCHES! PROD is in sync with DEV.")
    print(f"{'='*60}")

    return mismatches
```

---

## DEPLOYMENT WORKFLOW GOING FORWARD

Every time you change something on DEV:

### 1. Make changes on DEV UI or code

### 2. Export config
```bash
bench --site tub execute tub_suite.scripts.sync_config_from_dev.export_dev_config
```

### 3. Commit and push
```bash
cd ~/frappe-bench/apps/tub_suite
git add -A
git commit -m "description of changes"
git push origin refs/heads/v2.1.0
```

### 4. Deploy to PROD
```bash
# On PROD server - IMPORTANT: Use fetch + reset, NOT git pull
cd /home/taynaja/frappe-bench/apps/tub_suite
git fetch origin
git reset --hard origin/v2.1.0

# Run migrate for code changes (patches, doctypes, etc.)
cd /home/taynaja/frappe-bench
bench --site tub.x-desk.tech migrate

# Run config sync for database values
bench --site tub.x-desk.tech execute tub_suite.scripts.sync_config_from_dev.apply_to_prod

# Clear cache
bench --site tub.x-desk.tech clear-cache
```

**⚠️ CRITICAL**: NEVER use `git pull origin v2.1.0` because there's both a tag and branch with that name. Always use `git fetch origin && git reset --hard origin/v2.1.0`.

### 5. Verify
```bash
bench --site tub.x-desk.tech execute tub_suite.scripts.sync_config_from_dev.verify_sync
```

---

## IMPORTANT: What NOT to do

❌ DO NOT add sync scripts to patches.txt
❌ DO NOT commit from PROD server
❌ DO NOT modify PROD database then run migrate (migrate may reset your changes)
❌ DO NOT rely on fixtures to update existing records
❌ DO NOT create patches that bake in config values at a point in time
❌ DO NOT run `bench --site tub.x-desk.tech migrate` AFTER running the sync
    (migrate might reset values via fixtures - always run migrate BEFORE sync)

✅ DO export config from DEV after every change
✅ DO commit config JSON to the repo
✅ DO run sync manually on PROD after pulling code
✅ DO verify after sync
✅ DO run migrate BEFORE sync (migrate first, then sync)