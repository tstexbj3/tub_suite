# TUB Suite - New Site Deployment Checklist
**Complete guide to deploy TUB Suite on a fresh ERPNext site**

---

## ✅ What's Included in TUB Suite

The `tub_suite` app contains:
- Mobile maintenance portal UI (`/maintenance`)
- API endpoints for asset search, checklist, repairs
- Security features (rate limiting, audit logging)
- Approval workflow validation
- QR generation functions
- Client scripts for Asset page

---

## 📋 What You Need BEFORE Installing

### 1. ERPNext Requirements
- ✅ Frappe v15+ installed
- ✅ ERPNext v15+ installed
- ✅ Site created and running
- ✅ SSL certificate (for camera access)
- ✅ Email account configured (for notifications)

### 2. System Requirements
- ✅ Ubuntu 20.04+ or similar
- ✅ Python 3.10+
- ✅ MariaDB 10.6+
- ✅ Redis running
- ✅ Sudo access for package installation

### 3. ERPNext Data Requirements
- ✅ **Assets** - Must have Asset records
- ✅ **Asset Maintenance** - Must create Asset Maintenance for each asset
- ✅ **Asset Maintenance Tasks** - Each maintenance must have tasks
- ✅ **Users with roles**:
  - Maintenance Inspector
  - Maintenance Manager
  - Engineering Team

---

## 🚀 Complete Installation Steps

### Step 1: Install TUB Suite App

```bash
cd ~/frappe-bench

# Option A: From GitHub (after you push)
bench get-app https://github.com/tipubon/tub-suite.git

# Option B: From local files (for now)
# Copy tub_suite folder to apps/
cp -r /path/to/tub_suite apps/

# Install to your site
bench --site your-new-site install-app tub_suite
```

### Step 2: Install Python Dependencies

```bash
cd ~/frappe-bench
source env/bin/activate

# Install QR code library
pip install qrcode[pil]
```

### Step 3: Configure Site Settings

```bash
# Set site URL (IMPORTANT: No :8000 port)
bench --site your-new-site set-config host_name "https://your-domain.com"

# Optional: Enable CORS for testing
bench --site your-new-site set-config allow_cors "*"

# Optional: Disable CSRF for API testing
bench --site your-new-site set-config ignore_csrf 1
```

### Step 4: Setup Approval Fields

```bash
cd ~/frappe-bench

# Run setup script
bench --site your-new-site execute tub_suite.install_approval_fields.install
```

**Expected output**:
```
============================================================
Installing Asset Repair Approval Fields...
============================================================

✓ Created: repair_type
✓ Created: approval_section
✓ Created: approval_status
✓ Created: approval_column
✓ Created: approved_by
✓ Created: approval_time
✓ Created: approval_notes_break
✓ Created: approval_notes
✓ Created: approval_signature_break
✓ Created: approval_signature

============================================================
✅ Setup Complete!
   Created: 10 fields
============================================================
```

### Step 5: Create Client Script for Asset QR Button

1. Go to: `/app/client-script`
2. Click **"New"**
3. Fill in:
   - **Name**: `Asset Maintenance QR Button`
   - **DocType**: `Asset`
   - **Type**: `Form`
   - **Enabled**: ✅ Check
4. Copy contents from: `production_code/client_scripts/asset_custom_button.js`
5. Paste into **Script** field
6. Click **"Save"**

### Step 6: Setup User Roles

```bash
# Create roles if they don't exist
bench --site your-new-site console
```

In console:
```python
import frappe

# Create Maintenance Inspector role if needed
if not frappe.db.exists("Role", "Maintenance Inspector"):
    frappe.get_doc({
        "doctype": "Role",
        "role_name": "Maintenance Inspector",
        "desk_access": 0  # Mobile-only access
    }).insert()

# Add permissions for Maintenance Inspector
for doctype in ["Asset", "Asset Maintenance", "Asset Maintenance Log", "Asset Repair"]:
    if not frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": "Maintenance Inspector"}):
        frappe.get_doc({
            "doctype": "Custom DocPerm",
            "parent": doctype,
            "parenttype": "DocType",
            "parentfield": "permissions",
            "role": "Maintenance Inspector",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 0,
            "cancel": 0,
            "delete": 0
        }).insert()

frappe.db.commit()
exit()
```

### Step 7: Create Test User

```bash
# Add test user
bench --site your-new-site add-user inspector@company.com "Test Inspector"
```

Then go to: `/app/user/inspector@company.com` and add roles:
- ✅ Maintenance Inspector
- ✅ Maintenance User

### Step 8: Create Test Data (If New Site)

#### Create Asset
1. Go to: `/app/asset`
2. Create new Asset:
   - **Asset Name**: Test Pump #1
   - **Item Code**: PUMP-001
   - **Asset Category**: Machinery
   - **Location**: Factory Floor
   - **Status**: Submitted

#### Create Asset Maintenance
1. Go to: `/app/asset-maintenance`
2. Create new:
   - **Asset Name**: Test Pump #1
   - **Maintenance Status**: Planned

#### Add Maintenance Tasks
In the same Asset Maintenance, add tasks:

| Task | Periodicity | Maintenance Type |
|------|-------------|------------------|
| Check oil level | Daily | Preventive Maintenance |
| Inspect bearings | Weekly | Preventive Maintenance |
| Lubrication | Monthly | Preventive Maintenance |
| Performance test | Quarterly | Inspection |

Click **"Save"** and **"Submit"**

### Step 9: Clear Cache & Restart

```bash
cd ~/frappe-bench

# Clear all caches
bench --site your-new-site clear-cache
bench --site your-new-site clear-website-cache

# Restart bench
bench restart
```

### Step 10: Test Installation

#### Test 1: Portal Access
```bash
# Open in browser
https://your-domain.com/maintenance

# Should see:
# - Login prompt (if not logged in)
# - Maintenance portal UI (after login)
```

#### Test 2: API Endpoints
```bash
# Test asset search
curl -X GET "https://your-domain.com/api/method/tub_suite.api.asset.search_assets?asset_code=PUMP-001" \
  -H "Cookie: sid=YOUR_SESSION_ID"

# Should return JSON with asset data
```

#### Test 3: QR Generation
1. Go to: `/app/asset/TEST-ASSET-001`
2. Click **"Actions"** → **"🔧 Maintenance QR Code"**
3. QR dialog should appear
4. URL should NOT have `:8000` port

#### Test 4: Mobile Scanning
1. Generate QR code
2. Open QR image on PC
3. Scan with phone
4. Should open maintenance portal
5. Asset should load automatically

---

## 🔧 Configuration After Installation

### Email Notifications Setup

1. Go to: `/app/email-account`
2. Create new Email Account:
   - **Email ID**: noreply@company.com
   - **SMTP Server**: smtp.gmail.com (or your SMTP)
   - **Port**: 587
   - **Use TLS**: ✅ Check
   - **Username**: your-email@gmail.com
   - **Password**: your-app-password
   - **Default Outgoing**: ✅ Check

3. Test email:
   - Send test email from Email Account
   - Should receive successfully

### Site URL Configuration

```bash
# Production domain
bench --site your-new-site set-config host_name "https://erp.company.com"

# Development (with ngrok)
bench --site your-new-site set-config host_name "https://xxxx.ngrok-free.app"
```

**IMPORTANT**: No `:8000` port in production!

### CORS Configuration

**Development**:
```bash
bench --site your-new-site set-config allow_cors "*"
```

**Production** (more secure):
```bash
bench --site your-new-site set-config allow_cors "https://erp.company.com"
```

---

## 📦 What Gets Installed

### Files Created

```
~/frappe-bench/apps/tub_suite/
└── tub_suite/
    ├── api/
    │   └── asset.py                    ← API endpoints + security
    ├── www/
    │   └── maintenance/
    │       ├── index.html              ← Mobile portal UI
    │       └── index.py                ← Access control
    ├── hooks.py                        ← App configuration
    ├── install_approval_fields.py      ← Setup script
    └── patches.txt                     ← Migrations
```

### Database Changes

**Custom Fields Added**:
- Asset Repair:
  - `repair_type` (Select)
  - `approval_section` (Section Break)
  - `approval_status` (Select)
  - `approved_by` (Link)
  - `approval_time` (Datetime)
  - `approval_notes` (Small Text)
  - `approval_signature` (Signature)

**No DocTypes Created** - Uses standard ERPNext DocTypes

### Permissions Modified

Roles get access to:
- Asset (Read, Write)
- Asset Maintenance (Read)
- Asset Maintenance Log (Read, Write, Create)
- Asset Repair (Read, Write, Create)

---

## ❌ Common Installation Issues

### Issue 1: "App not found"

**Cause**: App not properly copied to apps/ folder

**Solution**:
```bash
ls ~/frappe-bench/apps/tub_suite
# Should show: tub_suite/ folder

# If not found, copy again
cp -r /path/to/tub_suite ~/frappe-bench/apps/
```

### Issue 2: "Module not found: qrcode"

**Cause**: Python library not installed

**Solution**:
```bash
cd ~/frappe-bench
source env/bin/activate
pip install qrcode[pil]
bench restart
```

### Issue 3: "Permission denied" when installing

**Cause**: User doesn't have bench permissions

**Solution**:
```bash
# Run as frappe user
sudo -u frappe bash
cd ~/frappe-bench
bench --site your-site install-app tub_suite
```

### Issue 4: "Port :8000 in QR URLs"

**Cause**: Site config has port or using get_url()

**Solution**:
```bash
# Check site_config.json
cat ~/frappe-bench/sites/your-site/site_config.json

# Remove :8000 from host_name
# Should be: "https://domain.com" NOT "https://domain.com:8000"

# Update if needed
nano ~/frappe-bench/sites/your-site/site_config.json
bench restart
```

### Issue 5: "Maintenance portal shows blank page"

**Causes**:
1. JavaScript error
2. Not logged in
3. No permissions

**Solutions**:
```bash
# Check browser console (F12) for errors
# Look for: "toggleQRScanner is not defined"

# If found, re-deploy index.html
cp production_code/www/maintenance/index.html \
   ~/frappe-bench/apps/tub_suite/tub_suite/www/maintenance/

bench --site your-site clear-cache
bench restart
```

---

## 🧪 Testing Checklist

After installation, test:

- [ ] **Login**: Can access `/maintenance` with inspector user
- [ ] **Search**: Can search for assets by code
- [ ] **QR Scanner**: Can open camera and scan QR
- [ ] **Checklist**: Asset checklist displays with tasks
- [ ] **Photos**: Can upload 1-5 photos
- [ ] **Compression**: Photos compress before upload
- [ ] **Submit**: Can submit checklist successfully
- [ ] **Repair**: Asset Repair created (Draft status)
- [ ] **Email**: Managers receive email notification
- [ ] **QR Button**: "Maintenance QR Code" button on Asset page
- [ ] **QR URL**: Generated QR has clean URL (no :8000)
- [ ] **Phone Scan**: QR opens correctly on mobile
- [ ] **Approval**: Can approve/reject Asset Repairs

---

## 📊 Post-Installation

### 1. Generate QR Codes for Assets

```bash
# Option A: One by one (using Asset page button)
# Open each asset → Click "Maintenance QR Code" → Download

# Option B: Bulk generation (coming soon)
# bench --site your-site execute tub_suite.api.asset.bulk_generate_qr
```

### 2. Print QR Labels

- Use weatherproof labels for outdoor assets
- Standard paper for indoor assets
- Include asset name and code on label
- Test scan before mass printing

### 3. Train Users

- Inspectors: How to use mobile portal
- Managers: How to approve repairs
- Engineers: How to complete repairs
- IT: System administration

### 4. Monitor Usage

Check these regularly:
- **Error Log**: `/app/error-log`
- **Activity Log**: `/app/activity-log`
- **Asset Repairs**: `/app/asset-repair`
- **Maintenance Logs**: `/app/asset-maintenance-log`

---

## 🔄 Updating TUB Suite

When new version is released:

```bash
cd ~/frappe-bench

# Pull latest from GitHub
cd apps/tub_suite
git pull origin main

# Migrate site
cd ~/frappe-bench
bench --site your-site migrate

# Clear cache
bench --site your-site clear-cache
bench restart
```

---

## 🆘 Getting Help

### Documentation
- 📖 [Main Documentation](docs/MAINTENANCE_MODULE_DOCUMENTATION.md)
- 🔧 [Troubleshooting](docs/TROUBLESHOOTING.md)
- 💬 [FAQ](docs/FAQ.md)

### Support Channels
- GitHub Issues: https://github.com/tipubon/tub-suite/issues
- Email: support@tipubon.com
- ERPNext Forum: https://discuss.erpnext.com

### Logs to Check
```bash
# Bench log
tail -f ~/frappe-bench/logs/bench-start.log

# Worker log
tail -f ~/frappe-bench/logs/worker.log

# Site-specific log
tail -f ~/frappe-bench/logs/your-site.log
```

---

## ✅ Installation Complete!

If all tests pass, TUB Suite is ready to use! 🎉

**Next steps**:
1. Create Asset Maintenance schedules for all assets
2. Generate and print QR codes
3. Train users
4. Start using the mobile portal

**Questions?** Check the documentation or open an issue on GitHub.

---

**Installation Version**: 1.0
**Last Updated**: December 4, 2025
**Status**: ✅ Production Ready
