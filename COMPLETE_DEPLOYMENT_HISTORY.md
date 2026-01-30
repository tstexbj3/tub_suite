# Complete Deployment History & Fixes - TUB Suite v2.1.x

**CRITICAL**: Read this ENTIRE document before making ANY changes to production.

---

## Session Summary: 2026-01-30

### What Was Broken

After deploying v2.1.11 to production, we discovered **MASSIVE configuration drift** between DEV and PROD:

1. **13 Custom Fields** had wrong visibility rules (depends_on = null instead of proper conditions)
2. **Received By/Received Date** fields were VISIBLE when they should be HIDDEN
3. **Child table grid columns** showed wrong fields
4. **Engineering Team permission** blocked from editing in "Pending Engineering Supervisor Review" state
5. **custom_docperm.json** fixture breaking migrations with KeyError

### Root Cause Analysis

**THE CORE PROBLEM**: Frappe's fixture system is fundamentally broken for updates.

```
How Frappe Fixtures Work (BY DESIGN):
1. Fixtures are meant for INITIAL deployment only
2. On import: if DB.modified >= Fixture.modified → SKIP UPDATE
3. Running "bench export-fixtures" does NOT guarantee capturing all database changes
4. Manually editing fields via Customize Form → changes stay in DB but DON'T export to fixtures
5. Deploying fixtures to production → OLD fixture values overwrite NEW database values
```

**What Actually Happened**:
1. Week 1: Configured all field visibility on DEV via Customize Form ✅
2. Week 1: Exported fixtures (but some `depends_on` values became NULL in JSON) ❌
3. Week 2: Deployed to production via `bench migrate`
4. Week 2: Fixtures imported with NULL values → OVERWROTE working database values ❌
5. Week 2-4: Spent 2 weeks manually fixing production, one field at a time ❌
6. Every new deployment → BROKE what was already fixed ❌

---

## What We Fixed (v2.1.12 - v2.1.15)

### Fix #1: Removed Custom Field from Fixtures (v2.1.13)

**File**: `tub_suite/hooks.py`

**Change**:
```python
# BEFORE:
fixtures = [
    {"dt": "Custom Field", "filters": [["dt", "in", ["Asset Repair"...]]]},
    ...
]

# AFTER:
fixtures = [
    # REMOVED: Custom Field fixture - causes field visibility to revert to bad values
    # Custom Fields are now managed via patches only (see patches/v2_1/)
    # {"dt": "Custom Field", "filters": [["dt", "in", ["Asset Repair"...]]]},
    ...
]
```

**Why**: Stop the bad fixture from overwriting correct database values on every migration.

**Commit**: `fix: Remove Custom Field from fixtures, use permanent patch instead (v2.1.13)`

---

### Fix #2: Created Permanent Patch for All 13 Field Differences (v2.1.14)

**File**: `tub_suite/patches/v2_1/set_custom_field_visibility_permanent.py`

**What It Does**:
- Sets correct `hidden`, `depends_on`, and `read_only_depends_on` for ALL 13 broken fields
- Is IDEMPOTENT - safe to run multiple times
- Registered in `patches.txt` to run on every deployment

**The 13 Fields Fixed**:
1. `received_by`: hidden=1
2. `received_date`: hidden=1
3. `final_remarks`: depends_on='eval:doc.workflow_state=="Finished"'
4. `cleanliness_after_area`: depends_on (verification states)
5. `cleanliness_after_machine`: depends_on (verification states)
6. `cleanliness_before_area`: depends_on (verification states)
7. `cleanliness_before_machine`: depends_on (verification states)
8. `parts_inserted`: depends_on (verification states)
9. `parts_removed`: depends_on (verification states)
10. `spare_parts_used`: depends_on (engineering states)
11. `repair_type`: depends_on + read_only_depends_on
12. `repair_source`: read_only_depends_on
13. `section_3b_break`, `fm_en_04_section_5`: depends_on

**How to verify it worked**:
```bash
# On production:
bench --site tub.x-desk.tech execute tub_suite.compare_dev_prod.find_all_differences

# Should show: TOTAL DIFFERENCES FOUND: 0
```

**Commit**: `fix: Update patch to fix ALL 13 Custom Field visibility differences (v2.1.14)`

---

### Fix #3: Child Table Grid Columns (v2.1.12)

**File**: `tub_suite/patches/v2_1/fix_child_table_grid_columns.py`

**What It Does**:
Updates `in_list_view` property for child DocType fields:
- **Repair Spare Part**: Show ONLY `item_name` and `qty` (2 columns)
- **Parts Inserted Item**: Show `item_code`, `item_name`, `qty` (3 columns)
- **Parts Removed Item**: Show `item_code`, `item_name`, `qty` (3 columns)
- **Engineering Todo Item**: Show all 5 columns

**NOTE**: This patch also ran successfully and fixed the grid columns.

**Commit**: `fix: Add deployment docs and fix child table grid columns (v2.1.12)`

---

### Fix #4: Engineering Team Permission (v2.1.15)

**File**: `tub_suite/overrides/asset_repair_override.py`

**Problem**: Override class had hardcoded permission check:
```python
# BEFORE - Line 227:
if is_eng_supervisor:
    return  # Allow Engineering Supervisor ONLY
```

This blocked Engineering Team from editing in "Pending Engineering Supervisor Review" state.

**Solution**:
```python
# AFTER:
if is_eng_supervisor or is_engineer:
    return  # Allow Engineering Supervisor and Engineering Team
```

**Why This Happened**:
- Workflow configuration said "Engineering Supervisor" can edit
- BUT the Python override class adds additional validation that overrides the workflow
- The override class is MORE RESTRICTIVE than the workflow

**Commit**: `fix: Allow Engineering Team to edit in Pending Engineering Supervisor Review state (v2.1.15)`

---

### Fix #5: Disabled Broken Fixture (custom_docperm.json)

**Problem**: `custom_docperm.json` has records without `name` field → causes KeyError on import

**Solution**: Renamed file to `.disabled` on production:
```bash
cd ~/frappe-bench/apps/tub_suite/tub_suite/fixtures
mv custom_docperm.json custom_docperm.json.disabled
```

**Permanent Fix on DEV**: Should be removed from git or fixed properly

---

## Tools Created for Future Debugging

### Tool #1: Comprehensive Audit Script

**File**: `tub_suite/audit_config.py`

**Usage**:
```bash
# On DEV:
bench --site tub execute tub_suite.audit_config.audit_all

# On PROD:
bench --site tub.x-desk.tech execute tub_suite.audit_config.audit_all
```

**What It Shows**:
- All 87 Custom Fields with their visibility rules
- All Property Setters
- Workflow states and transitions
- Server Scripts and Client Scripts
- Child DocType grid columns
- Override class status
- Roles
- Fixture files

**Use Case**: Run on BOTH sites, save output, compare side-by-side to find differences.

---

### Tool #2: DEV vs PROD Comparison Script

**File**: `tub_suite/compare_dev_prod.py`

**Usage**:
```bash
# On PROD:
bench --site tub.x-desk.tech execute tub_suite.compare_dev_prod.find_all_differences
```

**What It Does**:
- Compares 60+ critical Custom Fields between expected DEV values and actual PROD values
- Shows EXACT differences with current vs expected values
- Returns count of differences found

**Output Example**:
```
TOTAL DIFFERENCES FOUND: 13

❌ received_by.hidden: PROD=0, should be 1
❌ final_remarks.depends_on:
   PROD: None
   DEV:  'eval:doc.workflow_state=="Finished"'
...
```

**Use Case**: Run after EVERY deployment to verify production matches DEV.

---

## Documentation Created

### 1. DEPLOYMENT_PROCEDURES.md

**Location**: `tub_suite/DEPLOYMENT_PROCEDURES.md`

**Contents**:
- Why fixtures don't update existing records (Frappe design)
- Procedure 1: Deploy DocType schema changes
- Procedure 2: Deploy Custom Field changes (USE PATCHES!)
- Procedure 3: Deploy Workflow changes
- Procedure 4: Full version deployment checklist
- Common mistakes and solutions
- Emergency rollback procedure

**Key Principles**:
1. ALWAYS export after UI changes
2. NEVER manually edit database on production
3. TEST on DEV first
4. DOCUMENT everything
5. BACKUP before deploy
6. ONE change at a time

---

### 2. CLAUDE.md

**Location**: `tub_suite/CLAUDE.md`

**Contents**:
- ERPNext skills reference links
- Critical lessons learned (fixtures don't update!)
- Current state (as of v2.1.15)
- Files to ALWAYS check before deploying
- Quick reference commands
- Asset Repair workflow states
- Version history

**Purpose**: Read at start of EVERY session to avoid repeating mistakes.

---

### 3. This File (COMPLETE_DEPLOYMENT_HISTORY.md)

**Purpose**: Complete record of what happened, why, and how we fixed it.

---

## Mistakes Made & Lessons Learned

### Mistake #1: Relying on Fixtures for Updates

**What We Did Wrong**:
- Made changes via Customize Form on DEV
- Ran `bench export-fixtures`
- Assumed this would deploy correctly to production
- Deployed via `bench migrate`

**What Happened**:
- Fixtures had wrong/null values
- Production database got OVERWRITTEN with bad values
- Spent 2 weeks fixing manually

**Correct Approach**:
1. Make changes on DEV via Customize Form
2. Create a PATCH to apply those exact changes
3. Test patch on DEV
4. Deploy patch to production
5. Fixtures are ONLY for initial deployment, never for updates

---

### Mistake #2: Not Comparing DEV vs PROD After Deployment

**What We Did Wrong**:
- Deployed code
- Assumed if `bench migrate` succeeded, everything was correct
- Discovered issues weeks later when users reported problems

**Correct Approach**:
1. Deploy to production
2. IMMEDIATELY run comparison script
3. Verify 0 differences before considering deployment successful
4. If differences found → fix immediately with patch

---

### Mistake #3: Fixing Issues One at a Time

**What We Did Wrong**:
- Found "received_by" is visible → fixed it
- Next day found "final_remarks" broken → fixed it
- Took 2 weeks to find all 13 issues

**Correct Approach**:
1. Run comprehensive comparison FIRST
2. See ALL issues at once
3. Fix ALL issues in ONE patch
4. Deploy once

---

### Mistake #4: Not Understanding Override Class vs Workflow

**What We Did Wrong**:
- Changed workflow state to allow "Engineering Team"
- Assumed this would work
- Override class still blocked them

**What We Learned**:
- Workflow configuration is NOT enough
- Override class (`asset_repair_override.py`) adds ADDITIONAL validation
- Override class is MORE RESTRICTIVE than workflow
- Must update BOTH to change permissions

---

### Mistake #5: No Documentation

**What We Did Wrong**:
- Made hundreds of changes over weeks
- Didn't document what we changed or why
- Forgot what we did between sessions
- Repeated same fixes multiple times

**Correct Approach**:
- Document WHILE fixing, not after
- Update CLAUDE.md with every change
- Keep deployment history
- Future sessions start by reading docs

---

## What to Do in Future Deployments

### Pre-Deployment Checklist (DEV)

- [ ] All changes made via UI are exported to JSON files:
  ```bash
  # For DocType schema changes:
  bench --site tub export-doc "DocType" "Repair Spare Part"

  # For Custom Fields - DON'T use fixtures, create patch instead!
  ```

- [ ] All JSON files committed to git:
  ```bash
  git status  # Should show modified DocType JSON files
  git add tub_suite/tub_suite/doctype/*/
  git commit -m "fix: Updated DocType configurations"
  ```

- [ ] Test migration on DEV:
  ```bash
  bench --site tub migrate
  # Should complete with no errors
  ```

- [ ] All features tested on DEV

- [ ] Version bumped in `__init__.py`

- [ ] Git tag created:
  ```bash
  git tag v2.1.16
  git push origin v2.1.0 --tags
  ```

---

### Deployment Steps (PRODUCTION)

```bash
# 1. BACKUP
bench --site tub.x-desk.tech backup --with-files

# 2. Pull code
cd ~/frappe-bench/apps/tub_suite
git pull origin refs/heads/v2.1.0

# 3. Check what changed
git log --oneline -10

# 4. Run migration
cd ~/frappe-bench
bench --site tub.x-desk.tech migrate

# 5. If migration fails on custom_docperm.json:
cd ~/frappe-bench/apps/tub_suite/tub_suite/fixtures
mv custom_docperm.json custom_docperm.json.disabled
cd ~/frappe-bench
bench --site tub.x-desk.tech migrate

# 6. Clear cache
bench --site tub.x-desk.tech clear-cache

# 7. Restart services
sudo supervisorctl restart frappe-bench-web:
sudo supervisorctl restart frappe-bench-workers:
```

---

### Post-Deployment Verification

```bash
# 1. Run comparison to find differences
bench --site tub.x-desk.tech execute tub_suite.compare_dev_prod.find_all_differences

# Should show: TOTAL DIFFERENCES FOUND: 0
# If not 0, you have issues to fix!

# 2. Run full audit
bench --site tub.x-desk.tech execute tub_suite.audit_config.audit_all > prod_audit.txt

# 3. Manual testing:
# - Create new Asset Repair in each workflow state
# - Verify field visibility in each state
# - Test with different user roles (Technician, Supervisor, Engineering)
# - Verify child table columns show correctly
```

---

### If Deployment Breaks Production

```bash
# 1. Restore database
bench --site tub.x-desk.tech restore /path/to/backup.sql.gz

# 2. Rollback code
cd ~/frappe-bench/apps/tub_suite
git reset --hard <last-working-commit>

# 3. Restart
sudo supervisorctl restart frappe-bench-web:
sudo supervisorctl restart frappe-bench-workers:

# 4. Investigate before trying again
```

---

## How to Fix Custom Field Visibility Issues

**NEVER use fixtures. ALWAYS use patches.**

### Step 1: Identify ALL Differences

```bash
# On production:
bench --site tub.x-desk.tech execute tub_suite.compare_dev_prod.find_all_differences
```

Save the output - this shows ALL fields that need fixing.

---

### Step 2: Create a Patch

```bash
# On DEV:
cd ~/frappe-bench/apps/tub_suite/tub_suite/patches/v2_1
nano fix_field_visibility_v2_1_XX.py
```

**Template**:
```python
"""
Fix Custom Field visibility for Asset Repair.

Fields fixed:
- field_name_1: description
- field_name_2: description
"""

import frappe


def execute():
    """Set correct visibility for Asset Repair custom fields."""

    custom_field_config = {
        "Asset Repair-field_name_1": {
            "hidden": 1,
            "depends_on": None
        },
        "Asset Repair-field_name_2": {
            "depends_on": 'eval:doc.workflow_state=="Some State"'
        },
        # Add ALL fields that need fixing
    }

    updated_count = 0

    for field_name, properties in custom_field_config.items():
        if not frappe.db.exists("Custom Field", field_name):
            print(f"Custom Field {field_name} not found, skipping...")
            continue

        doc = frappe.get_doc("Custom Field", field_name)
        changed = False

        for prop, value in properties.items():
            current_value = getattr(doc, prop, None)
            if current_value != value:
                setattr(doc, prop, value)
                changed = True
                print(f"Updated {field_name}.{prop}: {current_value} → {value}")

        if changed:
            doc.save()
            updated_count += 1

    if updated_count > 0:
        frappe.db.commit()
        print(f"Successfully updated {updated_count} Custom Fields")
        frappe.clear_cache(doctype="Asset Repair")
    else:
        print("No Custom Fields needed updating - all values already correct")
```

---

### Step 3: Register the Patch

Edit `tub_suite/patches.txt`:

```ini
[post_model_sync]
tub_suite.patches.v2_1.fix_field_visibility_v2_1_XX #v2.1.XX - Description
```

---

### Step 4: Test on DEV

```bash
bench --site tub migrate
# Check output - should show fields being updated

# Verify
bench --site tub execute tub_suite.compare_dev_prod.find_all_differences
# Should show 0 differences
```

---

### Step 5: Deploy to Production

```bash
# Standard deployment process (see above)

# After migration, if patch didn't run (already executed), force it:
bench --site tub.x-desk.tech execute tub_suite.patches.v2_1.fix_field_visibility_v2_1_XX.execute
```

---

## Understanding the Override Class

**File**: `tub_suite/overrides/asset_repair_override.py`

### What It Does

The override class adds **additional validation** on top of ERPNext's standard Asset Repair DocType.

**Key Validations**:
1. **Role-based editing permissions** per workflow state
2. **Signature auto-fill** with timestamps
3. **Field locking** to prevent users from editing certain fields
4. **Workflow state transition validation**

### How Permissions Work

```python
# The class checks user roles:
user_roles = frappe.get_roles()
is_manager = any(role in user_roles for role in ["Maintenance Manager", "Quality Manager"])
is_engineer = any(role in user_roles for role in ["Engineering Team"])
is_eng_supervisor = any(role in user_roles for role in ["Engineering Supervisor"])

# Then enforces state-specific rules:
if workflow_state == "Pending Engineering Assessment":
    if not is_engineer:
        frappe.throw("Only Engineering Team can edit")

if workflow_state == "Pending Engineering Supervisor Review":
    if not (is_eng_supervisor or is_engineer):  # v2.1.15 - added is_engineer
        frappe.throw("Only Engineering Supervisor or Engineering Team can edit")
```

### Important Notes

1. **Override Class > Workflow**: The Python override is MORE RESTRICTIVE than workflow configuration
2. **Must Update Both**: Changing workflow alone is NOT enough - must also update override class
3. **Restart Required**: Changes to override class require bench restart to take effect

---

## Current Production State (as of v2.1.15)

### What's Working ✅

- All 13 Custom Field visibility rules are correct
- Child table grid columns show correct fields
- Engineering Team can edit in "Pending Engineering Supervisor Review" state
- Workflow transitions work correctly
- Override class validations working
- Signature auto-fill working

### What's Different Between DEV and PROD

**Extra on PROD (not on DEV)**:
1. Server Scripts:
   - "Asset Repair - Lock Reporter Fields"
   - "Asset repair approval"
2. Client Scripts:
   - "Asset Repair - Field Locking UI"
   - "Repair Approval"
3. Workflows:
   - "Repair Approval WorkFlow" (old workflow?)
4. Print Formats:
   - "ใบสั่งซ่อม" and "ใบสั่งซ่อม V2"

**Missing on PROD**:
- Roles: "Maintenance Inspector", "Maintenance Engineer" (not critical)

### Known Issues

1. **custom_docperm.json** still breaks migrations - disabled on PROD, needs proper fix on DEV
2. **Repair Spare Part** requires `item_code` - made optional via SQL, needs JSON file update on DEV

---

## Version History

### v2.1.15 (2026-01-30)
- ✅ Fixed Engineering Team permission in "Pending Engineering Supervisor Review" state
- File: `asset_repair_override.py`

### v2.1.14 (2026-01-30)
- ✅ Fixed ALL 13 Custom Field visibility differences
- File: `set_custom_field_visibility_permanent.py`

### v2.1.13 (2026-01-30)
- ✅ Removed Custom Field from fixtures (use patches instead)
- File: `hooks.py`

### v2.1.12 (2026-01-30)
- ✅ Fixed child table grid columns
- ✅ Created comprehensive documentation
- Files: `fix_child_table_grid_columns.py`, `DEPLOYMENT_PROCEDURES.md`, `CLAUDE.md`

### v2.1.11 (2026-01-30)
- ❌ Deployed to production - discovered massive configuration drift
- Photo field validation fix

### v2.1.9-2.1.10
- Fixture format changes
- Sync from DEV

### v2.1.7-2.1.8
- Repair source changes
- PM inspection updates

---

## Emergency Contacts & Resources

### If You Get Stuck

1. **Read the documentation**:
   - `CLAUDE.md` - Quick reference
   - `DEPLOYMENT_PROCEDURES.md` - Step-by-step procedures
   - This file - Complete history

2. **Run the diagnostic tools**:
   ```bash
   bench --site tub.x-desk.tech execute tub_suite.audit_config.audit_all
   bench --site tub.x-desk.tech execute tub_suite.compare_dev_prod.find_all_differences
   ```

3. **Check recent changes**:
   ```bash
   cd ~/frappe-bench/apps/tub_suite
   git log --oneline -20
   git diff HEAD~5..HEAD
   ```

4. **Restore from backup if needed** (see "If Deployment Breaks Production" above)

### ERPNext Resources

- Skills: `~/.claude/skills/impl/erpnext-*/`
- Frappe Docs: https://frappeframework.com/docs
- ERPNext Docs: https://docs.erpnext.com/

---

## Final Checklist: Before Closing This Session

- [ ] All changes committed to git
- [ ] DEPLOYMENT_PROCEDURES.md updated if workflow changed
- [ ] CLAUDE.md updated with current version
- [ ] This file updated with what was fixed
- [ ] Production verified working (comparison shows 0 differences)
- [ ] User tested key workflows

---

**Last Updated**: 2026-01-30
**Current Version**: v2.1.15
**Status**: ✅ Production is working, all 13 fields fixed, Engineering Team permission restored
