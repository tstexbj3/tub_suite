# TUB Suite Deployment Procedures

## Critical Understanding: How Frappe Syncs Configuration

### The Two-Way Sync Problem

Frappe has TWO places where DocType configuration lives:
1. **JSON files** in `tub_suite/doctype/*/` directories (version controlled)
2. **Database tables** (`tabDocType`, `tabDocField`, etc.)

**CRITICAL**: Changes can happen in EITHER place, and they DON'T automatically sync:

```
JSON File Changes              Database Changes
(via git/editor)              (via UI/Customize Form)
       ↓                              ↓
bench migrate                 bench export-doc
       ↓                              ↓
   Database                       JSON Files
```

### Why Fixtures DON'T Update Existing Records

From ERPNext Implementation docs (Decision 3: Patch vs Fixture):

> Frappe uses timestamp-based import logic:
> - If database `modified` >= fixture `modified`, import is **SKIPPED**
> - This is BY DESIGN in `frappe/modules/import_file.py` lines 125-128
> - Fixtures are for INITIAL configuration, not updates

**Use fixtures for**: Custom Fields, Property Setters, Workflows (first time)
**Use patches for**: Updating existing configuration records

---

## Procedure 1: Deploy DocType Schema Changes (Child Tables, Field Properties)

### What This Covers
- Changing `in_list_view` for child table columns
- Changing field types, labels, options
- Adding/removing fields from DocType
- Changing field order

### Steps

#### On DEV:

```bash
# 1. Make changes via UI (Customize Form)
# - Customize Form → Select DocType → Make changes → Save

# 2. Export the DocType definition to JSON
bench --site devsite export-doc "DocType" "Repair Spare Part"

# This updates: tub_suite/tub_suite/doctype/repair_spare_part/repair_spare_part.json

# 3. Verify JSON file has your changes
cat tub_suite/tub_suite/doctype/repair_spare_part/repair_spare_part.json

# 4. Commit to git
git add tub_suite/tub_suite/doctype/repair_spare_part/
git commit -m "fix: Update Repair Spare Part grid columns"

# 5. Push to branch
git push origin v2.1.0
```

#### On PRODUCTION:

```bash
# 1. Pull latest code
cd ~/frappe-bench/apps/tub_suite
git pull origin v2.1.0

# 2. Reload the specific DocType
bench --site prodsite reload-doctype "Repair Spare Part"

# OR migrate entire site (slower but safer)
bench --site prodsite migrate

# 3. Clear cache
bench --site prodsite clear-cache

# 4. Restart bench (if using production mode)
sudo supervisorctl restart frappe-bench-web:
sudo supervisorctl restart frappe-bench-workers:
```

### Verification

```bash
# Check field properties in database
bench --site prodsite console

>>> doc = frappe.get_meta("Repair Spare Part")
>>> for field in doc.fields:
...     if field.in_list_view:
...         print(f"{field.fieldname}: in_list_view={field.in_list_view}")
```

---

## Procedure 2: Deploy Custom Field Changes (Field Visibility, Depends On)

### What This Covers
- Changing `depends_on` conditions
- Changing `hidden` property
- Changing `read_only` property
- Any Custom Field configuration

### Steps

#### On DEV:

```bash
# 1. Make changes via Customize Form
# - Customize Form → Asset Repair → Find custom field → Modify properties

# 2. CRITICAL: Changes are in DATABASE, NOT in fixtures
# Need to export fixtures:
bench --site devsite export-fixtures --app tub_suite

# This updates: tub_suite/tub_suite/fixtures/custom_field.json

# 3. Verify fixture has correct values (not null)
cat tub_suite/tub_suite/fixtures/custom_field.json | grep -A5 "final_remarks"

# Should show:
# "depends_on": "eval:doc.workflow_state==\"Finished\"",
# NOT:
# "depends_on": null,

# 4. If fixture has wrong values, manually update it OR:
# Delete old fixture, make changes fresh, export again

# 5. Commit to git
git add tub_suite/tub_suite/fixtures/custom_field.json
git commit -m "fix: Update Custom Field visibility rules"
git push origin v2.1.0
```

#### On PRODUCTION:

**CRITICAL**: Fixtures don't update existing records. Use a PATCH instead:

```python
# Create: tub_suite/tub_suite/patches/v2_1/update_custom_field_visibility.py

import frappe

def execute():
    """Update Custom Field visibility rules that fixtures won't update."""

    # Asset Repair custom fields
    custom_fields = {
        "Asset Repair-final_remarks": {
            "depends_on": 'eval:doc.workflow_state=="Finished"',
            "hidden": 0
        },
        "Asset Repair-received_by": {
            "hidden": 1
        },
        "Asset Repair-received_date": {
            "hidden": 1
        },
        "Asset Repair-section_3b_break": {
            "depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'
        }
    }

    for field_name, properties in custom_fields.items():
        if frappe.db.exists("Custom Field", field_name):
            doc = frappe.get_doc("Custom Field", field_name)
            for key, value in properties.items():
                setattr(doc, key, value)
            doc.save()
            frappe.db.commit()
            print(f"Updated {field_name}")
```

```ini
# Add to: tub_suite/tub_suite/patches.txt
[post_model_sync]
tub_suite.patches.v2_1.update_custom_field_visibility
```

```bash
# On production:
cd ~/frappe-bench/apps/tub_suite
git pull origin v2.1.0
bench --site prodsite migrate  # Runs the patch
bench --site prodsite clear-cache
```

---

## Procedure 3: Deploy Workflow Changes

### Steps

#### On DEV:

```bash
# 1. Make changes via Workflow UI
# - Setup → Workflow → Asset Repair Workflow

# 2. Export fixtures
bench --site devsite export-fixtures --app tub_suite

# 3. Verify fixture files
ls -la tub_suite/tub_suite/fixtures/
# Should show: workflow.json, workflow_state.json, workflow_action_master.json

# 4. Commit and push
git add tub_suite/tub_suite/fixtures/workflow*.json
git commit -m "fix: Update Asset Repair workflow states"
git push origin v2.1.0
```

#### On PRODUCTION:

**OPTION 1: Fresh Install (No existing workflow)**
```bash
git pull origin v2.1.0
bench --site prodsite migrate  # Fixtures auto-import
```

**OPTION 2: Update Existing Workflow (PATCH REQUIRED)**
```python
# Create: tub_suite/tub_suite/patches/v2_1/update_workflows.py

import frappe
import json
import os

def execute():
    """Force update workflows from fixture files."""

    fixtures_path = frappe.get_app_path("tub_suite", "fixtures")

    # Update Workflow
    workflow_file = os.path.join(fixtures_path, "workflow.json")
    if os.path.exists(workflow_file):
        with open(workflow_file) as f:
            workflows = json.load(f)

        for workflow_data in workflows:
            if frappe.db.exists("Workflow", workflow_data["name"]):
                doc = frappe.get_doc("Workflow", workflow_data["name"])
                doc.update(workflow_data)
                doc.save()
                print(f"Updated Workflow: {workflow_data['name']}")

    frappe.db.commit()
```

---

## Procedure 4: Full Version Deployment Checklist

Use this checklist when deploying a new version (e.g., v2.1.11 → v2.1.12):

### Pre-Deployment (DEV)

- [ ] All changes made via UI are exported to JSON/fixtures
- [ ] All JSON files committed to git
- [ ] `bench --site devsite migrate` runs clean (no errors)
- [ ] All features tested on DEV
- [ ] Version bumped in `tub_suite/__init__.py`
- [ ] Git tag created: `git tag v2.1.12`
- [ ] Changes pushed: `git push origin v2.1.0 --tags`

### Deployment (PRODUCTION)

```bash
# 1. Backup production database
cd ~/frappe-bench
bench --site prodsite backup --with-files

# 2. Pull code changes
cd ~/frappe-bench/apps/tub_suite
git fetch origin
git checkout v2.1.0
git pull origin v2.1.0

# 3. Check what changed
git log --oneline -10

# 4. Check for new patches
cat tub_suite/patches.txt

# 5. Run migration
bench --site prodsite migrate

# 6. Clear all caches
bench --site prodsite clear-cache
bench --site prodsite clear-website-cache

# 7. Rebuild assets (if JS/CSS changes)
bench build --app tub_suite

# 8. Restart services (production mode)
sudo supervisorctl restart frappe-bench-web:
sudo supervisorctl restart frappe-bench-workers:

# 9. Check logs for errors
tail -f ~/frappe-bench/logs/web.error.log
```

### Post-Deployment Verification

- [ ] Check version: `bench --site prodsite console` → `frappe.get_attr("tub_suite.__version__")`
- [ ] Test key workflows: Draft → Submit → Approve
- [ ] Verify field visibility in all workflow states
- [ ] Check child table columns display correctly
- [ ] Test with different user roles (Technician, Supervisor, Engineering)

---

## Common Mistakes and Solutions

### Mistake 1: "I changed JSON file but DEV doesn't reflect changes"

**Problem**: JSON file changes don't auto-sync to database.

**Solution**:
```bash
bench --site devsite reload-doctype "DocType Name"
# OR
bench --site devsite migrate
```

### Mistake 2: "I changed via UI but PROD doesn't get updates"

**Problem**: Didn't export changes to JSON/fixtures before committing.

**Solution**:
```bash
# For DocType schema:
bench --site devsite export-doc "DocType" "DocType Name"

# For Custom Fields/Property Setters:
bench --site devsite export-fixtures --app tub_suite
```

### Mistake 3: "Fixtures deployed but nothing changed in PROD"

**Problem**: Frappe skips fixture import if DB record is newer.

**Solution**: Use a patch (see Procedure 2 above).

### Mistake 4: "I forgot what I changed on DEV 2 weeks ago"

**Problem**: No documentation of manual changes.

**Solution**:
1. Always export immediately after UI changes
2. Commit with descriptive messages
3. Document in this file what was changed and WHY

---

## Emergency Rollback Procedure

If deployment breaks production:

```bash
# 1. Restore database backup
cd ~/frappe-bench
bench --site prodsite restore /path/to/backup/sitename-database.sql.gz

# 2. Rollback code
cd ~/frappe-bench/apps/tub_suite
git log --oneline -10  # Find last working commit
git reset --hard <commit-hash>

# 3. Restart services
sudo supervisorctl restart frappe-bench-web:
sudo supervisorctl restart frappe-bench-workers:

# 4. Investigate what went wrong before trying again
```

---

## Key Principles

1. **ALWAYS export after UI changes** - JSON files are source of truth
2. **NEVER manually edit database on production** - Use patches for all updates
3. **TEST on DEV first** - `bench migrate` must run clean before deploying
4. **DOCUMENT everything** - Future you will thank present you
5. **BACKUP before deploy** - Database + files
6. **ONE change at a time** - Don't bundle unrelated changes in one deployment

---

## References

- ERPNext Custom App Implementation: `~/.claude/skills/impl/erpnext-impl-customapp/SKILL.md`
- ERPNext Hooks Implementation: `~/.claude/skills/impl/erpnext-impl-hooks/SKILL.md`
- Frappe Framework Docs: https://frappeframework.com/docs
- ERPNext Developer Guide: https://docs.erpnext.com/docs/user/en/guides/app-development
