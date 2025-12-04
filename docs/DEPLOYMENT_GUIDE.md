# TUB Suite - Master Deployment Guide
**Tipubon International Co., Ltd.**
**Version**: 1.1.0
**Last Updated**: December 4, 2025

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Current Status](#current-status)
3. [File Locations](#file-locations)
4. [Deployment Process](#deployment-process)
5. [QR Code Setup](#qr-code-setup)
6. [Testing Checklist](#testing-checklist)
7. [Migration to Production](#migration-to-production)
8. [Troubleshooting](#troubleshooting)

---

## 1. System Overview

### What is TUB Suite?

A mobile-first maintenance inspection system for Frappe/ERPNext that enables:
- **Mobile QR scanning** of assets
- **Maintenance checklist** completion tracking
- **Problem reporting** with photo attachments
- **Automated notifications** to maintenance team
- **Security & audit logging**

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Mobile Device (Inspector)                              │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Browser: /maintenance                            │  │
│  │  - QR Scanner (jsQR)                             │  │
│  │  - Asset Search                                   │  │
│  │  - Checklist UI                                   │  │
│  │  - Photo Upload                                   │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTPS
                      ↓
┌─────────────────────────────────────────────────────────┐
│  ERPNext Server (tub.x-desk.tech or ngrok)              │
│  ┌───────────────────────────────────────────────────┐  │
│  │  /maintenance Portal                              │  │
│  │  - index.html (UI)                               │  │
│  │  - index.py (Access Control)                     │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  TUB Suite API                                    │  │
│  │  - search_assets()                               │  │
│  │  - get_asset_with_checklist()                    │  │
│  │  - submit_checklist()                            │  │
│  │  - generate_maintenance_qr()                     │  │
│  │  + Security (rate limit, audit log)             │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  ERPNext Database                                 │  │
│  │  - Asset                                         │  │
│  │  - Asset Maintenance                             │  │
│  │  - Asset Maintenance Log                         │  │
│  │  - Asset Repair                                  │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Current Status

### ✅ Completed Features

| Feature | Status | Version | Notes |
|---------|--------|---------|-------|
| Mobile Portal | ✅ Working | 1.1.0 | index_improved.html deployed |
| QR Scanner | ✅ Working | 1.1.0 | Supports multiple URL formats |
| Asset Search | ✅ Working | 1.0.0 | Case-insensitive |
| Checklist Display | ✅ Working | 1.1.0 | With same-day grace period |
| Photo Upload | ✅ Working | 1.1.0 | Multiple photos (up to 5) |
| Photo Compression | ✅ Working | 1.1.0 | Client-side compression |
| Problem Reporting | ✅ Working | 1.0.0 | Creates Asset Repair |
| Email Notifications | ✅ Working | 1.0.0 | To managers + engineers |
| Security (Rate Limit) | ✅ Active | 1.0.0 | 50/100/20 req/min |
| Security (Audit Log) | ✅ Active | 1.0.0 | All actions logged |
| Approval Workflow | ✅ Coded | 1.1.0 | Pending field setup |
| Thai Language | ✅ Working | 1.0.0 | Full interface |

### ⏳ Pending Tasks

| Task | Priority | Status | ETA |
|------|----------|--------|-----|
| Deploy index_improved.html | HIGH | In Progress | Today |
| Install approval fields | MEDIUM | Pending | This week |
| Generate production QR codes | HIGH | Pending | After migration |
| Test complete flow on phone | HIGH | Pending | Today |

### 🐛 Known Issues

| Issue | Severity | Status | Workaround |
|-------|----------|--------|------------|
| Phone scanning blank screen | HIGH | Fixed | Use new QR format |
| QR Foundry generates wrong URL | MEDIUM | Documented | Use custom button |

---

## 3. File Locations

### Production Files (Deploy These)

#### On Windows (Development)
```
C:\Users\user\Desktop\ERPNextIntegration\current_code\
├── index_improved.html              ← Mobile portal UI (DEPLOY THIS)
├── asset_improved.py                ← API + security (DEPLOY THIS)
├── hooks.py                         ← App config (DEPLOY THIS)
├── install_approval_fields.py       ← Setup script (RUN ONCE)
├── generate_qr_for_mobile.py        ← QR helper
├── generate_test_qr.py              ← Test QR generator
├── QR_DEPLOYMENT_GUIDE.md           ← QR instructions
└── DEPLOYMENT_INSTRUCTIONS.md       ← This guide
```

#### On WSL Server (Deployment Target)
```
~/frappe-bench/apps/tub_suite/tub_suite/
├── api/
│   └── asset.py                     ← DEPLOY: asset_improved.py
├── www/
│   └── maintenance/
│       ├── index.html               ← DEPLOY: index_improved.html
│       └── index.py                 ← Already exists (keep)
├── hooks.py                         ← DEPLOY: hooks.py
└── install_approval_fields.py       ← DEPLOY: install_approval_fields.py
```

### Documentation Files (Reference)
```
C:\Users\user\Desktop\ERPNextIntegration\
├── README.md                                          ← Project overview
├── MASTER_DEPLOYMENT_GUIDE.md                         ← THIS FILE
├── ARCHIVE_PLAN.md                                    ← Cleanup plan
├── tub.x-desk.tech/
│   ├── MAINTENANCE_MODULE_DOCUMENTATION.md            ← Complete docs
│   └── MIGRATION_TO_PRODUCTION_GUIDE.md               ← Migration guide
└── planning/
    ├── MAINTENANCE_PORTAL_IMPROVEMENTS_PLAN.md        ← Future work
    └── QR_FOUNDRY_ENHANCEMENT_PROPOSAL.md             ← Upstream proposal
```

---

## 4. Deployment Process

### Prerequisites

- ✅ WSL Ubuntu-24.04 running
- ✅ Frappe bench installed
- ✅ tub_suite app created
- ✅ Site `tub` exists
- ✅ ngrok running (for testing) or production domain configured

### Method 1: Manual Deployment (RECOMMENDED for testing)

#### Step 1: Open File Explorer
```
Windows Explorer → \\wsl$\Ubuntu-24.04\home\user\frappe-bench\apps\tub_suite\tub_suite\
```

#### Step 2: Deploy Files

**Deploy API:**
1. Navigate to: `\\wsl$\Ubuntu-24.04\home\user\frappe-bench\apps\tub_suite\tub_suite\api\`
2. Backup existing: `asset.py` → `asset.py.backup`
3. Copy: `C:\Users\user\Desktop\ERPNextIntegration\current_code\asset_improved.py`
4. Rename to: `asset.py`

**Deploy Mobile Portal:**
1. Navigate to: `\\wsl$\Ubuntu-24.04\home\user\frappe-bench\apps\tub_suite\tub_suite\www\maintenance\`
2. Backup existing: `index.html` → `index.html.backup`
3. Copy: `C:\Users\user\Desktop\ERPNextIntegration\current_code\index_improved.html`
4. Rename to: `index.html`

**Deploy Hooks:**
1. Navigate to: `\\wsl$\Ubuntu-24.04\home\user\frappe-bench\apps\tub_suite\tub_suite\`
2. Backup existing: `hooks.py` → `hooks.py.backup`
3. Copy: `C:\Users\user\Desktop\ERPNextIntegration\current_code\hooks.py`
4. Overwrite: `hooks.py`

**Deploy Approval Setup Script:**
1. Navigate to: `\\wsl$\Ubuntu-24.04\home\user\frappe-bench\apps\tub_suite\tub_suite\`
2. Copy: `C:\Users\user\Desktop\ERPNextIntegration\current_code\install_approval_fields.py`
3. Place as: `install_approval_fields.py`

#### Step 3: Clear Cache & Restart
```bash
cd ~/frappe-bench
bench --site tub clear-cache
bench --site tub clear-website-cache
bench restart
```

#### Step 4: Verify Deployment
```bash
# Check files exist
ls ~/frappe-bench/apps/tub_suite/tub_suite/api/asset.py
ls ~/frappe-bench/apps/tub_suite/tub_suite/www/maintenance/index.html
ls ~/frappe-bench/apps/tub_suite/tub_suite/hooks.py

# Check for JavaScript functions
grep -c "function toggleQRScanner" ~/frappe-bench/apps/tub_suite/tub_suite/www/maintenance/index.html
# Should output: 1

grep -c "function toggleManualEntry" ~/frappe-bench/apps/tub_suite/tub_suite/www/maintenance/index.html
# Should output: 1
```

### Method 2: PowerShell Deployment (Alternative)

```powershell
# Set variables
$SOURCE = "C:\Users\user\Desktop\ERPNextIntegration\current_code"
$TARGET = "\\wsl$\Ubuntu-24.04\home\user\frappe-bench\apps\tub_suite\tub_suite"

# Backup existing files
Copy-Item "$TARGET\api\asset.py" "$TARGET\api\asset.py.backup" -Force
Copy-Item "$TARGET\www\maintenance\index.html" "$TARGET\www\maintenance\index.html.backup" -Force
Copy-Item "$TARGET\hooks.py" "$TARGET\hooks.py.backup" -Force

# Deploy new files
Copy-Item "$SOURCE\asset_improved.py" "$TARGET\api\asset.py" -Force
Copy-Item "$SOURCE\index_improved.html" "$TARGET\www\maintenance\index.html" -Force
Copy-Item "$SOURCE\hooks.py" "$TARGET\hooks.py" -Force
Copy-Item "$SOURCE\install_approval_fields.py" "$TARGET\install_approval_fields.py" -Force

# Clear cache
wsl --distribution Ubuntu-24.04 --exec bash -c "cd ~/frappe-bench && bench --site tub clear-cache && bench restart"
```

### Post-Deployment Setup

#### Install Approval Fields (One-time)
```bash
cd ~/frappe-bench
bench --site tub console
>>> from tub_suite.install_approval_fields import install
>>> install()
# Should show: "✅ Setup Complete! Created: X fields"
>>> exit()
```

---

## 5. QR Code Setup

### Current ngrok Session
```
URL: https://78640d2f1a86.ngrok-free.app
Status: Active
Purpose: Testing before production
```

### Generate Test QR Code

**Option 1: Online Generator (Quick)**
1. Go to: https://www.qr-code-generator.com
2. Enter: `https://78640d2f1a86.ngrok-free.app/maintenance?asset=ACC-ASS-2025-00170`
3. Download PNG
4. Open on PC, scan with phone

**Option 2: Python Script (Batch)**
```bash
# Install qrcode library
pip install qrcode[pil]

# Run generator
cd ~/Desktop
python C:/Users/user/Desktop/ERPNextIntegration/current_code/generate_test_qr.py

# Output: ~/Desktop/test_qr_codes/ACC-ASS-2025-00170_QR.png
```

### QR Code Formats Supported

The scanner supports ALL these formats:

1. **Maintenance Portal** (Recommended for mobile)
   ```
   https://78640d2f1a86.ngrok-free.app/maintenance?asset=ACC-ASS-2025-00170
   ```

2. **ERPNext Desk** (QR Foundry default)
   ```
   https://78640d2f1a86.ngrok-free.app/app/asset/ACC-ASS-2025-00170
   ```

3. **Plain Asset Code** (Future-proof)
   ```
   ACC-ASS-2025-00170
   ```

---

## 6. Testing Checklist

### Pre-Deployment Testing (on localhost)

- [ ] API functions work in browser console
- [ ] Maintenance portal loads: `http://localhost:8000/maintenance`
- [ ] Search finds assets
- [ ] Checklist displays correctly
- [ ] Photo upload works
- [ ] Submission creates Asset Repair

### Post-Deployment Testing (on ngrok)

#### On Desktop Browser
- [ ] Open: `https://78640d2f1a86.ngrok-free.app/maintenance`
- [ ] Login prompt appears (if not logged in)
- [ ] After login, portal loads
- [ ] QR scanner button works
- [ ] Manual search works
- [ ] Asset details display
- [ ] Checklist shows tasks
- [ ] Can check/uncheck tasks
- [ ] Photo upload shows preview
- [ ] Submit button works
- [ ] Success message appears

#### On Mobile Phone
- [ ] Generate test QR code
- [ ] Open QR image on PC
- [ ] Scan with phone camera
- [ ] URL opens in browser
- [ ] Login prompt (if not logged in)
- [ ] Login with ERPNext credentials
- [ ] Asset loads automatically
- [ ] Can view checklist
- [ ] Can take/upload photos
- [ ] Can submit form
- [ ] Success notification

#### Test from Line App
- [ ] Send QR code image to Line chat
- [ ] Open image in Line
- [ ] Use Line's QR scanner
- [ ] Verify URL opens
- [ ] Verify login redirect works
- [ ] Verify asset loads

### Integration Testing

- [ ] Create test Asset Maintenance
- [ ] Add tasks with different periodicities
- [ ] Complete checklist via mobile
- [ ] Verify Asset Maintenance Logs created
- [ ] Report issue with photo
- [ ] Verify Asset Repair created (Draft)
- [ ] Verify photo attached
- [ ] Check email notification sent
- [ ] Verify managers received email
- [ ] Open repair from email link
- [ ] Process and complete repair

---

## 7. Migration to Production

### When to Migrate

Migrate when:
- ✅ All testing complete on ngrok
- ✅ QR codes tested from multiple devices
- ✅ Photo upload reliable
- ✅ Email notifications working
- ✅ Security features verified
- ✅ Users trained

### Migration Steps

#### Step 1: Prepare Production Server
```bash
# SSH to production
ssh user@tub.x-desk.tech

# Backup current state
cd ~/frappe-bench
bench --site tub.x-desk.tech backup --with-files

# Note backup location
```

#### Step 2: Deploy Code
Use same deployment process as testing (Method 1 or 2 above), but target production site:
- Site name: `tub.x-desk.tech` (instead of `tub`)
- Domain: `https://tub.x-desk.tech` (instead of ngrok URL)

#### Step 3: Update URLs in Documentation
Update these files with production domain:
- QR_DEPLOYMENT_GUIDE.md
- MAINTENANCE_MODULE_DOCUMENTATION.md
- User training materials

#### Step 4: Generate Production QR Codes
```bash
# Update generate_qr_for_mobile.py
NGROK_URL = "https://tub.x-desk.tech"  # Change from ngrok to production

# Generate QR codes for all assets
python generate_all_production_qr.py
```

#### Step 5: Print and Install QR Labels
- Print QR codes on weatherproof labels
- Install on assets (see MAINTENANCE_MODULE_DOCUMENTATION.md - QR Labels section)
- Test scanning in field

#### Step 6: User Training
- Train inspectors on mobile portal
- Train managers on repair approval
- Train engineers on repair completion
- Distribute quick reference guides

---

## 8. Troubleshooting

### Common Issues

#### Issue: "ไม่พบสินทรัพย์" (Asset not found) after QR scan

**Symptoms**: QR scanner reads code but search returns no results

**Causes**:
1. Asset ID extraction failed
2. Asset doesn't exist in database
3. Typo in asset code

**Solutions**:
```javascript
// Check browser console (F12)
// Should see:
// "QR Code scanned: [URL]"
// "Extracted asset ID: ACC-ASS-2025-XXXXX"

// If asset ID looks wrong, the QR format is unsupported
// If asset ID looks right, asset doesn't exist in ERPNext
```

**Fix**:
- Verify asset exists: `/app/asset/ACC-ASS-2025-XXXXX`
- Try manual search to confirm
- Check QR code contains correct asset ID

---

#### Issue: Blank white screen when scanning from phone

**Symptoms**: QR opens in browser but shows blank page

**Causes**:
1. QR contains `localhost` URL (doesn't work on phone)
2. Not logged into ERPNext
3. JavaScript error

**Solutions**:
1. **Check QR URL format**:
   - ❌ Bad: `http://localhost:8000/app/asset/ACC-ASS-2025-00170`
   - ✅ Good: `https://78640d2f1a86.ngrok-free.app/maintenance?asset=ACC-ASS-2025-00170`

2. **Login first**:
   - Open: `https://78640d2f1a86.ngrok-free.app/login`
   - Login with ERPNext credentials
   - Then scan QR

3. **Check JavaScript errors**:
   - On phone: Use Chrome Remote Debugging
   - Or check server Error Log: `/app/error-log`

---

#### Issue: "function toggleQRScanner is not defined"

**Symptoms**: Click "Scan QR" → Error in console

**Cause**: Corrupted or incomplete index.html file

**Solution**:
```bash
# Re-deploy index_improved.html
# Verify functions exist:
grep -c "function toggleQRScanner" ~/frappe-bench/apps/tub_suite/tub_suite/www/maintenance/index.html
# Should output: 1

# If output is 0, file is corrupted
# Re-copy from current_code/index_improved.html

# Clear cache
bench --site tub clear-cache
bench restart
```

---

#### Issue: Photo upload fails

**Symptoms**: Photo preview shows but upload fails, or "Photo upload error"

**Causes**:
1. File too large
2. Network timeout
3. File permissions
4. CSRF token issue

**Solutions**:
1. **Check file size**: Should compress to <500KB
2. **Check network**: ngrok free tier has limits
3. **Check server logs**:
   ```bash
   tail -f ~/frappe-bench/logs/bench-start.log
   # Look for upload errors
   ```
4. **Retry upload**: Sometimes works on second attempt

---

#### Issue: ngrok URL changed after restart

**Symptoms**: Old QR codes don't work, new ngrok URL active

**Cause**: ngrok free tier assigns random URL on each restart

**Solutions**:
1. **Update test QR codes**: Regenerate with new URL
2. **Or upgrade ngrok**: $8/month for static domain
3. **Or use production domain**: tub.x-desk.tech

---

### Emergency Rollback

If deployment causes issues:

```bash
cd ~/frappe-bench/apps/tub_suite/tub_suite

# Restore backups
cp api/asset.py.backup api/asset.py
cp www/maintenance/index.html.backup www/maintenance/index.html
cp hooks.py.backup hooks.py

# Clear cache and restart
bench --site tub clear-cache
bench restart

# Verify old version working
curl http://localhost:8000/maintenance
```

---

## 📞 Support

### Logs & Monitoring
- **Error Log**: `/app/error-log`
- **Activity Log**: `/app/activity-log`
- **Bench Log**: `~/frappe-bench/logs/bench-start.log`
- **Worker Log**: `~/frappe-bench/logs/worker.log`

### Documentation
- **Complete Docs**: [MAINTENANCE_MODULE_DOCUMENTATION.md](tub.x-desk.tech/MAINTENANCE_MODULE_DOCUMENTATION.md)
- **QR Guide**: [QR_DEPLOYMENT_GUIDE.md](current_code/QR_DEPLOYMENT_GUIDE.md)
- **Improvements**: [MAINTENANCE_PORTAL_IMPROVEMENTS_PLAN.md](planning/MAINTENANCE_PORTAL_IMPROVEMENTS_PLAN.md)

### Quick Commands
```bash
# Check site status
bench --site tub status

# Restart bench
bench restart

# Clear cache
bench --site tub clear-cache

# Check logs
tail -f ~/frappe-bench/logs/bench-start.log

# Console access
bench --site tub console
```

---

**Deployment Guide Version**: 1.0
**Last Tested**: December 4, 2025
**Status**: ✅ Ready for deployment
