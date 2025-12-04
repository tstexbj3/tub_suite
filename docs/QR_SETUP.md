# Asset Maintenance QR Button Installation Guide
**Tipubon International Co., Ltd.**

---

## What This Does

Adds a **"🔧 Maintenance QR Code"** button to every Asset page that generates QR codes **without the `:8000` port**, pointing directly to the mobile maintenance portal.

### Before vs After

**❌ OLD (QR Foundry):**
- URL: `https://78640d2f1a86.ngrok-free.app:8000/app/asset/ACC-ASS-2025-00170`
- Opens ERPNext desk (not mobile-friendly)
- Includes port `:8000` (breaks on production)

**✅ NEW (Custom Button):**
- URL: `https://78640d2f1a86.ngrok-free.app/maintenance?asset=ACC-ASS-2025-00170`
- Opens mobile maintenance portal
- No port number (works on production)

---

## Installation Steps

### Step 1: Install qrcode Library

```bash
cd ~/frappe-bench
source env/bin/activate
pip install qrcode[pil]
```

### Step 2: Deploy Updated API

**Copy asset_improved.py to server:**

```bash
# Windows Explorer method:
# 1. Open: \\wsl$\Ubuntu-24.04\home\user\frappe-bench\apps\tub_suite\tub_suite\api\
# 2. Backup: asset.py → asset.py.backup
# 3. Copy: C:\Users\user\Desktop\ERPNextIntegration\current_code\asset_improved.py
# 4. Rename to: asset.py
```

### Step 3: Create Client Script

1. Open ERPNext: `/app/client-script`
2. Click **"New"**
3. Fill in details:
   - **Name**: `Asset Maintenance QR Button`
   - **DocType**: `Asset`
   - **Type**: `Form`
   - **Enabled**: ✅ Check
4. In the **Script** field, paste the contents of:
   ```
   C:\Users\user\Desktop\ERPNextIntegration\current_code\asset_custom_button.js
   ```
5. Click **"Save"**

### Step 4: Clear Cache & Restart

```bash
cd ~/frappe-bench
bench --site tub clear-cache
bench restart
```

### Step 5: Test the Button

1. Open any Asset: `/app/asset/ACC-ASS-2025-00170`
2. You should see a new button: **"Actions"** → **"🔧 Maintenance QR Code"**
3. Click it
4. QR code dialog appears with:
   - QR code image
   - Clean URL (no `:8000`)
   - Download button
   - Print button
   - Copy URL button

---

## Usage

### Generate QR for a Single Asset

1. Open Asset page: `/app/asset/ACC-ASS-2025-00170`
2. Click **"Actions"** → **"🔧 Maintenance QR Code"**
3. QR dialog appears
4. Options:
   - **Download** - Save as PNG
   - **Print** - Print directly
   - **Copy URL** - Copy to clipboard

### Generate QR for All Assets (Bulk)

Coming soon - batch QR generation script.

---

## Features

### ✅ Clean URLs
- No `:8000` port
- Uses configured `host_name` from site_config.json
- Automatically removes port if present

### ✅ Mobile-Optimized
- Points to `/maintenance` portal (not `/app/asset`)
- Mobile-first interface
- Works with phone camera, Line app, QR scanner apps

### ✅ Download & Print
- Download as PNG
- Print directly
- Copy URL to clipboard

### ✅ Preview Before Printing
- Shows QR code
- Shows URL
- Shows usage instructions

---

## Troubleshooting

### Issue: "QR code library not installed"

**Solution**:
```bash
cd ~/frappe-bench
source env/bin/activate
pip install qrcode[pil]
bench restart
```

### Issue: Button doesn't appear

**Causes**:
1. Client script not enabled
2. Cache not cleared
3. Browser cache

**Solutions**:
```bash
# 1. Check client script is enabled
# Go to: /app/client-script/Asset Maintenance QR Button
# Ensure "Enabled" checkbox is checked

# 2. Clear server cache
bench --site tub clear-cache
bench restart

# 3. Clear browser cache
# Press Ctrl+Shift+R (hard refresh)
```

### Issue: "function generate_maintenance_qr not found"

**Cause**: API not deployed correctly

**Solution**:
```bash
# Verify function exists in API
grep -n "def generate_maintenance_qr" ~/frappe-bench/apps/tub_suite/tub_suite/api/asset.py

# Should output line number like: 1072:def generate_maintenance_qr(asset_name):
# If not found, re-deploy asset_improved.py
```

### Issue: QR still has `:8000` port

**Cause**: Old site_config or API not updated

**Solutions**:

1. **Check site_config.json**:
```bash
cat ~/frappe-bench/sites/tub/site_config.json | grep host_name
# Should NOT include :8000
```

2. **Update if needed**:
```bash
# Remove port from host_name
nano ~/frappe-bench/sites/tub/site_config.json
# Change:
# "host_name": "https://78640d2f1a86.ngrok-free.app:8000",
# To:
# "host_name": "https://78640d2f1a86.ngrok-free.app",
```

3. **Restart**:
```bash
bench restart
```

---

## Comparison: Custom Button vs QR Foundry

| Feature | Custom Button | QR Foundry |
|---------|--------------|------------|
| **URL Format** | `/maintenance?asset=X` ✅ | `/app/asset/X` ❌ |
| **No Port** | Yes ✅ | No ❌ (adds :8000) |
| **Mobile Optimized** | Yes ✅ | No ❌ (desk view) |
| **Download QR** | Yes ✅ | Partial ⚠️ |
| **Print QR** | Yes ✅ | No ❌ |
| **Copy URL** | Yes ✅ | No ❌ |
| **Preview** | Yes ✅ | Basic ⚠️ |
| **Bulk Generation** | Coming soon ⏳ | No ❌ |

**Recommendation**: Use Custom Button for maintenance portal QR codes, keep QR Foundry for other use cases.

---

## Next Steps

1. ✅ Install button on test system
2. ✅ Generate test QR codes
3. ✅ Test scanning from phone
4. ⏳ Create bulk generation script
5. ⏳ Deploy to production
6. ⏳ Generate QR codes for all assets
7. ⏳ Print weatherproof labels
8. ⏳ Install on assets

---

## Files Modified/Created

### Modified:
- `current_code/asset_improved.py` - Added `generate_maintenance_qr()` function

### Created:
- `current_code/asset_custom_button.js` - Client script for Asset page
- `current_code/QR_BUTTON_INSTALLATION.md` - This file

### Deploy to Server:
- `asset_improved.py` → `~/frappe-bench/apps/tub_suite/tub_suite/api/asset.py`
- `asset_custom_button.js` → Create as Client Script in ERPNext

---

**Installation Status**: 📋 Ready to install
**Estimated Time**: 10 minutes
**Dependencies**: qrcode library, asset_improved.py deployed
