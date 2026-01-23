# Asset Repair Workflow Documentation
## TUB Suite v2.1.0

**Last Updated:** 2026-01-23
**Status:** Production - Supervisor Only Workflow

---

## Table of Contents
1. [Overview](#overview)
2. [Workflow Configuration](#workflow-configuration)
3. [Role Permissions](#role-permissions)
4. [State Transitions](#state-transitions)
5. [Code Overrides](#code-overrides)
6. [PM Issue Handling](#pm-issue-handling)
7. [Troubleshooting](#troubleshooting)
8. [Deployment Guide](#deployment-guide)

---

## Overview

The Asset Repair system uses a single workflow: **"Asset Repair Workflow - Supervisor Only"**

### Supported Flows:
1. **Supervisor-Reported Issues** (Main flow)
   - Supervisor/Maintenance Supervisor creates repair in ERPNext
   - Goes through full approval workflow
   - Same reporter verifies completion at end

2. **PM Issues** (Portal flow - bypass workflow entry)
   - Maintenance User reports from mobile portal
   - Auto-assigned to Maintenance Supervisor
   - Maintenance Supervisor enters workflow manually
   - NO reporter confirmation (supervisor handles)

---

## Workflow Configuration

### Workflow Name
`Asset Repair Workflow - Supervisor Only`

### Active Status
✅ **ACTIVE** (only 1 workflow allowed per DocType)

### Workflow States

| No. | State | Doc Status | Only Allow Edit For |
|-----|-------|-----------|---------------------|
| 1 | Draft | 0 | Supervisor |
| 2 | Draft | 0 | Maintenance Supervisor |
| 3 | Pending GM Approval Section 1 | 0 | Maintenance Manager |
| 4 | Pending Engineering Assessment | 0 | Engineering Team |
| 5 | Pending Engineering Supervisor Review | 0 | Engineering Supervisor |
| 6 | Pending GM Final Approval | 0 | Maintenance Manager |
| 7 | Approved for Repair | 0 | Engineering Supervisor |
| 8 | Pending Supervisor Verification | 0 | Supervisor |
| 9 | Pending Supervisor Verification | 0 | Maintenance Supervisor |
| 10 | Pending Reporter Confirmation | 1 | Supervisor |
| 11 | Pending Reporter Confirmation | 1 | Maintenance Supervisor |
| 12 | Finished | 1 | Maintenance Manager |
| 13 | Rejected | 0 | All |
| 14 | Cancelled | 2 | System Manager |

**Note:** Duplicate states (e.g., Draft with both Supervisor and Maintenance Supervisor) allow BOTH roles to work in that state.

### Workflow Transitions

| No. | From State | Action | To State | Allowed Role |
|-----|-----------|--------|----------|--------------|
| 1 | Draft | Supervisor Verify | Pending GM Approval Section 1 | Supervisor |
| 2 | Draft | Supervisor Verify | Pending GM Approval Section 1 | Maintenance Supervisor |
| 3 | Pending GM Approval Section 1 | GM Approve Section 1 | Pending Engineering Assessment | Maintenance Manager |
| 4 | Pending GM Approval Section 1 | GM Reject | Rejected | Maintenance Manager |
| 5 | Pending Engineering Assessment | Engineering Assessment Complete | Pending Engineering Supervisor Review | Engineering Team |
| 6 | Pending Engineering Supervisor Review | Supervisor Review Complete | Pending GM Final Approval | Engineering Supervisor |
| 7 | Pending GM Final Approval | GM Final Approve | Approved for Repair | Maintenance Manager |
| 8 | Pending GM Final Approval | GM Request Changes | Pending Engineering Assessment | Maintenance Manager |
| 9 | Approved for Repair | Finish Repair | Pending Supervisor Verification | Engineering Supervisor |
| 10 | Pending Supervisor Verification | Supervisor Verify | Pending Reporter Confirmation | Supervisor |
| 11 | Pending Supervisor Verification | Supervisor Verify | Pending Reporter Confirmation | Maintenance Supervisor |
| 12 | Pending Supervisor Verification | Supervisor Reject | Approved for Repair | Supervisor |
| 13 | Pending Supervisor Verification | Supervisor Reject | Approved for Repair | Maintenance Supervisor |
| 14 | Pending Reporter Confirmation | Reporter Confirm | Finished | Supervisor |
| 15 | Pending Reporter Confirmation | Reporter Confirm | Finished | Maintenance Supervisor |
| 16 | Finished | Cancel | Cancelled | System Manager |

---

## Role Permissions

### Asset Repair DocType Permissions

**Via Role Permission Manager (ERPNext UI):**

| Role | Read | Write | Create | Delete | Submit | Cancel | Report | Print |
|------|------|-------|--------|--------|--------|--------|--------|-------|
| Supervisor | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ |
| Maintenance Supervisor | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ |
| Maintenance Manager | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Engineering Team | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Engineering Supervisor | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Maintenance User | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |

**Note:** Maintenance User has READ permission but CANNOT create repairs via workflow (only via portal API).

### Related DocType Permissions

**Item, Purchase Order, Warehouse:**
- Engineering Team: Read, Select, Report, Print (for spare parts reference)

---

## State Transitions

### 1. Draft → Pending GM Approval Section 1
**Who:** Supervisor or Maintenance Supervisor
**Action:** "Supervisor Verify"
**Requirements:**
- Supervisor Section 1B signature filled
- Asset selected
- Description provided

### 2. Pending GM Approval Section 1 → Pending Engineering Assessment
**Who:** Maintenance Manager
**Action:** "GM Approve Section 1"
**Requirements:**
- GM Section 1 signature filled
- Approval notes (optional)

### 3. Pending Engineering Assessment → Pending Engineering Supervisor Review
**Who:** Engineering Team
**Action:** "Engineering Assessment Complete"
**Requirements:**
- Issue severity assessed
- Parts list filled (if needed)
- Engineering operator signature

### 4. Pending Engineering Supervisor Review → Pending GM Final Approval
**Who:** Engineering Supervisor
**Action:** "Supervisor Review Complete"
**Requirements:**
- Engineering supervisor signature
- Review notes

### 5. Pending GM Final Approval → Approved for Repair
**Who:** Maintenance Manager
**Action:** "GM Final Approve"
**Requirements:**
- Manager approval signature
- Asset status updated if Major severity

### 6. Approved for Repair → Pending Supervisor Verification
**Who:** Engineering Supervisor
**Action:** "Finish Repair"
**Requirements:**
- All repair work completed
- Hygienic safety section signature filled ← **CRITICAL for portal display**

### 7. Pending Supervisor Verification → Pending Reporter Confirmation
**Who:** Supervisor or Maintenance Supervisor
**Action:** "Supervisor Verify"
**Requirements:**
- Supervisor verification signature
- Verification notes

**Portal Display Rule:**
Only shows in portal "Pending Verifications" if `hygiene_safety_signature` is filled.

### 8. Pending Reporter Confirmation → Finished
**Who:** Supervisor or Maintenance Supervisor (original reporter)
**Action:** "Reporter Confirm"
**Via:** Mobile portal or ERPNext
**Requirements:**
- Confirmation photos (optional)
- Confirmation notes (optional)
- Must be original reporter (`reported_by` field)

---

## Code Overrides

### File Location
`tub_suite/overrides/asset_repair_override.py`

### Key Functions

#### 1. `validate_asset_repair(doc, method)`
**Purpose:** Enforce state-based editing permissions

**Logic:**
```python
supervisor_roles = ["Supervisor", "Maintenance Supervisor"]

# Draft state: Anyone with supervisor role can edit
# Pending Supervisor Verification: Only original reporter OR supervisor OR manager
# Pending Reporter Confirmation: Only original reporter OR supervisor OR manager
# Pending Engineering Assessment: Only Engineering Team
# Pending Engineering Supervisor Review: Only Engineering Supervisor
# Pending GM Final Approval: Only Maintenance Manager
```

**Critical Check at Line 165-170:**
```python
if check_state == "Pending Supervisor Verification":
    current_user = frappe.session.user
    is_original_reporter = (doc.get("reported_by") == current_user)
    if is_original_reporter or is_manager or is_supervisor:
        return  # Allow editing
```

#### 2. `update_asset_status_on_approval(doc)`
**Purpose:** Change asset status based on issue severity

**Logic:**
- `issue_severity = "Major - Asset Must Stop"` → Asset status = "Out of Order"
- `issue_severity = "Minor - Asset Operational"` → Asset status remains "Submitted" (or restored if no other major issues)

#### 3. `restore_asset_status_on_finish(doc)`
**Purpose:** Restore asset to operational when repair finished

**Logic:**
- Check for other open Major repairs
- If none exist → Restore asset to "Submitted"
- If other Major repairs → Keep "Out of Order"

#### 4. Auto-fill `completion_handover_date` (Lines 110-114)
**Purpose:** Automatically set completion handover date when repair is finished

**Logic:**
```python
# Approved for Repair → Pending Supervisor Verification (Finish Repair)
elif old_workflow == "Approved for Repair" and new_workflow == "Pending Supervisor Verification":
    if not self.get("completion_handover_date"):
        frappe.db.set_value("Asset Repair", self.name, "completion_handover_date", frappe.utils.today())
        frappe.db.commit()
```


#### 5. Notification Functions
- `notify_manager_on_submit()` - Notify managers when engineer submits
- `notify_engineer_on_approval()` - Notify engineer when approved
- `notify_engineer_on_rejection()` - Notify engineer when rejected
- `notify_reporter_to_verify()` - Notify reporter to verify (Pending Reporter Confirmation)

---

## PM Issue Handling

### Flow for PM Issues

```
Maintenance User (Portal)
    ↓
  Creates repair via submit_maintenance_task()
    ↓
  Repair created in Draft
    ↓
  Auto-assigned to Maintenance Supervisor (ERPNext assignment)
    ↓
  Email notification sent
    ↓
  Maintenance Supervisor opens in ERPNext
    ↓
  Submits through workflow (Supervisor Verify)
    ↓
  Continues through normal workflow...
    ↓
  At Pending Supervisor Verification:
     - Maintenance Supervisor verifies
     - Moves to Finished (NO reporter confirmation)
```

### Code Location
`tub_suite/api/maintenance.py` lines 130-168

### Key Implementation
```python
# After repair.insert()
supervisors = frappe.get_all("Has Role",
    filters={"role": "Maintenance Supervisor", "parenttype": "User"},
    fields=["parent"]
)

if supervisors:
    from frappe.desk.form.assign_to import add
    add({
        "assign_to": [supervisors[0].parent],
        "doctype": "Asset Repair",
        "name": repair.name,
        "description": f"PM Issue reported by {frappe.session.user}: {repair_subject}"
    })
```

### Portal Verification Filter
`tub_suite/api/maintenance.py` line 811

```python
repairs = frappe.get_all("Asset Repair",
    filters={
        "workflow_state": "Pending Supervisor Verification",
        "reported_by": frappe.session.user,
        "hygiene_safety_signature": ["!=", ""]  # Only show if engineer completed
    }
)
```

---

## Troubleshooting

### Issue: Supervisor can't edit in Pending Supervisor Verification

**Cause:** Missing supervisor role check in validation
**Fix:** Ensure `asset_repair_override.py` line 157 includes:
```python
supervisor_roles = ["Supervisor", "Maintenance Supervisor"]
```

### Issue: Portal shows repair before engineer finishes hygienic safety section

**Cause:** Missing filter in `get_repairs_needing_verification()`
**Fix:** Add filter at line 811:
```python
"hygiene_safety_signature": ["!=", ""]
```

### Issue: PM issues can't be created

**Cause:** Maintenance User role missing base READ permission
**Fix:** Add READ permission for Maintenance User via Role Permission Manager

### Issue: Asset status not updating

**Cause:** `issue_severity` field not set correctly
**Fix:** Ensure severity is set to either "Major - Asset Must Stop" or "Minor - Asset Operational" (exact match required)

### Issue: Duplicate notifications

**Cause:** Multiple hooks calling notification functions
**Fix:** Check `frappe.flags` for notification_key before sending:
```python
notification_key = f"notified_{doc.name}_{old_workflow}_to_{new_workflow}"
if not frappe.flags.get(notification_key):
    # Send notification
    frappe.flags[notification_key] = True
```

---

## Deployment Guide

### 1. Workflow Setup

1. Go to: **Workflow List** → Find "Asset Repair Workflow - Supervisor Only"
2. Verify **Is Active** = ✅
3. Ensure all states and transitions match tables above
4. **IMPORTANT:** Only 1 workflow can be active per DocType!

### 2. Role Permissions

1. Go to: **Role Permission Manager**
2. Select DocType: **Asset Repair**
3. Verify permissions match table in [Role Permissions](#role-permissions)
4. For each role, click row and set checkboxes
5. Click **Update**

### 3. Code Deployment

**Files to deploy:**
- `tub_suite/overrides/asset_repair_override.py`
- `tub_suite/api/maintenance.py`
- `tub_suite/public/maintenance/assets/index.js` (portal build)

**Commands:**
```bash
cd /home/user/frappe-bench
git pull origin v2.1.0
bench --site tub clear-cache
bench restart
```

**For portal changes:**
```bash
cd /home/user/frappe-bench/apps/tub_suite/maintenance-react-dev
npm run build
cd /home/user/frappe-bench
bench --site tub clear-cache
```

### 4. Property Setters (Spare Parts Fields)

**Already Applied - NO need to reapply:**

Spare parts fields are hidden via Property Setters:
- Repair Spare Part: Hide item_code, purchase_order, warehouse, etc.
- Parts Inserted Item: Hide item_code, serial_no
- Parts Removed Item: Hide item_code, serial_no, disposal_method

To view: **Property Setter List** → Filter by DocType

### 5. Testing Checklist

- [ ] Supervisor creates repair in Draft
- [ ] Supervisor submits (Supervisor Verify)
- [ ] Manager approves (GM Approve Section 1)
- [ ] Engineer assesses (Engineering Assessment Complete)
- [ ] Engineering Supervisor reviews (Supervisor Review Complete)
- [ ] Manager final approves (GM Final Approve)
- [ ] Engineer finishes and fills hygienic safety section
- [ ] Engineer submits (Finish Repair)
- [ ] Supervisor sees repair in portal "Pending Verifications"
- [ ] Supervisor verifies (Supervisor Verify) → Pending Reporter Confirmation
- [ ] Supervisor confirms via portal (Reporter Confirm) → Finished
- [ ] Confirmation fields saved (reporter_confirmation_date, photos, notes)
- [ ] Asset status updated correctly based on severity

**PM Issue Test:**
- [ ] Maintenance User reports PM issue from portal
- [ ] Maintenance Supervisor receives assignment notification
- [ ] Maintenance Supervisor opens repair in ERPNext
- [ ] Supervisor submits through workflow
- [ ] At end, supervisor verifies and repair goes to Finished (NO confirmation step)

### 6. Common Patch Scenarios

**Scenario: Add new role to workflow**
1. Create role in Role List
2. Assign to users
3. Add duplicate state rows in workflow for new role
4. Add transition rows for new role
5. Update `asset_repair_override.py` to include new role in checks
6. Clear cache and restart

**Scenario: Change workflow transition**
1. Open workflow in ERPNext
2. Modify transition row (change action name or next state)
3. Save workflow
4. Clear cache
5. Test transition

**Scenario: Fix permission issue**
1. Go to Role Permission Manager
2. Find role and doctype
3. Modify checkboxes
4. Click Update
5. Clear cache
6. Test with user account

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v2.1.0 | 2026-01-23 | Initial supervisor-only workflow, PM portal bypass, hygienic safety filter |
| v2.0.0 | 2026-01-15 | Workflow implementation, role-based permissions |

---

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review recent git commits: `git log --oneline -20`
3. Check ERPNext error logs: `/home/user/frappe-bench/sites/tub/logs/`
4. Contact development team

---

**END OF DOCUMENTATION**
