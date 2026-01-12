# TUB Suite v1.0 → v2.0 Production Migration Guide

**CRITICAL:** Follow these steps EXACTLY in order to avoid data loss or downtime.

---

## Pre-Migration Checklist

- [ ] **Backup database**: `bench --site [sitename] backup --with-files`
- [ ] **Note current version**: Check v1.0 is running
- [ ] **Schedule maintenance window**: Estimate 30-60 minutes downtime
- [ ] **Notify users**: Inform all users of scheduled downtime
- [ ] **Test on staging first**: If possible, run migration on copy of production first

---

## Migration Steps

### Step 1: Pull Latest Code (5 minutes)

```bash
cd /path/to/frappe-bench/apps/tub_suite
git pull origin main
```

### Step 2: Install New Dependencies (if any) (2 minutes)

```bash
cd /path/to/frappe-bench
bench setup requirements
```

### Step 3: Migrate Database & Apply Fixtures (10-15 minutes)

```bash
bench --site [sitename] migrate
```

**What this does:**
- ✅ Creates new custom fields (if not exists)
- ✅ Updates existing field properties
- ✅ Creates "Asset Repair Engineering Detail" child table
- ✅ Applies field locking configurations
- ✅ Updates workflows

**IMPORTANT:** Existing data is NOT modified - only schema changes applied.

### Step 4: Run Post-Migration Scripts (5 minutes)

#### 4.1 Setup Asset Repair Field Locking

```bash
bench --site [sitename] execute tub_suite.setup.asset_repair_setup.run_production_setup
```

**What this does:**
- ✅ Locks `description`, `failure_date`, `reported_by` fields
- ✅ Creates Server Script for backend validation
- ✅ Creates Client Script for UI behavior
- ✅ Fixes severity field options

#### 4.2 Fix Any Orphaned Task Completions (if needed)

```bash
bench --site [sitename] execute tub_suite.utils.fix_orphaned_tasks.fix_orphaned_task_completions
```

**What this does:**
- ✅ Finds tasks marked "completed today" but no log exists
- ✅ Clears completion date to unlock the task
- ✅ Only affects tasks from current day

### Step 5: Clear Cache & Rebuild (3 minutes)

```bash
bench --site [sitename] clear-cache
bench --site [sitename] build
```

### Step 6: Restart Services (2 minutes)

```bash
bench restart
```

### Step 7: Verify Migration Success (10 minutes)

#### 7.1 Check Asset Repair Fields

1. Open any Asset Repair document
2. Verify these fields exist:
   - ✅ **Repair Type** (ซ่อม/แก้ไข/ติดตั้งใหม่/ปรับปรุง/อื่นๆ)
   - ✅ **สาเหตุ** (Cause)
   - ✅ **ระบุสาเหตุ** (Other cause)
   - ✅ **ฝ่ายวิศวกรรม** section with action items table
   - ✅ **ใบสั่งของเลขที่** (Material Request link)

#### 7.2 Test Field Locking

1. Create test issue from maintenance portal
2. Open Asset Repair as engineer
3. Verify:
   - ✅ `description` is read-only (shows inspector's issue)
   - ✅ `failure_date` is read-only
   - ✅ `actions_performed` is editable
   - ✅ `custom_repair_type` dropdown works

#### 7.3 Test Task Badge

1. Submit a task with no issue
2. Verify badge shows "✓ Completed Today" (green)
3. Submit a task with issue
4. Verify badge shows "⚠ Issue Reported" (orange)
5. Refresh page - badge should stay orange

#### 7.4 Test Manager Approval Locking

1. Engineer sets severity, adds notes
2. Manager adds approval notes and signature
3. Save document
4. Reopen - verify manager cannot edit approval fields anymore

---

## Field Consolidation - CLEAN UP DUPLICATES

### Current Status - DUPLICATE FIELDS FOUND

**TWO approval timestamp systems exist:**

**System A (asset_repair_override.py):**
- `approval_timestamp` - Auto-filled when manager signs
- `approval_notes` - Manager notes
- `approval_signature` - Manager signature

**System B (asset.py API - NOT USED):**
- `approval_time` - From old approval API
- `approved_by` - From old approval API
- `approval_status` - From old approval API

### Recommended Action - DELETE System B

**BEFORE production migration**, delete unused fields:

```bash
bench --site [sitename] console
```

```python
import frappe

# Delete unused approval fields from System B
fields_to_delete = [
    "Asset Repair-approval_time",
    "Asset Repair-approved_by",
    "Asset Repair-approval_status"
]

for field in fields_to_delete:
    if frappe.db.exists("Custom Field", field):
        frappe.delete_doc("Custom Field", field)
        print(f"Deleted: {field}")

# Also delete the unused API function from asset.py
# (Manual code cleanup required)

frappe.db.commit()
print("✓ Cleanup complete")
```

**KEEP these fields (System A):**
- ✅ `approval_timestamp` - Used by override
- ✅ `approval_notes` - Manager editable
- ✅ `approval_signature` - Manager editable
- ✅ `approval_section` - Section break
- ✅ `engineer_signature` - Required field
- ✅ `workflow_state` - Required by workflow

---

## Rollback Plan (If Something Goes Wrong)

### Option 1: Restore from Backup

```bash
# List available backups
ls -lah ~/frappe-bench/sites/[sitename]/private/backups/

# Restore specific backup
bench --site [sitename] restore [backup-file-path]
```

### Option 2: Revert Code

```bash
cd /path/to/frappe-bench/apps/tub_suite
git log --oneline  # Find v1.0 commit hash
git checkout [v1.0-commit-hash]
bench --site [sitename] migrate
bench restart
```

---

## Post-Migration Monitoring

### Day 1-3 After Migration

1. **Monitor error logs:**
   ```bash
   tail -f ~/frappe-bench/sites/[sitename]/logs/web.error.log
   ```

2. **Check for user issues:**
   - Task submission failures
   - Field locking not working
   - Badge display issues

3. **Verify data integrity:**
   - All old Asset Repairs still accessible
   - Historical photos still viewable
   - Task completion dates preserved

### Common Issues & Fixes

#### Issue: "Task still locked after deleting log"
**Fix:**
```bash
bench --site [sitename] execute tub_suite.utils.fix_orphaned_tasks.fix_orphaned_task_completions
```

#### Issue: "Badge shows green instead of orange for issues"
**Fix:** Check server logs for `has_open_issue` query results - logging added for debugging

#### Issue: "Manager can still edit approval after signing"
**Fix:** Verify Client Script was created:
```bash
bench --site [sitename] console
```
```python
import frappe
script = frappe.db.exists("Client Script", "Asset Repair - Field Locking UI")
print("Script exists:", script)
```

---

## Data Compatibility Matrix

| v1.0 Field | v2.0 Field | Migration Action |
|------------|------------|------------------|
| `error_description` | `description` | ✅ Auto-mapped by ERPNext |
| `failure_description` | `description` | ✅ Auto-mapped by ERPNext |
| N/A | `custom_repair_type` | ⚠️ New field (empty for old records) |
| N/A | `custom_สาเหตุ` | ⚠️ New field (empty for old records) |
| N/A | `issue_severity` | ⚠️ New field (empty for old records) |
| `approval_time` | `approval_timestamp` | ⚠️ **DUPLICATE** - Need to consolidate |

**Note:** Old repair records will have empty values for new Thai fields - this is expected and safe.

---

## Support & Troubleshooting

If migration fails or encounters errors:

1. **DO NOT PANIC** - Database backup exists
2. **Capture error logs**:
   ```bash
   bench --site [sitename] console
   ```
   Check last migration errors
3. **Contact support** with:
   - Error message
   - Steps that failed
   - Backup timestamp

---

## Migration Completion Checklist

- [ ] All steps completed without errors
- [ ] Field locking verified working
- [ ] Task badges showing correctly
- [ ] Thai fields visible in Asset Repair
- [ ] Manager approval locking works
- [ ] Orphaned tasks script ran
- [ ] Cache cleared and rebuilt
- [ ] Services restarted
- [ ] User acceptance testing passed
- [ ] Backup verified and stored safely

**Migration Complete!** 🎉

Document any issues encountered and resolutions for future reference.
