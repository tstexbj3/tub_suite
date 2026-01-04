# Asset QR Label Printing Guide (Niimbot B1)

**Version:** 2.1.0
**Created:** 2025-01-02
**Purpose:** Print QR code labels for assets using Niimbot B1 thermal printer

---

## Overview

The TUB Suite now supports printing QR code labels for assets in a format optimized for the **Niimbot B1 thermal label printer** (50mm × 30mm labels).

### Features

- ✅ **Single Asset Print:** Print QR label for one asset from Asset form
- ✅ **Batch Printing:** Print multiple QR labels from Asset List
- ✅ **QR Foundry Integration:** Automatic QR code generation using QR Foundry app
- ✅ **Thai Language Support:** Asset names and locations display correctly in Thai
- ✅ **Continuous Tape:** Optimized for Niimbot B1 continuous thermal tape

---

## Label Layout

```
┌──────────────────────────────────┐
│  ▄▄▄▄▄▄    TUB ASSETS           │
│  █ QR █    ACC-ASS-2025-00167    │
│  █CODE█    เครื่องปรับอากาศ      │
│  ▄▄▄▄▄▄    📍 Building A-301     │
└──────────────────────────────────┘
        50mm × 30mm
```

**Label Contents:**
- **Left:** QR Code (26mm × 26mm)
- **Right:**
  - TUB ASSETS (branding)
  - Asset ID (e.g., ACC-ASS-2025-00167)
  - Asset Name in Thai (e.g., เครื่องปรับอากาศ)
  - Location (e.g., 📍 Building A-301)

**QR Code Content:**
- URL: `https://tub.x-desk.tech/maintenance?asset=ACC-ASS-2025-00167`
- Scanning the QR code opens the maintenance portal for that specific asset

---

## How to Use

### Method 1: Single Asset Print

**Use Case:** Print QR label for one asset

**Steps:**

1. **Open Asset:**
   - Go to **Asset List** (`/app/asset`)
   - Click on the asset you want to print (e.g., `ACC-ASS-2025-00167`)

2. **Open Print Dialog:**
   - Click **Print** button (top-right corner of form)
   - Or use **Menu** → **Print**

3. **Select Print Format:**
   - From the dropdown, select: **"Asset QR Label 50x30mm"**

4. **Print Preview:**
   - Print preview window opens showing the 50×30mm label
   - Verify QR code and asset information appear correctly

5. **Print to Niimbot:**
   - Click browser **Print** button
   - Select **Niimbot B1** as printer
   - Verify settings:
     - Paper size: Custom 50mm × 30mm
     - Margins: None (0mm)
     - Scale: 100%
   - Click **Print**

6. **Result:**
   - Niimbot B1 prints one label on continuous tape
   - Cut or tear the label from the tape

---

### Method 2: Batch Print (Multiple Assets)

**Use Case:** Print QR labels for 5, 10, 50+ assets at once

**Steps:**

1. **Open Asset List:**
   - Go to **Asset List** (`/app/asset`)

2. **Select Assets:**
   - Use checkboxes to select assets you want to print labels for
   - Example: Select 10 air conditioners that need labels

3. **Batch Print:**
   - Click **Actions** dropdown (top-right)
   - Select **"Print QR Labels (Niimbot)"**

4. **Confirm:**
   - Confirmation dialog appears: *"Print 10 QR label(s) for Niimbot B1 printer?"*
   - Click **Yes**

5. **Print Preview:**
   - New window opens with all 10 labels displayed
   - Each label is 50×30mm with page-break-after (continuous tape format)
   - Print dialog opens automatically

6. **Print to Niimbot:**
   - Printer: **Niimbot B1**
   - Settings:
     - Paper size: Custom 50mm × 30mm
     - Margins: None
     - Continuous feed: Enabled
   - Click **Print**

7. **Result:**
   - Niimbot B1 prints all 10 labels sequentially on continuous tape
   - Labels appear one after another:
     ```
     [Label 1]
     [Label 2]
     [Label 3]
     ...
     [Label 10]
     ```
   - Cut between labels or use auto-cut (if supported by printer)

---

## Niimbot B1 Printer Setup

### Required Equipment

- **Niimbot B1 Label Printer**
- **50mm × 30mm Thermal Labels** (continuous tape or die-cut)
- **USB Cable** or **Bluetooth** connection
- **Niimbot Driver/Software** installed on PC

### Printer Configuration

1. **Install Niimbot Driver:**
   - Download from: https://www.niimbot.net/enmobile/service_download.html
   - Install Niimbot software on the computer that will print labels

2. **Connect Printer:**
   - **USB:** Connect via USB cable
   - **Bluetooth:** Pair printer with PC

3. **Load Labels:**
   - Insert 50mm wide thermal label tape into Niimbot B1
   - Ensure tape is aligned correctly

4. **Test Print:**
   - Use Niimbot software to print a test label
   - Verify printer is working correctly

### Browser Print Settings

**When printing from ERPNext:**

- **Printer:** Niimbot B1
- **Page Size:** Custom (50mm × 30mm)
- **Orientation:** Portrait
- **Margins:** None (0mm all sides)
- **Scale:** 100% (do not scale)
- **Background Graphics:** Enabled
- **Headers/Footers:** Disabled

---

## QR Code Scanning

**What happens when someone scans the QR code?**

1. **QR Code Contains:** `https://tub.x-desk.tech/maintenance?asset=ACC-ASS-2025-00167`

2. **User Scans QR:**
   - Opens URL in mobile browser or QR scanner app

3. **Routing Logic:**
   - **Not logged in:** Redirects to login page, then to asset maintenance portal
   - **Inspector:** Opens maintenance portal for this asset (mobile-optimized view)
   - **Engineer/Manager:** Opens ERPNext Asset form (desktop view)

4. **Use Cases:**
   - Inspector scans QR during routine inspection
   - Engineer scans QR to log repair
   - Anyone can quickly access asset maintenance history

---

## Technical Details

### File Structure

```
tub_suite/
├── api/
│   └── print_qr_labels.py              # Batch print API endpoint
├── public/
│   └── js/
│       ├── asset.js                    # Asset form customizations
│       └── asset_list.js               # Batch print button
├── tub_suite/
│   └── print_format/
│       ├── asset_qr_label_50x30mm/     # Single label print format
│       │   ├── __init__.py
│       │   ├── asset_qr_label_50x30mm.json
│       │   └── asset_qr_label_50x30mm.html
│       └── asset_qr_label_batch.html   # Batch template (multi-label)
└── hooks.py                            # Configuration
```

### QR Foundry Integration

**How QR codes are generated:**

1. **Import in Template:**
   ```jinja
   {% from "qr_foundry.print_helpers" import qr_src %}
   ```

2. **Generate QR Image:**
   ```html
   <img src="{{ qr_src('Asset', doc.name) }}" alt="QR Code">
   ```

3. **QR Foundry Logic:**
   - Checks if QR List exists for this Asset
   - If yes: Returns existing QR image URL (cached)
   - If no: Generates new QR on-the-fly
   - QR Mode: **URL** (direct link to maintenance portal)

4. **QR Content:**
   - URL format: `https://tub.x-desk.tech/maintenance?asset=ASSET_ID`
   - Example: `https://tub.x-desk.tech/maintenance?asset=ACC-ASS-2025-00167`

### Batch Print API

**Endpoint:** `tub_suite.api.print_qr_labels.batch_print_qr_labels`

**Parameters:**
```json
{
  "asset_names": ["ACC-ASS-2025-00001", "ACC-ASS-2025-00002", ...]
}
```

**Response:**
```json
{
  "html": "<rendered HTML with all labels>",
  "count": 10
}
```

**Process:**
1. Validate user has read permission for all assets
2. Fetch asset data (name, asset_name, location)
3. Generate QR URL for each asset using QR Foundry
4. Render batch template with all labels
5. Return HTML with `page-break-after: always` for continuous tape

---

## Troubleshooting

### QR Code Not Showing

**Symptom:** Print preview shows empty space where QR should be

**Causes:**
1. QR Foundry app not installed
2. QR generation failed
3. Browser blocking data URI images

**Solutions:**
```bash
# Check if QR Foundry is installed
cd /home/user/frappe-bench
bench list-apps | grep qr_foundry

# If not installed:
bench get-app https://github.com/BBbrighton/qr_foundry --skip-assets
bench --site tub.x-desk.tech install-app qr_foundry

# Restart
bench restart
```

### Thai Text Not Displaying

**Symptom:** Thai characters show as boxes or question marks

**Cause:** Font not loaded

**Solution:**
- Ensure **Sarabun** or **TH Sarabun New** fonts are installed
- Print format CSS includes font fallbacks:
  ```css
  font-family: 'Sarabun', 'TH Sarabun New', Arial, sans-serif;
  ```

### Label Size Incorrect

**Symptom:** Labels print too large or too small

**Cause:** Browser scaling or incorrect paper size

**Solution:**
1. Check browser print settings: Scale = 100%
2. Verify paper size: Custom 50mm × 30mm
3. Disable "Fit to page" option
4. Ensure margins are 0mm

### Batch Print Button Not Appearing

**Symptom:** "Print QR Labels (Niimbot)" button missing in Asset List

**Cause:** JavaScript not loaded

**Solution:**
```bash
# Clear cache
bench --site localhost clear-cache

# Rebuild assets (hard reload)
bench build --app tub_suite

# Restart bench
bench restart
```

Then refresh browser (Ctrl+Shift+R for hard reload)

### Printer Not Found

**Symptom:** Niimbot B1 not appearing in printer list

**Cause:** Driver not installed or printer not connected

**Solution:**
1. Install Niimbot driver from official website
2. Connect printer via USB or Bluetooth
3. Verify printer appears in system printers
4. Test print from Niimbot software first

---

## Best Practices

### Label Organization

1. **Print labels for new assets immediately** after adding them to ERPNext
2. **Batch print by location** (e.g., print all Building A assets together)
3. **Keep label inventory** - track how many labels you've printed
4. **Quality check** - verify QR codes scan correctly before applying to assets

### Label Application

1. **Clean surface** before applying label (remove dust/oil)
2. **Apply firmly** - press label for 5-10 seconds
3. **Avoid curved surfaces** - labels work best on flat surfaces
4. **Protect from elements** - consider laminating labels for outdoor assets

### Maintenance Workflow

1. **New asset arrives:**
   - Add to ERPNext as Asset
   - Print QR label
   - Apply label to physical asset
   - Test QR scan

2. **Inspector routine:**
   - Scan QR code on asset
   - Opens maintenance portal
   - Log inspection or report issue

3. **Engineer repair:**
   - Scan QR or search asset
   - Log repair work
   - Take photos
   - Submit for approval

---

## Future Enhancements

**Planned features for v2.2.0:**

- [ ] **Grid layout option** for standard A4 paper (6×4 labels per page)
- [ ] **Export to Niimbot app** - Direct integration with Niimbot desktop software
- [ ] **Barcode support** - Add 1D barcode in addition to QR code
- [ ] **Custom label templates** - Allow users to customize label design
- [ ] **Auto-print on asset creation** - Option to auto-print when new asset is added

---

## Support

**Documentation:**
- [QR Foundry GitHub](https://github.com/BBbrighton/qr_foundry)
- [Niimbot Official](https://www.niimbot.net/)

**Issues:**
- Report bugs: https://github.com/tipubon/tub_suite/issues
- Email: it@tipubon.com

---

**Document Version:** 1.0
**Last Updated:** 2025-01-02
**Author:** TUB Suite Development Team
