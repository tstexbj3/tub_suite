# TUB Suite Deployment Guide

Complete guide for deploying TUB Suite v2.0.0 to production.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Fresh Installation](#fresh-installation)
3. [Upgrade from v1.x](#upgrade-from-v1x)
4. [Custom Fields Setup](#custom-fields-setup)
5. [Configuration](#configuration)
6. [Post-Installation](#post-installation)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Server Requirements
- **OS:** Ubuntu 20.04+ / Debian 11+
- **Python:** 3.10+
- **Node.js:** 18+
- **MariaDB:** 10.6+
- **Redis:** 6+
- **Frappe:** v15+
- **ERPNext:** v15+

### User Permissions
- Root or sudo access for installation
- Frappe bench user for app management

---

## Fresh Installation

### Step 1: Get the App

```bash
# Navigate to frappe-bench
cd ~/frappe-bench

# Get app from GitHub
bench get-app https://github.com/tstexbj3/tub_suite.git --branch main

# Or for specific version
bench get-app https://github.com/tstexbj3/tub_suite.git --branch v2.0.0
```

### Step 2: Install on Site

```bash
# Install app on your site
bench --site [your-site-name] install-app tub_suite

# This will:
# - Install the app
# - Create custom DocTypes
# - Apply custom fields via fixtures
# - Set up hooks and overrides
```

### Step 3: Migrate Database

```bash
# Run migrations (if any)
bench --site [your-site-name] migrate

# Clear cache
bench --site [your-site-name] clear-cache

# Restart bench
bench restart
```

### Step 4: Verify Installation

```bash
# Check installed apps
bench --site [your-site-name] list-apps

# Should show:
# frappe
# erpnext
# tub_suite
```

---

## Upgrade from v1.x

### Step 1: Backup Everything

```bash
# Backup database
bench --site [your-site-name] backup

# Backups stored in:
# ~/frappe-bench/sites/[your-site-name]/private/backups/

# Backup files (optional but recommended)
tar -czf tub_suite_backup.tar.gz ~/frappe-bench/apps/tub_suite
```

### Step 2: Pull Latest Code

```bash
cd ~/frappe-bench/apps/tub_suite

# Pull latest version
git fetch origin
git checkout main
git pull origin main

# Or specific version
git checkout v2.0.0
```

### Step 3: Update Dependencies

```bash
cd ~/frappe-bench

# Update app
bench update --apps tub_suite

# This runs:
# - git pull
# - pip install dependencies
# - npm install (if package.json exists)
```

### Step 4: Migrate & Apply Fixtures

```bash
# Apply custom fields from fixtures
bench --site [your-site-name] migrate

# Import fixtures manually (if needed)
bench --site [your-site-name] import-doc Custom\ Field tub_suite/tub_suite/fixtures/custom_fields.json

# Clear cache
bench --site [your-site-name] clear-cache

# Rebuild assets
bench build --app tub_suite

# Restart
bench restart
```

---

## Custom Fields Setup

Custom fields are **automatically installed** via fixtures when you install the app.

### How It Works

**Fixtures Configuration** ([hooks.py:10-18](tub_suite/hooks.py#L10-L18)):
```python
fixtures = [
    {"dt": "Custom Field"},  # ← Auto-imports custom fields
    {"dt": "Property Setter"},
    {"dt": "Workflow"},
    {"dt": "Workflow State"},
    {"dt": "Workflow Action Master"},
    {"dt": "Role"},
    {"dt": "Notification"},
]
```

**Custom Fields Location:**
- File: [tub_suite/fixtures/custom_fields.json](tub_suite/fixtures/custom_fields.json)
- Auto-imported during `bench install-app tub_suite`

### Fields Added to Asset Repair

| Field Name | Type | Description | Editable By |
|------------|------|-------------|-------------|
| `reported_by` | Link (User) | Inspector who reported the issue | Auto-set (LOCKED) |
| `expected_completion_date` | Date | When engineer expects to finish | Engineer |
| `issue_severity` | Select | Minor/Major severity | Engineer |
| `requires_inspector_verification` | Check | If inspector must verify repair | Auto-set |
| `verified_by` | Link (User) | Inspector who verified repair | Auto-set |
| `verification_date` | Datetime | When inspector verified | Auto-set |
| `verification_notes` | Small Text | Inspector's verification notes | Inspector |
| `verification_status` | Select | Pending/Verified-Passed/Failed | Inspector |

### Standard Fields Modified

| Field Name | Original Use | New Behavior |
|------------|--------------|--------------|
| `description` | Repair description | Issue description from inspector (LOCKED) |
| `actions_performed` | Repair notes | Engineer's repair documentation (EDITABLE) |
| `failure_date` | Date of failure | Date issue reported (LOCKED) |
| `completion_date` | Manual entry | Auto-filled when status = Completed |

### Fields Added to Asset

| Field Name | Type | Description |
|------------|------|-------------|
| `qr_code` | Attach Image | Generated QR code for asset |

### Manual Import (If Needed)

```bash
# If fixtures don't auto-import during installation
cd ~/frappe-bench

# Import custom fields
bench --site [your-site-name] import-doc \
  Custom\ Field \
  apps/tub_suite/tub_suite/fixtures/custom_fields.json

# Verify custom fields exist
bench --site [your-site-name] console

# In console:
>>> frappe.get_meta("Asset Repair").get_field("reported_by")
# Should return field definition
```

### Exporting Custom Fields (For Development)

```bash
# If you make changes in UI and want to update fixtures
bench --site [your-site-name] export-fixtures

# This updates files in tub_suite/fixtures/
# Then commit and push to GitHub
```

---

## Configuration

### 1. User Roles Setup

Assign users to maintenance roles:

**Via ERPNext UI:**
```
1. Go to: User List
2. Click on user
3. Scroll to "Roles" section
4. Add roles:
   - Maintenance User (for Inspectors)
   - Engineering Team (for Engineers)
   - Maintenance Manager (for Managers)
5. Save
```

**Via bench console:**
```bash
bench --site [your-site-name] console

# In console:
user = frappe.get_doc("User", "inspector@example.com")
user.add_roles("Maintenance User")
user.save()
```

### 2. Assignment Rules (Repair Auto-Assignment)

**See detailed guide:** [ERPNEXT_ASSIGNMENT_RULES.md](ERPNEXT_ASSIGNMENT_RULES.md)

**Quick Setup:**
```
1. Go to: Assignment Rule List
2. Create new Assignment Rule
3. Set Document Type: Asset Repair
4. Add condition: doc.repair_status == "Pending"
5. Assign to: Role = "Engineering Team"
6. Save
```

### 3. Email Alerts (Repair Notifications)

**Quick Setup:**
```
1. Go to: Email Alert List
2. Create new Email Alert
3. Document Type: Asset Repair
4. Event: New
5. Recipients: Role = "Engineering Team" + "Maintenance Manager"
6. Subject: "New Repair Request: {doc.name}"
7. Save and enable
```

### 4. Enable Mobile Search (Testing Only)

**In production:** Inspectors should only use QR scanning.

**For testing:** Allow manual search via configuration.

```bash
# Add to site_config.json
bench --site [your-site-name] set-config \
  enable_inspector_manual_search 1

# Disable in production:
bench --site [your-site-name] set-config \
  enable_inspector_manual_search 0
```

**Frontend checks this:**
```javascript
// Frontend reads: frappe.boot.sysdefaults.enable_inspector_manual_search
const canSearch = userRole === 'Maintenance Manager' ||
                  (frappe.boot.sysdefaults.enable_inspector_manual_search &&
                   ['Maintenance User', 'Engineering Team'].includes(userRole));
```

---

## Post-Installation

### 1. Run Asset Repair Field Setup

**IMPORTANT:** Run this setup script once after installation to configure Asset Repair field locking.

```bash
bench --site [your-site-name] execute tub_suite.setup.asset_repair_setup.run_production_setup
```

This script will:
- ✓ Fix severity field options (remove blank option)
- ✓ Lock protected fields (failure_date, description, reported_by)
- ✓ Create Server Script for backend validation
- ✓ Create Client Script for UI behavior
- ✓ Auto-fill completion_date when repair completed

**What gets locked:**
- `description`: Issue description from inspector (read-only for engineers)
- `failure_date`: Date issue reported (auto-set, read-only)
- `reported_by`: Inspector who reported (auto-set, read-only)

**What stays editable:**
- `actions_performed`: Engineer documents repair work here
- `issue_severity`: Engineer sets Minor/Major
- `expected_completion_date`: Engineer sets target date

### 2. Generate QR Codes for Assets

```bash
bench --site [your-site-name] console

# In console:
# Generate QR for all assets
assets = frappe.get_all("Asset", filters={"status": "Submitted"}, pluck="name")
for asset_name in assets:
    try:
        asset = frappe.get_doc("Asset", asset_name)
        # QR generation code here (if implemented)
        print(f"Generated QR for {asset_name}")
    except Exception as e:
        print(f"Error: {asset_name} - {e}")

frappe.db.commit()
```

### 2. Create Test Data (Development Only)

```bash
bench --site [your-site-name] console

# Create test asset
asset = frappe.get_doc({
    "doctype": "Asset",
    "asset_name": "Test Pump 001",
    "item_code": "PUMP-001",
    "asset_category": "Machinery",
    "location": "Factory Floor A",
    "company": "Your Company"
})
asset.insert()

# Create maintenance schedule
maint = frappe.get_doc({
    "doctype": "Asset Maintenance",
    "asset_name": asset.name,
    "company": "Your Company"
})
maint.append("asset_maintenance_tasks", {
    "maintenance_task": "Check oil level",
    "maintenance_type": "Preventive Maintenance",
    "periodicity": "Weekly",
    "start_date": frappe.utils.today()
})
maint.insert()
maint.submit()

frappe.db.commit()
```

### 3. Test Mobile Access

```
1. Open mobile browser
2. Navigate to: https://your-site.com/maintenance
3. Login as inspector
4. Test QR scanning
5. Complete a task
6. Report an issue with photos
```

### 4. Verify Notifications Work

```
1. Report issue as inspector
2. Check engineer receives email
3. Check engineer sees TODO item
4. Complete repair as engineer
5. Check inspector receives verification request
6. Verify as inspector
7. Check manager receives approval request
```

---

## Troubleshooting

### Issue: Custom Fields Not Showing

**Cause:** Fixtures not imported during installation.

**Solution:**
```bash
# Import manually
bench --site [your-site-name] import-doc \
  Custom\ Field \
  apps/tub_suite/tub_suite/fixtures/custom_fields.json

# Clear cache
bench --site [your-site-name] clear-cache
bench --site [your-site-name] clear-website-cache

# Reload browser with Ctrl+Shift+R
```

### Issue: Mobile Page Shows 404

**Cause:** Web routes not registered.

**Solution:**
```bash
# Check hooks.py has website_route_rules
cat apps/tub_suite/tub_suite/hooks.py | grep -A 3 "website_route_rules"

# Should show:
# website_route_rules = [
#     {"from_route": "/maintenance", "to_route": "maintenance"},
# ]

# Rebuild and restart
bench build --app tub_suite
bench restart
```

### Issue: Photos Not Uploading

**Cause:** File size limits or permissions.

**Solution:**
```bash
# Check site_config.json max file size
cat sites/[your-site-name]/site_config.json | grep max_file_size

# Increase if needed (in MB)
bench --site [your-site-name] set-config max_file_size 10

# Check file permissions
ls -la sites/[your-site-name]/public/files/
# Should be owned by frappe user

# Fix permissions if needed
sudo chown -R frappe:frappe sites/[your-site-name]/public/
```

### Issue: API Returns 403 Forbidden

**Cause:** User missing required roles.

**Solution:**
```bash
bench --site [your-site-name] console

# Check user roles
user = frappe.get_doc("User", "inspector@example.com")
print(user.get_roles())

# Add missing role
user.add_roles("Maintenance User")
user.save()
frappe.db.commit()
```

### Issue: TODO Items Not Created

**Cause:** Assignment Rules not configured.

**Solution:**
- See [ERPNEXT_ASSIGNMENT_RULES.md](ERPNEXT_ASSIGNMENT_RULES.md)
- Verify Assignment Rule is enabled
- Check conditions match your workflow

### Issue: Emails Not Sending

**Cause:** Email account not configured.

**Solution:**
```bash
# Check email account exists
bench --site [your-site-name] console

# In console:
frappe.get_all("Email Account", fields=["name", "enable_outgoing"])

# Setup email account in ERPNext:
# Setup → Email → Email Account → New
```

---

## Production Checklist

Before going live:

- [ ] Backup database: `bench --site [site] backup`
- [ ] Install app: `bench install-app tub_suite`
- [ ] Verify custom fields: Check Asset Repair form
- [ ] Assign user roles: Maintenance User, Engineering Team, Manager
- [ ] Configure Assignment Rules: For auto-assignment
- [ ] Setup Email Alerts: For notifications
- [ ] Generate QR codes: For all assets
- [ ] **Disable manual search:** Set `enable_inspector_manual_search = 0`
- [ ] Test complete workflow: Report → Repair → Verify → Approve
- [ ] Train users: Inspectors, Engineers, Managers
- [ ] Monitor logs: First 24 hours

---

## Support

- **Issues:** https://github.com/tstexbj3/tub_suite/issues
- **Email:** it@tipubon.com
- **Docs:** See [README.md](README.md) and [CHANGELOG.md](CHANGELOG.md)

---

**Last Updated:** 2025-12-15
**Version:** 2.0.0
