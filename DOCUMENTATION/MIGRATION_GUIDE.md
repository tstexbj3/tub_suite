# Migration Guide: v1.0 → v2.0

## Overview

This guide helps you upgrade from TUB Suite v1.0 to v2.0 on existing ERPNext instances.

**Version 2.0 is BACKWARD COMPATIBLE** - All v1.0 features continue to work. New features are additive.

---

## What's New in v2.0

### 1. Reporter Verification Workflow
- **New Feature:** Original reporter must verify completed repairs
- **7-Day Accountability Rule:** Reporter responsible for 7 days after verification
- **New Fields Added:**
  - `requires_inspector_verification` (checkbox)
  - `verified_by` (link to User)
  - `verification_date` (datetime)
  - `verification_notes` (small text)
  - `verification_photos` (attach image)
  - `verified_and_accepts_responsibility` (checkbox)

### 2. Issue Severity System
- **New Field:** `issue_severity` (Select: Major vs Minor)
- **Auto-Status Management:** Major issues set asset to "Out of Order" on approval
- **Smart Restoration:** Asset only restored when ALL Major repairs verified

### 3. Portal Settings
- **New DocType:** `Maintenance Portal Settings`
- **Configurable Search:** Show/hide search function for different roles
- **Production vs Testing Modes**

### 4. Enhanced APIs
- **New Endpoints:**
  - `/api/method/tub_suite.api.maintenance.verify_repair_completion`
  - `/api/method/tub_suite.api.maintenance.get_portal_settings`
  - `/api/method/tub_suite.api.maintenance.update_asset_status`
- **Enhanced Endpoints:**
  - `get_checklist` now includes asset status
  - `report_issue` now requires issue_severity
  - `get_asset_repairs` includes verification data

---

## Migration Steps

### For New Installations (Fresh ERPNext)

```bash
# Standard installation - no migration needed
bench get-app https://github.com/YOUR_REPO/tub_suite.git
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

### For Existing v1.0 Installations (UPGRADE)

#### Step 1: Backup Your Site

```bash
cd /home/user/frappe-bench
bench --site YOUR_SITE backup --with-files
```

**Backup Location:** `sites/YOUR_SITE/private/backups/`

#### Step 2: Pull Latest Code

```bash
cd apps/tub_suite
git fetch origin
git checkout v2.0.0-release
git pull origin v2.0.0-release
```

#### Step 3: Migrate Database

```bash
cd /home/user/frappe-bench
bench --site YOUR_SITE migrate
```

**What `migrate` does:**
1. Adds new custom fields to Asset Repair
2. Creates Maintenance Portal Settings DocType
3. Updates workflow states if needed
4. Applies all fixtures automatically

#### Step 4: Build React App

```bash
cd apps/tub_suite/maintenance-react-dev
npm install  # Update dependencies
npm run build
bash update-hash.sh
```

#### Step 5: Create Portal Settings Document

```bash
# In ERPNext:
# 1. Go to: Maintenance > Maintenance Portal Settings
# 2. Click "New"
# 3. Set "Show Search to All Users" (check/uncheck as needed)
# 4. Save
```

**Or via bench console:**

```bash
bench --site YOUR_SITE console
```

```python
import frappe

# Create default Portal Settings
settings = frappe.new_doc("Maintenance Portal Settings")
settings.show_search_to_all_users = 0  # Production mode (QR only)
settings.insert()
frappe.db.commit()
print("✅ Portal Settings created")
```

#### Step 6: Restart Services

```bash
cd /home/user/frappe-bench
bench restart
```

#### Step 7: Test Migration

**Test Checklist:**

```bash
# 1. Test existing repairs still load
curl -X GET "http://YOUR_SITE/api/method/tub_suite.api.maintenance.get_asset_repairs?asset_name=ASSET-001"

# 2. Test new portal settings
curl -X GET "http://YOUR_SITE/api/method/tub_suite.api.maintenance.get_portal_settings"

# 3. Test new verification endpoint
curl -X POST "http://YOUR_SITE/api/method/tub_suite.api.maintenance.verify_repair_completion" \
  -H "Content-Type: application/json" \
  -d '{"repair_id": "AR-001", "notes": "Test", "photo": ""}'
```

---

## Breaking Changes

### ⚠️ NONE - Fully Backward Compatible

**However, note these BEHAVIOR changes:**

### 1. Issue Reporting Now Requires Severity

**Before (v1.0):**
```python
# Severity was optional or didn't exist
tub_suite.api.maintenance.report_issue(
    asset_name="ASSET-001",
    issue_description="Broken"
)
```

**After (v2.0):**
```python
# Severity is REQUIRED
tub_suite.api.maintenance.report_issue(
    asset_name="ASSET-001",
    issue_description="Broken",
    issue_severity="Major - Asset Must Stop"  # NEW REQUIRED FIELD
)
```

**Migration:** Mobile app MUST be updated to prompt for severity selection.

### 2. Asset Status Auto-Management

**Before (v1.0):**
- Asset status managed manually by managers

**After (v2.0):**
- Major repairs automatically set asset to "Out of Order" on approval
- Asset automatically restored when all Major repairs verified

**Migration:** Inform managers that asset status is now automatic. Manual overrides still possible via Asset DocType directly.

### 3. Workflow State Behavior

**Before (v1.0):**
- Finished state was final

**After (v2.0):**
- Finished repairs may require verification
- New field: `requires_inspector_verification` controls this
- If checked, reporter must verify before truly complete

**Migration:** Existing repairs in "Finished" state are grandfathered (no verification required). Only NEW repairs after v2.0 require verification.

---

## Data Migration Notes

### Existing Asset Repair Records

**All existing repairs are preserved** with these defaults:

| Field | Default Value | Notes |
|-------|---------------|-------|
| `issue_severity` | `NULL` → Set to "Minor - Asset Operational" | Safe default - doesn't change asset status |
| `requires_inspector_verification` | `0` (No) | Existing repairs don't require verification |
| `verified_by` | `NULL` | N/A for old repairs |
| `verification_date` | `NULL` | N/A for old repairs |

### Handling NULL issue_severity

The system treats `NULL` severity as `"Minor - Asset Operational"` for backward compatibility.

**Optional cleanup script:**

```python
import frappe

# Update all NULL severities to Minor
repairs = frappe.get_all("Asset Repair", filters={"issue_severity": ["is", "not set"]})

for repair in repairs:
    doc = frappe.get_doc("Asset Repair", repair.name)
    doc.issue_severity = "Minor - Asset Operational"
    doc.save()
    print(f"✅ Updated {repair.name}")

frappe.db.commit()
print(f"✅ Updated {len(repairs)} repairs")
```

---

## Configuration Changes

### Portal Settings (NEW)

**Required Post-Migration:**

1. Create `Maintenance Portal Settings` document (see Step 5 above)
2. Configure search visibility:
   - **Production:** Uncheck "Show Search to All Users" (QR only)
   - **Testing:** Check to enable search for all roles

### Workflow Updates

**No changes required** - Existing workflow continues to work.

**New workflow states** (optional - for verification):
- Add "Pending Verification" state between "Finished" and final completion
- This is optional - v2.0 works with existing workflow

---

## Rollback Plan

If migration fails, rollback:

### Step 1: Restore Database

```bash
cd /home/user/frappe-bench
bench --site YOUR_SITE --force restore /path/to/backup.sql.gz
```

### Step 2: Revert Code

```bash
cd apps/tub_suite
git checkout v1.0.0  # Or previous version tag
```

### Step 3: Rebuild

```bash
cd maintenance-react-dev
npm run build
bash update-hash.sh
cd /home/user/frappe-bench
bench restart
```

---

## Testing Checklist

After migration, verify:

- [ ] Existing repairs load correctly in ERPNext Desk
- [ ] Mobile portal loads (QR scanner visible)
- [ ] Scan QR code → Checklist loads
- [ ] Report new issue with severity selection
- [ ] Manager can approve new issue
- [ ] Asset status changes on Major issue approval
- [ ] Complete repair as engineer
- [ ] Verify repair as original reporter
- [ ] Asset status restored after verification
- [ ] Portal Settings document exists and works
- [ ] Search function visibility controlled by settings

---

## FAQ

**Q: Do I need to update custom fields manually?**
A: No. `bench migrate` applies all fixtures automatically.

**Q: Will existing repairs require verification?**
A: No. Only NEW repairs created after v2.0 require verification (if enabled).

**Q: Can I disable verification workflow?**
A: Yes. Set `requires_inspector_verification = 0` when creating repairs. This is configurable per-repair.

**Q: What happens to in-progress repairs during migration?**
A: They continue normally. New fields are added but not required for old repairs.

**Q: Do I need to retrain users?**
A: Minimal training needed. Main changes:
  - Engineers: Must select issue severity
  - Maintenance Users: May need to verify completed repairs (new screen)
  - Managers: Asset status now automatic (less manual work)

**Q: Can v1.0 and v2.0 run simultaneously?**
A: No. Each site runs one version. But different sites can run different versions.

---

## Support

**Issues?** Report at: https://github.com/YOUR_REPO/tub_suite/issues

**Migration Support:**
Email: it@tipubon.com
Subject: "TUB Suite v2.0 Migration Support"

---

## Version History

- **v1.0.0** - Initial release (QR scanning, checklist, issue reporting)
- **v2.0.0** - Verification workflow, issue severity, portal settings (this version)

---

**Last Updated:** 2025-12-16
**Tested On:** ERPNext v15 / Frappe v15
