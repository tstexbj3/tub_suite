# Master Implementation Plan: Asset Repair FM-EN-04 Complete Redesign

**Date:** 2026-01-08
**Status:** Planning Phase
**Objective:** Rebuild Asset Repair workflow to match TUB's FM-EN-04 physical form with proper role-based access

---

## 🎯 Executive Summary

### What We're Building:
Complete redesign of Asset Repair system with:
- **3-Section Form** matching FM-EN-04 physical document
- **10 Workflow States** for proper approval hierarchy
- **Role-Based Portal Access** (Operator vs Maintenance User)
- **Reporter Confirmation** logged with photos
- **Auto-Status Changes** based on workflow
- **Section Locking** to prevent unauthorized edits
- **Thai/English bilingual** throughout

### Critical Success Factors:
✅ NO breaking changes to existing repairs
✅ Test locally FIRST before any deployment
✅ Progressive section locking (Section 1 → 2 → 3)
✅ Proper role-based permissions at every step

---

## 📋 Current State Analysis

### Portal Structure (EXISTING):
```
Routes:
- / (Home) - Shows role-based cards
- /search (AssetSearch) - Search for assets
- /todos (TodoList) - Maintenance User PM tasks
- /checklist/:assetName (Checklist) - PM checklist page
- /verify/:repairName (VerifyRepair) - Reporter verification page
```

### Current Roles:
- **Maintenance User** - Does PM checks, sees PM tasks + report issue option
- (Need to add) **Operator** - Can only report issues, no PM access
- **Engineering Team** - Does repairs (exists in backend)
- **Maintenance Manager** - Approves repairs (exists)
- **General Manager** - Approves budget/resources (need to add)

### Current Verification Flow (EXISTING - Will be Phase 8):
```javascript
// VerifyRepair.jsx (lines 36-44)
await api.verifyRepair({
  repair_name: repairName,
  verification_photos: photos,     // Array of photo URLs
  verification_notes: notes,        // Text
  verification_status: 'Verified - Passed'
})
```

**Backend updates** (maintenance.py:564-567):
- `verified_by` = frappe.session.user
- `verification_date` = now()
- `verification_notes` = notes
- `verification_status` = "Verified - Passed" / "Verified - Failed"

---

## 🏗️ New Workflow Design

### Complete Flow (10 States):

```
1. Draft (ร่าง)
   ↓ Operator fills form + submits

2. Pending GM Approval - Section 1 (รออนุมัติจาก GM)
   ↓ General Manager: Approve/Reject

3. Pending Engineering Assessment (รอช่างประเมิน)
   ↓ Engineering Operator fills Section 2

4. Pending Engineering Supervisor Review (รอหัวหน้าช่างตรวจสอบ)
   ↓ Engineering Supervisor reviews + signs

5. Pending GM Final Approval (รอ GM อนุมัติสุดท้าย)
   ↓ General Manager: Approve to start repair

6. Approved for Repair (อนุมัติให้ซ่อม)
   ↓ Repair work begins

7. Repair In Progress (กำลังซ่อม)
   ↓ Engineering Supervisor marks complete

8. Pending Reporter's Supervisor Verification (รอหัวหน้าแผนกตรวจสอบ)
   ↓ Reporter's Supervisor fills Section 3 (hygiene checklist)

9. Pending Reporter Confirmation (รอผู้แจ้งยืนยัน)
   ↓ Original Reporter confirms on portal

10. Finished (เสร็จสมบูรณ์)
    [LOCKED - No one can edit]
```

### Section Locking Rules:

| Section | Locked After State | Who Can Edit Before Lock |
|---------|-------------------|--------------------------|
| Section 1 | GM Approval (State 2) | Operator (Draft only) |
| Section 2 | GM Final Approval (State 5) | Engineering Operator, Engineering Supervisor |
| Section 3 | Reporter Confirmation (State 9) | Reporter's Supervisor |

**After Finished:** NO ONE can edit. Must create new repair doc if changes needed.

---

## 📝 Form Structure (FM-EN-04 Alignment)

### SECTION 1: Asset Info & Report (ข้อมูลเครื่องจักรและผู้แจ้งซ่อม)

**Filled by:** Operator on Portal
**Locked after:** GM Approval (State 2)

| Field Name | Thai Label | Fieldtype | Options | Required | Auto-fill |
|-----------|-----------|-----------|---------|----------|-----------|
| `repair_type` | ประเภทการดำเนินการ | Select | ซ่อม/แก้ไข<br>ติดตั้งใหม่/ปรับปรุง | ✅ | From portal |
| `repair_date` | วันที่ | Date | | ✅ | creation |
| `name` | เลขที่ใบแจ้ง | Data | | ✅ | auto (naming_series) |
| `reported_by` | ชื่อผู้แจ้ง | Link | User | ✅ | frappe.session.user |
| `reporter_department` | แผนกผู้แจ้ง | Data | | | From User dept |
| `asset` | ชื่อเครื่องจักร/อุปกรณ์ | Link | Asset | ✅ | From QR scan |
| `item_code` | รหัสเครื่องจักร/อุปกรณ์ | Data | | | Fetch from asset |
| `repair_subject` | เรื่องที่แจ้งดำเนินการ | Data | | ✅ | From portal |
| `repair_description` | รายละเอียด/สิ่งที่ต้องดำเนินการ | HTML | | ✅ | From portal (3 textboxes) |
| `reporter_signature` | ลายเซ็นผู้แจ้ง | Signature | | ✅ | From portal |
| `issue_photos` | รูปถ่ายปัญหา | Attach Image | | ✅ (min 1) | From portal |

**GM Approval Fields** (in Section 1):
| Field Name | Thai Label | Fieldtype | Required | Auto-fill |
|-----------|-----------|-----------|----------|-----------|
| `gm_section1_approved_by` | GM ผู้อนุมัติเบื้องต้น | Link (User) | ✅ | frappe.session.user |
| `gm_section1_approval_date` | วันที่อนุมัติ | Datetime | ✅ | now() |
| `gm_section1_notes` | หมายเหตุ GM | Small Text | ❌ | Manual |

---

### SECTION 2: Engineering Department (ฝ่ายวิศวกรรม)

**Filled by:** Engineering Operator → Engineering Supervisor reviews
**Locked after:** GM Final Approval (State 5)

#### 2.1 Engineering Operator Fields:

| Field Name | Thai Label | Fieldtype | Options | Required |
|-----------|-----------|-----------|---------|----------|
| `action_type` | การดำเนินการ | Select | ช่างภายใน (Internal)<br>ช่างภายนอก (External)<br>มีค่าใช้จ่าย (With Cost)<br>ไม่มีค่าใช้จ่าย (No Cost) | ✅ |
| `engineering_todo_items` | รายการ/สิ่งที่ต้องทำ | Table | Engineering Todo Item | ✅ (min 1) |
| `spare_parts_used` | รายการอะไหล่ที่ใช้ | Table | Repair Spare Part | ⚠️ (use "-" if none) |
| `expected_duration_days` | ระยะเวลาดำเนินการ (วัน) | Int | | ✅ |
| `repair_start_date` | วันที่เริ่มต้น | Date | | ✅ |
| `repair_end_date` | วันที่สิ้นสุด | Date | | ✅ |
| `engineering_operator_signature` | ลายเซ็นผู้ประเมิน | Signature | | ✅ |
| `engineering_operator_sign_date` | วันที่ประเมิน | Datetime | | ✅ (auto) |

**Child Table: Engineering Todo Item**
| Field | Thai | Fieldtype | Required |
|-------|------|-----------|----------|
| `todo_item` | รายการ | Data | ✅ |
| `procedure` | การแก้ไข/การดำเนินงาน | Small Text | ✅ |
| `responsible_person` | ผู้ดำเนินงาน | Data | ✅ |
| `status` | สถานะ | Select (Pending/Completed) | ✅ |

**Child Table: Repair Spare Part** (ALREADY CREATED):
| Field | Thai | Fieldtype | Required |
|-------|------|-----------|----------|
| `item_no` | ลำดับ | Int | ✅ |
| `item_code` | รหัสอะไหล่ | Link (Item) | ✅ |
| `item_name` | รายการ | Data (fetch) | - |
| `purchase_order` | ใบขอซื้อ/เลขที่ | Link (PO) | ❌ |
| `qty` | จำนวน | Float | ✅ |
| `uom` | หน่วย | Link (UOM) | ✅ |
| `warehouse` | คลังสินค้า | Link | ❌ |
| `remarks` | หมายเหตุ | Small Text | ❌ |

#### 2.2 Engineering Supervisor Review:

| Field Name | Thai Label | Fieldtype | Required | Auto-fill |
|-----------|-----------|-----------|----------|-----------|
| `eng_supervisor_reviewed_by` | หัวหน้าช่างตรวจสอบ | Link (User) | ✅ | frappe.session.user |
| `eng_supervisor_review_date` | วันที่ตรวจสอบ | Datetime | ✅ | now() |
| `eng_supervisor_signature` | ลายเซ็นหัวหน้าช่าง | Signature | ✅ | Manual |

#### 2.3 GM Final Approval:

| Field Name | Thai Label | Fieldtype | Required | Auto-fill |
|-----------|-----------|-----------|----------|-----------|
| `gm_final_approved_by` | GM ผู้อนุมัติสุดท้าย | Link (User) | ✅ | frappe.session.user |
| `gm_final_approval_date` | วันที่อนุมัติสุดท้าย | Datetime | ✅ | now() |
| `gm_final_notes` | หมายเหตุ GM | Small Text | ❌ | Manual |

#### 2.4 Repair Completion:

| Field Name | Thai Label | Fieldtype | Required | Auto-fill |
|-----------|-----------|-----------|----------|-----------|
| `repair_completed_by` | ผู้ทำการซ่อมเสร็จ | Link (User) | ✅ | frappe.session.user |
| `completion_date` | วันที่ซ่อมเสร็จ | Datetime | ✅ | now() |
| `actions_performed` | รายละเอียดการซ่อม | Text | ✅ | Manual |

---

### SECTION 3: Reporter's Supervisor Verification (การตรวจสอบจากหัวหน้าแผนก)

**Filled by:** Reporter's Supervisor (e.g., Production Supervisor)
**Locked after:** Reporter Confirmation (State 9)

| Field Name | Thai Label | Fieldtype | Options | Required |
|-----------|-----------|-----------|---------|----------|
| `hygiene_status` | สถานะสุขลักษณะ | Select | เรียบร้อย/สะอาดไม่เสี่ยงต่อการปนเปื้อน<br>ไม่เรียบร้อย/ต้องแก้ไขเรื่อง... | ✅ |
| `hygiene_issue_notes` | หมายเหตุปัญหาสุขลักษณะ | Small Text | | Conditional (if not clean) |
| `cleanliness_before_machine` | ความสะอาดเครื่องจักรก่อนซ่อม | Select | สะอาด (Clean)<br>ไม่สะอาด (Not Clean) | ✅ |
| `cleanliness_after_machine` | ความสะอาดเครื่องจักรหลังซ่อม | Select | สะอาด<br>ไม่สะอาด | ✅ |
| `cleanliness_before_area` | ความสะอาดสถานที่ก่อนซ่อม | Select | สะอาด<br>ไม่สะอาด | ✅ |
| `cleanliness_after_area` | ความสะอาดสถานที่หลังซ่อม | Select | สะอาด<br>ไม่สะอาด | ✅ |
| `parts_inserted` | อุปกรณ์ที่นำเข้า | Table | Parts Inserted Item | ⚠️ (use "-" if none) |
| `parts_removed` | อุปกรณ์ที่นำออก | Table | Parts Removed Item | ⚠️ (use "-" if none) |
| `supervisor_verification_notes` | หมายเหตุเพิ่มเติม | Text | | ❌ |
| `supervisor_verified_by` | หัวหน้าแผนกตรวจรับงาน | Link (User) | ✅ | frappe.session.user |
| `supervisor_verification_date` | วันที่ตรวจรับ | Datetime | ✅ | now() |
| `supervisor_signature` | ลายเซ็นหัวหน้าแผนก | Signature | ✅ | Manual |

**Child Table: Parts Inserted Item** (ALREADY CREATED):
| Field | Thai | Fieldtype | Required |
|-------|------|-----------|----------|
| `item_code` | รหัส | Link (Item) | ✅ |
| `item_name` | ชื่ออุปกรณ์ | Data (fetch) | - |
| `qty` | จำนวน | Float | ✅ |
| `serial_no` | หมายเลขซีเรียล | Link | ❌ |

**Child Table: Parts Removed Item** (ALREADY CREATED):
| Field | Thai | Fieldtype | Required |
|-------|------|-----------|----------|
| `item_code` | รหัส | Link (Item) | ✅ |
| `item_name` | ชื่ออุปกรณ์ | Data (fetch) | - |
| `qty` | จำนวน | Float | ✅ |
| `serial_no` | หมายเลขซีเรียล | Link | ❌ |
| `disposal_method` | วิธีการทิ้ง | Select (ทิ้ง/ขาย/นำกลับไปซ่อม/เก็บไว้) | ✅ |

---

### PHASE 8: Reporter Confirmation (EXISTING - Need to enhance)

**Portal:** `/verify/:repairName` (VerifyRepair.jsx)
**Backend:** `tub_suite.api.maintenance.verify_repair_completion()`

**Current Fields Updated:**
- `verified_by` ✅ (already exists)
- `verification_date` ✅ (already exists)
- `verification_notes` ✅ (already exists)
- `verification_status` ✅ (already exists: "Verified - Passed" / "Verified - Failed")

**NEW Fields to Add for Phase 8:**
| Field Name | Thai Label | Fieldtype | Required | Source |
|-----------|-----------|-----------|----------|--------|
| `reporter_confirmed` | ผู้แจ้งยืนยัน | Check | ✅ | Portal |
| `reporter_confirmation_date` | วันที่ยืนยัน | Datetime | ✅ | now() |
| `reporter_confirmation_photos` | รูปถ่ายยืนยัน | Attach Image | ✅ (min 1) | Portal |
| `reporter_confirmation_notes` | หมายเหตุผู้แจ้ง | Small Text | ❌ | Portal |
| `reporter_satisfaction` | ความพึงพอใจ | Select (พอใจ/ไม่พอใจ) | ✅ | Portal |

**Portal Enhancement Needed:**
```jsx
// Add to VerifyRepair.jsx after line 40:
reporter_confirmed: true,
reporter_confirmation_date: now(),
reporter_confirmation_photos: photos,
reporter_confirmation_notes: notes,
reporter_satisfaction: satisfied ? 'พอใจ' : 'ไม่พอใจ'
```

---

## 🎭 Role-Based Access Control

### Role Definitions:

| Role | Can Do | Portal Access |
|------|--------|---------------|
| **Operator** | Report issues via QR scan | ✅ Report Issue card only |
| **Supervisor** (any dept) | Same as Operator + approve reports | ✅ Report Issue card only |
| **Maintenance User** | PM checks + report issues | ✅ PM tasks + Report Issue cards |
| **Engineering Team** | Fill Section 2, do repairs | ❌ ERPNext desk only |
| **Engineering Supervisor** | Review Section 2, mark complete | ❌ ERPNext desk only |
| **Maintenance Manager** | Approve repairs (legacy) | ❌ ERPNext desk only |
| **General Manager** | Approve Section 1 & final budget | ❌ ERPNext desk only |

### Portal Homepage Logic:

```javascript
// Home.jsx - Update handleQRScan()
const handleQRScan = (assetName) => {
  // If Maintenance User - show both PM + Report options
  if (userRoles.includes('Maintenance User')) {
    navigate(`/asset-options/${assetName}`)  // NEW PAGE
  }
  // If Operator/Supervisor - go straight to Report Issue
  else {
    navigate(`/report-issue/${assetName}`)   // NEW PAGE
  }
}
```

**NEW PAGE:** `/asset-options/:assetName`
Shows cards:
- 📋 PM Checklist → `/checklist/:assetName`
- 🚨 Report Issue → `/report-issue/:assetName`

**NEW PAGE:** `/report-issue/:assetName`
Form fields:
1. Repair Type (Select)
2. เรื่องที่แจ้ง (Data)
3. รายละเอียด (3 HTML textareas that combine into 1 field)
4. Reporter Signature
5. Photo Upload (min 1)

---

## ⚙️ Workflow States Configuration

### Update workflow.json:

```json
{
  "doctype": "Workflow",
  "document_type": "Asset Repair",
  "name": "Repair Approval WorkFlow",
  "states": [
    {
      "state": "Draft",
      "doc_status": "0",
      "allow_edit": "All",
      "update_field": "repair_status",
      "update_value": "Pending"
    },
    {
      "state": "Pending GM Approval - Section 1",
      "doc_status": "0",
      "allow_edit": "General Manager",
      "update_field": "repair_status",
      "update_value": "Pending"
    },
    {
      "state": "Pending Engineering Assessment",
      "doc_status": "0",
      "allow_edit": "Engineering Team",
      "update_field": "repair_status",
      "update_value": "Pending"
    },
    {
      "state": "Pending Engineering Supervisor Review",
      "doc_status": "0",
      "allow_edit": "Engineering Supervisor",
      "update_field": "repair_status",
      "update_value": "Pending"
    },
    {
      "state": "Pending GM Final Approval",
      "doc_status": "0",
      "allow_edit": "General Manager",
      "update_field": "repair_status",
      "update_value": "Pending"
    },
    {
      "state": "Approved for Repair",
      "doc_status": "0",
      "allow_edit": "Engineering Team",
      "update_field": "repair_status",
      "update_value": "In Progress"
    },
    {
      "state": "Repair In Progress",
      "doc_status": "0",
      "allow_edit": "Engineering Supervisor",
      "update_field": "repair_status",
      "update_value": "In Progress"
    },
    {
      "state": "Pending Reporter's Supervisor Verification",
      "doc_status": "0",
      "allow_edit": "All",  // Supervisor fills Section 3
      "update_field": "repair_status",
      "update_value": "In Progress"
    },
    {
      "state": "Pending Reporter Confirmation",
      "doc_status": "1",
      "allow_edit": "No One",  // Only portal can update
      "update_field": "repair_status",
      "update_value": "Completed"
    },
    {
      "state": "Finished",
      "doc_status": "1",
      "allow_edit": "No One",  // LOCKED FOREVER
      "update_field": "repair_status",
      "update_value": "Completed"
    },
    {
      "state": "Rejected",
      "doc_status": "0",
      "allow_edit": "No One",
      "update_field": "repair_status",
      "update_value": "Cancelled"
    }
  ],
  "transitions": [
    // Operator submits
    {
      "state": "Draft",
      "action": "Submit to GM",
      "next_state": "Pending GM Approval - Section 1",
      "allowed": "All"
    },
    // GM approves Section 1
    {
      "state": "Pending GM Approval - Section 1",
      "action": "Approve",
      "next_state": "Pending Engineering Assessment",
      "allowed": "General Manager"
    },
    // GM rejects Section 1
    {
      "state": "Pending GM Approval - Section 1",
      "action": "Reject",
      "next_state": "Rejected",
      "allowed": "General Manager"
    },
    // Engineering Operator submits assessment
    {
      "state": "Pending Engineering Assessment",
      "action": "Submit Assessment",
      "next_state": "Pending Engineering Supervisor Review",
      "allowed": "Engineering Team"
    },
    // Engineering Supervisor reviews
    {
      "state": "Pending Engineering Supervisor Review",
      "action": "Submit to GM",
      "next_state": "Pending GM Final Approval",
      "allowed": "Engineering Supervisor"
    },
    // GM final approval
    {
      "state": "Pending GM Final Approval",
      "action": "Approve",
      "next_state": "Approved for Repair",
      "allowed": "General Manager"
    },
    // GM rejects final
    {
      "state": "Pending GM Final Approval",
      "action": "Reject",
      "next_state": "Rejected",
      "allowed": "General Manager"
    },
    // Start repair
    {
      "state": "Approved for Repair",
      "action": "Start Repair",
      "next_state": "Repair In Progress",
      "allowed": "Engineering Team"
    },
    // Mark repair complete
    {
      "state": "Repair In Progress",
      "action": "Mark Complete",
      "next_state": "Pending Reporter's Supervisor Verification",
      "allowed": "Engineering Supervisor"
    },
    // Supervisor verifies Section 3
    {
      "state": "Pending Reporter's Supervisor Verification",
      "action": "Submit Verification",
      "next_state": "Pending Reporter Confirmation",
      "allowed": "All"  // Reporter's supervisor
    },
    // Reporter confirms (portal only - handled by API)
    {
      "state": "Pending Reporter Confirmation",
      "action": "Reporter Confirms",
      "next_state": "Finished",
      "allowed": "All"  // API handles permission check
    }
  ]
}
```

---

## 🔒 Python Validation Logic

### Update `asset_repair_override.py`:

```python
def validate_asset_repair(doc, method):
    """Enhanced validation for FM-EN-04 workflow"""

    workflow_state = doc.get("workflow_state")
    user_roles = frappe.get_roles()

    # Section 1: Lock after GM Approval
    if workflow_state not in ["Draft", "Pending GM Approval - Section 1"]:
        section1_fields = ["repair_type", "repair_subject", "repair_description",
                          "reporter_signature", "issue_photos"]
        if doc_has_changed(doc, section1_fields):
            frappe.throw(_("Section 1 is locked after GM approval"))

    # Section 2: Lock after GM Final Approval
    if workflow_state not in ["Pending Engineering Assessment",
                               "Pending Engineering Supervisor Review",
                               "Pending GM Final Approval"]:
        section2_fields = ["action_type", "engineering_todo_items",
                          "spare_parts_used", "expected_duration_days"]
        if doc_has_changed(doc, section2_fields):
            frappe.throw(_("Section 2 is locked after GM final approval"))

    # Section 3: Lock after Reporter Confirmation
    if workflow_state == "Finished":
        frappe.throw(_("Document is finished and cannot be edited. Create new repair if needed."))

    # Role-based field restrictions
    is_gm = "General Manager" in user_roles
    is_eng_operator = "Engineering Team" in user_roles
    is_eng_supervisor = "Engineering Supervisor" in user_roles

    # GM can only edit approval fields
    if is_gm and not is_eng_operator:
        allowed_gm_fields = ["gm_section1_approved_by", "gm_section1_approval_date",
                             "gm_section1_notes", "gm_final_approved_by",
                             "gm_final_approval_date", "gm_final_notes"]
        if doc_has_changed_fields_except(doc, allowed_gm_fields):
            frappe.throw(_("GM can only edit approval fields"))

    # Engineering Operator cannot edit Section 1 or Section 3
    if is_eng_operator and not is_gm:
        if doc_has_changed(doc, section1_fields + section3_fields):
            frappe.throw(_("Engineering team cannot edit Section 1 or Section 3"))
```

---

## 📱 Portal Implementation

### File Structure:
```
maintenance-react-dev/src/
├── pages/
│   ├── Home.jsx                    (UPDATE - add role-based routing)
│   ├── AssetOptions.jsx            (NEW - for Maintenance User)
│   ├── ReportIssue.jsx             (NEW - report form)
│   ├── Checklist.jsx               (KEEP - PM checklist)
│   └── VerifyRepair.jsx            (UPDATE - add Phase 8 fields)
├── services/
│   └── api.js                      (UPDATE - add reportIssue())
└── App.jsx                         (UPDATE - add new routes)
```

### API Additions Needed:

```javascript
// api.js - Add this method
reportIssue: (params) =>
  callAPI('tub_suite.api.maintenance.create_operator_repair_request', params)
```

### Backend API Needed:

```python
# tub_suite/api/maintenance.py

@frappe.whitelist()
def create_operator_repair_request(
    asset_name,
    repair_type,
    repair_subject,
    repair_description,  # Combines 3 textboxes
    reporter_signature,
    issue_photos
):
    """
    Create Asset Repair from Operator report

    Returns:
        repair_id: ACC-ASR-2026-00123
    """

    # Validate Operator/Supervisor role
    user_roles = frappe.get_roles()
    if not any(role in user_roles for role in ["Operator", "Supervisor"]):
        frappe.throw(_("Only Operators/Supervisors can report issues"))

    # Create repair
    repair = frappe.get_doc({
        "doctype": "Asset Repair",
        "asset": asset_name,
        "repair_type": repair_type,
        "repair_subject": repair_subject,
        "repair_description": repair_description,
        "reported_by": frappe.session.user,
        "reporter_signature": reporter_signature,
        "failure_date": now(),
        "workflow_state": "Draft",
        "repair_status": "Pending"
    })

    # Attach photos
    for photo_url in issue_photos:
        attach_photo_to_doc("Asset Repair", repair.name, photo_url)

    repair.insert()

    # Auto-submit to GM
    repair.workflow_state = "Pending GM Approval - Section 1"
    repair.save()

    return {"repair_id": repair.name}
```

---

## 🖨️ Print Format Design

### Create: `asset_repair_fm_en_04.html`

**Structure:**
```html
<div class="fm-en-04">
  <header>
    <h1>ใบแจ้งซ่อม/ติดตั้งใหม่ (FM-EN-04 rev.00)</h1>
    <div class="doc-info">
      <span>เลขที่: {{ doc.name }}</span>
      <span>วันที่: {{ doc.repair_date }}</span>
    </div>
  </header>

  <!-- Section 1 -->
  <section class="section-1">
    <h2>Section 1: ข้อมูลเครื่องจักรและผู้แจ้งซ่อม</h2>
    <table>
      <tr>
        <td>ประเภท:</td>
        <td>{{ doc.repair_type }}</td>
      </tr>
      <!-- All Section 1 fields -->
    </table>

    {% if doc.gm_section1_approved_by %}
    <div class="approval-box">
      <strong>GM Approval:</strong> {{ doc.gm_section1_approved_by }}
      <br>Date: {{ doc.gm_section1_approval_date }}
    </div>
    {% endif %}
  </section>

  <!-- Section 2 -->
  <section class="section-2"
           style="{% if doc.workflow_state in ['Draft', 'Pending GM Approval - Section 1'] %}display:none{% endif %}">
    <h2>Section 2: ฝ่ายวิศวกรรม</h2>
    <!-- Section 2 fields -->
  </section>

  <!-- Section 3 -->
  <section class="section-3"
           style="{% if doc.workflow_state not in ['Pending Reporter Confirmation', 'Finished'] %}display:none{% endif %}">
    <h2>Section 3: การตรวจสอบจากหัวหน้าแผนก</h2>
    <!-- Section 3 fields -->
  </section>
</div>
```

---

## 📊 Implementation Phases

### Phase 1: Core Structure (Week 1)
- ✅ Create 3 child doctypes (DONE)
- ✅ Add basic custom fields (DONE)
- ⏳ Add ALL remaining fields from Sections 1, 2, 3
- ⏳ Add Phase 8 reporter confirmation fields
- ⏳ Test field creation locally

### Phase 2: Workflow & Validation (Week 2)
- Update workflow.json with 10 states
- Implement Python validation logic
- Add role checks
- Test state transitions locally

### Phase 3: Portal (Week 3)
- Create ReportIssue.jsx page
- Create AssetOptions.jsx page
- Update Home.jsx routing logic
- Add backend API for operator reports
- Enhance VerifyRepair.jsx for Phase 8
- Test end-to-end on local

### Phase 4: Print Format & Testing (Week 4)
- Design FM-EN-04 print format
- Add Thai/English translations
- Complete integration testing
- Deploy to staging (if available)
- User acceptance testing
- Document everything

---

## ✅ Testing Checklist

### Unit Tests:
- [ ] Field creation (no errors)
- [ ] Workflow state transitions
- [ ] Section locking validation
- [ ] Role-based edit restrictions
- [ ] Auto-status changes
- [ ] Portal routing by role

### Integration Tests:
- [ ] Operator creates repair → GM approves
- [ ] Engineering assessment → Supervisor review → GM final
- [ ] Repair completion → Supervisor verification → Reporter confirmation
- [ ] PM User discovers issue during checklist → same flow
- [ ] Photo attachments at each phase
- [ ] Print format displays correctly for each state

### User Acceptance:
- [ ] Operator can report (no PM access)
- [ ] Maintenance User sees both PM + Report
- [ ] GM can approve without editing other fields
- [ ] Engineering team fills Section 2 properly
- [ ] Reporter's supervisor can verify
- [ ] Original reporter can confirm fix
- [ ] Print matches physical FM-EN-04 form

---

## 🚨 Risk Mitigation

### Critical Risks:

| Risk | Impact | Mitigation |
|------|--------|------------|
| Break existing repairs | 🔴 HIGH | Test on local first, backup DB, rollback plan |
| Wrong role permissions | 🟡 MEDIUM | Careful role checks, test each transition |
| Section locking breaks workflow | 🟡 MEDIUM | Python validation with clear error messages |
| Portal routing confusion | 🟢 LOW | Clear UI, role-based cards, Thai/English help |

### Rollback Plan:
1. Git revert all changes
2. Restore database from backup
3. Document what went wrong
4. Re-plan and re-test

---

## 📝 Questions to Resolve

### Section Locking:
**User said:** "nobody should be able to edit, should they duplicate and create a new doc for it instead of editing????"

**My answer:** YES - After Finished state, create NEW repair doc if changes needed. This maintains audit trail.

**Implementation:** Show "Create Corrected Repair" button on Finished docs that:
- Copies relevant data
- Creates new draft
- Links to original via custom field `corrects_repair_id`

### Repair Status Auto-Change:
**User asked:** "it should be auto-change but how can engineering supervisor confirm for the fix?"

**My answer:**
- Auto-status based on workflow state
- Engineering Supervisor manually clicks "Mark Complete" button
- This triggers transition: Repair In Progress → Pending Supervisor Verification
- Status auto-changes from "In Progress" → "Completed"

---

## 🎯 Success Metrics

### Must Achieve:
✅ Zero data loss or corruption
✅ All existing repairs remain functional
✅ Operators can report without PM access
✅ Complete audit trail (who did what when)
✅ Print format matches FM-EN-04 exactly
✅ Thai + English throughout

### Nice to Have:
- Mobile-optimized CSS
- Photo thumbnails in list view
- Notification emails at each state
- Repair history timeline view

---

## 📚 Next Steps

1. **Review this document with user** - Confirm all understanding is correct
2. **Get approval to proceed** - Do not code until user confirms
3. **Implement Phase 1 fields** - Add all remaining fields to custom_field.json
4. **Test locally on `tub` site** - bench migrate and verify
5. **One phase at a time** - Do not rush, test each phase

---

**Document Version:** 1.0
**Last Updated:** 2026-01-08
**Status:** Awaiting user confirmation before implementation

