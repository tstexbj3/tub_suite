# PM Issue Reporting - Complete System Guide
## TUB Suite v2.1.0

**Last Updated:** 2026-01-25
**Status:** Production System
**Purpose:** Complete reference for PM (Planned Maintenance) issue reporting workflow

---

## CRITICAL UNDERSTANDING

### What This System Does

**When a Maintenance User finds a problem during a PM task inspection:**

1. User reports issue from mobile portal (Checklist.jsx)
2. System creates **Asset Repair** document directly (NOT a separate PM Issue Report)
3. Asset Repair starts in **Draft** state with `repair_status: "Draft"`
4. Maintenance Supervisor receives email notification
5. Supervisor opens repair in ERPNext desk
6. Supervisor reviews and submits to workflow (Supervisor Verify)
7. Repair continues through normal Asset Repair workflow
8. At end, Supervisor verifies completion (NO reporter confirmation for PM issues)

### What This System DOES NOT Do

❌ Does NOT create a "PM Issue Report" DocType record
❌ Does NOT use two-step approval (PM Report → Asset Repair)
❌ Does NOT require reporter confirmation for PM issues
❌ Portal users do NOT see PM-reported repairs in their verification queue

---

## System Architecture

### Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    MOBILE PORTAL                             │
│  Maintenance User scans asset → Opens PM checklist          │
│                                                              │
│  ┌────────────────────────────────────────────┐             │
│  │  Checklist.jsx                              │             │
│  │  - Shows PM tasks (Daily/Weekly/Monthly)    │             │
│  │  - User finds issue during inspection       │             │
│  │  - Clicks "Report Issue" button             │             │
│  │                                              │             │
│  │  Issue Report Form Shows:                   │             │
│  │  ├─ เรื่องที่แจ้ง (repair_subject) *        │             │
│  │  ├─ ประเภทการซ่อม (repair_type) *          │             │
│  │  │  Options:                                 │             │
│  │  │  - ซ่อม (Repair)                          │             │
│  │  │  - แก้ไข (Fix/Correction)                 │             │
│  │  │  - ติดตั้งใหม่ (New Installation)          │             │
│  │  │  - ปรับปรุง (Improvement)                  │             │
│  │  │  - ซ่อมบำรุงตามแผน (Planned Maintenance)  │             │
│  │  │  - อื่นๆ (Other)                          │             │
│  │  ├─ รายละเอียดปัญหา (issue_description)     │             │
│  │  └─ Photos (issue_photos) - minimum 2      │             │
│  │                                              │             │
│  │  [Submit Task Button]                       │             │
│  └────────────────────────────────────────────┘             │
│                       │                                       │
│                       │ API Call                              │
│                       ↓                                       │
└───────────────────────┼───────────────────────────────────────┘
                        │
                        │
┌───────────────────────┼───────────────────────────────────────┐
│               BACKEND API                                      │
│                       │                                       │
│  ┌────────────────────▼──────────────────────┐               │
│  │  submit_maintenance_task()                │               │
│  │  (tub_suite/api/maintenance.py:13-180)   │               │
│  │                                            │               │
│  │  Parameters received:                     │               │
│  │  - maintenance_name                        │               │
│  │  - task_name                               │               │
│  │  - asset_name                              │               │
│  │  - has_issue = 1                           │               │
│  │  - repair_subject (from portal)            │               │
│  │  - repair_type (from portal)               │               │
│  │  - issue_description                       │               │
│  │  - issue_photos[]                          │               │
│  │                                            │               │
│  │  Line 109: if has_issue:                   │               │
│  │  Line 117-129: Create Asset Repair:       │               │
│  │  {                                         │               │
│  │    "doctype": "Asset Repair",              │               │
│  │    "asset": asset_name,                    │               │
│  │    "failure_date": now(),                  │               │
│  │    "description": issue_description,       │               │
│  │    "repair_subject": repair_subject OR     │               │
│  │                      f"PM Issue: {task}",  │  ← Default    │
│  │    "repair_type": repair_type OR "ซ่อม",   │  ← Default    │
│  │    "repair_source": "Planned Maintenance   │               │
│  │                      (ตามแผน)",            │  ← Fixed value│
│  │    "repair_status": "Draft",               │  ← CRITICAL!  │
│  │    "reported_by": frappe.session.user,     │               │
│  │    "reporter_department": user_dept,       │               │
│  │    "maintenance_task": task_label          │               │
│  │  }                                         │               │
│  │                                            │               │
│  │  Line 130: repair.insert()                 │               │
│  │                                            │               │
│  │  Line 134-136: Attach photos to repair    │               │
│  │                                            │               │
│  │  Line 140-159: Notify Maintenance          │               │
│  │                Supervisor via email        │               │
│  └────────────────────────────────────────────┘               │
│                       │                                       │
└───────────────────────┼───────────────────────────────────────┘
                        │
                        │
┌───────────────────────▼───────────────────────────────────────┐
│               ERPNEXT DESK                                     │
│                                                               │
│  ┌──────────────────────────────────────────┐                │
│  │  Maintenance Supervisor                   │                │
│  │  - Receives email notification            │                │
│  │  - Opens Asset Repair in Draft state      │                │
│  │  - Reviews details:                       │                │
│  │    * Asset                                 │                │
│  │    * repair_subject                        │                │
│  │    * repair_type                           │                │
│  │    * Issue photos                          │                │
│  │    * Reported by                           │                │
│  │  - Can add notes                           │                │
│  │  - Clicks "Supervisor Verify" button       │                │
│  │  - Repair moves to "Pending GM Approval    │                │
│  │    Section 1"                              │                │
│  └──────────────────────────────────────────┘                │
│                       │                                       │
│                       ↓                                       │
│  ┌──────────────────────────────────────────┐                │
│  │  Normal Asset Repair Workflow             │                │
│  │  Draft → GM Approval → Engineering →      │                │
│  │  → Supervisor Review → GM Final Approval   │                │
│  │  → Approved for Repair → Finished         │                │
│  └──────────────────────────────────────────┘                │
│                       │                                       │
│                       ↓                                       │
│  ┌──────────────────────────────────────────┐                │
│  │  Supervisor Verification                  │                │
│  │  - Repair at "Pending Supervisor          │                │
│  │    Verification" state                    │                │
│  │  - Supervisor verifies completion          │                │
│  │  - NO reporter confirmation (PM issues)    │                │
│  │  - Goes directly to Finished               │                │
│  └──────────────────────────────────────────┘                │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## Critical Code Locations

### 1. Portal Frontend - Issue Reporting Form

**File:** `maintenance-react-dev/src/pages/Checklist.jsx`

**Lines 250-297: Issue Report Fields (shown when hasIssue = true)**

```jsx
{hasIssue && (
  <>
    {/* Issue Description */}
    <div className="form-group">
      <label>{t('issue_description')}</label>
      <textarea
        placeholder={t('issue_description')}
        value={issueDesc}
        onChange={(e) => setIssueDesc(e.target.value)}
        rows="4"
      />
    </div>

    {/* Repair Subject - เรื่องที่แจ้ง */}
    <div className="form-group">
      <label>เรื่องที่แจ้ง (Repair Subject) *</label>
      <input
        type="text"
        placeholder="ระบุเรื่องที่แจ้ง เช่น ปั้มน้ำเสีย, มอเตอร์ไม่ทำงาน"
        value={repairSubject}
        onChange={(e) => setRepairSubject(e.target.value)}
        required
      />
    </div>

    {/* Repair Type - ประเภทการซ่อม */}
    <div className="form-group">
      <label>ประเภทการซ่อม (Repair Type) *</label>
      <select
        value={repairType}
        onChange={(e) => setRepairType(e.target.value)}
        required
      >
        <option value="">-- เลือกประเภทการซ่อม --</option>
        <option value="ซ่อม (Repair)">ซ่อม (Repair)</option>
        <option value="แก้ไข (Fix/Correction)">แก้ไข (Fix/Correction)</option>
        <option value="ติดตั้งใหม่ (New Installation)">ติดตั้งใหม่ (New Installation)</option>
        <option value="ปรับปรุง (Improvement)">ปรับปรุง (Improvement)</option>
        <option value="ซ่อมบำรุงตามแผน (Planned Maintenance)">ซ่อมบำรุงตามแผน (Planned Maintenance)</option>
        <option value="อื่นๆ (Other)">อื่นๆ (Other)</option>
      </select>
    </div>
  </>
)}
```

**Lines 82-90: Frontend Validation**

```jsx
if (hasIssue && !repairSubject.trim()) {
  alert('Please provide repair subject / กรุณาระบุเรื่องที่แจ้ง')
  return
}

if (hasIssue && !repairType) {
  alert('Please select repair type / กรุณาเลือกประเภทการซ่อม')
  return
}
```

**Lines 93-104: API Call**

```jsx
const response = await api.submitTask({
  maintenance_name: selectedTask.parent,
  task_name: selectedTask.name,
  asset_name: assetName,
  has_issue: hasIssue ? 1 : 0,
  notes,
  issue_description: issueDesc,
  repair_subject: repairSubject,  // Sent to backend
  repair_type: repairType,        // Sent to backend
  inspection_photos: hasIssue ? [] : photos,
  issue_photos: hasIssue ? photos : []
})
```

---

### 2. Backend API - Asset Repair Creation

**File:** `tub_suite/api/maintenance.py`

**Lines 13-16: Function Signature**

```python
@frappe.whitelist()
def submit_maintenance_task(maintenance_name, task_name, asset_name, has_issue=0,
                      issue_description="", notes="", inspection_photos=None,
                      issue_photos=None, before_photo=None, after_photo=None,
                      repair_subject="", repair_type=""):  # ← PM fields
```

**Lines 109-130: Asset Repair Creation (PM Issues Only)**

```python
if has_issue:
    # Get task details to populate maintenance_task field
    task_doc = frappe.get_doc("Asset Maintenance Task", task_name)
    task_label = task_doc.maintenance_task or task_doc.task_name or "Unnamed Task"

    # Get user's department
    user_dept = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "department") or None

    repair = frappe.get_doc({
        "doctype": "Asset Repair",
        "asset": asset_name,
        "failure_date": frappe.utils.now(),
        "description": issue_description,

        # CRITICAL: Default values for PM issues
        "repair_subject": repair_subject or f"PM Issue: {task_label}",
        "repair_type": repair_type or "ซ่อม",

        # Fixed values for PM issues
        "repair_source": "Planned Maintenance (ตามแผน)",
        "repair_status": "Draft",  # ← MUST BE "Draft", NOT "Pending"!

        # Tracking fields
        "reported_by": frappe.session.user,
        "reporter_department": user_dept,
        "maintenance_task": task_label
    })
    repair.insert(ignore_permissions=True)
    repair_name = repair.name
```

**WHY "Draft" NOT "Pending":**
- `repair_status` field options: "Pending", "Under Repair", "Completed", "Cancelled"
- "Draft" is NOT in the options but is the workflow_state
- Setting `repair_status: "Draft"` actually doesn't set the field (invalid value)
- The workflow_state starts as NULL for docstatus=0 documents
- Workflow assigns `workflow_state: "Draft"` when supervisor submits

**Lines 134-136: Attach Issue Photos**

```python
# Attach issue photos to repair request
for idx, photo_url in enumerate(issue_photos):
    if photo_url:
        attach_file_to_doc("Asset Repair", repair.name, photo_url, f"Issue Photo {idx + 1}")
```

**Lines 140-159: Notify Maintenance Supervisor**

```python
try:
    supervisors = frappe.get_all("Has Role",
        filters={"role": "Maintenance Supervisor", "parenttype": "User"},
        fields=["parent"]
    )
    for supervisor in supervisors:
        frappe.sendmail(
            recipients=[supervisor.parent],
            subject=f"New PM Issue Reported: {repair_subject}",
            message=f"""
                <p><strong>New PM Issue Reported</strong></p>
                <p>Asset: {asset_name}</p>
                <p>Task: {task_label}</p>
                <p>Subject: {repair_subject}</p>
                <p>Type: {repair_type}</p>
                <p>Repair ID: {repair.name}</p>
                <p>Please review and verify in ERPNext.</p>
            """
        )
except Exception as e:
    frappe.logger().error(f"Failed to notify Maintenance Supervisor: {str(e)}")
```

---

### 3. Asset Repair Workflow Configuration

**File:** `tub_suite/fixtures/workflow.json`

**Workflow Name:** "Asset Repair Workflow - Supervisor Only"

**States:**
```
1. Draft (docstatus=0)
   - Allowed roles: Supervisor, Maintenance Supervisor
   - Can edit all fields

2. Pending GM Approval Section 1 (docstatus=0)
   - Allowed roles: Maintenance Manager

3. Pending Engineering Assessment (docstatus=0)
   - Allowed roles: Engineering Team

4. Pending Engineering Supervisor Review (docstatus=0)
   - Allowed roles: Engineering Supervisor

5. Pending GM Final Approval (docstatus=0)
   - Allowed roles: Maintenance Manager

6. Approved for Repair (docstatus=0)
   - Allowed roles: Engineering Supervisor

7. Pending Supervisor Verification (docstatus=0)
   - Allowed roles: Supervisor, Maintenance Supervisor

8. Pending Reporter Confirmation (docstatus=1)
   - Allowed roles: Supervisor, Maintenance Supervisor
   - NOTE: PM issues skip this for supervisor-reported issues

9. Finished (docstatus=1)

10. Rejected (docstatus=0)

11. Cancelled (docstatus=2)
```

**Transitions:**
```
Draft → Supervisor Verify → Pending GM Approval Section 1
Pending GM Approval Section 1 → GM Approve Section 1 → Pending Engineering Assessment
Pending GM Approval Section 1 → GM Reject → Rejected
Pending Engineering Assessment → Engineering Assessment Complete → Pending Engineering Supervisor Review
Pending Engineering Supervisor Review → Supervisor Review Complete → Pending GM Final Approval
Pending GM Final Approval → GM Final Approve → Approved for Repair
Pending GM Final Approval → GM Request Changes → Pending Engineering Assessment
Approved for Repair → Finish Repair → Pending Supervisor Verification
Pending Supervisor Verification → Supervisor Verify → Pending Reporter Confirmation
Pending Supervisor Verification → Supervisor Reject → Approved for Repair
Pending Reporter Confirmation → Reporter Confirm → Finished
```

---

## Field Reference

### Asset Repair DocType Custom Fields

**PM-Specific Fields:**
```
repair_subject (Data)
├─ Label: เรื่องที่แจ้ง / Repair Subject
├─ Required: Yes (for PM issues)
├─ Example: "ปั้มน้ำเสีย", "มอเตอร์ไม่ทำงาน"
└─ Source: Portal form input

repair_type (Select)
├─ Label: ประเภทการซ่อม / Repair Type
├─ Required: Yes (for PM issues)
├─ Options:
│  ├─ ซ่อม (Repair)
│  ├─ แก้ไข (Fix/Correction)
│  ├─ ติดตั้งใหม่ (New Installation)
│  ├─ ปรับปรุง (Improvement)
│  ├─ ซ่อมบำรุงตามแผน (Planned Maintenance)
│  └─ อื่นๆ (Other)
├─ Default for PM: "ซ่อม"
└─ Source: Portal dropdown

repair_source (Select)
├─ Label: แหล่งที่มา / Repair Source
├─ Options:
│  ├─ Portal (แจ้งผ่านระบบ) - for standalone reports
│  ├─ Manual (แจ้งด้วยตนเอง) - for desk-created
│  └─ Planned Maintenance (ตามแผน) - for PM issues ← ALWAYS this for PM
└─ Fixed value for PM: "Planned Maintenance (ตามแผน)"

repair_status (Select)
├─ Label: Repair Status
├─ Options:
│  ├─ Pending
│  ├─ Under Repair
│  ├─ Completed
│  └─ Cancelled
├─ Initial value: "Draft" (actually invalid, relies on workflow_state)
└─ NOTE: This field is NOT the same as workflow_state!

maintenance_task (Data)
├─ Label: Maintenance Task
├─ Value: Task label from PM checklist
├─ Example: "Check oil level", "Inspect belts"
└─ Used to link repair back to originating PM task

reported_by (Link to User)
├─ Label: Reported By
├─ Value: frappe.session.user (portal user's email)
├─ Used for tracking original reporter
└─ NOTE: For PM issues, this is the Maintenance User, but they DON'T confirm

reporter_department (Link to Department)
├─ Label: Reporter Department
├─ Value: Retrieved from Employee doctype
├─ Query: Employee.department WHERE Employee.user_id = reported_by
└─ May be NULL if employee record not found
```

---

## Common Issues and Solutions

### Issue 1: "Repair Status cannot be 'Draft'" Validation Error

**Error Message:**
```
frappe.exceptions.ValidationError: Repair Status cannot be "Draft".
It should be one of "Pending", "Under Repair", "Completed", "Cancelled"
```

**Root Cause:**
- Code had `"repair_status": "Pending"` instead of `"repair_status": "Draft"`
- The field `repair_status` has options that don't include "Draft"
- Setting it to "Pending" triggers validation error

**Fix:**
```python
# WRONG - causes validation error
"repair_status": "Pending"

# CORRECT - "Draft" is invalid but ignored, workflow_state handles it
"repair_status": "Draft"
```

**Location to Fix:** `tub_suite/api/maintenance.py` line 125

---

### Issue 2: Frontend Fields Not Showing

**Symptoms:**
- User clicks "Report Issue" on portal
- repair_subject and repair_type fields don't appear
- Only issue_description and photos show

**Root Cause:**
- React app not rebuilt after code changes
- Browser serving stale cached JavaScript

**Fix:**
```bash
cd ~/frappe-bench/apps/tub_suite/maintenance-react-dev
npm run build
cd ~/frappe-bench
bench clear-cache
bench restart
```

**Verification:**
- Check `tub_suite/public/maintenance/assets/index.js` modification time
- Should be recent (after your changes)
- Clear browser cache: Ctrl+Shift+R (hard reload)

---

### Issue 3: Empty repair_subject or repair_type Causing MandatoryError

**Error Message:**
```
frappe.exceptions.MandatoryError: [Asset Repair, ACC-ASR-2026-00026]: repair_subject
```

**Root Cause:**
- Portal sends empty strings `""` when user doesn't fill fields
- Python treats `""` as falsy, so field appears empty
- Asset Repair DocType has these as mandatory fields

**Fix:**
Add default values in backend:
```python
# Before fix - empty strings cause error
"repair_subject": repair_subject,
"repair_type": repair_type,

# After fix - provide defaults
"repair_subject": repair_subject or f"PM Issue: {task_label}",
"repair_type": repair_type or "ซ่อม",
```

**Location:** `tub_suite/api/maintenance.py` lines 122-123

---

### Issue 4: Python Code Changes Not Loading

**Symptoms:**
- Changed code in maintenance.py
- Restarted bench multiple times
- Old code still executing
- inspect.getsource() shows new code but errors show old behavior

**Root Cause:**
- Python bytecode (.pyc files) cached
- Gunicorn workers not reloading
- __pycache__ directories persisting

**Fix:**
```bash
# Delete all Python cache
find ~/frappe-bench/apps/tub_suite -type f -name "*.pyc" -delete
find ~/frappe-bench/apps/tub_suite -type d -name "__pycache__" -exec rm -rf {} +

# Force reload
bench clear-cache
bench restart

# Verify no cache remains
find ~/frappe-bench/apps/tub_suite/tub_suite/api -name "*.pyc"
# Should return nothing
```

---

### Issue 5: Maintenance User Can Edit Draft Repairs

**Symptoms:**
- Maintenance User creates repair via portal
- User can still open and edit the repair in ERPNext desk
- Should be restricted to Maintenance Supervisor only

**Root Cause:**
- Draft repairs have `workflow_state = NULL` (not "Draft")
- Validation code allows editing when `workflow_state` is NULL
- Only enters workflow when Supervisor clicks "Supervisor Verify"

**Expected Behavior:**
- Maintenance User creates repair via portal API (ignore_permissions=True)
- Repair is in Draft state but NOT in workflow yet
- Maintenance Supervisor opens and submits (enters workflow)
- After submission, workflow permissions take over

**This is by design** - PM issues bypass normal workflow entry to allow portal submission without desk permissions.

---

## Testing Checklist

### End-to-End PM Issue Reporting Test

**Prerequisites:**
- [ ] Maintenance User account created with role "Maintenance User"
- [ ] Maintenance Supervisor account with role "Maintenance Supervisor"
- [ ] Asset with PM schedule configured
- [ ] PM tasks created (Daily/Weekly/Monthly)
- [ ] Portal accessible at /portal/maintenance

**Test Steps:**

1. **Portal Login**
   - [ ] Login as Maintenance User
   - [ ] Navigate to /portal/maintenance
   - [ ] Scan QR code or search for asset
   - [ ] Asset checklist loads successfully

2. **Issue Reporting**
   - [ ] Click "Report Issue" checkbox
   - [ ] Verify fields appear:
     - [ ] เรื่องที่แจ้ง (Repair Subject) - text input
     - [ ] ประเภทการซ่อม (Repair Type) - dropdown with 6 options
     - [ ] รายละเอียดปัญหา (Issue Description) - textarea
     - [ ] Photo upload (minimum 2 required)
   - [ ] Fill in repair subject: "Test PM Issue - Water Pump Leaking"
   - [ ] Select repair type: "แก้ไข (Fix/Correction)"
   - [ ] Enter description: "Found water leak under pump during inspection"
   - [ ] Upload 2 photos
   - [ ] Click "Submit Task"
   - [ ] Verify success message appears

3. **Backend Verification**
   - [ ] Open ERPNext desk
   - [ ] Go to Asset Repair list
   - [ ] Find newest repair (sort by Created date)
   - [ ] Verify fields:
     - [ ] asset = correct asset name
     - [ ] repair_subject = "Test PM Issue - Water Pump Leaking"
     - [ ] repair_type = "แก้ไข (Fix/Correction)"
     - [ ] repair_source = "Planned Maintenance (ตามแผน)"
     - [ ] repair_status = "Draft"
     - [ ] workflow_state = NULL (not in workflow yet)
     - [ ] reported_by = Maintenance User email
     - [ ] maintenance_task = correct task name
   - [ ] Verify 2 photos attached

4. **Supervisor Notification**
   - [ ] Check Maintenance Supervisor email
   - [ ] Verify notification received with:
     - [ ] Subject: "New PM Issue Reported: Test PM Issue - Water Pump Leaking"
     - [ ] Asset name
     - [ ] Task name
     - [ ] Repair ID
     - [ ] Link to repair (optional)

5. **Supervisor Review**
   - [ ] Login as Maintenance Supervisor
   - [ ] Open the Asset Repair in desk
   - [ ] Review all fields and photos
   - [ ] Add supervisor notes (optional)
   - [ ] Click "Supervisor Verify" button
   - [ ] Repair moves to "Pending GM Approval Section 1"
   - [ ] workflow_state now = "Pending GM Approval Section 1"

6. **Workflow Progression**
   - [ ] GM approves (Section 1)
   - [ ] Engineering assesses
   - [ ] Engineering Supervisor reviews
   - [ ] GM final approval
   - [ ] Engineer marks "Finish Repair"
   - [ ] Supervisor verifies completion
   - [ ] Repair goes to Finished (skips Reporter Confirmation for PM)

**Expected Results:**
- ✅ Asset Repair created with all PM fields populated
- ✅ Supervisor notified via email
- ✅ Repair progresses through workflow
- ✅ No errors in console or logs
- ✅ Photos attached correctly
- ✅ Reporter tracking accurate

---

## Deployment Guide

### Files to Deploy

**Backend:**
```
tub_suite/api/maintenance.py
tub_suite/overrides/asset_repair_override.py
tub_suite/fixtures/workflow.json
```

**Frontend:**
```
maintenance-react-dev/src/pages/Checklist.jsx
tub_suite/public/maintenance/assets/index.js (built output)
tub_suite/public/maintenance/assets/index.css (built output)
```

### Deployment Steps

**1. Pull Latest Code:**
```bash
cd ~/frappe-bench/apps/tub_suite
git pull origin v2.1.0
```

**2. Rebuild React Portal:**
```bash
cd ~/frappe-bench/apps/tub_suite/maintenance-react-dev
npm run build
```

**3. Clear Cache:**
```bash
cd ~/frappe-bench
bench --site tub clear-cache
```

**4. Delete Python Cache:**
```bash
find ~/frappe-bench/apps/tub_suite -type f -name "*.pyc" -delete
find ~/frappe-bench/apps/tub_suite -type d -name "__pycache__" -exec rm -rf {} +
```

**5. Restart Bench:**
```bash
bench restart
```

**6. Verify Workflow Configuration:**
- Go to: Workflow List
- Find: "Asset Repair Workflow - Supervisor Only"
- Verify: Is Active = ✅
- Verify: All states and transitions present

**7. Verify Permissions:**
- Go to: Role Permission Manager
- Select: Asset Repair
- Verify: Maintenance Supervisor has Read, Write, Create, Submit permissions

**8. Test End-to-End:**
- Follow testing checklist above
- Verify all steps complete successfully

---

## Maintenance and Monitoring

### Daily Checks
- [ ] Check for PM issues in Draft state > 24 hours old
- [ ] Verify Maintenance Supervisor email delivery
- [ ] Review error logs for PM submission failures

### Weekly Checks
- [ ] Audit PM-reported repairs vs completed repairs
- [ ] Verify asset repair_source tagging accuracy
- [ ] Check for orphaned PM tasks (issue reported but not in repair workflow)

### Monthly Checks
- [ ] Review PM issue types breakdown
- [ ] Analyze response time: Report → Supervisor Review → Completion
- [ ] Update documentation with new edge cases

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v2.1.0 | 2026-01-22 | Initial PM workflow with Maintenance Supervisor role |
| v2.1.1 | 2026-01-25 | Fixed repair_status "Draft" vs "Pending" issue, added defaults for empty fields |

---

## Support and Troubleshooting

**For Issues:**
1. Check this guide first
2. Review error logs: `~/frappe-bench/sites/tub/logs/`
3. Verify bench restart completed successfully
4. Check browser console for frontend errors
5. Clear all caches (Python, bench, browser)

**Contact:**
- Development Team: it@tipubon.com
- System Administrator: [contact info]

---

**END OF GUIDE**
