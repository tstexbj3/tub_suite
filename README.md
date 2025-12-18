# TUB Suite

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/tstexbj3/tub_suite/releases)
[![ERPNext](https://img.shields.io/badge/ERPNext-v15-orange.svg)](https://erpnext.com)

Custom maintenance management modules for **Tipubon International Co., Ltd.**

Built on **ERPNext v15** / **Frappe Framework v15**

---

## 🚀 What's New in v2.0.0

**Major rewrite from jQuery to React 19.2.0!**

- ✅ Modern React frontend with Vite build system
- ✅ Bilingual support (English/Thai) with i18next
- ✅ Multi-photo upload for issue reporting
- ✅ Enhanced mobile UX and responsive design
- ✅ Auto-calculated next due dates
- ✅ Task completion protection (same-day grace period)
- ✅ Security features (rate limiting, audit logging)

📝 See [CHANGELOG.md](CHANGELOG.md) for full details.

**⚠️ Breaking Changes:** This version requires rebuilding the frontend. Old v1.x jQuery version available in branch `v1-jquery-legacy`.

📖 **[Complete Workflow Documentation](docs/WORKFLOW.md)** - Read this to understand roles, photo requirements, and issue severity system.

---

## 📋 Features

### Mobile QR-Based Maintenance Portal
- **QR Code Scanning:** Quick asset identification via mobile camera
- **Maintenance Checklists:** Task-based inspections with due dates
- **Issue Reporting:** Multi-photo upload with descriptions
- **Repair Workflow:** Automatic repair request creation with reporter verification
- **Asset Status Management:** Out of Order detection and automatic restoration
- **Verification System:** Original reporter verifies completed repairs before asset restoration
- **Pending Verifications:** Home page alerts for repairs awaiting verification
- **Bilingual Interface:** Switch between English/Thai

### Backend API
- **Security:** Rate limiting, permission validation, audit logging
- **Role-Based Access:** Inspector, Manager, Engineer roles
- **Smart Task Ordering:** Respects Asset Maintenance idx
- **Duplicate Prevention:** Same-day completion grace period
- **Auto-Calculations:** Next due dates based on periodicity

---

## 🛠️ Installation

### Requirements
- **Frappe Framework:** v15+
- **ERPNext:** v15+
- **Python:** 3.10+
- **Node.js:** 18+ (for frontend build)
- **npm:** 9+

### Install via Bench

```bash
cd ~/frappe-bench

# Get the app from GitHub
bench get-app https://github.com/tstexbj3/tub_suite.git

# Install on your site
bench --site [site-name] install-app tub_suite

# Clear cache
bench --site [site-name] clear-cache

# Restart
bench restart
```

### Frontend Build (React Portal)

```bash
cd ~/frappe-bench/apps/tub_suite/maintenance-react-dev

# First time setup
npm install

# Build and deploy (automated - updates template hash automatically)
./deploy.sh

# Manual build (requires manual hash update in maintenance.html)
npm run build
./update-hash.sh

# Development mode (with hot reload)
npm run dev
```

**⚠️ Important:** After building, always run `./deploy.sh` or `./update-hash.sh` to sync asset hashes in the HTML template.

### Migration from v1.x

If upgrading from jQuery version (v1.x):

```bash
# Pull latest code
cd ~/frappe-bench/apps/tub_suite
git pull

# Build frontend with new automated deploy
cd maintenance-react-dev
npm install
./deploy.sh

# Migrate database (if needed)
bench --site [site-name] migrate

# Clear cache and restart
bench --site [site-name] clear-cache
bench restart
```

---

## 📱 Usage

### Accessing the Portal

**Mobile Maintenance Portal:**
```
https://your-erpnext-site.com/maintenance
```

**QR Code Scanner:**
```
https://your-erpnext-site.com/qr-scanner
```

**ERPNext Desk:**
```
https://your-erpnext-site.com/app
```

### User Roles

| Role | Access | Permissions |
|------|--------|-------------|
| **Maintenance User** | Mobile portal ONLY | QR scanning, checklist completion, issue reporting, repair verification |
| **Engineering Team** | ERPNext desk + portal | Repair management, work completion, full CRUD |
| **Maintenance Manager** | ERPNext desk + portal | Approval workflow, reports, override verification |

**Note:** Maintenance User role has NO desk access - they work exclusively through the mobile portal.

### Complete Repair Workflow

#### 1. Issue Reporting (Inspector/Maintenance User)
- Scan asset QR code via mobile portal
- Complete maintenance checklist
- Report issue with photos and description
- **System tracks `reported_by` field** (original reporter email)

#### 2. Repair Creation & Approval (Engineer + Manager)
- System auto-creates Asset Repair document
- Engineer fills repair details and sets **Issue Severity**:
  - **Minor - Asset Operational**: Asset stays operational
  - **Major - Asset Must Stop**: Asset goes "Out of Order" upon approval
- Engineer submits for manager approval

#### 3. Manager Approval
- Manager reviews repair request
- If approved and severity = "Major" → **Asset status changes to "Out of Order"**

#### 4. Repair Completion (Engineer)
- Engineer performs repair work
- Clicks workflow: **"Job Finished"**
- **System auto-fills `completion_date`** (timestamp when engineer finished)
- **System sends notification** to original reporter
- Asset stays "Out of Order" until verified

#### 5. Verification (Original Reporter)
- Original reporter opens mobile portal
- **Home page shows red alert** with pending verifications counter
- Reporter scans asset QR code
- Uploads verification photos
- Adds verification notes
- Selects status: "Verified - Passed" or "Verified - Failed"
- Submits verification

#### 6. Asset Restoration (Automatic)

**If verification = "Verified - Passed":**
- System checks for other open Major repairs on same asset
- If none → **Asset automatically restores to "Submitted" (operational)**
- If other Major repairs exist → Asset stays "Out of Order"

**If verification = "Verified - Failed":**
- Asset stays "Out of Order"
- Workflow state stays "Finished"
- Engineer must re-do the repair
- Manager can see verification notes and decide next action:
  - Reject repair → Send back to engineer
  - Or manually change workflow back to "Approved" for engineer to fix

**Data Stored:**
```
Asset Repair Document:
├── completion_date: When engineer finished job
├── verification_date: When reporter verified
├── verification_status: "Verified - Passed" / "Verified - Failed"
├── verification_notes: Reporter's notes
├── verified_by: Reporter's email
└── Attached Files: Verification photos
```

---

## 🔧 Configuration

### Custom Fields Setup

The app creates custom fields automatically via fixtures. Key doctypes:

- **Asset Maintenance** - Checklist tasks with periodicity
- **Asset Maintenance Task** - Individual inspection items
- **Asset Maintenance Log** - Completed task records
- **Asset Repair** - Repair requests with approval workflow

### Roles & Permissions

Assign users to roles in ERPNext:

```
User List → Edit User → Roles → Add:
- Maintenance Inspector (for mobile workers)
- Maintenance Engineer (for technicians)
- Maintenance Manager (for supervisors)
```

### QR Code Generation

Generate QR codes for assets:

```python
# In ERPNext Console
frappe.get_doc("Asset", "ASSET-NAME").generate_qr_code()
```

Or use the Asset form's QR Code button.

---

## 🏗️ Project Structure

```
tub_suite/
├── tub_suite/
│   ├── api/                      # Backend API endpoints
│   │   ├── maintenance.py        # Main maintenance API
│   │   ├── asset.py              # Asset operations & security
│   │   └── qr_scanner.py         # QR code routing
│   ├── maintenance_qr/           # Custom DocTypes
│   │   └── doctype/
│   │       ├── maintenance_schedule/
│   │       ├── maintenance_log/
│   │       └── maintenance_checklist_item/
│   ├── overrides/                # DocType overrides
│   │   └── asset_repair_override.py
│   ├── public/                   # Static assets
│   │   └── maintenance/          # React build output
│   ├── www/                      # Web pages
│   │   ├── maintenance.html      # React SPA entry
│   │   └── maintenance.py        # Context provider
│   ├── config/                   # App configuration
│   └── hooks.py                  # Frappe hooks
├── maintenance-react-dev/        # React source (if included)
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── services/             # API client
│   │   ├── i18n/                 # Translations
│   │   └── App.jsx               # Main app
│   ├── package.json
│   └── vite.config.js
├── CHANGELOG.md                  # Version history
├── README.md                     # This file
└── pyproject.toml                # Python dependencies
```

---

## 🔐 Security Features

- **Rate Limiting:** API endpoints protected against abuse
- **Permission Validation:** Role-based access control
- **Input Sanitization:** XSS and injection prevention
- **Audit Logging:** Security events tracked
- **CSRF Protection:** Token validation on all requests
- **File Upload Validation:** Type and size checks

---

## 🌐 API Endpoints

### Maintenance API

```python
# Get asset maintenance checklist
GET /api/method/tub_suite.api.maintenance.get_maintenance_by_asset
Parameters: asset_name

# Submit maintenance task
POST /api/method/tub_suite.api.maintenance.submit_maintenance_task
Parameters: maintenance_name, task_name, asset_name, has_issue, notes, photos

# Get pending repairs
GET /api/method/tub_suite.api.maintenance.get_pending_repairs
Parameters: asset_name (optional)

# Complete repair
POST /api/method/tub_suite.api.maintenance.complete_repair
Parameters: repair_name, repair_notes, after_repair_photos
```

### Asset API

```python
# Search assets
GET /api/method/tub_suite.api.asset.search_assets
Parameters: asset_code

# Get asset with checklist
GET /api/method/tub_suite.api.asset.get_asset_with_checklist
Parameters: asset_name

# Submit checklist
POST /api/method/tub_suite.api.asset.submit_checklist
Parameters: asset_name, checklist_data, issue_description
```

---

## 🧪 Development

### Contributing

This app uses `pre-commit` for code quality:

```bash
cd apps/tub_suite

# Install pre-commit
pip install pre-commit

# Enable hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

Tools configured:
- **ruff** - Python linting
- **eslint** - JavaScript linting
- **prettier** - Code formatting
- **pyupgrade** - Python syntax upgrades

### Development Workflow

```bash
# Start Frappe bench
cd ~/frappe-bench
source env/bin/activate
bench start

# In another terminal, start React dev server (optional)
cd ~/frappe-bench/apps/tub_suite/maintenance-react-dev
npm run dev

# Access dev server at http://localhost:5173 (proxies to Frappe)
```

### Building for Production

```bash
cd ~/frappe-bench/apps/tub_suite

# Build React app
npm run build

# Output goes to:
# - tub_suite/public/maintenance/
# - tub_suite/www/maintenance/

# Clear Frappe cache
bench --site [site-name] clear-cache
```

---

## 📚 Documentation

- **API Documentation:** See [tub_suite/api/](tub_suite/api/) docstrings
- **Changelog:** See [CHANGELOG.md](CHANGELOG.md)
- **Migration Guide:** See CHANGELOG.md v2.0.0 section
- **Legacy Version:** Branch `v1-jquery-legacy`

---

## 🐛 Troubleshooting

### Frontend not loading
```bash
# Rebuild frontend
npm run build

# Clear browser cache
# Hard reload: Ctrl+Shift+R (Chrome/Firefox)
```

### API errors
```bash
# Check Frappe logs
tail -f ~/frappe-bench/sites/[site-name]/logs/web.error.log

# Check worker logs
tail -f ~/frappe-bench/logs/worker.error.log
```

### Permission denied
```bash
# Check user roles in ERPNext
# User → Roles → Add required maintenance roles
```

---

## 🧩 Integration

### ERPNext Modules Used
- **Assets** - Core asset management
- **Maintenance** - Asset Maintenance, Tasks, Logs
- **Stock** - Items, Item Groups
- **HR** - User roles and permissions

### Custom Workflow
- **Asset Repair Approval** - Manager approval for repair requests
- **Asset Status Management** - Auto status change on issues

---

## 📄 License

MIT License

Copyright (c) 2024 Tipubon International Co., Ltd.

See [license.txt](license.txt) for full text.

---

## 🙋 Support

- **Issues:** https://github.com/tstexbj3/tub_suite/issues
- **Discussions:** https://github.com/tstexbj3/tub_suite/discussions
- **Email:** it@tipubon.com

---

## 🏆 Credits

**Developed by:** Tipubon International Co., Ltd.
**Built for:** ERPNext v15 / Frappe Framework v15
**Frontend:** React 19.2.0 + Vite 6.0.3
**Backend:** Python 3.12+

---

## 📊 Version History

| Version | Date | Description |
|---------|------|-------------|
| **2.0.0** | 2025-12-15 | React migration, major rewrite |
| 1.1.0 | 2024-12-04 | jQuery version improvements |
| 1.0.0 | 2024-11-30 | Initial release |

**Latest:** [v2.0.0](https://github.com/tstexbj3/tub_suite/releases/tag/v2.0.0)

---

## 🔮 Roadmap

- [ ] Mobile app (React Native)
- [ ] Offline support (PWA)
- [ ] Barcode scanning
- [ ] Advanced analytics dashboard
- [ ] Email/SMS notifications
- [ ] PDF report generation
- [ ] Integration with external CMMS systems

---

**Made with ❤️ for better maintenance management**
