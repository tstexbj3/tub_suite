# Asset Repair Workflow & Fields - SINGLE SOURCE OF TRUTH

**Last Updated:** 2026-01-12
**Status:** CURRENT AND ACCURATE
**Version:** 2.1.0 (Supervisor-Only Workflow)

## Recent Bug Fixes (2026-01-12)
1. **Fixed FM-EN-04 Print Format:**
   - Letterhead banner now displays in header (not logo)
   - Asset item_code shown instead of asset ID
   - ตัวแทนผู้แจ้ง and ผู้อนุมัติ(GM) displayed side by side
   - All signature dates showing correctly
   - รายการ/ลักษณะของงาน and ผู้ดำเนินงาน columns in table

2. **Added Missing API Function:**
   - Created `create_operator_repair_request()` in maintenance.py
   - Enables repair reporting from maintenance portal

3. **Fixed Verification List Bug:**
   - `get_repairs_needing_verification()` now correctly filters for "Pending Supervisor Verification"
   - Previously showed "Finished" repairs causing duplicates
   - Completed repairs no longer appear in ยืนยันการซ่อม list

---

## ⚠️ CRITICAL: THIS IS THE ONLY CORRECT DOCUMENTATION

**DO NOT CREATE NEW DOCUMENTATION FILES.**
**UPDATE THIS FILE ONLY.**

**IGNORE ALL OTHER .md FILES EXCEPT:**
- README.md (project overview)
- CHANGELOG.md (version history)
- DEPLOYMENT_GUIDE_v2.1.0.md (deployment instructions)

---

## 📋 Workflow Overview

**Key Change (2026-01-10):** Operators REMOVED from workflow. Supervisors handle everything.

### Complete Flow (9 States):

```
1. Draft
   ├─ Supervisor reports issue via portal (on behalf of team)
   ├─ Supervisor fills Section 1 fields
   └─ Action: [Supervisor Verify] → Pending GM Approval Section 1

2. Pending GM Approval Section 1
   ├─ GM reviews and approves initial request
   ├─ Fields: gm_section1_notes, gm_section1_signature
   ├─ Action: [GM Approve Section 1] → Pending Engineering Assessment
   └─ Alternative: [GM Reject] → Rejected

3. Pending Engineering Assessment
   ├─ Engineering Team fills Section 2 (assessment details)
   ├─ Fields: action_type, cost_type, todo_items, spare_parts, dates, signature
   └─ Action: [Engineering Assessment Complete] → Pending Engineering Supervisor Review

4. Pending Engineering Supervisor Review
   ├─ Engineering Supervisor signs off on assessment
   └─ Action: [Supervisor Review Complete] → Pending GM Final Approval

5. Pending GM Final Approval
   ├─ GM gives final approval for repair work
   └─ Action: [GM Final Approve] → Approved for Repair

6. Approved for Repair
   ├─ Engineer goes to fix asset (offline work)
   ├─ After repair done, engineer fills Section 3 fields:
   │  - repair_result_status (Select - EDITABLE)
   │  - completion_handover_date (Date - AUTO-FILLED on next transition)
   └─ Action: [Finish Repair] → Pending Supervisor Verification

7. Pending Supervisor Verification
   ├─ Supervisor (who originally reported) verifies repair
   ├─ Section 3B shows: Hygiene checklist, cleanliness checks
   └─ Action: [Supervisor Verify] → Finished

8. Finished
   └─ LOCKED - All fields read-only

9. Rejected
   └─ Can happen at: GM Approval S1, GM Final Approval, or Supervisor Verification
```

---

## 🏗️ Section Structure

### Section 1: Asset Info & Reporter (ข้อมูลเครื่องจักรและผู้แจ้ง)

**Visible:** All states
**Filled by:** Supervisor (in Draft state)

#### Section 1A: Issue Details
**Fields:**
- `repair_type` - ประเภทการซ่อม (Select)
- `repair_source` - แหล่งที่มา (Select: Portal/Desk)
- `repair_subject` - เรื่องที่แจ้ง (Data) - EDITABLE IN DRAFT ONLY
- `issue_photos` - รูปถ่ายปัญหา (Attach Image)
- `reported_by` - Inspector who reported (Link: User) - Auto-filled
- `reporter_department` - แผนกผู้แจ้ง (Link: Department)
- `failure_date` - วันที่เกิดปัญหา (Datetime)
- `description` - Error Description (Text Editor) - EDITABLE IN DRAFT ONLY

#### Section 1B: GM Approval Section 1
**Visible when:** `eval:doc.workflow_state=="Pending GM Approval Section 1"`
**Fields:**
- `gm_section1_notes` - หมายเหตุ GM (Small Text)
- `gm_section1_signature` - ลายเซ็น GM (Signature) ✅ MANDATORY

---

### Section 2: Engineering Department (สำหรับฝ่ายวิศวกรรม)

**Visible from:** Pending Engineering Assessment onwards

#### Engineering Section 1
**Visible when:** `eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)`

**Fields:**
- `action_type` - การดำเนินการ (Select) ✅ MANDATORY
  - Options: ช่างภายใน (Internal), ช่างภายนอก (External)
- `custom_cost_type` - ค่าใช้จ่าย (Select) ✅ MANDATORY
  - Options: มีค่าใช้จ่าย (With Cost), ไม่มีค่าใช้จ่าย (No Cost)
- `custom_engineering_todo_items` - Engineering Todo Items (Table) ✅ MANDATORY
  - Child DocType: Asset Repair Engineering Detail
  - Fields: todo_item, procedure, responsible_person, status
- `spare_parts_used` - Spare Parts Used (Table) - OPTIONAL
  - Child DocType: Repair Spare Part
  - Fields: item_code, item_name, qty, uom, warehouse

#### Engineering Section 2
**Visible when:** Same as Section 1

**Standard ERPNext Fields:**
- `expected_duration_days` - ระยะเวลาคาดการณ์ (Int) ✅ MANDATORY
- `repair_start_date` - วันที่เริ่มซ่อม (Date) ✅ MANDATORY
- `repair_end_date` - วันที่เสร็จสิ้น (Date) ✅ MANDATORY
- `engineering_operator_signature` - ลายเซ็นผู้ประเมิน (Signature) ✅ MANDATORY
- `engineering_operator_sign_date` - วันที่ประเมิน (Datetime) - Auto
- `engineering_operator_signed_by` - Signed By (Link: User) - Auto
- `eng_supervisor_signature` - ผู้ควบคุมตรวจสอบ Supervisor Signature (Signature) ✅ MANDATORY
- `eng_supervisor_review_date` - Review Date (Datetime) - Auto
- `approval_signature` - ผู้อนุมัติ Manager Signature (Signature) ✅ MANDATORY
- `manager_approval_date` - Approval Date (Datetime) - Auto
- `manager_approved_by` - Approved By (Link: User) - Auto

#### Engineering Section 3
**Visible when:** Same as Section 1
**Editable in:** Approved for Repair state (engineer fills after completing repair)

**Fields:**
- `completion_handover_date` - วันที่ส่งมอบงาน (Date) - READ-ONLY (auto-filled on "Finish Repair")
- `repair_result_status` - ผลการดำเนินการ (Select) - EDITABLE
  - Options: เรียบร้อย (Satisfactory), ไม่เรียบร้อย (Unsatisfactory), อื่นๆ (Other)

---

### Section 3: Hygiene & Safety (บันทึกสุขลักษณะ/ความปลอดภัย)

**Fieldname:** `section_3b_break`
**Visible when:** `eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"`
**Filled by:** Supervisor (in Pending Supervisor Verification state)

**Fields:**
- `hygiene_status` - Hygiene Status (สถานะสุขลักษณะ) (Select)
- `cleanliness_before_machine` - Machine Cleanliness Before (Select)
- `cleanliness_after_machine` - Machine Cleanliness After (Select)
- `cleanliness_before_area` - Area Cleanliness Before (Select)
- `cleanliness_after_area` - Area Cleanliness After (Select)
- `parts_inserted` - Parts Inserted (อุปกรณ์ที่นำเข้า) (Table)
- `parts_removed` - Parts Removed (อุปกรณ์ที่นำออก) (Table)
- `supervisor_verification_notes` - Final Remarks (หมายเหตุ) (Small Text)
- `supervisor_signature` - Supervisor Signature (ลายเซ็น) (Signature) ✅ MANDATORY
- `supervisor_verified_by` - Verified By (Link: User) - Auto
- `supervisor_verification_date` - Verification Date (Datetime) - Auto
- `hygiene_issue_notes` - Hygiene Issue Notes (Small Text)
- `confirmation_date` - Confirmation Date (Datetime) - Auto

---

## 🔄 Auto-Fill Behavior

### completion_handover_date
**When:** User clicks "Finish Repair" (Approved for Repair → Pending Supervisor Verification)
**Value:** Today's date (`frappe.utils.today()`)
**Location:** `asset_repair_override.py` line 98-103

```python
# Approved for Repair → Pending Supervisor Verification (Finish Repair button clicked)
elif old_workflow == "Approved for Repair" and new_workflow == "Pending Supervisor Verification":
    print(f"   ✅ Finish Repair - setting completion handover date")
    if not self.get("completion_handover_date"):
        frappe.db.set_value("Asset Repair", self.name, "completion_handover_date", frappe.utils.today())
        frappe.db.commit()
```

---

## 👥 Role Permissions

| Role | Access | Portal | States |
|------|--------|--------|--------|
| **Supervisor** | Desk + Portal | ✅ | Draft, Pending Supervisor Verification |
| **Maintenance Manager (GM)** | Desk only | ❌ | Pending GM Approval S1, Pending GM Final Approval |
| **Engineering Team** | Desk only | ❌ | Pending Engineering Assessment |
| **Engineering Supervisor** | Desk only | ❌ | Pending Eng Supervisor Review, Approved for Repair |

### Removed Roles:
- ❌ **Maintenance User (Operator)** - Completely removed (2026-01-10)

---

## 📱 Portal Pages

### 1. Report Issue
**URL:** `/maintenance/report-issue`
**Access:** Supervisor role ONLY
**Purpose:** Supervisor reports issues on behalf of their team
**Creates:** Asset Repair in Draft state

### 2. Verify Repair
**URL:** `/maintenance/verify/:repairName`
**Access:** Supervisor role ONLY (must be the one who reported)
**Purpose:** Supervisor verifies completed repair and fills hygiene checklist
**Updates:** Asset Repair from Pending Supervisor Verification → Finished

---

## 🚫 Common Mistakes to Avoid

### 1. Field Visibility Conditions
**WRONG:**
```javascript
depends_on: 'eval:doc.workflow_state=="Pending Reporter Supervisor Verification"'
```
❌ Old state name

**CORRECT:**
```javascript
depends_on: 'eval:doc.workflow_state=="Pending Supervisor Verification"'
```
✅ New state name (supervisor-only workflow)

### 2. Checking for Operator Fields
**WRONG:**
```javascript
depends_on: 'eval:doc.reporter_confirmed==1'
```
❌ Field doesn't exist anymore

**CORRECT:**
```javascript
depends_on: 'eval:doc.workflow_state=="Pending Supervisor Verification"'
```
✅ Check workflow state only

### 3. Section Naming
**Current sections:**
- ✅ Engineering Section 1 (action_type, cost_type, etc.)
- ✅ Engineering Section 2 (dates, signatures) - STANDARD ERPNEXT FIELDS
- ✅ Engineering Section 3 (completion_handover_date, repair_result_status)
- ✅ Hygiene Section (section_3b_break)

Do NOT delete Section 2 - it contains standard ERPNext fields that appear automatically.

---

## 🔧 Technical Implementation

### Files Modified:
1. **asset_repair_override.py** - Auto-fill completion_handover_date on "Finish Repair"
2. **maintenance.py** - API endpoints restricted to Supervisor role only
3. **Custom Fields** - Updated visibility conditions to new workflow state names
4. **Workflow** - Created "Asset Repair Workflow - Supervisor Only" (9 states)
5. **Client Script** - "Asset Repair - Field Locking UI" controls field editability

### Key Changes (2026-01-10 to 2026-01-11):
- ✅ Removed "Pending Reporter Confirmation" state
- ✅ Renamed "Pending Reporter Supervisor Verification" → "Pending Supervisor Verification"
- ✅ Updated Section 3B hygiene visibility condition
- ✅ Made repair_result_status editable in Approved for Repair state
- ✅ Auto-fill completion_handover_date on "Finish Repair" transition
- ✅ Fixed Subject and Error Description editability (Draft state only)
- ✅ Deleted Supervisor Notes field
- ✅ Hidden "Actions performed" field from GM Section 1
- ✅ Locked Subject field after Draft state

---

## 📝 Field Naming Convention

### ✅ CORRECT:
- **Fieldnames:** English only (e.g., `custom_engineering_section`)
- **Labels:** Can use Thai with vowels/tone marks (e.g., "สำหรับฝ่ายวิศวกรรม")

### ❌ WRONG:
- **Fieldnames:** Thai with special characters (e.g., `custom_การดำเนินการ`)

**Reason:** Thai vowel marks cause errors in fieldname validation.

---

## 🔍 Debugging Commands

### Clear Cache:
```bash
cd /home/user/frappe-bench
source env/bin/activate
bench --site tub clear-cache
```

### Check Field Visibility:
```python
import frappe
field = frappe.get_doc("Custom Field", {"dt": "Asset Repair", "fieldname": "FIELDNAME"})
print(f"depends_on: {field.depends_on}")
print(f"hidden: {field.hidden}")
```

### Check Workflow State:
```python
import frappe
repair = frappe.get_doc("Asset Repair", "ACC-ASR-2026-00001")
print(f"workflow_state: {repair.workflow_state}")
```

---

## ⚠️ IMPORTANT REMINDERS

1. **DO NOT CREATE NEW DOCUMENTATION FILES** - Update this file only
2. **Workflow is supervisor-only** - No operators involved
3. **Section 2 is standard ERPNext** - Don't delete it, it's not custom
4. **completion_handover_date auto-fills** - Don't make it editable
5. **repair_result_status is editable** - Engineer fills this in Approved for Repair
6. **Hygiene section shows in Pending Supervisor Verification** - Not in Approved for Repair

---

**Document Version:** 1.0
**Last Updated By:** Claude AI
**Next Review:** When workflow changes occur

**IF YOU FORGET THIS OR CREATE NEW DOCS, THE USER WILL BE VERY ANGRY.**
