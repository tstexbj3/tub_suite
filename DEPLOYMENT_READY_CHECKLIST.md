# 🚀 TUB Suite v2.1.0 - Production Deployment Checklist

**Date:** 2026-01-27
**Version:** 2.1.0 - Supervisor Permissions by Repair Source
**Status:** READY FOR PRODUCTION

---

## ✅ PRE-DEPLOYMENT TASKS (Run these NOW)

### 1. Update hooks.py to Include Print Format

Open `tub_suite/hooks.py` and make these TWO changes:

**Change #1:** Add to `fixtures` list (around line 20):
```python
fixtures = [
    "fixtures/custom_field.json",
    "fixtures/property_setter.json",
    "fixtures/workflow.json",
    "fixtures/workflow_state.json",
    "fixtures/workflow_action_master.json",
    "fixtures/role.json",
    "fixtures/doctype.json",
    "fixtures/notification.json",
    "fixtures/print_format.json"  # ← ADD THIS LINE
]
```

**Change #2:** Add to `export_fixtures` list (around line 52):
```python
    {
        "dt": "Notification",
        "filters": [["is_standard", "=", 0]]
    },
    {
        "dt": "Print Format",
        "filters": [["name", "=", "FM-EN-04"]]
    }  # ← ADD THIS ENTRY
]
```

### 2. Update CHANGELOG.md

Copy content from `CHANGELOG_v2.1.0_ENTRY.md` and paste it at line 9 in `CHANGELOG.md` (right after the "---" line).

### 3. Export All Fixtures

Run the export script from **WSL terminal**:
```bash
cd /home/user/frappe-bench/apps/tub_suite
bash EXPORT_FIXTURES.sh
```

This will:
- Export all fixtures (Custom Fields, Workflows, etc.) to `tub_suite/fixtures/`
- Export FM-EN-04 print format
- Show you the list of exported files

**⚠️ CRITICAL:** Verify `tub_suite/fixtures/print_format.json` was created.

### 4. Clean Up Temporary Files

Run the cleanup script:
```bash
bash CLEANUP_TEMP_FILES.sh
```

This will delete all temporary scripts and backup files, keeping only essential documentation.

### 5. Verify Changes

Check what will be committed:
```bash
git status
git diff tub_suite/overrides/asset_repair_override.py
git diff tub_suite/api/maintenance.py
```

**Expected modified files:**
- ✅ `tub_suite/overrides/asset_repair_override.py` (workflow validation fixes)
- ✅ `tub_suite/api/maintenance.py` (supervisor filtering)
- ✅ `tub_suite/hooks.py` (print format added)
- ✅ `CHANGELOG.md` (v2.1.0 entry added)
- ✅ `tub_suite/fixtures/*.json` (updated fixtures)
- ✅ `tub_suite/public/maintenance/assets/index.js` (if React was rebuilt)

**New files to commit:**
- ✅ `CLEANUP_AND_DEPLOY.md` (deployment guide)
- ✅ `DEPLOYMENT_READY_CHECKLIST.md` (this file)

### 6. Commit Changes

```bash
git add .
git status  # Review what will be committed

git commit -m "feat: Supervisor permissions by repair source (v2.1.0)

- Fix workflow validation check_state logic
- Separate Regular Supervisor and Maintenance Supervisor roles
- Restrict supervisors by repair source (Portal vs PM)
- Fix portal display to show repairs only to supervisors
- Fix Engineering Supervisor workflow transition
- Export FM-EN-04 print format to fixtures

Closes #[issue_number] (if applicable)"
```

### 7. Tag Release

```bash
git tag -a v2.1.0 -m "Release v2.1.0: Supervisor Permissions by Repair Source"
git push origin v2.1.0
git push origin --tags
```

---

## 📦 PRODUCTION DEPLOYMENT (Run on Production Server)

### Pre-Deployment Safety:

1. **Backup Production Database**
   ```bash
   cd /path/to/production/frappe-bench
   bench --site <production_site> backup --with-files
   ```

2. **Note Current Version**
   ```bash
   cd apps/tub_suite
   git log -1 --oneline  # Record current commit
   ```

### Deployment Steps:

```bash
# 1. Pull latest code
cd /path/to/production/frappe-bench/apps/tub_suite
git fetch --all --tags
git checkout v2.1.0

# 2. Verify version
git log -1 --oneline

# 3. Run migration (applies fixtures automatically)
cd ../..
bench --site <production_site> migrate

# 4. Clear all caches
bench --site <production_site> clear-cache
bench --site <production_site> clear-website-cache

# 5. Build assets
bench build --app tub_suite

# 6. Restart all services
sudo supervisorctl restart all
```

### Verify Deployment:

```bash
# Check logs for errors
tail -f ~/frappe-bench/logs/web.error.log
tail -f ~/frappe-bench/logs/worker.error.log

# Verify app version
bench --site <production_site> console
>>> frappe.get_hooks("app_version", app_name="tub_suite")
>>> exit()
```

---

## 🧪 POST-DEPLOYMENT TESTING

### Test Case 1: Regular Supervisor
**Login as:** User with "Supervisor" role (NOT Maintenance Supervisor)

1. Go to maintenance portal
2. **Expected:** See "Pending Verifications" section showing ONLY Portal repairs
3. Try to open a Portal repair in "Pending Supervisor Verification" → Should work ✅
4. Try to open a PM repair in "Pending Supervisor Verification" → Should show error ❌
5. Click "Supervisor Verify" on Portal repair → Should complete successfully ✅

### Test Case 2: Maintenance Supervisor
**Login as:** User with "Maintenance Supervisor" role

1. Go to maintenance portal
2. **Expected:** See "Pending Verifications" section showing ONLY PM repairs
3. Try to open a PM repair in "Pending Supervisor Verification" → Should work ✅
4. Try to open a Portal repair in "Pending Supervisor Verification" → Should show error ❌
5. Click "Supervisor Verify" on PM repair → Should complete successfully ✅

### Test Case 3: Maintenance User (Reporter)
**Login as:** User with "Maintenance User" role (NO Supervisor roles)

1. Go to maintenance portal
2. **Expected:** Should NOT see "Pending Verifications" section at all ✅
3. **Expected:** Should ONLY see "Awaiting Confirmation" section (for their own repairs) ✅
4. Open repair in "Pending Reporter Confirmation" → Should work ✅
5. Click "Confirm Completion" → Should complete successfully ✅

### Test Case 4: Engineering Supervisor
**Login as:** User with "Engineering Supervisor" role

1. Open Asset Repair in "Pending Engineering Supervisor Review"
2. Fill in required fields (eng_supervisor_signature, etc.)
3. Click "Supervisor Review Complete" workflow action
4. **Expected:** Should transition to "Pending GM Final Approval" ✅
5. **Expected:** Should NOT see permission error ✅

### Test Case 5: Print Format
**Any user:**

1. Open any Asset Repair document
2. Click "Print" → Select "FM-EN-04"
3. **Expected:** Print format loads correctly with all sections ✅
4. **Expected:** No missing fields or layout issues ✅

---

## 🔧 TROUBLESHOOTING

### Issue: Permission errors after deployment

**Solution:**
```bash
# Clear cache again
bench --site <production_site> clear-cache

# Reload permissions
bench --site <production_site> --force reload-doc Asset Repair

# Restart
sudo supervisorctl restart all
```

### Issue: Print format not showing

**Solution:**
```bash
# Check if fixture was imported
bench --site <production_site> console
>>> frappe.db.exists("Print Format", "FM-EN-04")
>>> exit()

# If not exists, manually import
bench --site <production_site> import-doc apps/tub_suite/tub_suite/fixtures/print_format.json
```

### Issue: Portal showing wrong repairs

**Solution:**
```bash
# Clear website cache
bench --site <production_site> clear-website-cache

# Rebuild
bench build --app tub_suite

# Hard refresh browser (Ctrl+Shift+R)
```

### Issue: Workflow transition blocked

**Check:**
1. User has correct role assigned
2. Document is in correct workflow state
3. Required fields are filled
4. Check browser console for JavaScript errors

```bash
# Reload doctype
bench --site <production_site> --force reload-doc Asset Repair

# Check workflow
bench --site <production_site> console
>>> doc = frappe.get_doc("Asset Repair", "ACC-ASR-XXXX")
>>> print(doc.workflow_state)
>>> print(frappe.get_roles())
>>> exit()
```

---

## 🔄 ROLLBACK PLAN (If Something Goes Wrong)

### Quick Rollback:

```bash
# 1. Restore database backup
cd /path/to/production/frappe-bench
bench --site <production_site> restore /path/to/backup.sql

# 2. Revert code to previous version
cd apps/tub_suite
git checkout <previous_commit_or_tag>

# 3. Migrate back
cd ../..
bench --site <production_site> migrate

# 4. Clear cache and restart
bench --site <production_site> clear-cache
sudo supervisorctl restart all
```

### Verify Rollback:

```bash
# Check current version
cd apps/tub_suite
git log -1 --oneline

# Test critical functionality
# (Use Test Cases above)
```

---

## 📊 DEPLOYMENT SUMMARY

### What Changed:
- ✅ Fixed 7 critical workflow validation bugs
- ✅ Separated supervisor roles by repair source
- ✅ Fixed portal display filtering
- ✅ Added print format to fixtures

### What's Safe:
- ✅ No database schema changes
- ✅ No new custom fields
- ✅ No breaking API changes
- ✅ Backward compatible with existing documents
- ✅ No manual data migration needed

### Risk Level: **LOW** ⚡
- Only Python logic changes
- Fixtures automatically applied via migrate
- Existing workflow states unchanged
- Can rollback easily if needed

---

## 📞 SUPPORT

### If Issues Occur:

1. Check logs: `~/frappe-bench/logs/web.error.log`
2. Check browser console (F12)
3. Verify user roles are assigned correctly
4. Test with different user accounts
5. Clear all caches (bench + browser)

### Debug Commands:

```bash
# Check current workflow state
bench --site <site> console
>>> doc = frappe.get_doc("Asset Repair", "ACC-ASR-XXXX")
>>> print(doc.workflow_state)
>>> print(doc.repair_source)

# Check user roles
>>> user = frappe.get_doc("User", "user@example.com")
>>> print(user.get_roles())

# Check fixture import status
>>> frappe.db.exists("Print Format", "FM-EN-04")
```

---

## ✅ FINAL CHECKLIST

Before going live:
- [ ] hooks.py updated with print_format.json
- [ ] CHANGELOG.md updated with v2.1.0 entry
- [ ] All fixtures exported (ran EXPORT_FIXTURES.sh)
- [ ] Temporary files cleaned (ran CLEANUP_TEMP_FILES.sh)
- [ ] Changes committed to git
- [ ] Release tagged (v2.1.0)
- [ ] Production database backed up
- [ ] Code pulled on production
- [ ] Migration run successfully
- [ ] Caches cleared
- [ ] Assets built
- [ ] Services restarted
- [ ] All 5 test cases passed

After go-live:
- [ ] Monitor logs for 24 hours
- [ ] Collect user feedback
- [ ] Document any issues encountered
- [ ] Update internal documentation if needed

---

**🎉 You're ready for production deployment!**

**Estimated Deployment Time:** 15-20 minutes
**Downtime Required:** ~2-3 minutes (during restart)
**Rollback Time:** 5-10 minutes (if needed)

---

**Created:** 2026-01-27
**For Version:** TUB Suite v2.1.0
**Deployment Guide:** CLEANUP_AND_DEPLOY.md
