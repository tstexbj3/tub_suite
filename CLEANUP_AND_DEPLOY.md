# TUB Suite v2.1.0 - Deployment Preparation

**Date:** 2026-01-27
**Critical Changes:** Supervisor workflow permissions by repair source

---

## 🎯 CHANGES MADE IN THIS SESSION

### 1. Fixed Workflow Validation Logic (`asset_repair_override.py`)
**Lines modified:** 152, 70-73, 164-166, 171-180, 183-196, 208-215, 217-229

#### Fix #1: Line 152 - check_state logic
**Problem:** Used old_workflow_state causing permission issues
**Solution:** Changed to use current workflow_state
```python
check_state = workflow_state  # FIXED 2026-01-27
```

#### Fix #2: Lines 70-73 - Reporter Confirm action handler
**Added:** Auto-complete repair_status when reporter confirms
```python
if self.workflow_state == "Pending Reporter Confirmation" and workflow_action == "Reporter Confirm":
    self.repair_status = "Completed"
```

#### Fix #3: Lines 164-166 - Supervisor role handling
**Problem:** Single is_supervisor variable for both types
**Solution:** Separate Regular Supervisor from Maintenance Supervisor
```python
is_regular_supervisor = "Supervisor" in user_roles
is_maintenance_supervisor = "Maintenance Supervisor" in user_roles
is_any_supervisor = is_regular_supervisor or is_maintenance_supervisor
```

#### Fix #4: Lines 171-180 - PM repair restrictions (Draft/Approved states)
**Problem:** Regular Supervisor could edit PM repairs
**Solution:** Block Regular Supervisor from PM repairs in Draft/Approved states
```python
if is_regular_supervisor and not is_maintenance_supervisor and is_pm_repair:
    frappe.throw(_("Only Maintenance Supervisor can edit PM repairs"))
```

#### Fix #5: Lines 183-196 - Supervisor verification by repair source
**Problem:** Both supervisor types could verify any repair
**Solution:**
- Regular Supervisor → ONLY Portal repairs
- Maintenance Supervisor → ONLY PM repairs
```python
if is_regular_supervisor and not is_maintenance_supervisor:
    if repair_source == "Portal (แจ้งผ่านระบบ)":
        return
    else:
        frappe.throw(_("Regular Supervisor can only verify Portal repairs."))

if is_maintenance_supervisor:
    if repair_source == "Planned Maintenance (ตามแผน)":
        return
    else:
        frappe.throw(_("Maintenance Supervisor can only verify Planned Maintenance repairs."))
```

#### Fix #6: Lines 208-215 - Pending Reporter Confirmation permissions
**Changed:** Updated to use is_any_supervisor instead of is_supervisor

#### Fix #7: Lines 217-229 - Engineering Supervisor workflow transition
**Problem:** Eng Supervisor couldn't transition to GM Final Approval
**Solution:** Added workflow transition detection logic
```python
if old_workflow_state and old_workflow_state != check_state:
    if is_eng_supervisor and old_workflow_state == "Pending Engineering Supervisor Review":
        return  # Allow transition to GM Final Approval
```

### 2. Fixed Portal Display Logic (`maintenance.py`)
**Function:** `get_repairs_needing_verification()` (Lines 801-837)

**Problem:** Showed "Pending Supervisor Verification" to ALL users including Maintenance Users
**Solution:** Only show to actual supervisors, filtered by repair source
```python
# Check if current user is a supervisor
user_roles = frappe.get_roles()
is_regular_supervisor = "Supervisor" in user_roles
is_maintenance_supervisor = "Maintenance Supervisor" in user_roles

if not is_regular_supervisor and not is_maintenance_supervisor:
    return []  # Not a supervisor, return empty

# Filter by repair source
if is_regular_supervisor and not is_maintenance_supervisor:
    filters["repair_source"] = "Portal (แจ้งผ่านระบบ)"
elif is_maintenance_supervisor:
    filters["repair_source"] = "Planned Maintenance (ตามแผน)"
```

---

## 📦 FILES TO DELETE (Temporary/Obsolete)

### Root Directory Cleanup:
```bash
# Temporary fix scripts
rm -f APPLY_ALL_FIXES.py
rm -f FIX_REPAIR_TYPE_OPTIONS.py
rm -f FIX_PHOTO_FIELD_SQL.py
rm -f CONSOLIDATE_CLIENT_SCRIPTS.py
rm -f DELETE_FIELDS_PERMANENTLY.py
rm -f RESTORE_FIELD_VISIBILITY.py
rm -f ADD_PM_ACTIONS_TO_FIXTURE.py
rm -f HIDE_DEPRECATED_FIELDS_NOW.py
rm -f CHECK_DATABASE_FIELDS.py
rm -f HIDE_CUSTOM_REPAIR_TYPE.py
rm -f RESTORE_REPORTER_CONFIRMATION_FIELDS.py
rm -f HIDE_UNWANTED_SECTIONS.py
rm -f FORCE_FIX_EVERYTHING.py
rm -f CREATE_PM_WORKFLOW_ACTIONS.py

# Shell scripts
rm -f FORCE_HIDE_FIELDS.sh
rm -f REVERT_CONDITIONAL_WORKFLOW.sh

# Outdated documentation
rm -f CLEANUP_SUMMARY_2026_01_26.md
rm -f PM_WORKFLOW_TEST_SESSION_STATE.md
rm -f OPTION_3_FEASIBILITY_CHECK.md
rm -f OPTION_2_ULTRATHINK_ANALYSIS.md
rm -f PM_WORKFLOW_SOLUTION_PLAN.md
rm -f OPTION_4_CONDITIONAL_TRANSITIONS.md
rm -f ASSET_REPAIR_FIELD_VISIBILITY_REFERENCE.md
rm -f ASSET_REPAIR_FIELD_VISIBILITY_REFERENCE.md.backup_20260126
rm -f SAFE_TO_DELETE_FIELDS.md
rm -f REVERT_PM_WORKFLOW.md
rm -f PM_ISSUE_REPORTING_COMPLETE_GUIDE.md
rm -f PM_ISSUE_PROBLEM_ANALYSIS.md
rm -f SAFETY_AND_REVERT_GUIDE.md

# Old HTML backup
rm -f FM_EN_04_PRINT_FORMAT.html

# Backup files
rm -f tub_suite/overrides/asset_repair_override.py.backup
rm -f tub_suite/fixtures/workflow.json.backup_before_conditional_transitions_20260127_185116
rm -f tub_suite/fixtures/workflow.json.backup_before_pm_states
```

### Keep These Documentation Files:
- ✅ `CHANGELOG.md` - Version history
- ✅ `WORKFLOW_DOCUMENTATION.md` - Workflow reference
- ✅ `CONDITIONAL_WORKFLOW_IMPLEMENTATION_SUMMARY.md` - Implementation guide
- ✅ `ASSET_REPAIR_SIGNATURE_AUTOFILL.md` - Signature logic reference
- ✅ `ASSET_REPAIR_CLIENT_SCRIPTS.md` - Client script documentation
- ✅ `PM_WORKFLOW_IMPLEMENTATION.md` - PM workflow guide
- ✅ `PM_WORKFLOW_NEW_STATES_DESIGN.md` - Design document
- ✅ `PRINT_FORMAT_UPDATES.md` - Print format changes
- ✅ `CLAUDE_RULES.md` - Development guidelines

---

## 🔧 FIXTURES EXPORT (CRITICAL)

### Command to export all fixtures:
```bash
cd /home/user/frappe-bench
bench --site tub export-fixtures
```

This will export according to `hooks.py` export_fixtures configuration:
- ✅ Custom Fields (Asset Repair, Asset, Asset Maintenance)
- ✅ Property Setters
- ✅ Workflow & Workflow States
- ✅ Workflow Action Master
- ✅ Roles
- ✅ DocTypes
- ✅ Notifications

### Export Print Format (FM-EN-04):
```bash
bench --site tub export-doc "Print Format" "FM-EN-04" --export-dir apps/tub_suite/tub_suite/fixtures/
```

### Update hooks.py to include Print Format:
Add to `export_fixtures`:
```python
{
    "dt": "Print Format",
    "filters": [["name", "=", "FM-EN-04"]]
}
```

Add to `fixtures` list:
```python
"fixtures/print_format.json",
```

---

## 🚀 PRODUCTION DEPLOYMENT STEPS

### Pre-Deployment:
1. **Export all fixtures** (run commands above)
2. **Commit changes** to git
3. **Create backup** of production database
4. **Test on staging** if available

### Deployment Commands:
```bash
# On production server
cd /path/to/frappe-bench

# Pull latest code
cd apps/tub_suite
git pull origin v2.1.0

# Migrate (applies fixtures automatically)
cd ../..
bench --site <production_site> migrate

# Clear cache
bench --site <production_site> clear-cache
bench --site <production_site> clear-website-cache

# Build assets
bench build --app tub_suite

# Restart services
sudo supervisorctl restart all
```

---

## ⚠️ MIGRATION COMPATIBILITY

### No breaking changes:
- ✅ No new custom fields added
- ✅ No field type changes
- ✅ No DocType structure changes
- ✅ Only Python logic changes (backward compatible)
- ✅ Workflow states unchanged (only permissions logic)

### Existing documents will:
- ✅ Continue to work with new validation logic
- ✅ No data migration needed
- ✅ All existing workflow states remain valid

### Post-deployment verification:
1. Test supervisor permissions by repair source
2. Verify portal shows correct repairs to each user type
3. Test workflow transitions (Eng Supervisor → GM Final Approval)
4. Verify print format FM-EN-04 displays correctly

---

## 📋 DEPLOYMENT CHECKLIST

### Before Deployment:
- [ ] Export all fixtures (`bench export-fixtures`)
- [ ] Export FM-EN-04 print format
- [ ] Update hooks.py to include print format
- [ ] Delete temporary files (see list above)
- [ ] Update CHANGELOG.md with version notes
- [ ] Commit all changes
- [ ] Tag release: `git tag v2.1.0-supervisor-permissions`
- [ ] Backup production database

### During Deployment:
- [ ] Pull latest code
- [ ] Run `bench migrate`
- [ ] Clear all caches
- [ ] Build assets
- [ ] Restart services

### After Deployment:
- [ ] Test as Regular Supervisor (Portal repairs only)
- [ ] Test as Maintenance Supervisor (PM repairs only)
- [ ] Test as Maintenance User (should NOT see Pending Supervisor Verification)
- [ ] Test Engineering Supervisor workflow transition
- [ ] Verify print format renders correctly
- [ ] Check logs for errors

---

## 🔍 VERIFICATION TESTS

### Test Case 1: Regular Supervisor
**User:** Has "Supervisor" role
**Expected:**
- ✅ Can edit/verify Portal repairs in "Pending Supervisor Verification"
- ❌ CANNOT edit/verify PM repairs (should see error)
- ✅ Portal shows ONLY Portal repairs needing verification

### Test Case 2: Maintenance Supervisor
**User:** Has "Maintenance Supervisor" role
**Expected:**
- ✅ Can edit/verify PM repairs in "Pending Supervisor Verification"
- ❌ CANNOT edit/verify Portal repairs (should see error)
- ✅ Portal shows ONLY PM repairs needing verification

### Test Case 3: Maintenance User (Reporter)
**User:** Has "Maintenance User" role, NOT Supervisor
**Expected:**
- ❌ Should NOT see "Pending Verifications" section at all
- ✅ Should ONLY see "Awaiting Confirmation" for their own repairs
- ✅ Can confirm repairs in "Pending Reporter Confirmation"

### Test Case 4: Engineering Supervisor
**User:** Has "Engineering Supervisor" role
**Expected:**
- ✅ Can edit repairs in "Pending Engineering Supervisor Review"
- ✅ Can transition to "Pending GM Final Approval" (workflow action)
- ❌ CANNOT edit once in GM Final Approval (only view/transition)

---

## 📝 NOTES

### Critical Files Modified:
1. `tub_suite/overrides/asset_repair_override.py` - **CORE LOGIC**
2. `tub_suite/api/maintenance.py` - **PORTAL API**

### Fixture Files (will be updated by export):
- `tub_suite/fixtures/custom_field.json`
- `tub_suite/fixtures/property_setter.json`
- `tub_suite/fixtures/workflow.json`
- `tub_suite/fixtures/print_format.json` (NEW)

### No changes to:
- React frontend (maintenance-react-dev/) - uses existing API
- Workflow structure (states/actions unchanged)
- Database schema (no migrations needed)
- Other ERPNext apps (isolated changes)

---

## 🆘 ROLLBACK PLAN

If deployment fails:
```bash
# Restore database backup
bench --site <production_site> restore /path/to/backup.sql

# Revert code
cd apps/tub_suite
git checkout <previous_tag>

# Migrate back
cd ../..
bench --site <production_site> migrate

# Clear cache and restart
bench --site <production_site> clear-cache
sudo supervisorctl restart all
```

---

**Created:** 2026-01-27
**Last Updated:** 2026-01-27
**Version:** 2.1.0-supervisor-permissions
