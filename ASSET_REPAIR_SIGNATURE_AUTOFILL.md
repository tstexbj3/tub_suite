# Asset Repair Signature Auto-fill Mechanism

**Last Updated:** 2026-01-26
**Status:** WORKING

---

## Overview

When authorized users sign Asset Repair forms, corresponding date fields are automatically filled with the current timestamp. This is handled by the `before_save_asset_repair()` hook in `asset_repair_override.py`.

---

## Signature Fields and Auto-fill Dates

| Workflow State | Signature Field | Auto-filled Date Field | Notes |
|----------------|-----------------|----------------------|-------|
| Pending GM Approval Section 1 | `custom_gm_signature` | `gm_section1_approval_date` | GM approves Section 1 |
| Pending GM Approval Section 1 | `gm_section1_signature` | `gm_section1_approval_date` | Legacy field (backward compatibility) |
| Pending Engineering Assessment | `engineering_operator_signature` | `engineering_operator_sign_date` | Engineer signs assessment |
| Pending Engineering Supervisor Review | `eng_supervisor_signature` | `eng_supervisor_review_date` | Engineering Supervisor reviews |
| Pending GM Final Approval | `approval_signature` | `gm_final_approval_date` | GM final approval |
| Pending Supervisor Verification | `supervisor_signature` | `supervisor_verification_date` | Supervisor verifies completion |
| Finished | `reporter_signature` | `reporter_confirmation_date` | Reporter confirms via portal |

---

## Implementation Details

### File: `tub_suite/overrides/asset_repair_override.py`

**Function:** `before_save_asset_repair(doc, method)`

**How it Works:**

1. Fetch old document values to compare changes:
   ```python
   old_doc = frappe.db.get_value("Asset Repair", doc.name,
       ["approval_notes", "approval_signature", "approval_timestamp", "issue_severity", "workflow_state",
        "supervisor_section1_signature", "supervisor_section1_date",
        "custom_gm_signature", "gm_section1_signature", "gm_section1_approval_date",
        "engineering_operator_signature", "engineering_operator_sign_date",
        "eng_supervisor_signature", "eng_supervisor_review_date",
        "approval_signature", "gm_final_approval_date",
        "supervisor_signature", "supervisor_verification_date",
        "reporter_signature", "reporter_confirmation_date"], as_dict=True)
   ```

2. Check each signature field - if it has a value now but didn't before, auto-fill the date:
   ```python
   # GM Section 1 - custom_gm_signature (current field)
   if doc.get("custom_gm_signature") and not old_doc.get("custom_gm_signature"):
       if not doc.get("gm_section1_approval_date"):
           doc.gm_section1_approval_date = now()

   # GM Section 1 - gm_section1_signature (legacy field for backward compatibility)
   if doc.get("gm_section1_signature") and not old_doc.get("gm_section1_signature"):
       if not doc.get("gm_section1_approval_date"):
           doc.gm_section1_approval_date = now()

   # Engineering Operator
   if doc.get("engineering_operator_signature") and not old_doc.get("engineering_operator_signature"):
       if not doc.get("engineering_operator_sign_date"):
           doc.engineering_operator_sign_date = now()

   # Engineering Supervisor
   if doc.get("eng_supervisor_signature") and not old_doc.get("eng_supervisor_signature"):
       if not doc.get("eng_supervisor_review_date"):
           doc.eng_supervisor_review_date = now()

   # GM Final Approval
   if doc.get("approval_signature") and not old_doc.get("approval_signature"):
       if not doc.get("gm_final_approval_date"):
           doc.gm_final_approval_date = now()

   # Supervisor Verification
   if doc.get("supervisor_signature") and not old_doc.get("supervisor_signature"):
       if not doc.get("supervisor_verification_date"):
           doc.supervisor_verification_date = now()

   # Reporter Confirmation
   if doc.get("reporter_signature") and not old_doc.get("reporter_signature"):
       if not doc.get("reporter_confirmation_date"):
           doc.reporter_confirmation_date = now()
   ```

---

## Print Format Integration

The FM-EN-04 print format displays these signatures and dates:

**Section 1C - GM Approval Section 1:**
```html
<!-- Line 248 -->
<img src="{{ doc.custom_gm_signature }}" style="max-height:30px;">

<!-- Line 255 -->
วันที่: {{ frappe.utils.formatdate(doc.gm_section1_approval_date, "dd/MM/yyyy") if doc.gm_section1_approval_date else "___/___/___" }}
```

**Section 2C - GM Final Approval:**
```html
<!-- Line 355 -->
<img src="{{ doc.approval_signature }}" style="max-height:30px;">

<!-- Line 358 -->
วันที่: {{ frappe.utils.formatdate(doc.gm_final_approval_date, "dd/MM/yyyy") if doc.gm_final_approval_date else "___/___/___" }}
```

---

## Common Issues and Fixes

### Issue 1: Signature shows but date is blank

**Symptom:** Signature image appears in print format but date shows "___/___/___"

**Root Cause:** Signature field name mismatch between form and auto-fill logic

**Example:** Document uses `custom_gm_signature` but auto-fill code only checks `gm_section1_signature`

**Fix:** Update auto-fill logic to check both fields:
```python
# Check for custom_gm_signature (newer field)
if doc.get("custom_gm_signature") and not old_doc.get("custom_gm_signature"):
    if not doc.get("gm_section1_approval_date"):
        doc.gm_section1_approval_date = now()

# Check for gm_section1_signature (legacy field)
if doc.get("gm_section1_signature") and not old_doc.get("gm_section1_signature"):
    if not doc.get("gm_section1_approval_date"):
        doc.gm_section1_approval_date = now()
```

### Issue 2: Wrong date field being set

**Symptom:** Date field remains blank even though signature is filled

**Root Cause:** Auto-fill code sets wrong date field name

**Example:** Code sets `manager_approval_date` but print format uses `gm_final_approval_date`

**Fix:** Update auto-fill logic to use correct field name:
```python
# BEFORE (WRONG)
if doc.get("approval_signature") and not old_doc.get("approval_signature"):
    if not doc.get("manager_approval_date"):
        doc.manager_approval_date = now()

# AFTER (CORRECT)
if doc.get("approval_signature") and not old_doc.get("approval_signature"):
    if not doc.get("gm_final_approval_date"):
        doc.gm_final_approval_date = now()
```

### Issue 3: Missing field in old_doc fetch

**Symptom:** Auto-fill doesn't trigger even when signature changes

**Root Cause:** Signature field not included in `old_doc` fetch list, so comparison always fails

**Fix:** Add missing field to fetch list:
```python
old_doc = frappe.db.get_value("Asset Repair", doc.name,
    [..., "custom_gm_signature", ...], as_dict=True)
```

---

## Testing Checklist

**Before committing auto-fill changes:**

- [ ] Test GM Section 1 signature - verify `gm_section1_approval_date` auto-fills
- [ ] Test Engineering signature - verify `engineering_operator_sign_date` auto-fills
- [ ] Test Engineering Supervisor signature - verify `eng_supervisor_review_date` auto-fills
- [ ] Test GM Final signature - verify `gm_final_approval_date` auto-fills
- [ ] Test Supervisor signature - verify `supervisor_verification_date` auto-fills
- [ ] Test Reporter signature - verify `reporter_confirmation_date` auto-fills
- [ ] Test print format FM-EN-04 - all signatures and dates should display correctly
- [ ] Test backward compatibility - old documents with `gm_section1_signature` should still work

---

## Debugging Tips

### Check if signature field has value:
```python
import frappe
doc = frappe.get_doc("Asset Repair", "ACC-ASR-2026-00031")
print("custom_gm_signature:", doc.custom_gm_signature)
print("gm_section1_approval_date:", doc.gm_section1_approval_date)
print("approval_signature:", doc.approval_signature)
print("gm_final_approval_date:", doc.gm_final_approval_date)
```

### Check which fields are in old_doc fetch:
```bash
cd ~/frappe-bench/apps/tub_suite
grep -A 10 "old_doc = frappe.db.get_value" tub_suite/overrides/asset_repair_override.py
```

### Check print format field references:
```bash
cd ~/frappe-bench/apps/tub_suite
grep "gm.*approval.*date" FM_EN_04_PRINT_FORMAT.html
```

---

## Version History

| Date | Changes | By |
|------|---------|-----|
| 2026-01-26 | Fixed custom_gm_signature auto-fill for gm_section1_approval_date | Claude |
| 2026-01-26 | Fixed approval_signature auto-fill to use gm_final_approval_date instead of manager_approval_date | Claude |
| 2026-01-26 | Added custom_gm_signature to old_doc fetch list | Claude |
| 2026-01-26 | Updated print format to use gm_final_approval_date | Claude |

---

**END OF DOCUMENTATION**
