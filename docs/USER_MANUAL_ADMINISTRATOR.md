# ⚙️ System Administrator Manual
**Role:** System Manager / IT Administrator
**Platform:** ERPNext Desktop + Server Console
**Version:** v2.1.0

---

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Installation and Setup](#installation-and-setup)
4. [User Management](#user-management)
5. [Customization Management](#customization-management)
6. [Backup and Recovery](#backup-and-recovery)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)
9. [Security and Compliance](#security-and-compliance)
10. [Upgrade Procedures](#upgrade-procedures)

---

## Overview

### Your Responsibilities
As **System Administrator**, you are responsible for:
- ✅ Installing and configuring the tub_suite app
- ✅ Managing user accounts and roles
- ✅ Maintaining system performance
- ✅ Performing backups and recovery
- ✅ Troubleshooting technical issues
- ✅ Applying updates and patches
- ✅ Ensuring data security
- ✅ Training users and creating documentation

### System Components
```
┌─────────────────────────────────────────┐
│         ERPNext v15 Platform            │
│  (Frappe Framework v15)                 │
├─────────────────────────────────────────┤
│         tub_suite Custom App            │
│  - Asset Repair Workflow                │
│  - Mobile Inspector Portal              │
│  - Approval System                      │
│  - Photo Management                     │
│  - Notifications                        │
├─────────────────────────────────────────┤
│         React Frontend                  │
│  - maintenance-react-dev                │
│  - QR Scanner                           │
│  - Photo Capture                        │
├─────────────────────────────────────────┤
│         Backend Services                │
│  - Python API (Frappe)                  │
│  - MariaDB Database                     │
│  - Redis Cache                          │
│  - Nginx Web Server                     │
│  - Supervisor Process Manager           │
└─────────────────────────────────────────┘
```

---

## System Architecture

### Production Environment
**Server:** tub.x-desk.tech
**OS:** Ubuntu 24.04 LTS
**Users:**
- Server user: `taynaja`
- Database: MariaDB
- Site: `tub.x-desk.tech`

### Directory Structure
```
/home/user/frappe-bench/
├── apps/
│   ├── frappe/              # Core framework
│   ├── erpnext/             # ERPNext app
│   └── tub_suite/           # Custom maintenance app
│       ├── tub_suite/
│       │   ├── api/         # Backend APIs
│       │   ├── overrides/   # DocType overrides
│       │   ├── fixtures/    # Custom fields, workflows
│       │   ├── www/         # Web assets
│       │   │   └── maintenance/  # React build output
│       │   └── setup/       # Installation scripts
│       ├── maintenance-react-dev/  # React source code
│       └── docs/            # Documentation
├── sites/
│   └── tub.x-desk.tech/
│       ├── private/         # Uploaded files
│       ├── public/          # Web-accessible files
│       └── site_config.json # Site configuration
└── logs/                    # Application logs
```

**[SCREENSHOT 1: Directory structure via SSH]**

### Network Architecture
```
Internet
   ↓
HTTPS (443) → Nginx Reverse Proxy
   ↓
ERPNext (port 8000) → Gunicorn Workers
   ↓
MariaDB (port 3306) → Database
   ↓
Redis (port 6379) → Cache
```

**[SCREENSHOT 2: Port status check]**

---

## Installation and Setup

### Initial Installation (Production)
**Reference:** `DEPLOYMENT_GUIDE_v2.1.0.md`

### Post-Installation Setup

#### Step 1: Install Custom Fields and Workflows
```bash
bench --site tub.x-desk.tech execute tub_suite.setup.asset_repair_setup.run_production_setup
```

**What this does:**
- Installs custom fields on Asset Repair
- Creates workflow (Draft → Pending Approval → Approved → Finished)
- Sets up Client Script for field locking
- Configures Property Setters

**[SCREENSHOT 3: Running production setup]**

#### Step 2: Create User Roles
```bash
bench --site tub.x-desk.tech console
```

Then in console:
```python
# Create custom roles (if not in fixtures)
from frappe import get_doc

roles = ["Maintenance Inspector", "Maintenance Engineer"]
for role_name in roles:
    if not frappe.db.exists("Role", role_name):
        role = get_doc({
            "doctype": "Role",
            "role_name": role_name,
            "desk_access": 0 if "Inspector" in role_name else 1
        })
        role.insert()
        print(f"✓ Created role: {role_name}")
```

**[SCREENSHOT 4: Creating roles in console]**

#### Step 3: Configure Permissions
Navigate to: **Setup → Permissions → Role Permissions Manager**

**Asset Repair Permissions:**

| Role | Read | Write | Create | Submit | Approve |
|---|---|---|---|---|---|
| Maintenance User | ✅ | ✅ | ✅ | ❌ | ❌ |
| Engineering Team | ✅ | ✅ | ❌ | ✅ | ❌ |
| Maintenance Manager | ✅ | ✅ | ❌ | ❌ | ✅ |
| System Manager | ✅ | ✅ | ✅ | ✅ | ✅ |

**[SCREENSHOT 5: Role Permissions Manager]**

#### Step 4: Build React Frontend
```bash
cd ~/frappe-bench/apps/tub_suite/maintenance-react-dev
npm install
npm run build
```

Output builds to: `tub_suite/www/maintenance/assets/`

**[SCREENSHOT 6: React build output]**

#### Step 5: Clear Cache and Restart
```bash
bench --site tub.x-desk.tech clear-cache
bench restart
```

**[SCREENSHOT 7: Bench restart output]**

---

## User Management

### Creating New Users

#### Inspector Users (Mobile Portal Only)
1. Go to: **Setup → Users → User**
2. Click **New**
3. Fill details:
   - **Email:** inspector1@tipubon.com
   - **First Name:** Inspector Name
   - **Send Welcome Email:** Yes
   - **Roles:** Add "Maintenance User"
   - **User Type:** Website User (no desk access)

**[SCREENSHOT 8: Creating inspector user]**

#### Engineer Users (Desktop Access)
1. Create user as above
2. **Roles:** Add "Engineering Team"
3. **User Type:** System User (desk access)

**[SCREENSHOT 9: Creating engineer user]**

#### Manager Users (Desktop Access)
1. Create user as above
2. **Roles:** Add "Maintenance Manager" + "Engineering Team" (optional)
3. **User Type:** System User

**[SCREENSHOT 10: Creating manager user]**

### User Access Control

#### Restricting Inspector to Mobile Only
In user profile:
- **Module Access:** Disable all modules
- **Roles:** Only "Maintenance User"
- **User Type:** Website User

Inspectors should access: `https://tub.x-desk.tech/maintenance` only

**[SCREENSHOT 11: Inspector role restrictions]**

#### Engineer Desktop Access
- **Module Access:** Enable "Assets" module
- **Roles:** "Engineering Team"
- **Restrict to DocTypes:** Asset Repair only (via Role Permissions)

**[SCREENSHOT 12: Engineer module access]**

### Resetting Passwords
**Method 1: Admin Reset**
1. Go to User list
2. Click user
3. Click **Reset Password**
4. Email sent to user

**[SCREENSHOT 13: Password reset button]**

**Method 2: Console (Emergency)**
```bash
bench --site tub.x-desk.tech console
```
```python
frappe.set_value("User", "user@example.com", "new_password", "TempPass123!")
frappe.db.commit()
```

---

## Customization Management

### Managing Custom Fields

#### Viewing Current Custom Fields
```bash
bench --site tub.x-desk.tech console
```
```python
fields = frappe.get_all("Custom Field",
    filters={"dt": "Asset Repair"},
    fields=["fieldname", "label", "fieldtype", "insert_after"]
)
for f in fields:
    print(f)
```

**[SCREENSHOT 14: Console output of custom fields]**

#### Exporting Clean Fixtures
**Reference:** `FIXTURE_MANAGEMENT.md`

```bash
cd ~/frappe-bench/apps/tub_suite
bench --site tub.x-desk.tech export-fixtures
git add tub_suite/fixtures/
git commit -m "Update fixtures from production"
git push origin v2.1.0
```

**[SCREENSHOT 15: Exporting fixtures command]**

#### Deleting Custom Fields (Console)
```python
# Delete a specific custom field
field = frappe.get_doc("Custom Field", {"dt": "Asset Repair", "fieldname": "old_field"})
field.delete()
frappe.db.commit()
```

**[SCREENSHOT 16: Deleting custom field in console]**

### Managing Workflows

#### Viewing Workflow States
1. Go to: **Setup → Workflow → Workflow**
2. Open "Asset Repair Approval Workflow"
3. View states and transitions

**[SCREENSHOT 17: Workflow configuration page]**

#### Modifying Workflow States
**Caution:** Changing workflow affects all in-progress repairs.

**Safe changes:**
- Adding new optional states
- Modifying email templates
- Changing state colors

**Risky changes:**
- Removing states (can orphan documents)
- Renaming states (breaks existing repairs)
- Changing transition logic

**[SCREENSHOT 18: Workflow states table]**

---

## Backup and Recovery

### Manual Backup

#### Full Backup with Files
```bash
bench --site tub.x-desk.tech backup --with-files
```

Backup location: `~/frappe-bench/sites/tub.x-desk.tech/private/backups/`

**[SCREENSHOT 19: Backup command output]**

#### Database Only Backup
```bash
bench --site tub.x-desk.tech backup
```

Faster, smaller, excludes uploaded files.

### Automated Backups

#### Configure Cron Job
```bash
crontab -e
```

Add:
```cron
# Daily backup at 2 AM with files
0 2 * * * cd /home/user/frappe-bench && /home/user/.local/bin/bench --site tub.x-desk.tech backup --with-files >> /home/user/backup.log 2>&1

# Weekly cleanup (keep last 14 days)
0 3 * * 0 find /home/user/frappe-bench/sites/tub.x-desk.tech/private/backups/ -name "*.sql.gz" -mtime +14 -delete
```

**[SCREENSHOT 20: Crontab configuration]**

### Restore from Backup

#### Step 1: List Available Backups
```bash
ls -lh ~/frappe-bench/sites/tub.x-desk.tech/private/backups/
```

**[SCREENSHOT 21: Listing backup files]**

#### Step 2: Restore Database
```bash
bench --site tub.x-desk.tech restore \
  ~/frappe-bench/sites/tub.x-desk.tech/private/backups/20251218_023000-tub_x_desk_tech-database.sql.gz
```

**[SCREENSHOT 22: Restore command]**

#### Step 3: Restore Files (if needed)
```bash
bench --site tub.x-desk.tech restore \
  ~/frappe-bench/sites/tub.x-desk.tech/private/backups/20251218_023000-tub_x_desk_tech-files.tar
```

#### Step 4: Clear Cache and Restart
```bash
bench --site tub.x-desk.tech clear-cache
bench restart
```

---

## Monitoring and Maintenance

### System Health Checks

#### Check Bench Status
```bash
bench status
```

Output shows:
- Nginx: Active/Inactive
- Redis: Running/Stopped
- Worker: Running/Stopped

**[SCREENSHOT 23: Bench status output]**

#### Check Supervisor Status
```bash
sudo supervisorctl status
```

**[SCREENSHOT 24: Supervisor status]**

#### Check Disk Usage
```bash
df -h
du -sh ~/frappe-bench/sites/tub.x-desk.tech/private/files/
du -sh ~/frappe-bench/sites/tub.x-desk.tech/private/backups/
```

**[SCREENSHOT 25: Disk usage check]**

#### Check Database Size
```bash
bench --site tub.x-desk.tech mariadb
```
```sql
SELECT table_schema "Database",
       ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) "Size (MB)"
FROM information_schema.tables
WHERE table_schema = 'bab1fc02fa2ff81c'
GROUP BY table_schema;
```

**[SCREENSHOT 26: Database size query]**

### Log Monitoring

#### Application Logs
```bash
tail -f ~/frappe-bench/logs/web.log
tail -f ~/frappe-bench/logs/worker.log
tail -f ~/frappe-bench/logs/console.log
```

**[SCREENSHOT 27: Tailing logs]**

#### Error Log Analysis
```bash
grep "ERROR" ~/frappe-bench/logs/*.log | tail -20
```

**[SCREENSHOT 28: Recent errors]**

### Performance Monitoring

#### Check Active Users
```bash
bench --site tub.x-desk.tech console
```
```python
from frappe.utils import now_datetime
from datetime import timedelta

# Users active in last hour
active_users = frappe.get_all("User",
    filters={
        "last_active": [">", now_datetime() - timedelta(hours=1)]
    },
    fields=["name", "full_name", "last_active"]
)
print(f"Active users: {len(active_users)}")
for u in active_users:
    print(u)
```

**[SCREENSHOT 29: Active users console output]**

#### Database Query Performance
```sql
-- Long-running queries
SHOW FULL PROCESSLIST;

-- Slow query log
SELECT * FROM mysql.slow_log ORDER BY start_time DESC LIMIT 10;
```

**[SCREENSHOT 30: Query performance check]**

### Cache Management

#### Clear All Caches
```bash
bench --site tub.x-desk.tech clear-cache
```

#### Clear Specific Cache
```bash
bench --site tub.x-desk.tech console
```
```python
# Clear hooks cache (after editing hooks.py)
frappe.cache().delete_key("app_hooks")

# Clear user permissions
frappe.clear_cache(user="user@example.com")
```

**[SCREENSHOT 31: Cache clearing commands]**

---

## Troubleshooting

### Common Issues

#### Issue 1: Mobile Portal Not Loading
**Symptoms:** `/maintenance` returns 404 or blank page

**Diagnosis:**
```bash
# Check if React build exists
ls -lh ~/frappe-bench/apps/tub_suite/tub_suite/www/maintenance/assets/

# Check web.py routing
cat ~/frappe-bench/apps/tub_suite/tub_suite/www/maintenance/index.py
```

**Solution:**
```bash
cd ~/frappe-bench/apps/tub_suite/maintenance-react-dev
npm run build
bench restart
```

**[SCREENSHOT 32: Rebuild React frontend]**

---

#### Issue 2: "Engineer Signature Required" Error
**Cause:** Client Script not loaded or cached

**Solution:**
```bash
# Reinstall client script
bench --site tub.x-desk.tech execute tub_suite.setup.asset_repair_setup.run_production_setup

# Clear cache
bench --site tub.x-desk.tech clear-cache
bench restart
```

**[SCREENSHOT 33: Reinstall setup command]**

---

#### Issue 3: Workflow Buttons Missing
**Symptoms:** User can't see "Submit for Approval" or "Approve" buttons

**Diagnosis:**
1. Check user roles
2. Check workflow permissions
3. Check document state

**Solution:**
```bash
bench --site tub.x-desk.tech console
```
```python
# Check workflow state
doc = frappe.get_doc("Asset Repair", "MAT-REP-2025-00123")
print(f"Workflow State: {doc.workflow_state}")

# Check user roles
user_roles = frappe.get_roles("user@example.com")
print(f"Roles: {user_roles}")
```

**[SCREENSHOT 34: Workflow debugging in console]**

---

#### Issue 4: Photos Not Uploading
**Symptoms:** "File upload failed" error

**Diagnosis:**
```bash
# Check file upload size limit
grep "client_max_body_size" /etc/nginx/nginx.conf

# Check disk space
df -h

# Check permissions
ls -ld ~/frappe-bench/sites/tub.x-desk.tech/private/files/
```

**Solution:**
```bash
# Increase upload limit in nginx
sudo nano /etc/nginx/nginx.conf
# Add: client_max_body_size 50M;

sudo nginx -t
sudo systemctl reload nginx
```

**[SCREENSHOT 35: Nginx configuration edit]**

---

#### Issue 5: Notification Not Sent
**Symptoms:** Manager/Engineer not receiving notifications

**Diagnosis:**
```bash
bench --site tub.x-desk.tech console
```
```python
# Check if notification was created
notifications = frappe.get_all("Notification Log",
    filters={
        "document_type": "Asset Repair",
        "document_name": "MAT-REP-2025-00123"
    },
    fields=["name", "subject", "for_user", "creation"]
)
for n in notifications:
    print(n)
```

**Solution:**
- Check code in `asset_repair_override.py`
- Ensure `notify_*` functions are being called
- Check frappe.cache() for stored email addresses

**[SCREENSHOT 36: Notification debugging]**

---

#### Issue 6: Bench Won't Start
**Symptoms:** `bench start` fails with errors

**Common Causes:**
1. Port already in use
2. Redis not running
3. MariaDB not running
4. Permission errors

**Diagnosis:**
```bash
# Check ports
sudo netstat -tlnp | grep -E '8000|6379|3306'

# Check Redis
sudo systemctl status redis-server

# Check MariaDB
sudo systemctl status mariadb

# Check supervisor
sudo supervisorctl status
```

**Solution:**
```bash
# Kill conflicting processes
pkill -f bench

# Restart services
sudo systemctl restart redis-server
sudo systemctl restart mariadb

# Restart bench
bench start
```

**[SCREENSHOT 37: Service status checks]**

---

### Database Maintenance

#### Repair Tables
```bash
bench --site tub.x-desk.tech mariadb
```
```sql
USE `bab1fc02fa2ff81c`;
REPAIR TABLE `tabAsset Repair`;
OPTIMIZE TABLE `tabAsset Repair`;
```

**[SCREENSHOT 38: Table repair commands]**

#### Remove Orphaned Records
```python
# Console
# Find Asset Repairs with non-existent assets
repairs = frappe.db.sql("""
    SELECT r.name, r.asset
    FROM `tabAsset Repair` r
    LEFT JOIN `tabAsset` a ON r.asset = a.name
    WHERE a.name IS NULL
""", as_dict=True)

print(f"Orphaned repairs: {len(repairs)}")
```

---

## Security and Compliance

### Access Control

#### Review User Permissions
```bash
bench --site tub.x-desk.tech console
```
```python
# List all users and their roles
users = frappe.get_all("User",
    filters={"enabled": 1, "name": ["not in", ["Administrator", "Guest"]]},
    fields=["name", "full_name", "last_login"]
)

for user in users:
    roles = frappe.get_roles(user.name)
    print(f"{user.full_name}: {', '.join(roles)}")
```

**[SCREENSHOT 39: User roles audit]**

#### Audit Field Access
Check who can edit manager approval fields:
```python
# Should ONLY be Maintenance Manager
meta = frappe.get_meta("Asset Repair")
for field in meta.fields:
    if "approval" in field.fieldname:
        print(f"{field.fieldname}: read_only={field.read_only}")
```

### Audit Trail

#### View Document History
1. Open any Asset Repair
2. Click **Menu (3 dots)** → **Version History**
3. View all changes with timestamps

**[SCREENSHOT 40: Version history view]**

#### Export Audit Log
```python
# Get all changes to specific repair
versions = frappe.get_all("Version",
    filters={"ref_doctype": "Asset Repair", "docname": "MAT-REP-2025-00123"},
    fields=["*"],
    order_by="creation desc"
)

for v in versions:
    print(f"{v.creation} - {v.owner}")
    print(v.data)
```

**[SCREENSHOT 41: Audit log export]**

### Data Protection

#### Backup Encryption
```bash
# Backup with encryption
bench --site tub.x-desk.tech backup --with-files

# Encrypt backup file
gpg --symmetric --cipher-algo AES256 \
  ~/frappe-bench/sites/tub.x-desk.tech/private/backups/20251218_023000-tub_x_desk_tech-database.sql.gz
```

**[SCREENSHOT 42: Encrypted backup]**

#### Sensitive Data Removal (if needed)
```python
# Remove old repair attachments (after X months)
from datetime import timedelta
old_date = now_datetime() - timedelta(days=365)

old_repairs = frappe.get_all("Asset Repair",
    filters={"creation": ["<", old_date], "workflow_state": "Finished"}
)

for repair in old_repairs:
    # Get attachments
    files = frappe.get_all("File",
        filters={"attached_to_doctype": "Asset Repair", "attached_to_name": repair.name}
    )
    # Delete files (be VERY careful!)
    for f in files:
        frappe.delete_doc("File", f.name)
```

---

## Upgrade Procedures

### Upgrading tub_suite App

#### Step 1: Backup First (ALWAYS)
```bash
bench --site tub.x-desk.tech backup --with-files
```

#### Step 2: Pull Latest Code
```bash
cd ~/frappe-bench/apps/tub_suite
git fetch origin
git checkout v2.1.0  # Or specific version
git pull origin v2.1.0
```

**[SCREENSHOT 43: Git pull output]**

#### Step 3: Rebuild React Frontend
```bash
cd ~/frappe-bench/apps/tub_suite/maintenance-react-dev
npm install  # Update dependencies if needed
npm run build
```

#### Step 4: Run Migration
```bash
cd ~/frappe-bench
bench --site tub.x-desk.tech migrate
```

**[SCREENSHOT 44: Migration output]**

#### Step 5: Clear Cache and Restart
```bash
bench --site tub.x-desk.tech clear-cache
bench restart
```

#### Step 6: Verify Upgrade
1. Check version:
```bash
bench --site tub.x-desk.tech console
```
```python
app_version = frappe.get_attr("tub_suite.__version__")
print(f"tub_suite version: {app_version}")
```

2. Test functionality:
   - Login as inspector → Test mobile portal
   - Login as engineer → Test repair submission
   - Login as manager → Test approval

**[SCREENSHOT 45: Version verification]**

### Rollback Procedure

#### If Upgrade Fails:
```bash
# Restore from backup
bench --site tub.x-desk.tech restore \
  ~/frappe-bench/sites/tub.x-desk.tech/private/backups/BACKUP_BEFORE_UPGRADE.sql.gz

# Checkout previous version
cd ~/frappe-bench/apps/tub_suite
git checkout v2.0.0  # Previous working version

# Rebuild
cd maintenance-react-dev
npm run build

# Clear cache and restart
bench --site tub.x-desk.tech clear-cache
bench restart
```

**[SCREENSHOT 46: Rollback process]**

---

## Appendix A: Command Reference

### Bench Commands
```bash
# Site management
bench new-site site_name
bench drop-site site_name
bench migrate
bench clear-cache
bench restart

# App management
bench get-app app_name
bench install-app app_name --site site_name
bench uninstall-app app_name --site site_name

# Backup/Restore
bench backup
bench backup --with-files
bench restore backup_file.sql.gz

# Console
bench console
bench mariadb

# Build
bench build
bench build --app tub_suite

# Updates
bench update --patch
bench update --reset
```

### Fixture Management
```bash
# Export fixtures
bench export-fixtures

# Import specific fixture
bench import-doc fixtures/custom_field.json
```

### Useful Console Commands
```python
# Reload doctype
frappe.reload_doctype("Asset Repair")

# Clear specific cache
frappe.cache().delete_key("key_name")

# Get document
doc = frappe.get_doc("Asset Repair", "name")

# SQL query
data = frappe.db.sql("SELECT * FROM `tabAsset Repair` LIMIT 10", as_dict=True)

# Commit database changes
frappe.db.commit()
```

---

## Appendix B: Screenshot Checklist

| # | Screenshot Needed | Status |
|---|---|---|
| 1 | Directory structure via SSH | ⬜ Pending |
| 2 | Port status check | ⬜ Pending |
| 3 | Running production setup | ⬜ Pending |
| 4 | Creating roles in console | ⬜ Pending |
| 5 | Role Permissions Manager | ⬜ Pending |
| 6 | React build output | ⬜ Pending |
| 7 | Bench restart output | ⬜ Pending |
| 8 | Creating inspector user | ⬜ Pending |
| 9 | Creating engineer user | ⬜ Pending |
| 10 | Creating manager user | ⬜ Pending |
| 11 | Inspector role restrictions | ⬜ Pending |
| 12 | Engineer module access | ⬜ Pending |
| 13 | Password reset button | ⬜ Pending |
| 14 | Console custom fields output | ⬜ Pending |
| 15 | Exporting fixtures | ⬜ Pending |
| 16 | Deleting custom field | ⬜ Pending |
| 17 | Workflow configuration | ⬜ Pending |
| 18 | Workflow states table | ⬜ Pending |
| 19 | Backup command output | ⬜ Pending |
| 20 | Crontab configuration | ⬜ Pending |
| 21 | Listing backup files | ⬜ Pending |
| 22 | Restore command | ⬜ Pending |
| 23 | Bench status output | ⬜ Pending |
| 24 | Supervisor status | ⬜ Pending |
| 25 | Disk usage check | ⬜ Pending |
| 26 | Database size query | ⬜ Pending |
| 27 | Tailing logs | ⬜ Pending |
| 28 | Recent errors grep | ⬜ Pending |
| 29 | Active users console | ⬜ Pending |
| 30 | Query performance | ⬜ Pending |
| 31 | Cache clearing | ⬜ Pending |
| 32 | Rebuild React | ⬜ Pending |
| 33 | Reinstall setup | ⬜ Pending |
| 34 | Workflow debugging | ⬜ Pending |
| 35 | Nginx configuration | ⬜ Pending |
| 36 | Notification debugging | ⬜ Pending |
| 37 | Service status checks | ⬜ Pending |
| 38 | Table repair | ⬜ Pending |
| 39 | User roles audit | ⬜ Pending |
| 40 | Version history | ⬜ Pending |
| 41 | Audit log export | ⬜ Pending |
| 42 | Encrypted backup | ⬜ Pending |
| 43 | Git pull output | ⬜ Pending |
| 44 | Migration output | ⬜ Pending |
| 45 | Version verification | ⬜ Pending |
| 46 | Rollback process | ⬜ Pending |

---

## Appendix C: File Locations

### Configuration Files
```
~/frappe-bench/sites/tub.x-desk.tech/site_config.json - Site settings
/etc/nginx/nginx.conf - Web server config
/etc/supervisor/conf.d/frappe-bench.conf - Process manager
```

### Application Files
```
~/frappe-bench/apps/tub_suite/tub_suite/hooks.py - App configuration
~/frappe-bench/apps/tub_suite/tub_suite/fixtures/ - Custom fields, workflows
~/frappe-bench/apps/tub_suite/tub_suite/api/ - Backend APIs
~/frappe-bench/apps/tub_suite/tub_suite/overrides/ - DocType overrides
```

### Data Files
```
~/frappe-bench/sites/tub.x-desk.tech/private/files/ - Uploaded attachments
~/frappe-bench/sites/tub.x-desk.tech/private/backups/ - Database backups
~/frappe-bench/sites/tub.x-desk.tech/public/files/ - Public files
```

### Log Files
```
~/frappe-bench/logs/web.log - Web requests
~/frappe-bench/logs/worker.log - Background jobs
~/frappe-bench/logs/console.log - Console output
~/frappe-bench/logs/bench.log - Bench operations
```

---

## Contact and Support

### Internal Escalation
- **Development Team:** [DEV TEAM CONTACT]
- **Frappe Support:** https://discuss.erpnext.com
- **Emergency Contact:** [EMERGENCY NUMBER]

### External Resources
- **ERPNext Documentation:** https://docs.erpnext.com
- **Frappe Framework:** https://frappeframework.com/docs
- **tub_suite Repository:** https://github.com/tstexbj3/tub_suite

---

**Document Version:** 1.0
**Last Updated:** 2025-12-18
**Next Review:** 2026-01-18
