# PM Workflow Implementation (2026-01-22)

## Overview
Implemented workflow for Maintenance Users to report issues during PM tasks, with Maintenance Supervisor verification.

## Changes Made

### 1. New Role: Maintenance Supervisor
**Created role:** `Maintenance Supervisor`
- Separate from existing "Supervisor" role
- Handles PM issue verification AND repair completion verification

**Permissions:**
- Asset Repair: Read, Write, Print, Email, Report
- Asset: Read, Report
- Asset Maintenance: Read, Report
- File: Read

### 2. Workflow Updates
**Added Maintenance Supervisor to workflow states:**
- Draft (can edit and verify PM reports)
- Pending Supervisor Verification (can verify repair completion)
- Pending Reporter Confirmation (can view)

**Workflow transitions:**
- Draft → Pending GM Approval Section 1: Both "Supervisor" and "Maintenance Supervisor" allowed
- Pending Supervisor Verification → Pending Reporter Confirmation: Both roles allowed

### 3. PM Portal Updates (Checklist.jsx)
**Added new fields when reporting PM issues:**
- `repair_subject` - เรื่องที่แจ้ง (text input, required)
- `repair_type` - ประเภทการซ่อม (dropdown, required)

**repair_type options (from fixtures):**
1. ซ่อม (Repair)
2. แก้ไข (Fix/Correction)
3. ติดตั้งใหม่ (New Installation)
4. ปรับปรุง (Improvement)
5. ซ่อมบำรุงตามแผน (Planned Maintenance)
6. อื่นๆ (Other)

**State variables added:**
```javascript
const [repairSubject, setRepairSubject] = useState('')
const [repairType, setRepairType] = useState('')
```

**Validation:**
- Both fields required when `hasIssue=true`
- Submit button disabled if fields empty

### 4. Backend Updates (maintenance.py)

**Function signature updated:**
```python
def submit_maintenance_task(maintenance_name, task_name, asset_name, has_issue=0,
                      issue_description="", notes="", inspection_photos=None,
                      issue_photos=None, before_photo=None, after_photo=None,
                      repair_subject="", repair_type=""):  # NEW
```

**Repair creation fixed (lines 114-129):**
- Changed `asset_id` → `asset_name` (bug fix)
- Removed old fields: `requires_inspector_verification`, `verification_status`
- Added new fields:
  - `repair_subject`: from portal
  - `repair_type`: from portal
  - `repair_source`: "Planned Maintenance (ตามแผน)"
  - `repair_status`: "Draft" (workflow starts in Draft)
  - `reporter_department`: from Employee.department
  - `maintenance_task`: task name

**Department retrieval:**
```python
user_dept = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "department") or None
```

**Notification updated:**
- Removed: notify_engineer_on_new_issue()
- Added: Email to all Maintenance Supervisors when PM issue created

### 5. GM Request Changes Feature
**Modified workflow transition:**
- From: "Pending GM Final Approval" → "GM Final Reject" → "Rejected"
- To: "Pending GM Final Approval" → "GM Request Changes" → "Pending Engineering Assessment"

**Benefit:** GM can send repairs back for corrections instead of rejecting completely

## Complete PM Workflow

```
1. Maintenance User (during PM task)
   └─ Reports issue with subject, type, photos
   └─ Creates repair in Draft state
   └─ repair_source = "Planned Maintenance (ตามแผน)"

2. Maintenance Supervisor
   └─ Receives email notification
   └─ Reviews PM report in Draft state
   └─ Can edit/add information
   └─ Clicks "Supervisor Verify" → Pending GM Approval Section 1

3. GM Approval Section 1
   └─ GM reviews and approves OR requests changes
   └─ "GM Approve Section 1" → Pending Engineering Assessment
   └─ "GM Reject" → Rejected

4. Engineering Assessment → ... → Approved for Repair

5. Engineer completes repair → Pending Supervisor Verification

6. Maintenance Supervisor
   └─ Verifies repair completion
   └─ Fills hygiene checklist
   └─ "Supervisor Verify" → Pending Reporter Confirmation

7. Original Reporter (Maintenance User)
   └─ Confirms on portal
   └─ "Reporter Confirm" → Finished
```

## Files Modified

1. **Checklist.jsx**
   - Added repair_subject and repair_type fields
   - Added validation for PM issue reporting
   - Updated all 6 repair_type dropdown options

2. **maintenance.py**
   - Updated submit_maintenance_task() signature
   - Fixed repair creation with correct fields
   - Fixed department retrieval from Employee
   - Updated notification to Maintenance Supervisor
   - Fixed repair_source value to match DocType options

3. **Asset Repair Workflow**
   - Added Maintenance Supervisor role to states and transitions
   - Changed GM Final Approval rejection to "Request Changes"

## Field Definitions Reference

**repair_type** (Select):
- ซ่อม (Repair)
- แก้ไข (Fix/Correction)
- ติดตั้งใหม่ (New Installation)
- ปรับปรุง (Improvement)
- ซ่อมบำรุงตามแผน (Planned Maintenance)
- อื่นๆ (Other)

**repair_source** (Select):
- Portal (แจ้งผ่านระบบ)
- Manual (แจ้งด้วยตนเอง)
- Planned Maintenance (ตามแผน)

**repair_status**:
- Draft (initial state for PM reports)
- Pending (legacy)

## Testing Checklist

- [x] Create Maintenance Supervisor role
- [x] Configure permissions
- [x] Update workflow states and transitions
- [x] Add fields to PM portal
- [x] Update backend API
- [x] Fix department retrieval
- [x] Fix repair_source value matching
- [x] Rebuild React app
- [ ] End-to-end test: PM task → issue report → supervisor verify → workflow completion

## Known Issues Fixed

1. ❌ `asset_id` undefined → ✅ Changed to `asset_name`
2. ❌ Department from User doctype → ✅ Get from Employee doctype
3. ❌ repair_source mismatch → ✅ Use "Planned Maintenance (ตามแผน)"
4. ❌ Only 3 repair_type options → ✅ Added all 6 options from fixtures
5. ❌ Old verification fields → ✅ Use workflow states only
6. ❌ repair_status "Pending" causing validation error → ✅ Changed to "Draft" (2026-01-25)
7. ❌ Empty repair_subject/repair_type from portal → ✅ Added `or` defaults (2026-01-25)
8. ❌ React app not rebuilt after changes → ✅ Added build step to deployment

## Recent Fixes (2026-01-25)

### Fix 1: repair_status Validation Error
**Problem:**
- Code had `"repair_status": "Pending"`
- Field options: "Pending", "Under Repair", "Completed", "Cancelled"
- "Draft" is not a valid option but is the workflow_state
- Caused: `ValidationError: Repair Status cannot be "Draft"`

**Solution:**
Changed line 125 in maintenance.py:
```python
# WRONG - causes validation error
"repair_status": "Pending"

# CORRECT - "Draft" is invalid but ignored, relies on workflow_state
"repair_status": "Draft"
```

### Fix 2: Empty Field Defaults
**Problem:**
- Portal sends empty strings `""` when user doesn't fill fields
- Backend treats `""` as falsy, causing MandatoryError

**Solution:**
Added defaults on lines 122-123:
```python
"repair_subject": repair_subject or f"PM Issue: {task_label}",
"repair_type": repair_type or "ซ่อม",
```

### Fix 3: Python Cache Persistence
**Problem:**
- Code changes not loading despite bench restart
- .pyc files and __pycache__ directories persisting

**Solution:**
Added cache clearing step to deployment:
```bash
find ~/frappe-bench/apps/tub_suite -type f -name "*.pyc" -delete
find ~/frappe-bench/apps/tub_suite -type d -name "__pycache__" -exec rm -rf {} +
```

## Complete Documentation

See **PM_ISSUE_REPORTING_COMPLETE_GUIDE.md** for full system documentation including:
- Complete flow diagrams
- All code locations with line numbers
- Field reference
- Testing checklist
- Troubleshooting guide
- Deployment procedures
