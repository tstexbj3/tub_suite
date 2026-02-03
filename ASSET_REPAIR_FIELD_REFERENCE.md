# Asset Repair Form - Complete Field Reference

**Document Type:** Technical Reference
**Audience:** Developers, System Administrators
**Version:** 2.0 (Complete Rewrite)
**Last Updated:** 2026-02-03
**Authoritative Source:** Actual Asset Repair form as configured by user + `asset_repair_override.py`

---

## Table of Contents

1. [Document Overview](#document-overview)
2. [Complete Workflow States](#complete-workflow-states)
3. [Complete Workflow Transitions](#complete-workflow-transitions)
4. [State-by-State Field Visibility](#state-by-state-field-visibility)
5. [Form Section Structure](#form-section-structure)
6. [Signature Auto-Fill Mechanism](#signature-auto-fill-mechanism)
7. [Validation Rules](#validation-rules)
8. [Print Format Field Mappings](#print-format-field-mappings)

---

## Document Overview

**Asset Repair** is a custom ERPNext DocType tracking maintenance repairs through a **9-state workflow**.

**Purpose:** Track PM and Portal repairs from reporting → GM approval → engineering assessment → repair → supervisor verification → completion.

**Key Characteristics:**
- **9 workflow states** (Draft → Finished)
- **Cumulative locking** - Previous sections lock as workflow progresses
- **Dual repair paths**: PM Issue Report vs Portal repairs
- **6 signature/date pairs** - Signatures auto-fill hidden date fields, dates show after signing
- **Section visibility** - Sections appear/hide based on workflow state

---

## Complete Workflow States

| # | State | Editable By | Editable Sections | Required Signatures |
|---|-------|-------------|-------------------|---------------------|
| 1 | **Draft** | Supervisor, Maintenance Supervisor | Supervisor Verification | `supervisor_section1_signature` |
| 2 | **Pending GM Approval Section 1** | Maintenance Manager | GM Verification | `custom_gm_signature` |
| 3 | **Pending Engineering Assessment** | Engineering Team | Engineering Dept 1, Engineering Dept 2 | `engineering_operator_signature` |
| 4 | **Pending Engineering Supervisor Review** | Engineering Supervisor | Engineering Dept 1, Engineering Dept 2 | `eng_supervisor_signature` |
| 5 | **Pending GM Final Approval** | Maintenance Manager | (Signature only) | `approval_signature` |
| 6 | **Approved for Repair** | Engineering Supervisor ONLY | Engineering Dept 3 | None (action-based) |
| 7 | **Pending Supervisor Verification** | Supervisor (Portal) OR Maintenance Supervisor (PM) | Section 3 (Hygiene), Section 5 (Signature) | `supervisor_signature` |
| 8 | **Pending Reporter Confirmation** | Original Reporter | (None - portal confirmation) | None (portal only) |
| 9 | **Finished** | Read-only | (None - all locked) | None |

---

## Complete Workflow Transitions

**Total Transitions:** 16 (including conditional branches)

| # | From State | Action Button | To State | Allowed Role | Condition |
|---|------------|---------------|----------|--------------|-----------|
| 1 | Draft | Supervisor Verify | Pending GM Approval Section 1 | Supervisor | None |
| 2 | Pending GM Approval Section 1 | GM Approve Section 1 | Pending Engineering Assessment | Maintenance Manager | None |
| 3 | Pending GM Approval Section 1 | GM Reject | Rejected | Maintenance Manager | None |
| 4 | Pending Engineering Assessment | Engineering Assessment Complete | Pending Engineering Supervisor Review | Engineering Team | None |
| 5 | Pending Engineering Supervisor Review | Supervisor Review Complete | Pending GM Final Approval | Engineering Supervisor | None |
| 6 | Pending GM Final Approval | GM Final Approve | Approved for Repair | Maintenance Manager | None |
| 7 | Pending GM Final Approval | GM Request Changes | Pending Engineering Assessment | Maintenance Manager | None |
| 8 | Approved for Repair | Finish Repair | Pending Supervisor Verification | Engineering Supervisor | None |
| 9 | Pending Supervisor Verification | Supervisor Verify | Pending Reporter Confirmation | Supervisor | `repair_source != "Planned Maintenance (ตามแผน)"` |
| 10 | Pending Supervisor Verification | Supervisor Reject | Approved for Repair | Supervisor | `repair_source != "Planned Maintenance (ตามแผน)"` |
| 11 | Pending Supervisor Verification | PM Supervisor Verify | Pending Reporter Confirmation | Maintenance Supervisor | `repair_source == "Planned Maintenance (ตามแผน)"` |
| 12 | Pending Supervisor Verification | PM Supervisor Reject | Approved for Repair | Maintenance Supervisor | `repair_source == "Planned Maintenance (ตามแผน)"` |
| 13 | Pending Reporter Confirmation | Reporter Confirm | Finished | Maintenance User | None |
| 14 | Pending Reporter Confirmation | Reporter Confirm | Finished | Supervisor | None |
| 15 | Pending Reporter Confirmation | Reporter Confirm | Finished | Maintenance Supervisor | None |
| 16 | Finished | Cancel | Cancelled | System Manager | None |

**Critical Conditional Branching:**
- **Pending Supervisor Verification** shows different buttons based on `repair_source`:
  - Portal repairs: "Supervisor Verify/Reject" (Supervisor role)
  - PM repairs: "PM Supervisor Verify/Reject" (Maintenance Supervisor role)

---

## State-by-State Field Visibility

### STATE 1: Draft (PM Issue Report)

**Visible Sections:**

#### Pre-Section (Standard Fields - Read-only)
- `asset`: ACC-ASS-2025-00187
- `repair_status`: Pending
- `asset_name`: เครื่องปรับอากาศสี่ทิศทาง

#### Section 1: Asset Info & Reporter (ข้อมูลเครื่องจักรและผู้แจ้ง) - Read-only
| Field | Value | Notes |
|-------|-------|-------|
| `repair_type` | แก้ไข (Fix/Correction) | Pre-filled from portal |
| `repair_source` | Planned Maintenance (ตามแผน) | **PM Issue Report** |
| `repair_subject` | เรื่องที่แจ้ง... | Pre-filled from portal |
| `issue_photos` | /files/ACCASS202500187_ISSUE... | Photos from reporter |
| `reported_by` | test_maintenance_repair@test.com | Inspector who reported |
| `reporter_department` | Maintenance Department | Reporter's department |
| `maintenance_task` | ทำความสะอาด Filter | **PM only** - linked task |

#### (Unlabeled Section) - Read-only
| Field | Value |
|-------|-------|
| `failure_date` | 02-02-2026 16:45:59 |
| `description` | รายละเอียดปัญหา... |

#### Supervisor Verification (หัวหน้าแผนกตรวจสอบ) - ⭐ EDITABLE
| Field | Required | Auto-fills | Shows After Signing |
|-------|----------|-----------|---------------------|
| `supervisor_section1_signature` | ✅ Yes | `supervisor_section1_date` | Date shows after signing |

**Note:** Supervisor signature section remains **visible in all later states** (read-only) as part of approval audit trail.

---

### STATE 2: Pending GM Approval Section 1

**Changes from Draft:**
- All previous sections: **READ-ONLY** (locked)
- **Supervisor Verification section**: Still visible (showing captured signature + date from Draft)

#### GM Verification (GM ตรวจสอบ) - ⭐ EDITABLE
| Field | Required | Auto-fills | Shows After Signing |
|-------|----------|-----------|---------------------|
| `custom_gm_signature` | ✅ Yes | `gm_section1_approval_date` | Date shows after signing |

---

### STATE 3: Pending Engineering Assessment

**Changes from previous:**
- All previous sections: **READ-ONLY** (locked)
- Supervisor & GM Verification sections: **Signatures visible with dates**

#### สำหรับฝ่ายวิศวกรรม (Engineering Department) 1 - ⭐ EDITABLE
| Field | Required | Type | Options/Notes |
|-------|----------|------|---------------|
| `action_type` | ✅ Yes | Select | ช่างภายใน (Internal) / ช่างภายนอก (External) |
| `custom_cost_type` | ✅ Yes | Select | มีค่าใช้จ่าย (With Cost) / ไม่มีค่าใช้จ่าย (No Cost) |
| `custom_engineering_todo_items` | ✅ Yes | Table | Todo items: รายการสิ่งที่ต้องทำ, การแก้ไข/ดำเนินการ, ผู้ดำเนินงาน |
| `spare_parts_used` | ❌ No | Table | Spare parts: Item Name, Quantity (OPTIONAL) |

#### สำหรับฝ่ายวิศวกรรม (Engineering Department) 2 - ⭐ EDITABLE
| Field | Required | Type | Auto-fills | Shows After Signing |
|-------|----------|------|-----------|---------------------|
| `expected_duration_days` | ✅ Yes | Int | - | - |
| `engineering_operator_signature` | ✅ Yes | Signature | `engineering_operator_sign_date` | Date shows after signing |
| `repair_start_date` | ✅ Yes | Date | - | - |
| `repair_end_date` | ✅ Yes | Date | - | - |

---

### STATE 4: Pending Engineering Supervisor Review

**Changes from previous:**
- Engineering Department 1 & 2: **Still EDITABLE**
- `engineering_operator_signature`: **HIDDEN** (already signed)

#### สำหรับฝ่ายวิศวกรรม (Engineering Department) 2 - ⭐ EDITABLE (Changes)
| Field | Required | Status | Auto-fills | Shows After Signing |
|-------|----------|--------|-----------|---------------------|
| `expected_duration_days` | ✅ Yes | Editable | - | - |
| `engineering_operator_signature` | - | **HIDDEN** | - | - |
| `eng_supervisor_signature` | ✅ Yes | **Visible + Editable** | `eng_supervisor_review_date` | Date shows after signing |
| `repair_start_date` | ✅ Yes | Editable | - | - |
| `repair_end_date` | ✅ Yes | Editable | - | - |

---

### STATE 5: Pending GM Final Approval

**Changes from previous:**
- All engineering sections: **READ-ONLY** (locked)

#### ⭐ ONLY EDITABLE FIELD
| Field | Required | Auto-fills | Shows After Signing |
|-------|----------|-----------|---------------------|
| `approval_signature` | ✅ Yes | `gm_final_approval_date` | Date shows after signing |

---

### STATE 6: Approved for Repair

**Changes from previous:**
- All previous sections: **READ-ONLY** (locked)

#### สำหรับฝ่ายวิศวกรรม (Engineering Department) 3 - ⭐ EDITABLE
| Field | Required | Type | Options | Auto-fill Trigger |
|-------|----------|------|---------|-------------------|
| `completion_handover_date` | ✅ Yes | Date | - | Auto-filled when "Finish Repair" action |
| `repair_result_status` | ✅ Yes | Select | เรียบร้อย (Satisfactory) / ไม่เรียบร้อย (Unsatisfactory) | - |

---

### STATE 7: Pending Supervisor Verification

**Changes from previous:**
- All previous sections: **READ-ONLY** (locked)
- Engineering Department 3 visible with locked values

#### Section 3: Hygiene & Safety (บันทึกสุขลักษณะ/ความปลอดภัย) - ⭐ EDITABLE
| Field | Required | Type | Options |
|-------|----------|------|---------|
| `hygiene_status` | ✅ Yes | Select | 1 / เรียบร้อย/สะอาดไม่เสี่ยงต่อการปนเปื้อน (Clean) / ไม่เรียบร้อย/ต้องแก้ไข (Not Clean) |
| `cleanliness_before_machine` | ✅ Yes | Select | สะอาด (Clean) / ไม่สะอาด (Not Clean) |
| `cleanliness_after_machine` | ✅ Yes | Select | สะอาด (Clean) / ไม่สะอาด (Not Clean) |
| `cleanliness_before_area` | ✅ Yes | Select | สะอาด (Clean) / ไม่สะอาด (Not Clean) |
| `cleanliness_after_area` | ✅ Yes | Select | สะอาด (Clean) / ไม่สะอาด (Not Clean) |
| `parts_inserted` | ❌ No | Table | Parts inserted: Item Name, Quantity (OPTIONAL) |
| `parts_removed` | ❌ No | Table | Parts removed: Item Name, Quantity (OPTIONAL) |

#### Section 5: Final Remarks (หมายเหตุเพิ่มเติม) - ⭐ EDITABLE
| Field | Required | Auto-fills | Shows After Signing |
|-------|----------|-----------|---------------------|
| `supervisor_signature` | ✅ Yes | `supervisor_verification_date` | Date shows after signing |

---

### STATE 8: Pending Reporter Confirmation

**Changes from previous:**
- All sections: **READ-ONLY** (completely locked)
- Section 3 & Section 5 visible with locked values
- **NO EDITABLE FIELDS** - Waiting for reporter to confirm via portal

---

### STATE 9: Finished

**Changes from previous:**
- All sections: **READ-ONLY** (completely locked)

#### Reporter Confirmation (ผู้แจ้งยืนยัน) - ⭐ NEW VISIBLE SECTION
| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `reporter_confirmation_date` | Datetime | 02-02-2026 16:29:37 | When reporter confirmed |
| `reporter_confirmation_photos` | Attach Image | /files/ACCASS202500028_CONFIRM... | Photos from reporter |
| `reporter_confirmation_notes` | Small Text | Additional Notes (Optional)... | Reporter's notes |

---

## Form Section Structure

**As arranged in actual Asset Repair form:**

### 1. Pre-Section (No Label)
**Standard ERPNext fields:**
- `asset` (Link)
- `repair_status` (Select)
- `asset_name` (Data)

### 2. Section 1: Asset Info & Reporter (ข้อมูลเครื่องจักรและผู้แจ้ง)
**Visible:** Draft onwards
**Editable:** Never (pre-filled from portal)
**Fields:** `repair_type`, `repair_source`, `repair_subject`, `issue_photos`, `reported_by`, `reporter_department`, `maintenance_task`

### 3. (Unlabeled Section)
**Was:** "Section 0: Document Header" - **Label removed per user request**
**Visible:** Draft onwards
**Editable:** Never (pre-filled from portal)
**Fields:** `failure_date`, `description`

### 4. Supervisor Verification (หัวหน้าแผนกตรวจสอบ)
**Visible:** Draft
**Editable:** Draft only
**Fields:** `supervisor_section1_signature`, `supervisor_section1_date` (shows after signing)

### 5. GM Verification (GM ตรวจสอบ)
**Visible:** Pending GM Approval Section 1
**Editable:** Pending GM Approval Section 1 only
**Fields:** `custom_gm_signature`, `gm_section1_approval_date` (shows after signing)

### 6. สำหรับฝ่ายวิศวกรรม (Engineering Department) 1
**Visible:** Pending Engineering Assessment onwards
**Editable:** Pending Engineering Assessment, Pending Engineering Supervisor Review
**Fields:** `action_type`, `custom_cost_type`, `custom_engineering_todo_items` (table), `spare_parts_used` (table - optional)

### 7. สำหรับฝ่ายวิศวกรรม (Engineering Department) 2
**Visible:** Pending Engineering Assessment onwards
**Editable:** Pending Engineering Assessment, Pending Engineering Supervisor Review
**Fields:**
- Pending Engineering Assessment: `expected_duration_days`, `engineering_operator_signature`, `repair_start_date`, `repair_end_date`
- Pending Engineering Supervisor Review: Same fields + `eng_supervisor_signature` (replaces operator signature)

### 8. (Signature field for GM Final Approval)
**Visible:** Pending GM Final Approval
**Editable:** Pending GM Final Approval only
**Fields:** `approval_signature`, `gm_final_approval_date` (shows after signing)

### 9. สำหรับฝ่ายวิศวกรรม (Engineering Department) 3
**Visible:** Approved for Repair onwards
**Editable:** Approved for Repair only
**Fields:** `completion_handover_date`, `repair_result_status`

### 10. Section 3: Hygiene & Safety (บันทึกสุขลักษณะ/ความปลอดภัย)
**Visible:** Pending Supervisor Verification onwards
**Editable:** Pending Supervisor Verification only
**Fields:** `hygiene_status`, `cleanliness_before_machine`, `cleanliness_after_machine`, `cleanliness_before_area`, `cleanliness_after_area`, `parts_inserted` (table - optional), `parts_removed` (table - optional)

### 11. Section 5: Final Remarks (หมายเหตุเพิ่มเติม)
**Visible:** Pending Supervisor Verification onwards
**Editable:** Pending Supervisor Verification only
**Fields:** `supervisor_signature`, `supervisor_verification_date` (shows after signing)

### 12. Reporter Confirmation (ผู้แจ้งยืนยัน)
**Visible:** Finished only
**Editable:** Never (filled from portal)
**Fields:** `reporter_confirmation_date`, `reporter_confirmation_photos`, `reporter_confirmation_notes`

---

## Signature Auto-Fill Mechanism

**6 Signature/Date Pairs** (reporter signature removed per user request):

| # | Signature Field | Date Field | State When Signed | Date Visibility |
|---|-----------------|------------|-------------------|-----------------|
| 1 | `supervisor_section1_signature` | `supervisor_section1_date` | Draft | Shows **after signing** (depends_on: signature exists) |
| 2 | `custom_gm_signature` | `gm_section1_approval_date` | Pending GM Approval Section 1 | Shows **after signing** |
| 3 | `engineering_operator_signature` | `engineering_operator_sign_date` | Pending Engineering Assessment | Shows **after signing** |
| 4 | `eng_supervisor_signature` | `eng_supervisor_review_date` | Pending Engineering Supervisor Review | Shows **after signing** |
| 5 | `approval_signature` | `gm_final_approval_date` | Pending GM Final Approval | Shows **after signing** |
| 6 | `supervisor_signature` | `supervisor_verification_date` | Pending Supervisor Verification | Shows **after signing** |

**Implementation Logic** (from `asset_repair_override.py` lines 365-402):

```python
def before_save_asset_repair(doc, method):
    """Auto-fill all signature timestamps"""
    if not doc.is_new():
        old_doc = frappe.db.get_value("Asset Repair", doc.name, [signature fields], as_dict=True)

        # For each signature/date pair:
        if doc.get("supervisor_section1_signature") and not old_doc.get("supervisor_section1_signature"):
            if not doc.get("supervisor_section1_date"):
                doc.supervisor_section1_date = now()

        # ... same pattern for all 6 pairs
```

**Date Field Visibility:**
- Date fields have `depends_on: eval:doc.[signature_field]`
- Hidden until signature exists
- Shows on form **after signing**
- Always shows on print format

---

## Validation Rules

### 1. Signature Validation (lines 141-147, 417-422 of override)

**Engineer Signature** - Required before submission:
```python
if not doc.get("engineer_signature"):
    frappe.throw(_("Engineer Signature is required before submission"))
```

**Manager Signature** - Required for approval/rejection:
```python
if new_workflow in ["Approved", "Rejected"] and old_workflow == "Pending Approval":
    if not doc.get("approval_signature"):
        frappe.throw(_("Manager Signature is required for approval or rejection"))
```

### 2. Field Edit Validation (lines 186-195 of override)

**Engineering Supervisor Exclusive Access** to "Approved for Repair":
```python
if check_state == "Approved for Repair":
    if is_eng_supervisor:
        return  # Allow ONLY Engineering Supervisor
    else:
        frappe.throw(_("Only Engineering Supervisor can edit in Approved for Repair state"))
```

### 3. Supervisor Permission Validation (lines 198-222 of override)

**Regular Supervisor** (has "Supervisor" role):
- Can ONLY edit Portal repairs (`repair_source = "Portal (แจ้งผ่านระบบ)"`)
- Blocked from PM repairs with error: "Regular Supervisor can only verify Portal repairs."

**Maintenance Supervisor** (has "Maintenance Supervisor" role):
- Can ONLY edit PM repairs (`repair_source = "Planned Maintenance (ตามแผน)"`)
- Blocked from Portal repairs with error: "Maintenance Supervisor can only verify Planned Maintenance repairs."

### 4. Required Fields by State

**Draft:**
- `supervisor_section1_signature` ✅

**Pending GM Approval Section 1:**
- `custom_gm_signature` ✅

**Pending Engineering Assessment:**
- `action_type` ✅
- `custom_cost_type` ✅
- `custom_engineering_todo_items` ✅ (table - at least 1 row)
- `expected_duration_days` ✅
- `engineering_operator_signature` ✅
- `repair_start_date` ✅
- `repair_end_date` ✅

**Pending Engineering Supervisor Review:**
- All previous fields remain required
- `eng_supervisor_signature` ✅

**Pending GM Final Approval:**
- `approval_signature` ✅

**Approved for Repair:**
- `completion_handover_date` ✅
- `repair_result_status` ✅

**Pending Supervisor Verification:**
- `hygiene_status` ✅
- `cleanliness_before_machine` ✅
- `cleanliness_after_machine` ✅
- `cleanliness_before_area` ✅
- `cleanliness_after_area` ✅
- `supervisor_signature` ✅

---

## Print Format Field Mappings

**Print Format:** FM-EN-04 (Asset Repair Print Format)

### Signature + Date Display on Print:

| Signature Field | Date Field | Print Label (Thai) | Print Label (English) |
|-----------------|------------|-------------------|----------------------|
| `supervisor_section1_signature` | `supervisor_section1_date` | หัวหน้าแผนก | Supervisor Section 1 |
| `custom_gm_signature` | `gm_section1_approval_date` | ผู้อนุมัติ GM | GM Approval |
| `engineering_operator_signature` | `engineering_operator_sign_date` | ผู้ประเมิน | Engineering Operator |
| `eng_supervisor_signature` | `eng_supervisor_review_date` | ผู้ควบคุมตรวจสอบ | Engineering Supervisor |
| `approval_signature` | `gm_final_approval_date` | ผู้อนุมัติสุดท้าย | Final Approval |
| `supervisor_signature` | `supervisor_verification_date` | หัวหน้าตรวจรับ | Supervisor Verification |

**Signature Box Dimensions** (from PRINT_FORMAT_UPDATES.md):
- Width: 100px
- Height: 50px
- Padding: 1px 2px

**Font Sizes:**
- Headers: 12px
- Tables: 8px
- Normal text: 10px

---

## Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 2.0 | 2026-02-03 | **COMPLETE REWRITE** - Based on actual form structure user provided state-by-state | User + AI |
| 1.0 | 2026-02-03 | Initial comprehensive field reference (contained errors) | AI |

**Major Changes in v2.0:**
- ✅ Removed incorrect "Section 0-14" numbering - now uses actual section labels
- ✅ State-by-state field visibility based on real form behavior
- ✅ Corrected all field options (action_type, cleanliness, cost_type, hygiene_status, repair_result_status)
- ✅ Removed reporter_signature (only 6 signature pairs needed)
- ✅ Added signature date visibility rule (shows after signing)
- ✅ Documented actual cumulative locking pattern
- ✅ Removed Section 0 label from form per user request

---

## See Also

- **CLAUDE.md** - Master reference (Section 13 Session Log)
- **WORKFLOW_DOCUMENTATION.md** - Complete workflow states and transitions
- **SECTION_5_VISIBILITY_EXPLANATION.md** - Section 5 visibility pattern
- **ASSET_REPAIR_SIGNATURE_AUTOFILL.md** - Signature auto-fill mechanism
- **ASSET_REPAIR_CLIENT_SCRIPTS.md** - Client-side field locking
- **PM_WORKFLOW_IMPLEMENTATION.md** - PM workflow specifics
- **DEPLOYMENT_ISSUES_v2.1.20-v2.1.23.md** - Critical incident report
- **asset_repair_override.py** - Complete validation code
- **tub_suite/tub_suite/custom/asset_repair.json** - Complete field definitions

---

**Document Status:** ✅ COMPLETE v2.0 - Based on actual user form structure
**Next Actions:**
1. Add signature date `depends_on` conditions to all 6 date fields
2. Export customizations
3. Update CLAUDE.md session log

**Maintainer:** Development Team
**Contact:** See CLAUDE.md for support procedures
