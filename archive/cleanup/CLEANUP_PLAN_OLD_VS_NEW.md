# Cleanup Plan: Old vs New Fields & Settings

**Date:** 2026-01-08
**Purpose:** Remove/replace conflicting old fields before implementing new FM-EN-04 structure

---

## 🔍 AUDIT RESULTS

### Current Asset Repair Custom Fields (23 total):

```
1. reported_by ✅ KEEP (used in portal)
2. workflow_state ✅ KEEP (core workflow)
3. expected_completion_date ✅ KEEP
4. issue_severity ✅ KEEP (Major/Minor)
5. custom_repair_type ⚠️ REPLACE with new "repair_type"
6. custom_สาเหตุ ❌ DELETE (old cause field, not in FM-EN-04)
7. custom_ระบุสาเหตุ ❌ DELETE (old cause specify field)
8. verification_section ✅ KEEP (section break)
9. requires_inspector_verification ✅ KEEP
10. verified_by ✅ KEEP (Phase 8 uses this)
11. custom_ใบส่งของเลขที่ ❓ UNKNOWN - What is this?
12. verification_date ✅ KEEP (Phase 8)
13. verification_notes ✅ KEEP (Phase 8)
14. verification_status ✅ KEEP (Phase 8)
15. custom_ฝ่ายวิศวกรรม ✅ KEEP (Engineering section break)
16. custom_การดำเนินการ ⚠️ CHECK if same as engineering_todo_items
17. engineer_signature ✅ KEEP
18. approved_by ✅ KEEP
19. approval_time ✅ KEEP
20. approval_section ✅ KEEP
21. approval_notes ✅ KEEP
22. approval_signature ✅ KEEP
23. approval_timestamp ✅ KEEP
```

### Current Workflow States (6 total):

```
1. Draft (ร่าง) - allow_edit: All ✅ KEEP
2. Pending Approval (รออนุมัติ) - allow_edit: All ⚠️ MODIFY
3. Approved (อนุมัติ) - allow_edit: All ✅ KEEP
4. Rejected (ไม่อนุมัติ) - allow_edit: All ✅ KEEP
5. Cancelled (ยกเลิก) - allow_edit: All ✅ KEEP
6. Finished - allow_edit: All ⚠️ CHANGE to "No One"
```

---

## 🗑️ FIELDS TO DELETE

### 1. `custom_สาเหตุ` (Cause category)
**Reason:** Not in FM-EN-04 form
**Action:** Delete from custom_field.json
**Impact:** Low - not used in current portal

### 2. `custom_ระบุสาเหตุ` (Specify cause)
**Reason:** Not in FM-EN-04 form
**Action:** Delete from custom_field.json
**Impact:** Low - not used in current portal

### 3. `custom_ใบส่งของเลขที่`
**Question:** What is this field? Delivery note number?
**Action:** ⚠️ **USER MUST CONFIRM** - Delete or keep?

---

## 🔄 FIELDS TO REPLACE

### 1. `custom_repair_type` → `repair_type`

**Old Field:**
```json
{
  "fieldname": "custom_repair_type",
  "fieldtype": "Select",
  "label": "Repair Type",
  "options": "ซ่อม\nแก้ไข\nติดตั้งใหม่\nปรับปรุง\nอื่นๆ",
  "insert_after": "repair_status"
}
```

**New Field:**
```json
{
  "fieldname": "repair_type",
  "fieldtype": "Select",
  "label": "ประเภทการดำเนินการ",
  "options": "ซ่อม/แก้ไข\nติดตั้งใหม่/ปรับปรุง",
  "insert_after": "fm_en_04_section_0",
  "reqd": 1
}
```

**Changes:**
- ❌ Remove "อื่นๆ" option
- ✅ Combine "ซ่อม" and "แก้ไข" into one option
- ✅ Combine "ติดตั้งใหม่" and "ปรับปรุง" into one option
- ✅ Move to Section 0 (top of form)
- ✅ Make required

**Migration Script Needed:**
```python
# Map old values to new
frappe.db.sql("""
  UPDATE `tabAsset Repair`
  SET repair_type = CASE
    WHEN custom_repair_type IN ('ซ่อม', 'แก้ไข') THEN 'ซ่อม/แก้ไข'
    WHEN custom_repair_type IN ('ติดตั้งใหม่', 'ปรับปรุง') THEN 'ติดตั้งใหม่/ปรับปรุง'
    WHEN custom_repair_type = 'อื่นๆ' THEN 'ซ่อม/แก้ไข'
    ELSE 'ซ่อม/แก้ไข'
  END
""")
```

---

## ❓ FIELDS TO INVESTIGATE

### `custom_การดำเนินการ` (Engineering Todo Table)

**Current Settings:**
- Fieldtype: Table
- Options: "Asset Repair Engineering Detail"
- Label: "การดำเนินการ"

**Question:** Is "Asset Repair Engineering Detail" the same as our new "Engineering Todo Item"?

**Action Required:** Check if child doctype "Asset Repair Engineering Detail" exists

**If EXISTS:**
- Compare field structure
- If SAME → Keep and rename to `engineering_todo_items`
- If DIFFERENT → Replace with new child doctype

**If NOT EXISTS:**
- Error in fixtures - field points to non-existent doctype
- Replace with new `Engineering Todo Item` child doctype

---

## 🔧 WORKFLOW TO MODIFY

### Current Issues:

1. **"Pending Approval" → needs split**
   - Currently: Reporter → Manager
   - Should be: Reporter → Reporter's Supervisor → Manager

2. **"Finished" allows editing**
   - Currently: `allow_edit: "All"`
   - Should be: `allow_edit: "No One"`

### New Workflow States Needed:

```
Add AFTER Draft:
- "Pending Reporter's Supervisor Approval" (รอหัวหน้าแผนกผู้แจ้งอนุมัติ)

Rename existing:
- "Pending Approval" → "Pending Manager Approval - Section 1"

Add NEW states:
- "Pending Engineering Assessment" (รอช่างประเมิน)
- "Pending Engineering Supervisor Review" (รอหัวหน้าช่างตรวจสอบ)
- "Pending Manager Final Approval" (รอ Manager อนุมัติสุดท้าย)
- "Approved for Repair" (อนุมัติให้ซ่อม)
- "Repair In Progress" (กำลังซ่อม)
- "Pending Reporter's Supervisor Verification" (รอหัวหน้าแผนกตรวจสอบ)
- "Pending Reporter Confirmation" (รอผู้แจ้งยืนยัน)

Keep existing:
- "Finished" ✅ (but change allow_edit to "No One")
- "Rejected" ✅
- "Cancelled" ✅
```

---

## 📋 CORRECTED WORKFLOW (WITH SUPERVISOR STEP)

### Complete Flow:

```
1. Draft (ร่าง)
   ↓ Operator fills form on portal + submits

1.5 Pending Reporter's Supervisor Approval (รอหัวหน้าแผนกผู้แจ้งอนุมัติ) ← NEW
   ↓ Reporter's Supervisor reviews Section 1 + can add notes + signs

2. Pending Manager Approval - Section 1 (รอ Manager อนุมัติ)
   ↓ Maintenance Manager: Approve/Reject

3. Pending Engineering Assessment (รอช่างประเมิน)
   ↓ Engineering Operator fills Section 2

4. Pending Engineering Supervisor Review (รอหัวหน้าช่างตรวจสอบ)
   ↓ Engineering Supervisor reviews + signs

5. Pending Manager Final Approval (รอ Manager อนุมัติสุดท้าย)
   ↓ Maintenance Manager: Approve to start repair

6. Approved for Repair (อนุมัติให้ซ่อม)
   ↓ Repair work begins

7. Repair In Progress (กำลังซ่อม)
   ↓ Engineering Supervisor marks complete

8. Pending Reporter's Supervisor Verification (รอหัวหน้าแผนกตรวจสอบ)
   ↓ Reporter's Supervisor fills Section 3 (hygiene checklist)

9. Pending Reporter Confirmation (รอผู้แจ้งยืนยัน)
   ↓ Original Reporter confirms on portal (Phase 8)

10. Finished (เสร็จสมบูรณ์)
    [LOCKED - No one can edit]
```

### Section Locking Updates:

| Section | Locked After State | Editable By Before Lock |
|---------|-------------------|-------------------------|
| Section 1 | Reporter's Supervisor Approval (State 1.5) | Operator (Draft), Reporter's Supervisor (can add notes) |
| Section 2 | Manager Final Approval (State 5) | Engineering Operator, Engineering Supervisor |
| Section 3 | Reporter Confirmation (State 9) | Reporter's Supervisor |

---

## 🎭 ROLES CLARIFICATION

### Roles to CREATE:

```
1. Operator (NEW)
   - Report issues via portal
   - Confirm repairs (Phase 8)
   - NO access to PM tasks
   - NO access to ERPNext desk

2. Engineering Supervisor (NEW)
   - Review Section 2
   - Mark repairs complete
   - ERPNext desk access only
```

### Roles to USE (Existing):

```
3. Supervisor (EXISTS)
   - Approve Section 1 reports
   - Verify Section 3 (hygiene)
   - Portal + ERPNext desk access

4. Maintenance User (EXISTS)
   - Do PM checks
   - Report issues
   - Portal only

5. Engineering Team (EXISTS)
   - Fill Section 2
   - Do repairs
   - ERPNext desk only

6. Maintenance Manager (EXISTS)
   - Acts as "General Manager" in FM-EN-04
   - Approves Section 1 and Section 2 (final)
   - ERPNext desk only
```

---

## 📝 NEW FIELDS FOR REPORTER'S SUPERVISOR

### Section 1 Enhancement:

Add AFTER `reporter_signature`:

```json
{
  "fieldname": "section_break_supervisor_review",
  "fieldtype": "Section Break",
  "label": "Reporter's Supervisor Review (หัวหน้าแผนกตรวจสอบ)",
  "depends_on": "eval:doc.workflow_state != 'Draft'"
},
{
  "fieldname": "supervisor_review_notes",
  "fieldtype": "Small Text",
  "label": "Supervisor Notes (หมายเหตุหัวหน้าแผนก)",
  "description": "Supervisor can add corrections or additional information"
},
{
  "fieldname": "supervisor_approved_by",
  "fieldtype": "Link",
  "label": "Approved By (ผู้อนุมัติ)",
  "options": "User",
  "read_only": 1
},
{
  "fieldname": "column_break_supervisor",
  "fieldtype": "Column Break"
},
{
  "fieldname": "supervisor_signature",
  "fieldtype": "Signature",
  "label": "Supervisor Signature (ลายเซ็น)",
  "reqd": 1,
  "mandatory_depends_on": "eval:doc.workflow_state == 'Pending Reporter\\'s Supervisor Approval'"
},
{
  "fieldname": "supervisor_approval_date",
  "fieldtype": "Datetime",
  "label": "Approval Date (วันที่)",
  "read_only": 1
}
```

---

## ⚠️ MIGRATION RISKS

### High Risk:

1. **Deleting `custom_repair_type` breaks existing reports**
   - Mitigation: Copy data to new `repair_type` first
   - Test query: `SELECT COUNT(*) FROM tabAsset Repair WHERE custom_repair_type IS NOT NULL`

2. **Changing workflow states breaks in-progress repairs**
   - Mitigation: Map old states to new states
   - Keep "Pending Approval" as alias for backward compatibility

### Medium Risk:

3. **`custom_การดำเนินการ` table replacement**
   - If child doctype exists, data migration needed
   - If doesn't exist, just remove field

### Low Risk:

4. **Deleting `custom_สาเหตุ` fields**
   - Check usage: `SELECT COUNT(*) FROM tabAsset Repair WHERE custom_สาเหตุ IS NOT NULL`
   - If used, notify user before deletion

---

## ✅ CLEANUP CHECKLIST

Before implementation:

- [ ] Check if "Asset Repair Engineering Detail" doctype exists
- [ ] Count repairs using `custom_repair_type`
- [ ] Count repairs using `custom_สาเหตุ`
- [ ] Identify what `custom_ใบส่งของเลขที่` is (ask user)
- [ ] Backup database
- [ ] Test migration script on copy of data
- [ ] Get user approval

---

## 🔄 STEP-BY-STEP CLEANUP PROCESS

### Step 1: Backup
```bash
mysqldump -u root -p tub > backup_before_cleanup_2026-01-08.sql
```

### Step 2: Check Field Usage
```sql
-- Check custom_repair_type usage
SELECT custom_repair_type, COUNT(*) as count
FROM `tabAsset Repair`
GROUP BY custom_repair_type;

-- Check custom_สาเหตุ usage
SELECT custom_สาเหตุ, COUNT(*) as count
FROM `tabAsset Repair`
WHERE custom_สาเหตุ IS NOT NULL
GROUP BY custom_สาเหตุ;

-- Check custom_ใบส่งของเลขที่ usage
SELECT COUNT(*) FROM `tabAsset Repair` WHERE custom_ใบส่งของเลขที่ IS NOT NULL;
```

### Step 3: Add new `repair_type` field
```bash
# Don't delete custom_repair_type yet
# Add new field alongside
bench migrate
```

### Step 4: Migrate Data
```python
# Copy old data to new field
frappe.db.sql("""
  UPDATE `tabAsset Repair`
  SET repair_type = CASE
    WHEN custom_repair_type IN ('ซ่อม', 'แก้ไข') THEN 'ซ่อม/แก้ไข'
    WHEN custom_repair_type IN ('ติดตั้งใหม่', 'ปรับปรุง') THEN 'ติดตั้งใหม่/ปรับปรุง'
    ELSE 'ซ่อม/แก้ไข'
  END
  WHERE repair_type IS NULL OR repair_type = ''
""")
frappe.db.commit()
```

### Step 5: Test
- Open existing repairs - verify `repair_type` shows correct value
- Create new repair - verify `repair_type` required and works

### Step 6: Delete Old Fields
```python
# After confirming data migration success
frappe.delete_doc("Custom Field", "Asset Repair-custom_repair_type")
frappe.delete_doc("Custom Field", "Asset Repair-custom_สาเหตุ")
frappe.delete_doc("Custom Field", "Asset Repair-custom_ระบุสาเหตุ")
frappe.db.commit()
```

---

## 📞 QUESTIONS FOR USER

1. **`custom_ใบส่งของเลขที่`** - What is this field? Delete or keep?

2. **`custom_การดำเนินการ` table** - Does "Asset Repair Engineering Detail" child doctype exist? If yes, what fields does it have?

3. **Reporter's Supervisor notes** - Can they ONLY add notes to existing fields, or can they edit the description?

4. **Migration timing** - Do this cleanup NOW or after Phase 1 testing?

---

**Status:** Awaiting user answers before proceeding
**Next:** Update master plan with corrections
