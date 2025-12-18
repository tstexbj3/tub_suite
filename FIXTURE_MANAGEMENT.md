# Custom Field & Fixture Management Guide

**Purpose:** Ensure custom fields stay aligned across development, staging, and production environments.

---

## 📋 Current Custom Fields (v2.1.0)

### Asset Repair Custom Fields (25 fields)

**Core Repair Fields:**
- `reported_by` - Inspector who reported issue
- `maintenance_task` - Links to maintenance task
- `expected_completion_date` - When engineer expects to finish
- `issue_severity` - "Major" or "Minor"
- `engineer_signature` - Engineer's signature (required)

**Verification Fields:**
- `requires_inspector_verification` - Enable verification workflow
- `verification_status` - "Pending Verification", "Verified - Passed", "Verified - Failed"
- `verified_by` - Inspector who verified
- `verification_date` - When verified
- `verification_notes` - Inspector's verification notes
- `verification_photo_1`, `verification_photo_2`, `verification_photo_3` - Verification photos

**Manager Approval Fields:**
- `approval_notes` - Manager's approval/rejection notes (required in v2.1.0)
- `approval_signature` - Manager's signature (required in v2.1.0)
- `approval_timestamp` - Auto-filled when manager signs

**Thai Custom Fields:**
- `custom_สาเหต` - Cause (Thai)
- `custom_ฝายวศวกรรม` - Engineering section (Thai)
- `custom_การดำเนนการ` - Engineering actions table (Thai)

---

## 🔧 How to Export Fixtures (When Making Changes)

### Export from Production (Clean Source)

```bash
# SSH to production
ssh taynaja@tub.x-desk.tech

# Run export script
bench --site tub.x-desk.tech console
```

```python
import frappe
import json
from frappe.utils import get_bench_path
import os

# Export Asset Repair custom fields
custom_fields = frappe.get_all("Custom Field",
    filters={"dt": "Asset Repair"},
    fields=["*"],
    order_by="idx")

fixtures = []
for cf in custom_fields:
    doc = frappe.get_doc("Custom Field", cf.name)
    fixture = doc.as_dict()

    # Remove fields that shouldn't be in fixtures
    remove_fields = [
        "modified", "modified_by", "creation", "owner",
        "docstatus", "idx", "_user_tags", "_comments",
        "_assign", "_liked_by"
    ]
    for field in remove_fields:
        fixture.pop(field, None)

    fixtures.append(fixture)

# Save to tmp
output_path = "/tmp/custom_field_asset_repair.json"
with open(output_path, "w") as f:
    json.dump(fixtures, f, indent=1, default=str, ensure_ascii=False)

print(f"✅ Exported {len(fixtures)} custom fields")
print(f"📁 File: {output_path}")
print("\nNext: Copy this to apps/tub_suite/tub_suite/fixtures/")

exit()
```

### Copy to Development

```bash
# From your local machine
scp taynaja@tub.x-desk.tech:/tmp/custom_field_asset_repair.json \
    ~/frappe-bench/apps/tub_suite/tub_suite/fixtures/

# Or on Windows with WSL
scp taynaja@tub.x-desk.tech:/tmp/custom_field_asset_repair.json \
    /mnt/c/Users/YourUser/Downloads/
```

---

## 📦 How to Update Fixtures in App

### Method 1: Replace Fixture File

```bash
# On development machine
cd ~/frappe-bench/apps/tub_suite

# Backup old fixture
cp tub_suite/fixtures/custom_field.json tub_suite/fixtures/custom_field.json.backup

# Replace with new export
cp /path/to/custom_field_asset_repair.json tub_suite/fixtures/custom_field.json

# Commit to git
git add tub_suite/fixtures/custom_field.json
git commit -m "chore: Update Asset Repair custom field fixtures from production"
git push origin v2.1.0
```

### Method 2: Use Frappe Export Fixtures Command

```bash
# On development (if you have matching fields)
cd ~/frappe-bench

# Export using built-in command
bench --site YOUR_SITE export-fixtures
```

But this requires `export_fixtures` in hooks.py:

```python
# In tub_suite/hooks.py
export_fixtures = [
    {
        "dt": "Custom Field",
        "filters": [["dt", "=", "Asset Repair"]]
    }
]
```

---

## 🚀 How to Apply Fixtures on New Sites

### Automatic (During Migration)

Fixtures auto-install when you run:

```bash
bench --site SITE_NAME migrate
```

### Manual (Force Install)

```bash
# Force reinstall all fixtures
bench --site SITE_NAME install-app tub_suite --force

# Or install specific fixture
bench --site SITE_NAME execute frappe.modules.utils.sync_fixtures
```

---

## ⚠️ Common Issues & Solutions

### Issue 1: Duplicate Custom Fields

**Cause:** Old custom fields not deleted before installing new ones

**Solution:**
```python
# Delete old custom fields first
import frappe

old_fields = [
    "custom_approval_status",
    "custom_approved_by",
    "custom_signature",
    "custom_approval_date",
    "custom_approval_note",
    "custom_repair_type"
]

for fieldname in old_fields:
    try:
        cf = frappe.get_doc("Custom Field", {"dt": "Asset Repair", "fieldname": fieldname})
        cf.delete()
    except:
        pass

frappe.db.commit()
```

### Issue 2: Custom Fields Not Appearing

**Cause:** Fixtures not synced or cache not cleared

**Solution:**
```bash
# Clear cache
bench --site SITE_NAME clear-cache

# Reinstall fixtures
bench --site SITE_NAME install-app tub_suite --force

# Restart
bench restart
```

### Issue 3: Field Order Wrong

**Cause:** `idx` field determines order, but it's removed in fixtures

**Solution:**
Manually set `insert_after` in fixture:

```json
{
  "fieldname": "approval_notes",
  "insert_after": "engineer_signature",
  ...
}
```

---

## 📝 Best Practices

### 1. **Single Source of Truth**

Always export fixtures from **production** after making changes there, not from dev.

### 2. **Version Control**

Commit fixture changes with meaningful messages:

```bash
git add tub_suite/fixtures/
git commit -m "feat: Add verification_status field to Asset Repair"
```

### 3. **Test on Staging First**

Before deploying to production:
1. Pull latest code on staging
2. Run `bench migrate`
3. Verify custom fields appear correctly
4. Test workflows
5. Then deploy to production

### 4. **Document Changes**

Update this file whenever you:
- Add new custom fields
- Remove custom fields
- Change field properties

### 5. **Clean Up Old Fields**

Before exporting fixtures, delete deprecated fields to avoid carrying forward unused fields.

---

## 🔄 Migration Strategy

### For Existing Sites (with old fields)

1. **Before deployment:**
   ```bash
   # Delete old duplicate fields
   bench --site SITE execute tub_suite.migrations.cleanup_old_custom_fields
   ```

2. **Deploy new code:**
   ```bash
   git pull
   bench migrate
   ```

3. **Verify:**
   ```bash
   bench --site SITE console
   ```
   ```python
   fields = frappe.get_all("Custom Field", filters={"dt": "Asset Repair"}, fields=["fieldname"])
   print(f"Total fields: {len(fields)}")
   ```

### For New Sites (fresh install)

Just run:
```bash
bench new-site NEW_SITE
bench --site NEW_SITE install-app tub_suite
```

Fixtures auto-install during app installation.

---

## 📊 Current v2.1.0 Field Count

| DocType | Expected Count | Current Production |
|---------|---------------|-------------------|
| Asset Repair | 25 | ✅ 25 |
| Other DocTypes | - | - |

---

## 🛠️ Maintenance Commands

### Export All Fixtures

```bash
bench --site SITE_NAME export-fixtures
```

### Import Specific Fixture

```bash
bench --site SITE_NAME import-doc path/to/fixture.json
```

### List All Custom Fields

```bash
bench --site SITE_NAME console
```
```python
import frappe
fields = frappe.get_all("Custom Field",
    filters={"dt": "Asset Repair"},
    fields=["fieldname", "label", "fieldtype"],
    order_by="idx")
for f in fields:
    print(f"{f.fieldname:40} {f.fieldtype:20} {f.label}")
```

---

**Last Updated:** 2025-12-18
**Version:** v2.1.0
**Maintained By:** TUB Suite Development Team
