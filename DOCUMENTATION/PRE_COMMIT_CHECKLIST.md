# Pre-Commit Checklist for TUB Suite

## Before Committing - Verification Steps

### 1. Essential Files Present ✓

- [x] `pyproject.toml` - Package configuration
- [x] `tub_suite/__init__.py` - Version file
- [x] `tub_suite/hooks.py` - Frappe hooks
- [x] `tub_suite/modules.txt` - Module definition
- [x] `README.md` - Main documentation
- [x] `license.txt` - License file
- [x] `INSTALLATION.md` - Installation guide (NEW)

### 2. React App Built and Ready

```bash
cd /home/user/frappe-bench/apps/tub_suite/maintenance-react-dev
npm run build
bash update-hash.sh
```

Verify:
- [ ] `tub_suite/public/maintenance/assets/` has built files
- [ ] `maintenance.html` has correct asset hashes
- [ ] No build errors

### 3. Documentation Complete

- [x] `DOCUMENTATION/README.md` - Documentation index
- [x] `DOCUMENTATION/01_MAINTENANCE_USER_MANUAL.md`
- [x] `DOCUMENTATION/02_ENGINEERING_TEAM_MANUAL.md`
- [x] `DOCUMENTATION/03_MAINTENANCE_MANAGER_MANUAL.md`
- [x] `DOCUMENTATION/04_SYSTEM_WORKFLOWS_AND_ARCHITECTURE.md`
- [x] `DOCUMENTATION/KNOWN_ISSUES_AND_INVESTIGATION.md`

**Note:** Screenshots not yet added (marked with placeholders)

### 4. Custom DocTypes

- [x] `Maintenance Portal Settings` DocType created
  - Location: `tub_suite/tub_suite/doctype/maintenance_portal_settings/`
  - Files: `.json`, `.py`, `__init__.py`

### 5. Core Files to Commit

**API Files:**
- [x] `tub_suite/api/asset.py`
- [x] `tub_suite/api/maintenance.py`
- [x] `tub_suite/api/file_utils.py`
- [x] `tub_suite/api/qr_scanner.py`
- [x] `tub_suite/api/asset_repair_config.py`

**Override Files:**
- [x] `tub_suite/overrides/asset_repair_override.py`

**React App Source:**
- [x] `maintenance-react-dev/src/` (all files)
- [x] `maintenance-react-dev/package.json`
- [x] `maintenance-react-dev/vite.config.js`
- [x] `maintenance-react-dev/deploy.sh`
- [x] `maintenance-react-dev/update-hash.sh`

**Built React App:**
- [x] `tub_suite/public/maintenance/` (built files)
- [x] `tub_suite/public/templates/maintenance.html`

**Configuration:**
- [x] `maintenance-react-dev/src/config.js`

### 6. Git Configuration

Check `.gitignore` excludes:
```
# Node modules
maintenance-react-dev/node_modules/
maintenance-react-dev/dist/

# Python cache
__pycache__/
*.pyc
*.pyo

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Environment
.env
*.env.local
```

### 7. Version Check

Current version in `tub_suite/__init__.py`:
```python
__version__ = "0.0.1"
```

Consider updating to reflect new features:
- `"1.0.0"` - First production release with complete documentation
- `"0.1.0"` - Beta with verification workflow
- Keep `"0.0.1"` - Still in development

### 8. Files to EXCLUDE from Commit

**Do NOT commit:**
- `maintenance-react-dev/node_modules/` (huge, auto-installed)
- `maintenance-react-dev/dist/` (build output, redundant)
- `__pycache__/` directories
- `.pyc` files
- Any `.env` files with credentials
- Personal IDE settings

### 9. Test Installation Locally

Before committing, test that app can be installed:

```bash
# In another bench (or after removing app)
cd /home/user/test-bench
bench get-app /home/user/frappe-bench/apps/tub_suite
bench --site test.site install-app tub_suite
bench --site test.site migrate
bench restart
```

Verify:
- [ ] App installs without errors
- [ ] Portal accessible at /maintenance
- [ ] Maintenance Portal Settings DocType exists
- [ ] Workflows registered

### 10. README Update

Ensure main `README.md` has:
- [ ] Installation instructions
- [ ] Link to documentation
- [ ] Basic usage guide
- [ ] Support contact info
- [ ] License information

## Git Commit Commands

### Check What's Changed

```bash
cd /home/user/frappe-bench/apps/tub_suite
git status
git diff
```

### Stage Files

**Option A: Stage All Changes**
```bash
git add .
```

**Option B: Stage Specific Directories**
```bash
# Documentation
git add DOCUMENTATION/

# Source code
git add tub_suite/

# React app
git add maintenance-react-dev/src/
git add maintenance-react-dev/package*.json
git add maintenance-react-dev/*.config.js
git add maintenance-react-dev/*.sh

# Public files (built app)
git add tub_suite/public/

# Root files
git add *.md
git add pyproject.toml
```

### Create Commit

```bash
git commit -m "Add complete maintenance portal with verification workflow and documentation

Features:
- Mobile portal with QR scanning (React 19)
- Asset inspection checklists
- Issue reporting with photos
- Repair approval workflow (Major/Minor severity)
- Reporter verification system (7-day accountability)
- Portal settings configuration (search visibility toggle)
- Role-based access control (Maintenance User, Engineering Team, Manager)

Technical:
- Asset status auto-management on approval/verification
- Custom Asset Repair override with field locking
- Portal Settings DocType for configuration
- Complete API layer for mobile portal
- Workflow state management

Documentation:
- Complete user manuals for all 3 roles
- System architecture and workflow diagrams
- API reference
- Installation guide
- Known issues tracking

🤖 Generated with Claude Code"
```

### Push to Remote

```bash
# First time
git remote add origin https://github.com/YOUR_USERNAME/tub_suite.git
git branch -M main
git push -u origin main

# Subsequent pushes
git push
```

## After Commit - Installation Test

### Test Fresh Installation

On a clean bench:

```bash
bench get-app https://github.com/YOUR_USERNAME/tub_suite.git
bench --site YOUR_SITE install-app tub_suite

# Build React app
cd apps/tub_suite/maintenance-react-dev
npm install
npm run build
bash update-hash.sh

# Restart
cd /home/user/frappe-bench
bench restart
```

### Verify Installation

1. **Check App Installed:**
```bash
bench --site YOUR_SITE list-apps
# Should show: tub_suite
```

2. **Access Portal:**
```
http://YOUR_DOMAIN/maintenance
```

3. **Check Settings:**
```bash
bench --site YOUR_SITE console
```
```python
import frappe
settings = frappe.get_single("Maintenance Portal Settings")
print(settings.as_dict())
exit()
```

## Troubleshooting

### Issue: "Module not found"

**Solution:**
```bash
bench --site YOUR_SITE migrate
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

### Issue: Git push rejected

**Solution:**
```bash
# Pull first, then push
git pull origin main --rebase
git push origin main
```

## Final Checklist Before Push

- [ ] All code tested and working
- [ ] Documentation complete (except screenshots)
- [ ] React app built successfully
- [ ] No console errors
- [ ] No credentials in code
- [ ] `.gitignore` properly configured
- [ ] Commit message descriptive
- [ ] Ready for production use

## Notes

**About Screenshots:**
- Placeholders marked in all manuals
- Can be added later via separate commit
- Does not block functionality

**About Known Issues:**
- Asset status badge issue documented
- Investigation guide provided
- Workarounds available
- Can be fixed in future commit

**About Version:**
- Current: 0.0.1 (development)
- Consider: 1.0.0 (first production release)
- Update `tub_suite/__init__.py` before committing

---

**Ready to Commit:** December 16, 2024
**Prepared By:** TUB Suite Development Team
