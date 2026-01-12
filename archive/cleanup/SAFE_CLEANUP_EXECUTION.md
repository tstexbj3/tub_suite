# SAFE Cleanup Execution Plan

**Date:** 2026-01-08
**CRITICAL:** Only touch CUSTOM fields, NEVER delete original ERPNext fields

---

## ⚠️ GOLDEN RULES

1. **NEVER DELETE** fields from original `asset_repair.json`
2. **ONLY DELETE** fields from `tub_suite/fixtures/custom_field.json`
3. **HIDE** original ERPNext fields we don't use (not delete)
4. **TEST on local** before any production deployment
5. **BACKUP DATABASE** before any changes

---

## 📋 ORIGINAL ERPNEXT FIELDS (DO NOT TOUCH)

These are from `erpnext/assets/doctype/asset_repair/asset_repair.json`:

```
✋ NEVER DELETE THESE:
- asset (Link to Asset)
- asset_name (Read Only)
- company (Link to Company)
- naming_series (ACC-ASR-.YYYY.-)
- failure_date (Datetime) ✅ WE USE THIS
- completion_date (Datetime) ✅ WE USE THIS
- repair_status (Select: Pending/Completed/Cancelled) ✅ WE USE THIS
- description (Long Text) ✅ WE USE THIS (Error Description)
- actions_performed (Long Text) ✅ WE USE THIS
- downtime (Data)
- repair_cost (Currency)
- capitalize_repair_cost (Check)
- stock_consumption (Check)
- stock_items (Table: Asset Repair Consumed Item) ⚠️ Different from our spare_parts_used
- total_repair_cost (Currency)
- increase_in_asset_life (Int)
- purchase_invoice (Link)
- cost_center (Link)
- project (Link)
- amended_from (Link)

STRATEGY FOR UNUSED ORIGINAL FIELDS:
→ HIDE them with custom field property setters (NOT delete)
```

---

## 🗑️ CUSTOM FIELDS TO DELETE (Safe to remove)

These are in `tub_suite/fixtures/custom_field.json`:

### DELETE NOW:

```python
fields_to_delete = [
    "Asset Repair-custom_สาเหตุ",           # Old cause field
    "Asset Repair-custom_ระบุสาเหตุ",      # Old specify cause
    "Asset Repair-custom_ใบส่งของเลขที่",  # Unknown delivery field
]
```

### REPLACE (Delete after data migration):

```python
fields_to_replace = [
    "Asset Repair-custom_repair_type"  # Replace with new "repair_type"
]
```

### KEEP ALL OTHERS:

```python
fields_to_keep = [
    "Asset Repair-reported_by",                    # ✅ Portal uses
    "Asset Repair-workflow_state",                 # ✅ Core workflow
    "Asset Repair-expected_completion_date",       # ✅ Keep
    "Asset Repair-issue_severity",                 # ✅ Major/Minor
    "Asset Repair-verification_section",           # ✅ Section break
    "Asset Repair-requires_inspector_verification",# ✅ Keep
    "Asset Repair-verified_by",                    # ✅ Phase 8
    "Asset Repair-verification_date",              # ✅ Phase 8
    "Asset Repair-verification_notes",             # ✅ Phase 8
    "Asset Repair-verification_status",            # ✅ Phase 8
    "Asset Repair-custom_ฝ่ายวิศวกรรม",            # ✅ Engineering section
    "Asset Repair-custom_การดำเนินการ",           # ⚠️ Check if needed
    "Asset Repair-engineer_signature",             # ✅ Keep
    "Asset Repair-approved_by",                    # ✅ Keep
    "Asset Repair-approval_time",                  # ✅ Keep
    "Asset Repair-approval_section",               # ✅ Keep
    "Asset Repair-approval_notes",                 # ✅ Keep
    "Asset Repair-approval_signature",             # ✅ Keep
    "Asset Repair-approval_timestamp",             # ✅ Keep
]
```

---

## 🔍 INVESTIGATE: `custom_การดำเนินการ` Table

**Current settings:**
- Fieldtype: Table
- Options: "Asset Repair Engineering Detail"

**User confirmed:** "Asset Repair Engineering Detail" child doctype does NOT exist

**Action:**
- ❌ DELETE this field (it's broken - points to non-existent doctype)
- ✅ REPLACE with new `engineering_todo_items` table

```python
# Add to delete list
fields_to_delete.append("Asset Repair-custom_การดำเนินการ")
```

---

## 📝 FIELDS TO HIDE (Original ERPNext fields we don't use)

Use Property Setter to hide without deleting:

```python
# Hide unused original ERPNext fields
fields_to_hide = [
    "repair_cost",              # We don't track cost in Section 1-3
    "capitalize_repair_cost",   # Accounting feature we don't use
    "stock_consumption",        # We use spare_parts_used instead
    "stock_items",              # We use spare_parts_used table
    "total_repair_cost",        # Don't track
    "increase_in_asset_life",   # Don't use
    "purchase_invoice",         # Don't link to PI
    "cost_center",              # Don't use accounting dimensions
    "project",                  # Don't link to projects
    "downtime",                 # We calculate differently
]

# Create Property Setters
for fieldname in fields_to_hide:
    frappe.make_property_setter({
        "doctype": "Asset Repair",
        "fieldname": fieldname,
        "property": "hidden",
        "value": 1,
        "property_type": "Check"
    })
```

---

## 🔄 STEP-BY-STEP EXECUTION

### STEP 1: Backup (CRITICAL)

```bash
# Backup entire database
cd /home/user/frappe-bench
bench --site tub backup --with-files

# Verify backup created
ls -lh sites/tub/private/backups/
```

### STEP 2: Check Field Usage

```python
# Open bench console
cd /home/user/frappe-bench
bench --site tub console

# Check what data exists in fields we're deleting
import frappe

# Check custom_repair_type
print("\n=== custom_repair_type usage ===")
data = frappe.db.sql("""
    SELECT custom_repair_type, COUNT(*) as count
    FROM `tabAsset Repair`
    WHERE custom_repair_type IS NOT NULL
    GROUP BY custom_repair_type
""", as_dict=True)
for row in data:
    print(f"{row.custom_repair_type}: {row.count} repairs")

# Check custom_สาเหตุ
print("\n=== custom_สาเหตุ usage ===")
count = frappe.db.count("Asset Repair", {"custom_สาเหตุ": ["!=", ""]})
print(f"Repairs with สาเหตุ: {count}")

# Check custom_ใบส่งของเลขที่
print("\n=== custom_ใบส่งของเลขที่ usage ===")
count = frappe.db.count("Asset Repair", {"custom_ใบส่งของเลขที่": ["!=", ""]})
print(f"Repairs with ใบส่งของเลขที่: {count}")

# Check custom_การดำเนินการ table
print("\n=== custom_การดำเนินการ usage ===")
# This will likely error if child doctype doesn't exist
try:
    count = frappe.db.count("Asset Repair Engineering Detail")
    print(f"Engineering Detail records: {count}")
except Exception as e:
    print(f"ERROR (expected): {e}")
    print("Child doctype does NOT exist - safe to delete field")
```

**EXPECTED OUTPUT:**
```
=== custom_repair_type usage ===
ซ่อม: 45 repairs
แก้ไข: 12 repairs
ติดตั้งใหม่: 3 repairs
ปรับปรุง: 1 repair

=== custom_สาเหตุ usage ===
Repairs with สาเหตุ: 0

=== custom_ใบส่งของเลขที่ usage ===
Repairs with ใบส่งของเลขที่: 0

=== custom_การดำเนินการ usage ===
ERROR: Table 'tabAsset Repair Engineering Detail' doesn't exist
Child doctype does NOT exist - safe to delete field
```

### STEP 3: Edit custom_field.json (MANUAL - Safest)

**Open file:**
```bash
code /home/user/frappe-bench/apps/tub_suite/tub_suite/fixtures/custom_field.json
```

**Find and DELETE these field blocks** (search for fieldname):

1. Search for `"fieldname": "custom_สาเหตุ"` → Delete entire block (from opening `{` to closing `}`)
2. Search for `"fieldname": "custom_ระบุสาเหตุ"` → Delete entire block
3. Search for `"fieldname": "custom_ใบส่งของเลขที่"` → Delete entire block
4. Search for `"fieldname": "custom_การดำเนินการ"` → Delete entire block

**DO NOT delete:**
- Any field starting with just letters (no "custom_" prefix) - these might be references
- Any field you're unsure about

**Save file**

### STEP 4: Add New `repair_type` Field (Before deleting old one)

**Edit:** `tub_suite/fixtures/asset_repair_fm_en_04_fields.json`

Find the `repair_type` field and UPDATE it:

```json
{
  "fieldname": "repair_type",
  "fieldtype": "Select",
  "label": "ประเภทการดำเนินการ (Repair Type)",
  "options": "ซ่อม/แก้ไข\nติดตั้งใหม่/ปรับปรุง",
  "insert_after": "fm_en_04_section_0",
  "reqd": 0,  // NOT required yet (allow existing repairs to work)
  "dt": "Asset Repair",
  "doctype": "Custom Field"
  // ... all other properties
}
```

### STEP 5: Run Migration

```bash
cd /home/user/frappe-bench
bench --site tub migrate
bench --site tub clear-cache
```

**Check for errors:**
- If migration succeeds → Good!
- If errors about missing child doctype → Expected (we're removing broken field)
- If errors about other things → STOP and investigate

### STEP 6: Migrate Data (custom_repair_type → repair_type)

```python
# bench console
import frappe

# Copy data from old to new field
frappe.db.sql("""
    UPDATE `tabAsset Repair`
    SET repair_type = CASE
        WHEN custom_repair_type IN ('ซ่อม', 'แก้ไข') THEN 'ซ่อม/แก้ไข'
        WHEN custom_repair_type IN ('ติดตั้งใหม่', 'ปรับปรุง') THEN 'ติดตั้งใหม่/ปรับปรุง'
        WHEN custom_repair_type = 'อื่นๆ' THEN 'ซ่อม/แก้ไข'
        ELSE 'ซ่อม/แก้ไข'
    END
    WHERE (repair_type IS NULL OR repair_type = '')
      AND custom_repair_type IS NOT NULL
""")
frappe.db.commit()

# Verify migration
print("\n=== Verification ===")
data = frappe.db.sql("""
    SELECT
        custom_repair_type as old,
        repair_type as new,
        COUNT(*) as count
    FROM `tabAsset Repair`
    GROUP BY custom_repair_type, repair_type
""", as_dict=True)

for row in data:
    print(f"{row.old} → {row.new}: {row.count} repairs")

# Check for any unmapped
unmapped = frappe.db.sql("""
    SELECT COUNT(*) as count
    FROM `tabAsset Repair`
    WHERE (repair_type IS NULL OR repair_type = '')
""", as_dict=True)[0]

if unmapped.count > 0:
    print(f"\n⚠️  WARNING: {unmapped.count} repairs have no repair_type!")
else:
    print("\n✅ All repairs migrated successfully")
```

### STEP 7: Test Existing Repairs

```bash
# Open ERPNext
# Go to Asset Repair list
# Open a few existing repairs
# Check:
# - repair_type shows correct value ✅
# - No errors loading document ✅
# - All sections visible ✅
```

### STEP 8: Delete `custom_repair_type` Field

**Only after confirming Step 7 works!**

**Edit:** `tub_suite/fixtures/custom_field.json`

Search for `"fieldname": "custom_repair_type"` → Delete entire block

### STEP 9: Final Migration

```bash
bench --site tub migrate
bench --site tub clear-cache
bench restart
```

### STEP 10: Hide Unused Original Fields

```python
# bench console
import frappe

fields_to_hide = [
    "repair_cost",
    "capitalize_repair_cost",
    "stock_consumption",
    "stock_items",
    "total_repair_cost",
    "increase_in_asset_life",
    "purchase_invoice",
    "cost_center",
    "project",
    "downtime"
]

for fieldname in fields_to_hide:
    # Check if property setter already exists
    exists = frappe.db.exists("Property Setter", {
        "doctype_or_field": "DocField",
        "doc_type": "Asset Repair",
        "field_name": fieldname,
        "property": "hidden"
    })

    if not exists:
        ps = frappe.get_doc({
            "doctype": "Property Setter",
            "doctype_or_field": "DocField",
            "doc_type": "Asset Repair",
            "field_name": fieldname,
            "property": "hidden",
            "value": "1",
            "property_type": "Check"
        })
        ps.insert()
        print(f"✅ Hidden: {fieldname}")
    else:
        print(f"⏭️  Already hidden: {fieldname}")

frappe.db.commit()
print("\n✅ All original ERPNext fields hidden successfully")
```

### STEP 11: Final Verification

**Test checklist:**
- [ ] Open existing Asset Repair → No errors
- [ ] `repair_type` field visible and populated
- [ ] Hidden ERPNext fields not visible
- [ ] Deleted custom fields (`custom_สาเหตุ`, etc.) not visible
- [ ] Create new Asset Repair → Works
- [ ] Portal still works → No errors
- [ ] Workflow transitions work
- [ ] Print format works

---

## 🚨 ROLLBACK PROCEDURE

If something breaks:

### Option 1: Restore Database Backup

```bash
cd /home/user/frappe-bench

# List backups
ls -lh sites/tub/private/backups/

# Restore (replace with your backup filename)
bench --site tub restore sites/tub/private/backups/20260108_backup.sql.gz
```

### Option 2: Git Revert

```bash
cd /home/user/frappe-bench/apps/tub_suite

# Revert custom_field.json changes
git checkout HEAD -- tub_suite/fixtures/custom_field.json

# Run migrate to restore fields
cd /home/user/frappe-bench
bench --site tub migrate
```

### Option 3: Manual Re-add Fields

If you need to restore deleted fields, re-add them to `custom_field.json` and run `bench migrate`.

---

## 📋 CLEANUP SUMMARY

### DELETED (Safe - Custom fields only):
- `custom_สาเหตุ` ✅
- `custom_ระบุสาเหตุ` ✅
- `custom_ใบส่งของเลขที่` ✅
- `custom_การดำเนินการ` ✅ (broken, points to non-existent doctype)
- `custom_repair_type` ✅ (after data migration)

### HIDDEN (Original ERPNext fields):
- `repair_cost`, `stock_consumption`, `stock_items`, etc. ✅

### KEPT (Custom fields still in use):
- All verification fields ✅
- All approval fields ✅
- `reported_by`, `issue_severity`, etc. ✅

### ADDED (New):
- `repair_type` (replaces `custom_repair_type`) ✅

---

## ✅ SUCCESS CRITERIA

After cleanup:
- ✅ Zero errors in bench logs
- ✅ Existing repairs load without issues
- ✅ New repairs can be created
- ✅ Portal works (can scan QR, submit tasks)
- ✅ Workflow transitions work
- ✅ Data preserved (no repairs lost)

---

**NEXT STEP:** After cleanup succeeds, proceed with adding remaining FM-EN-04 fields (Sections 1, 2, 3)

**DO NOT PROCEED** with Phase 2 (workflow changes) until cleanup is confirmed working!
