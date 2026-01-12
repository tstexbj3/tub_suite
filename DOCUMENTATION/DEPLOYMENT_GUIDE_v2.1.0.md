# Production Deployment Guide - v2.1.0

**Target Site:** tub.x-desk.tech
**Current Version:** v1.0
**Target Version:** v2.1.0
**Deployment Date:** 2025-12-18
**Risk Level:** ⚠️ HIGH - Requires Migration

---

## ⚠️ CRITICAL WARNING

**v2.1.0 is built on v2.0.0 which has BREAKING CHANGES from v1.0.**

You have TWO deployment options:

### Option A: Two-Stage Deployment (RECOMMENDED - SAFER)
1. Deploy v2.0.0-release first → Test thoroughly
2. Deploy v2.1.0 after v2.0.0 is stable

### Option B: Direct Deployment (HIGHER RISK)
1. Deploy v2.1.0 directly (includes all v2.0.0 changes + v2.1.0 fixes)

**This guide covers OPTION B (Direct Deployment)**

---

## 📋 PRE-DEPLOYMENT CHECKLIST

### 1. Backup Everything

```bash
# SSH to production server
ssh frappe@tub.x-desk.tech

# Navigate to bench directory
cd /home/frappe-bench

# Create backup with files
bench --site tub.x-desk.tech backup --with-files

# Backup location will be shown - SAVE THIS PATH
# Example: /home/frappe-bench/sites/tub.x-desk.tech/private/backups/

# Copy backup to safe location
cp sites/tub.x-desk.tech/private/backups/*.sql.gz ~/backups/pre_v2.1.0_$(date +%Y%m%d_%H%M%S).sql.gz
cp sites/tub.x-desk.tech/private/backups/*-files.tar ~/backups/pre_v2.1.0_$(date +%Y%m%d_%H%M%S)-files.tar
```

### 2. Export Current Data

```bash
# Export existing Asset Repair data
bench --site tub.x-desk.tech export-csv "Asset Repair"

# Check how many repairs exist
bench --site tub.x-desk.tech console
```

```python
# In Frappe console:
frappe.db.sql("SELECT COUNT(*) FROM `tabAsset Repair` WHERE docstatus = 1")
# Note this number - you'll verify after migration
exit()
```

### 3. Schedule Maintenance Window

**Recommended:** 30-60 minutes during off-hours
- System will be DOWN during deployment
- Users cannot access mobile portal
- Repairs in progress will be paused

---

## 🚀 DEPLOYMENT STEPS

### Step 1: Stop Bench

```bash
cd /home/frappe-bench
bench --site tub.x-desk.tech set-maintenance-mode on
sudo supervisorctl stop frappe-bench:*
# OR if using systemd:
sudo systemctl stop frappe-bench
```

### Step 2: Pull New Code

```bash
cd /home/frappe-bench/apps/tub_suite

# Check current branch/version
git branch
git log --oneline -3

# Fetch latest changes
git fetch origin

# Checkout v2.1.0
git checkout v2.1.0

# Verify you're on correct version
git log --oneline -1
# Should show: 0302b82 feat: Comprehensive workflow fixes and validation improvements
```

### Step 3: Install Dependencies

```bash
# Install Node.js dependencies (if package.json changed)
cd /home/frappe-bench/apps/tub_suite/maintenance-react-dev
npm install

# Build React frontend
npm run build

# Verify build succeeded
ls -lh ../tub_suite/public/maintenance/assets/
# Should see: index.js, index.css with today's timestamp
```

### Step 4: Update Backend

```bash
cd /home/frappe-bench

# Install Python dependencies (if requirements.txt changed)
./env/bin/pip install -e apps/tub_suite

# Run migration (CRITICAL - installs custom fields, workflows)
bench --site tub.x-desk.tech migrate

# Watch for errors - migration MUST complete successfully
# Look for:
# - "Updating customizations..."
# - "Syncing tub_suite"
# - "Migrated to..."
```

### Step 5: Install Fixtures (CRITICAL)

```bash
# Force reinstall to ensure all fixtures are applied
bench --site tub.x-desk.tech install-app tub_suite --force

# This will install:
# - Custom Fields (15+ fields on Asset Repair)
# - Workflows (Asset Repair Workflow)
# - Property Setters
# - Custom DocTypes
```

### Step 6: Verify Custom Fields Installed

```bash
bench --site tub.x-desk.tech console
```

```python
# In Frappe console:
fields = frappe.get_all("Custom Field",
    filters={"dt": "Asset Repair"},
    fields=["fieldname", "label"])

print(f"Total custom fields: {len(fields)}")
for f in fields:
    print(f"  - {f.fieldname}: {f.label}")

# Should show 15+ fields including:
# - reported_by
# - maintenance_task
# - issue_severity
# - verification_status
# - verified_by
# etc.

# If count < 15, something went wrong - DO NOT PROCEED
exit()
```

### Step 7: Fix Existing Repairs (CRITICAL!)

Existing Asset Repair documents don't have the new required fields. This script sets safe defaults:

```bash
bench --site tub.x-desk.tech console
```

```python
# In Frappe console:
import frappe

# Get all submitted repairs
repairs = frappe.get_all("Asset Repair",
    filters={"docstatus": 1},
    fields=["name", "repair_status"])

print(f"Found {len(repairs)} existing repairs to update")

updated = 0
errors = []

for repair in repairs:
    try:
        doc = frappe.get_doc("Asset Repair", repair.name)

        # Set safe defaults for new required fields
        if not doc.get("requires_inspector_verification"):
            doc.requires_inspector_verification = 0

        if not doc.get("verification_status"):
            doc.verification_status = "Not Required"

        if not doc.get("issue_severity"):
            doc.issue_severity = "Minor - Asset Operational"

        if not doc.get("reported_by"):
            doc.reported_by = doc.owner

        # Bypass validation for existing records
        doc.flags.ignore_validate_update_after_submit = True
        doc.flags.ignore_mandatory = True
        doc.save(ignore_permissions=True)

        updated += 1
        if updated % 10 == 0:
            print(f"Updated {updated} repairs...")

    except Exception as e:
        errors.append(f"Error updating {repair.name}: {str(e)}")
        print(f"ERROR on {repair.name}: {e}")

frappe.db.commit()

print(f"\n✓ Successfully updated {updated} repairs")
if errors:
    print(f"\n✗ Errors: {len(errors)}")
    for err in errors:
        print(f"  {err}")

exit()
```

### Step 8: Assign New Roles to Users

```bash
bench --site tub.x-desk.tech console
```

```python
# In Frappe console:
import frappe

# Get all users with Maintenance User role
users = frappe.get_all("Has Role",
    filters={"role": "Maintenance User"},
    fields=["parent"],
    pluck="parent")

print(f"Found {len(users)} maintenance users")

# Assign new roles
new_roles = ["Maintenance Inspector"]  # Add as needed

for user_email in users:
    user = frappe.get_doc("User", user_email)

    for role_name in new_roles:
        # Check if role already exists
        if not any(r.role == role_name for r in user.roles):
            user.append("roles", {"role": role_name})
            print(f"Added {role_name} to {user_email}")

    user.save(ignore_permissions=True)

frappe.db.commit()
print("✓ Roles updated")

exit()
```

### Step 9: Clear Cache

```bash
bench --site tub.x-desk.tech clear-cache
bench --site tub.x-desk.tech clear-website-cache
bench build --app tub_suite
```

### Step 10: Start Bench & Test

```bash
# Start services
sudo supervisorctl start frappe-bench:*
# OR if using systemd:
sudo systemctl start frappe-bench

# Wait 30 seconds for services to start
sleep 30

# Check if site is accessible
curl -I https://tub.x-desk.tech
# Should return HTTP 200

# Turn off maintenance mode
bench --site tub.x-desk.tech set-maintenance-mode off
```

### Step 11: Smoke Tests

```bash
bench --site tub.x-desk.tech console
```

```python
# Test 1: Check API endpoint works
import frappe
frappe.set_user("Administrator")

# Test get_maintenance_tasks API
from tub_suite.api.maintenance import get_maintenance_tasks
result = get_maintenance_tasks(user_email="test_maintenance_repair@test.com")
print(f"API returned {len(result.get('message', []))} assets")

# Test 2: Check workflow exists
workflow = frappe.get_doc("Workflow", "Asset Repair Workflow")
print(f"Workflow found: {workflow.name}")
print(f"States: {[s.state for s in workflow.states]}")

# Test 3: Verify custom fields accessible
repair = frappe.get_all("Asset Repair", limit=1)
if repair:
    doc = frappe.get_doc("Asset Repair", repair[0].name)
    print(f"Sample repair has issue_severity: {doc.issue_severity}")
    print(f"Sample repair has verification_status: {doc.verification_status}")

exit()
```

### Step 12: Manual UI Test

1. **Mobile Portal Access:**
   - Open: https://tub.x-desk.tech/maintenance
   - Login as inspector: test_maintenance_repair@test.com
   - Scan QR code
   - Verify task list loads
   - Submit task with no issue
   - Verify task shows "✓ Completed Today"

2. **Issue Reporting:**
   - Report issue with photos
   - Verify task locks and shows "🔧 Repair In Progress"
   - Verify Asset Repair created

3. **ERPNext Desk:**
   - Login as engineer
   - Open Asset Repair
   - Fill details, sign, submit for approval
   - Verify task stays locked

4. **Manager Approval:**
   - Login as manager
   - Open repair
   - Try to approve WITHOUT signature → Should block with error
   - Add signature + notes → Should allow approval
   - Verify task stays locked

5. **Verification:**
   - Engineer marks job finished
   - Verify task stays locked
   - Login as inspector on portal
   - Verify repair completion
   - Verify task unlocks and shows completed

---

## 🔄 ROLLBACK PROCEDURE

If deployment fails at ANY step:

### Quick Rollback (Code Only)

```bash
cd /home/frappe-bench

# Stop services
bench --site tub.x-desk.tech set-maintenance-mode on
sudo supervisorctl stop frappe-bench:*

# Revert code
cd apps/tub_suite
git checkout main  # or v1.0 or v2.0.0-release

# Rebuild
cd /home/frappe-bench
bench build --app tub_suite

# Restart
sudo supervisorctl start frappe-bench:*
bench --site tub.x-desk.tech set-maintenance-mode off
```

### Full Rollback (Database + Code)

```bash
cd /home/frappe-bench

# Stop services
sudo supervisorctl stop frappe-bench:*

# Restore database
bench --site tub.x-desk.tech restore ~/backups/pre_v2.1.0_YYYYMMDD_HHMMSS.sql.gz

# Restore files
tar -xvf ~/backups/pre_v2.1.0_YYYYMMDD_HHMMSS-files.tar -C sites/tub.x-desk.tech/

# Revert code
cd apps/tub_suite
git checkout main

# Rebuild
cd /home/frappe-bench
bench build --app tub_suite

# Restart
sudo supervisorctl start frappe-bench:*
bench --site tub.x-desk.tech set-maintenance-mode off
```

---

## 📊 POST-DEPLOYMENT MONITORING

### First 24 Hours

Monitor these logs for errors:

```bash
# Application errors
tail -f /home/frappe-bench/logs/bench.log

# Web server errors
tail -f /home/frappe-bench/logs/web.error.log

# Worker errors
tail -f /home/frappe-bench/logs/worker.error.log
```

### Watch For:

- ❌ API errors when submitting tasks
- ❌ Workflow transition failures
- ❌ Missing field errors
- ❌ Asset status not updating
- ❌ Verification failures

### Success Metrics:

- ✅ All existing repairs still accessible
- ✅ New repairs created successfully
- ✅ Workflow transitions working
- ✅ Tasks locking/unlocking properly
- ✅ Verification workflow functioning

---

## 🆘 EMERGENCY CONTACTS

If deployment fails and you need help:

1. **Rollback immediately** (see Rollback Procedure)
2. **Capture error logs:**
   ```bash
   tail -100 /home/frappe-bench/logs/bench.log > ~/deployment_error.log
   ```
3. **Contact support** with error logs

---

## 📝 DEPLOYMENT DIFFERENCES: v2.0.0 vs v2.1.0

**v2.1.0 adds these fixes on top of v2.0.0:**

1. **Task Locking System**
   - Tasks lock during entire repair workflow
   - Only unlock on rejection or verification passed

2. **Validation Improvements**
   - Manager signature required for approval/rejection
   - Engineers cannot edit rejected repairs

3. **Bug Fixes**
   - Fixed wrong maintenance log updates
   - Fixed premature task unlocking
   - Fixed asset-specific log completion

**No new custom fields, DocTypes, or workflows in v2.1.0**

---

## ✅ FINAL CHECKLIST

Before declaring deployment successful:

- [ ] All services running
- [ ] Mobile portal accessible
- [ ] Can submit tasks without issues
- [ ] Can report issues and create repairs
- [ ] Workflow transitions work (Draft → Pending → Approved → Finished)
- [ ] Manager signature validation working
- [ ] Task locking/unlocking working
- [ ] Verification workflow working
- [ ] All existing repairs still accessible
- [ ] No errors in logs
- [ ] Maintenance mode turned off
- [ ] All users can login

---

**Document Version:** 1.0
**Last Updated:** 2025-12-18
**Prepared By:** Claude (AI Assistant)
