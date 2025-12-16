# TUB Suite - Production Deployment & Debugging Guide

**Version:** 2.0.1
**Last Updated:** 2025-12-16

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Deployment Steps](#deployment-steps)
3. [Post-Deployment Verification](#post-deployment-verification)
4. [Production Debugging Guide](#production-debugging-guide)
5. [Common Issues & Solutions](#common-issues--solutions)
6. [Rollback Procedures](#rollback-procedures)
7. [Maintenance Commands](#maintenance-commands)

---

## Pre-Deployment Checklist

### 1. Database Backup

**CRITICAL: Always backup before deploying!**

```bash
# Backup entire site
bench --site YOUR_SITE backup --with-files

# Backup only database (faster)
bench --site YOUR_SITE backup

# Backups saved to:
# ~/frappe-bench/sites/YOUR_SITE/private/backups/
```

### 2. Check Current Version

```bash
cd ~/frappe-bench/apps/tub_suite

# Check current version
git log -1 --oneline

# Check if there are uncommitted changes
git status
```

### 3. Review Changes

```bash
# See what will be deployed
git fetch origin
git log HEAD..origin/main --oneline

# See file changes
git diff HEAD..origin/main
```

### 4. Test on Staging First

**Never deploy directly to production without testing!**

- Test on development/staging site first
- Verify all user roles work correctly
- Test badge system with actual issue reports
- Test field locking with Engineer/Manager roles
- Test asset status changes

---

## Deployment Steps

### Step 1: Pull Latest Code

```bash
cd ~/frappe-bench/apps/tub_suite

# Pull latest version
git fetch origin
git checkout main  # or specific version tag
git pull origin main

# Verify version
git log -1 --oneline
```

### Step 2: Check for Old Scripts

**Check for duplicate/old Client and Server Scripts before running setup:**

```bash
# List all Asset Repair scripts
bench --site YOUR_SITE console

>>> import frappe
>>>
>>> # Check Client Scripts
>>> client = frappe.get_all("Client Script",
...     filters={"reference_doctype": "Asset Repair"},
...     fields=["name", "enabled", "modified"])
>>> print(f"Client Scripts: {len(client)}")
>>> for s in client:
...     print(f"  - {s.name} (enabled={s.enabled}, modified={s.modified})")
>>>
>>> # Check Server Scripts
>>> server = frappe.get_all("Server Script",
...     filters={"reference_doctype": "Asset Repair"},
...     fields=["name", "disabled", "modified"])
>>> print(f"Server Scripts: {len(server)}")
>>> for s in server:
...     print(f"  - {s.name} (disabled={s.disabled}, modified={s.modified})")
```

**Expected output (v2.0.1):**
- Client Scripts: 1 → "Asset Repair - Field Locking UI"
- Server Scripts: 1 → "Asset Repair - Validation and Status"

**If you see duplicates, delete old ones:**

```python
# Delete old duplicate scripts
old_names = [
    "Asset Repair - Field Locking",  # Old without "UI"
    "Asset Repair - Lock All Fields Except Approval",
    "Asset Repair - Lock Fields After Submit",
    "Repair Approval",
    "Show Approval Fields - Asset Repair",
]

for name in old_names:
    if frappe.db.exists("Client Script", name):
        frappe.delete_doc("Client Script", name, force=1)
        print(f"Deleted: {name}")

frappe.db.commit()
```

### Step 3: Run Setup Scripts

```bash
# Run production setup (creates/updates Client and Server Scripts)
bench --site YOUR_SITE execute tub_suite.setup.asset_repair_setup.run_production_setup

# Expected output:
# ✓ Server Script updated (validation logic)
# ✓ Client Script updated (UI behavior)
```

### Step 4: Migrate Database

```bash
# Run migrations (if any schema changes)
bench --site YOUR_SITE migrate

# This runs:
# - Custom field updates
# - Workflow changes
# - Any database schema updates
```

### Step 5: Fix Existing Data (One-Time for v2.0.1)

**Only needed when upgrading to v2.0.1:**

```bash
# Fix asset status for repairs approved before v2.0.1
bench --site YOUR_SITE execute tub_suite.utils.fix_existing_approved_repairs.fix_approved_repairs

# Expected output:
# Found X Approved Major repairs
# ✅ FIXED Y assets
```

### Step 6: Clear Cache

```bash
# Clear backend cache
bench --site YOUR_SITE clear-cache

# Clear Redis cache (if needed)
redis-cli FLUSHALL
```

### Step 7: Restart Services

```bash
# For production with supervisor
sudo supervisorctl restart all

# For development
bench restart
```

---

## Post-Deployment Verification

### 1. Check Services Running

```bash
# Check if all services are up
sudo supervisorctl status

# Should show:
# frappe-bench-web:frappe-bench-frappe-web      RUNNING
# frappe-bench-workers:*                        RUNNING
```

### 2. Test API Endpoints

```bash
# Test maintenance API
curl -X GET "https://YOUR_DOMAIN/api/method/tub_suite.api.maintenance.get_maintenance_by_asset?asset_name=YOUR_ASSET" \
  -H "Authorization: token YOUR_API_KEY:YOUR_API_SECRET"

# Should return JSON with tasks array
```

### 3. Test User Flows

**As Inspector:**
- [ ] Login to mobile portal
- [ ] Scan QR code / search asset
- [ ] Complete a task without issue → Badge should be green "✓ Completed Today"
- [ ] Complete a task WITH issue → Badge should be orange "⚠ Issue Reported"
- [ ] Refresh page → Badge should STAY orange

**As Engineer:**
- [ ] Open Asset Repair in Draft state
- [ ] Fill actions_performed and engineer_signature
- [ ] Submit for approval
- [ ] Try to edit fields → Should be LOCKED (greyed out)
- [ ] Try to save → Should get error message

**As Manager:**
- [ ] Open Asset Repair in Pending Approval
- [ ] Try to edit engineer fields → Should be LOCKED
- [ ] Can edit approval_notes and approval_signature
- [ ] Approve repair (Major severity)
- [ ] Check asset status → Should be "Out of Order"
- [ ] Try to edit approval fields → Should be LOCKED

### 4. Check Logs for Errors

```bash
# Check web logs
tail -50 ~/frappe-bench/sites/YOUR_SITE/logs/web.log

# Check for errors
grep ERROR ~/frappe-bench/sites/YOUR_SITE/logs/web.log | tail -20

# Check worker logs
tail -50 ~/frappe-bench/logs/worker.log
```

---

## Production Debugging Guide

### Debug Badge Not Showing Orange

**Symptom:** Badge turns green after refresh even though issue was reported

**Debug Steps:**

1. **Check if API is returning has_open_issue = 1**

```bash
# Call API manually
curl "https://YOUR_DOMAIN/api/method/tub_suite.api.maintenance.get_maintenance_by_asset?asset_name=YOUR_ASSET" \
  -H "Authorization: token YOUR_KEY:YOUR_SECRET" | python3 -m json.tool

# Look for in response:
# "has_open_issue": 1  // Should be 1 if issue exists
```

2. **Check if repair exists and has correct workflow_state**

```bash
bench --site YOUR_SITE console

>>> import frappe
>>> from frappe.utils import nowdate
>>>
>>> asset = "YOUR_ASSET_NAME"
>>> today = nowdate()
>>>
>>> repairs = frappe.get_all("Asset Repair",
...     filters={
...         "asset": asset,
...         "failure_date": today
...     },
...     fields=["name", "workflow_state", "maintenance_task"])
>>>
>>> print(f"Repairs today: {len(repairs)}")
>>> for r in repairs:
...     print(f"  {r.name}: {r.workflow_state}, task={r.maintenance_task}")
```

3. **Check type of last_completion_date**

```bash
>>> tasks = frappe.get_all("Asset Maintenance Task",
...     filters={"maintenance_task": "YOUR_TASK_NAME"},
...     fields=["name", "last_completion_date"])
>>>
>>> for t in tasks:
...     lcd = t.last_completion_date
...     print(f"Task: {t.name}")
...     print(f"  Last completed: {lcd} (type: {type(lcd)})")
...     print(f"  Today: {today} (type: {type(today)})")
...     print(f"  Match: {str(lcd) if lcd else None == today}")
```

4. **Enable debug logging**

Edit `tub_suite/api/maintenance.py` and add:

```python
# At top of get_maintenance_by_asset function
frappe.log_error(f"API called for asset: {asset_name}", "Badge Debug")
```

Then check:
```bash
# View error logs
bench --site YOUR_SITE show-error-log
```

### Debug Field Locking Not Working

**Symptom:** Engineer can edit fields after submission

**Debug Steps:**

1. **Check if Client Script is loaded**

```bash
bench --site YOUR_SITE console

>>> script = frappe.get_doc("Client Script", "Asset Repair - Field Locking UI")
>>> print(f"Enabled: {script.enabled}")
>>> print(f"Modified: {script.modified}")
>>> print(f"Script length: {len(script.script)} chars")
>>>
>>> # Check if it has workflow_state checks
>>> if "workflow_state" in script.script:
...     print("✓ Has workflow_state logic")
>>> else:
...     print("✗ Missing workflow_state logic - NEEDS UPDATE")
```

2. **Check if Server Script validation is running**

```bash
# Create test repair and try to edit
>>> repair = frappe.get_doc("Asset Repair", "YOUR_REPAIR_NAME")
>>> print(f"Workflow State: {repair.workflow_state}")
>>>
>>> # Try to change a field
>>> repair.actions_performed = "Changed after submission"
>>> try:
...     repair.save()
...     print("✗ SAVE SUCCEEDED - Validation not working!")
>>> except Exception as e:
...     print(f"✓ SAVE BLOCKED: {str(e)}")
```

3. **Check user's browser cache**

- Press F12 (DevTools)
- Go to Network tab
- Look for `index-XXXXX.js` file
- Check the hash in filename changes after deployment
- If old hash, user needs hard refresh: Ctrl+Shift+R

### Debug Asset Status Not Changing

**Symptom:** Asset doesn't go "Out of Order" when Major repair approved

**Debug Steps:**

1. **Check repair workflow state**

```bash
>>> repair = frappe.get_doc("Asset Repair", "YOUR_REPAIR_NAME")
>>> print(f"Workflow State: {repair.workflow_state}")
>>> print(f"Issue Severity: {repair.issue_severity}")
>>> print(f"Approval Timestamp: {repair.approval_timestamp}")
```

2. **Check asset current status**

```bash
>>> asset = frappe.get_doc("Asset", repair.asset)
>>> print(f"Current Status: {asset.status}")
```

3. **Manually trigger status update**

```bash
>>> # Import the function
>>> from tub_suite.overrides.asset_repair_override import update_asset_status_on_approval
>>>
>>> # Run it manually
>>> update_asset_status_on_approval(repair)
>>>
>>> # Check asset again
>>> asset.reload()
>>> print(f"New Status: {asset.status}")
```

4. **Check if hook is registered**

```bash
>>> import frappe
>>> from tub_suite.hooks import doc_events
>>>
>>> print("Asset Repair hooks:")
>>> print(doc_events.get("Asset Repair"))
```

Should show:
```python
{
    'validate': ['tub_suite.overrides.asset_repair_override.validate_asset_repair'],
    'before_save': ['tub_suite.overrides.asset_repair_override.before_save_asset_repair'],
    ...
}
```

---

## Common Issues & Solutions

### Issue 1: Badge Turns Green After Refresh

**Symptoms:**
- Orange badge shows initially
- After F5 refresh, badge turns green
- Issue repair still exists and is not Finished

**Root Causes:**
1. Type mismatch between `date` object and `str`
2. Query not filtering by specific maintenance_task
3. Query using `repair_status` instead of `workflow_state`

**Solution:**
```bash
# Check maintenance.py has correct query (v2.0.1+)
grep -A 5 "maintenance_task.*get.*maintenance_task" ~/frappe-bench/apps/tub_suite/tub_suite/api/maintenance.py

# Should see:
# "maintenance_task": task.get("maintenance_task"),
```

**Fix if missing:**
```bash
cd ~/frappe-bench/apps/tub_suite
git pull origin main
bench --site YOUR_SITE clear-cache
sudo supervisorctl restart all
```

### Issue 2: Engineer Can Edit After Submission

**Symptoms:**
- Engineer submits for approval
- Can still edit actions_performed or engineer_signature
- No error when saving

**Root Causes:**
1. Client Script not updated
2. Server Script validation not running
3. Old duplicate scripts interfering

**Solution:**
```bash
# Re-run setup
bench --site YOUR_SITE execute tub_suite.setup.asset_repair_setup.run_production_setup

# Clear cache
bench --site YOUR_SITE clear-cache

# Restart
sudo supervisorctl restart all

# User must hard-refresh browser: Ctrl+Shift+R
```

### Issue 3: Asset Status Wrong Timing

**Symptoms:**
- Asset goes "Out of Order" when engineer reports Major issue
- Should only go "Out of Order" when manager approves

**Root Causes:**
- Old code triggered on severity change, not approval
- v2.0.1 fixes this

**Solution:**
```bash
# Upgrade to v2.0.1+
cd ~/frappe-bench/apps/tub_suite
git pull origin main

# Fix existing approved repairs
bench --site YOUR_SITE execute tub_suite.utils.fix_existing_approved_repairs.fix_approved_repairs

# Restart
sudo supervisorctl restart all
```

### Issue 4: Orphaned Task Completions

**Symptoms:**
- Deleted Asset Repair or Maintenance Log
- Task card still shows "Completed Today"
- Can't submit again

**Solution:**
```bash
# Run fix utility
bench --site YOUR_SITE execute tub_suite.utils.fix_orphaned_tasks.fix_orphaned_task_completions

# This removes completion records for deleted repairs/logs
```

### Issue 5: 417 EXPECTATION FAILED Error

**Symptoms:**
- API calls fail with 417 error
- Browser console shows network errors

**Root Causes:**
- CSRF token expired
- Session invalid
- Nginx/proxy misconfiguration

**Solution:**
```bash
# User side:
# 1. Logout and login again
# 2. Clear cookies for site
# 3. Restart browser

# Server side:
# Check nginx config
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx

# Check CSRF settings in site_config.json
cat ~/frappe-bench/sites/YOUR_SITE/site_config.json | grep csrf
```

---

## Rollback Procedures

### Quick Rollback (Code Only)

```bash
cd ~/frappe-bench/apps/tub_suite

# Find previous version
git log --oneline -10

# Rollback to previous commit
git checkout COMMIT_HASH

# Clear cache
bench --site YOUR_SITE clear-cache

# Restart
sudo supervisorctl restart all
```

### Full Rollback (Database + Code)

```bash
# 1. Stop services
sudo supervisorctl stop all

# 2. Restore database
bench --site YOUR_SITE restore /path/to/backup.sql.gz

# 3. Rollback code
cd ~/frappe-bench/apps/tub_suite
git checkout PREVIOUS_VERSION

# 4. Clear cache
bench --site YOUR_SITE clear-cache

# 5. Start services
sudo supervisorctl start all
```

---

## Maintenance Commands

### Useful Utilities

```bash
# Check all Asset Repair scripts
bench --site YOUR_SITE execute tub_suite.utils.audit_scripts.audit_all_scripts

# List all Client/Server Scripts
bench --site YOUR_SITE execute tub_suite.utils.list_all_scripts.list_all_scripts

# Fix orphaned task completions
bench --site YOUR_SITE execute tub_suite.utils.fix_orphaned_tasks.fix_orphaned_task_completions

# Fix existing approved repairs (one-time for v2.0.1)
bench --site YOUR_SITE execute tub_suite.utils.fix_existing_approved_repairs.fix_approved_repairs

# Debug today's repairs and badge status
bench --site YOUR_SITE execute tub_suite.utils.debug_today_repairs.check_today
```

### Clean Up Old Scripts

```bash
# Delete old duplicate Client Scripts
bench --site YOUR_SITE execute tub_suite.utils.cleanup_old_scripts.cleanup_old_scripts
```

### Monitor Logs in Real-Time

```bash
# Web logs
tail -f ~/frappe-bench/sites/YOUR_SITE/logs/web.log

# Worker logs
tail -f ~/frappe-bench/logs/worker.log

# Error logs only
tail -f ~/frappe-bench/sites/YOUR_SITE/logs/web.log | grep ERROR

# Watch for specific asset
tail -f ~/frappe-bench/sites/YOUR_SITE/logs/web.log | grep "ACC-ASS-2025"
```

### Performance Monitoring

```bash
# Check database size
bench --site YOUR_SITE mariadb

MariaDB> SELECT table_schema AS "Database",
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS "Size (MB)"
FROM information_schema.tables
WHERE table_schema = "YOUR_SITE_DB"
GROUP BY table_schema;

# Check slow queries
MariaDB> SHOW FULL PROCESSLIST;

# Check table sizes
MariaDB> SELECT table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS "Size (MB)"
FROM information_schema.tables
WHERE table_schema = "YOUR_SITE_DB"
ORDER BY (data_length + index_length) DESC
LIMIT 20;
```

---

## Health Check Script

Create this script for quick production health checks:

```bash
#!/bin/bash
# ~/frappe-bench/health_check.sh

SITE="YOUR_SITE"

echo "================================"
echo "TUB Suite Health Check"
echo "================================"

echo -e "\n1. Services Status:"
sudo supervisorctl status | grep frappe

echo -e "\n2. App Version:"
cd ~/frappe-bench/apps/tub_suite && git log -1 --oneline

echo -e "\n3. Scripts Status:"
bench --site $SITE console << EOF
import frappe
client = frappe.db.count("Client Script", {"reference_doctype": "Asset Repair", "enabled": 1})
server = frappe.db.count("Server Script", {"reference_doctype": "Asset Repair", "disabled": 0})
print(f"Client Scripts: {client} (expect: 1)")
print(f"Server Scripts: {server} (expect: 1)")
EOF

echo -e "\n4. Recent Errors:"
tail -5 ~/frappe-bench/sites/$SITE/logs/web.log | grep ERROR

echo -e "\n5. Disk Space:"
df -h ~/frappe-bench

echo -e "\n================================"
```

**Usage:**
```bash
chmod +x ~/frappe-bench/health_check.sh
./health_check.sh
```

---

## Emergency Contacts

- **IT Support:** it@tipubon.com
- **GitHub Issues:** https://github.com/tstexbj3/tub_suite/issues
- **ERPNext Forums:** https://discuss.frappe.io

---

**Last Updated:** 2025-12-16
**Maintained By:** Tipubon International Co., Ltd.
