# TUB Suite - Installation Guide

## Prerequisites

- ERPNext v15 / Frappe Framework v15
- Node.js 16+ and npm
- Python 3.10+
- MariaDB/MySQL database
- Redis server

## Installation via bench get-app

### Step 1: Get the App

```bash
cd /home/user/frappe-bench
bench get-app https://github.com/YOUR_USERNAME/tub_suite.git
```

Or for development:
```bash
bench get-app --branch develop https://github.com/YOUR_USERNAME/tub_suite.git
```

### Step 2: Install on Site

```bash
bench --site YOUR_SITE_NAME install-app tub_suite
```

### Step 3: Build React Frontend

```bash
cd apps/tub_suite/maintenance-react-dev
npm install
npm run build
bash update-hash.sh
```

### Step 4: Restart Server

```bash
cd /home/user/frappe-bench
bench restart
```

### Step 5: Initial Configuration

1. **Create Portal Settings:**
```bash
bench --site YOUR_SITE_NAME console
```

```python
import frappe
doc = frappe.get_doc({
    "doctype": "Maintenance Portal Settings",
    "enable_search_for_all_users": 0
})
doc.insert()
frappe.db.commit()
exit()
```

2. **Assign User Roles:**
   - Go to: User → Select user
   - Add role: "Maintenance User" or "Engineering Team" or "Maintenance Manager"

3. **Configure Workflow:**
   - Workflow "Repair Approval WorkFlow" should be auto-installed
   - Go to: Workflow → Repair Approval WorkFlow
   - Verify it's assigned to "Asset Repair" DocType

### Step 6: Test Installation

1. **Access Mobile Portal:**
   - URL: `http://YOUR_DOMAIN/maintenance`
   - Login with ERPNext credentials
   - Should see home page with QR scanner

2. **Test Search (Manager only):**
   - Search for an asset
   - Verify search works

3. **Test QR Code:**
   - Create test asset with QR code
   - Scan and verify checklist loads

## Post-Installation

### Configure Email Notifications

```bash
bench --site YOUR_SITE_NAME set-config mail_server "smtp.example.com"
bench --site YOUR_SITE_NAME set-config mail_port 587
bench --site YOUR_SITE_NAME set-config use_tls 1
bench --site YOUR_SITE_NAME set-config mail_login "your@email.com"
bench --site YOUR_SITE_NAME set-config mail_password "yourpassword"
```

### Enable Scheduled Tasks (Optional)

Edit `tub_suite/hooks.py` and uncomment scheduler if needed.

### Generate QR Codes for Assets

For each asset:
1. Open Asset document
2. Use QR code generator
3. Print and affix to physical asset

## Troubleshooting Installation

### Issue: "App not found"

**Solution:**
```bash
bench --site YOUR_SITE_NAME list-apps
# Should show tub_suite
```

If not listed:
```bash
bench --site YOUR_SITE_NAME install-app tub_suite
```

### Issue: "Module not found"

**Solution:**
```bash
cd /home/user/frappe-bench
bench migrate
bench build
bench restart
```

### Issue: "React app not loading"

**Solution:**
```bash
cd apps/tub_suite/maintenance-react-dev
npm install
npm run build
bash update-hash.sh
cd /home/user/frappe-bench
bench restart
```

### Issue: "Maintenance Portal Settings not found"

**Solution:** Run Step 5 above to create settings document.

## Updating the App

```bash
cd /home/user/frappe-bench
bench get-app tub_suite --skip-assets  # Pull latest
bench --site YOUR_SITE_NAME migrate     # Run migrations
cd apps/tub_suite/maintenance-react-dev
npm run build                           # Rebuild React
bash update-hash.sh                     # Update hashes
cd /home/user/frappe-bench
bench restart                           # Restart
```

## Uninstallation

```bash
bench --site YOUR_SITE_NAME uninstall-app tub_suite
bench remove-app tub_suite
```

⚠️ **Warning:** This will delete all maintenance data!

## Support

For issues, contact:
- Email: [Your support email]
- GitHub Issues: [Your repo]/issues
- Documentation: apps/tub_suite/DOCUMENTATION/README.md

---

**Version:** 1.0
**Last Updated:** December 16, 2024
