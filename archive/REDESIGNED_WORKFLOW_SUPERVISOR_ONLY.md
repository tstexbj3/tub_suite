# Asset Repair Workflow - SUPERVISOR ONLY (No Operators)

**Date:** 2026-01-10
**Change:** Remove operators from workflow entirely, make everything supervisor-driven

---

## 🎯 Key Changes

### Before (With Operators):
- Operator reports issue via portal
- Supervisor verifies/approves
- Operator confirms completion

### After (Supervisor Only):
- **Supervisor** reports issue via portal (on behalf of their team)
- **Supervisor** verifies completion
- No operator involvement at all

---

## 📋 New Workflow (8 States)

```
┌─────────────────────────────────────────────────────────────────┐
│ SECTION 1: ISSUE REPORTING & APPROVAL                          │
└─────────────────────────────────────────────────────────────────┘

1. Draft (แบบร่าง)
   Role: Supervisor
   Portal: /maintenance/report-issue

   Fields to fill:
   ├─ Section 1A: Issue Details (via Portal)
   │  ├─ asset (Asset)
   │  ├─ failure_date (Date)
   │  ├─ description (Text)
   │  ├─ issue_photos (Multiple photos upload)
   │  └─ issue_severity (Select: Major/Minor)
   │
   └─ Section 1B: Supervisor Verification (via Desk)
      ├─ supervisor_section1_notes (Small Text)
      └─ supervisor_section1_signature (Signature) ✅ MANDATORY

   Action: [Supervisor Verify] → Pending GM Approval Section 1

   WHO: Supervisor fills BOTH Section 1A (portal) AND Section 1B (desk)

---

2. Pending GM Approval Section 1 (รอ GM อนุมัติ - Section 1)
   Role: Maintenance Manager (GM)
   Portal: ❌ Desk only

   Fields to fill:
   └─ Section 1C: GM Initial Approval
      ├─ gm_section1_notes (Small Text)
      └─ gm_section1_signature (Signature) ✅ MANDATORY

   Actions:
   ├─ [GM Approve Section 1] → Pending Engineering Assessment
   └─ [GM Reject] → Rejected

---

┌─────────────────────────────────────────────────────────────────┐
│ SECTION 2: ENGINEERING ASSESSMENT                               │
└─────────────────────────────────────────────────────────────────┘

3. Pending Engineering Assessment (รอวิศวกรประเมิน)
   Role: Engineering Team
   Portal: ❌ Desk only

   Fields to fill:
   └─ Section 2: Engineering Assessment
      ├─ action_type (Select) ✅ MANDATORY
      ├─ custom_cost_type (Select) ✅ MANDATORY
      ├─ custom_engineering_todo_items (Table) ✅ MANDATORY
      ├─ spare_parts_used (Table) - Optional
      ├─ expected_duration_days (Int) ✅ MANDATORY
      ├─ repair_start_date (Date) ✅ MANDATORY
      ├─ repair_end_date (Date) ✅ MANDATORY
      └─ engineering_operator_signature (Signature) ✅ MANDATORY

   Action: [Engineering Assessment Complete] → Pending Engineering Supervisor Review

---

4. Pending Engineering Supervisor Review (รอหัวหน้าวิศวกรตรวจสอบ)
   Role: Engineering Supervisor
   Portal: ❌ Desk only

   Fields to fill:
   └─ eng_supervisor_signature (Signature) ✅ MANDATORY

   Action: [Supervisor Review Complete] → Pending GM Final Approval

---

5. Pending GM Final Approval (รอ GM อนุมัติขั้นสุดท้าย)
   Role: Maintenance Manager (GM)
   Portal: ❌ Desk only

   Fields to fill:
   └─ approval_signature (Signature) ✅ MANDATORY

   Actions:
   ├─ [GM Final Approve] → Approved for Repair
   └─ [GM Final Reject] → Rejected

---

┌─────────────────────────────────────────────────────────────────┐
│ SECTION 3: REPAIR EXECUTION & COMPLETION                        │
└─────────────────────────────────────────────────────────────────┘

6. Approved for Repair (อนุมัติให้ซ่อม)
   Role: Engineering Supervisor
   Portal: ❌ Desk only

   Fields to fill (Completion Info):
   └─ repair_result_status (Select) - Optional
      ├─ เรียบร้อย (Satisfactory)
      ├─ ไม่เรียบร้อย (Unsatisfactory)
      └─ อื่นๆ (Other)

   Action: [Finish Repair] → Pending Supervisor Verification

   NOTE: Engineering Supervisor marks repair as complete

---

7. Pending Supervisor Verification (รอหัวหน้าแผนกตรวจสอบ)
   Role: Supervisor (Same supervisor who reported)
   Portal: ✅ /maintenance/verify/:repairName

   Fields to fill:
   └─ Section 3: Final Verification
      ├─ supervisor_verification_notes (Text)
      ├─ supervisor_signature (Signature) ✅ MANDATORY
      └─ Hygiene Checklist (if applicable)

   Actions:
   ├─ [Supervisor Verify] → Finished ✅
   └─ [Supervisor Reject] → Rejected (needs new repair request)

---

8. Finished (เสร็จสมบูรณ์)
   Status: LOCKED
   Docstatus: 1 (Submitted)

   All fields read-only
   Asset status restored (if no other Major repairs)

---

┌─────────────────────────────────────────────────────────────────┐
│ REJECTED STATE                                                   │
└─────────────────────────────────────────────────────────────────┘

9. Rejected (ถูกปฏิเสธ)
   Reasons:
   ├─ GM rejected initial approval (false alarm)
   ├─ GM rejected final approval (not needed)
   └─ Supervisor rejected verification (repair unsatisfactory)

   Action: Create NEW repair request (cannot reuse rejected one)
```

---

## 🔄 Complete Workflow Flow Chart

```
                    SUPERVISOR REPORTS ISSUE
                            ↓
                    ┌───────────────┐
                    │  1. Draft     │  ← Supervisor fills Section 1A (portal)
                    │               │    + Section 1B signature (desk)
                    └───────┬───────┘
                            │ [Supervisor Verify]
                            ↓
              ┌─────────────────────────────┐
              │ 2. Pending GM Approval S1   │  ← GM signs Section 1C
              └─────────┬─────────┬─────────┘
                        │         │ [GM Reject]
        [GM Approve S1] │         └──────────────────┐
                        ↓                            │
          ┌─────────────────────────────┐            │
          │ 3. Pending Eng Assessment   │            │
          │    (Engineering Team fills  │            │
          │     Section 2)              │            │
          └─────────┬───────────────────┘            │
                    │ [Engineering Assessment Complete]
                    ↓                                │
          ┌─────────────────────────────┐            │
          │ 4. Pending Eng Supervisor   │            │
          │    Review                   │            │
          └─────────┬───────────────────┘            │
                    │ [Supervisor Review Complete]   │
                    ↓                                │
          ┌─────────────────────────────┐            │
          │ 5. Pending GM Final         │            │
          │    Approval                 │            │
          └─────────┬─────────┬─────────┘            │
                    │         │ [GM Final Reject]    │
    [GM Final Approve]        └──────────────────────┤
                    ↓                                │
          ┌─────────────────────────────┐            │
          │ 6. Approved for Repair      │            │
          │    (Eng Supervisor fills    │            │
          │     completion info)        │            │
          └─────────┬───────────────────┘            │
                    │ [Finish Repair]                │
                    ↓                                │
          ┌─────────────────────────────┐            │
          │ 7. Pending Supervisor       │            │
          │    Verification             │            │
          │    (Supervisor verifies     │            │
          │     via portal)             │            │
          └─────────┬─────────┬─────────┘            │
                    │         │ [Supervisor Reject]  │
      [Supervisor Verify]     └──────────────────────┤
                    ↓                                │
          ┌─────────────────────────────┐            │
          │ 8. Finished                 │            │
          │    ✅ Complete              │            │
          └─────────────────────────────┘            │
                                                     │
                                                     ↓
                                        ┌─────────────────────┐
                                        │ 9. Rejected         │
                                        │    ❌ Closed        │
                                        └─────────────────────┘
```

---

## 👥 Role Mapping

### Roles in System:

| Role | Access | Portal | Responsibilities |
|------|--------|--------|------------------|
| **Supervisor** | Desk + Portal | ✅ | Report issues on behalf of team, verify completion |
| **Maintenance Manager (GM)** | Desk only | ❌ | Approve/reject repairs (Section 1 & Final) |
| **Engineering Team** | Desk only | ❌ | Fill engineering assessment (Section 2) |
| **Engineering Supervisor** | Desk only | ❌ | Review engineering assessment, mark repair complete |

### Removed Roles:
- ❌ **Maintenance User (Operator)** - Completely removed from workflow

---

## 📱 Portal Changes Required

### Current Portal Pages:
1. `/maintenance/report-issue` - Operator reports issue
2. `/maintenance/verify/:repairName` - Operator verifies completion

### New Portal Pages (Supervisor Only):
1. `/maintenance/report-issue`
   - **Change:** Only accessible by Supervisor role
   - **Remove:** Maintenance User role access
   - **UI:** Add note "Report issues on behalf of your team"

2. `/maintenance/verify/:repairName`
   - **Change:** Only accessible by Supervisor role
   - **Remove:** Maintenance User role access
   - **UI:** Add hygiene checklist fields

### Authentication Changes:
```javascript
// OLD: Check for Maintenance User OR Supervisor
if (!hasRole(frappe.session.user, ["Maintenance User", "Supervisor"])) {
    window.location.href = "/login";
}

// NEW: Check for Supervisor ONLY
if (!hasRole(frappe.session.user, ["Supervisor"])) {
    window.location.href = "/login";
}
```

---

## 🔧 Technical Changes Required

### 1. Custom Field Updates

**Field: reported_by**
- Old: Link to Maintenance User
- New: Link to Supervisor
- **Change:** Update label to "Reported By Supervisor"

**Field: issue_photos**
- Keep as is (supervisor uploads photos)

### 2. API Endpoint Changes

**File:** `tub_suite/api/maintenance.py`

**Function:** `create_repair_from_portal()`

Change validation:
```python
# OLD:
user_roles = frappe.get_roles()
if "Maintenance User" not in user_roles:
    frappe.throw("Only Maintenance Users can report issues via portal")

# NEW:
user_roles = frappe.get_roles()
if "Supervisor" not in user_roles:
    frappe.throw("Only Supervisors can report issues via portal")
```

**Function:** `verify_repair_completion()`

Change validation:
```python
# OLD:
# Allow original reporter OR supervisor
if repair.reported_by != frappe.session.user:
    # Check if user is supervisor
    ...

# NEW:
# Only allow supervisor who reported
if repair.reported_by != frappe.session.user:
    frappe.throw("Only the supervisor who reported this issue can verify completion")
```

### 3. Workflow State Changes

**Remove State:**
- ❌ "Pending Reporter Confirmation" (operator confirmation step)

**Keep States:**
1. Draft
2. Pending GM Approval Section 1
3. Pending Engineering Assessment
4. Pending Engineering Supervisor Review
5. Pending GM Final Approval
6. Approved for Repair
7. Pending Supervisor Verification (renamed from "Pending Reporter Supervisor Verification")
8. Finished
9. Rejected

**Workflow Transitions:**

| From State | Action | To State | Role |
|------------|--------|----------|------|
| Draft | Supervisor Verify | Pending GM Approval Section 1 | Supervisor |
| Pending GM Approval Section 1 | GM Approve Section 1 | Pending Engineering Assessment | Maintenance Manager |
| Pending GM Approval Section 1 | GM Reject | Rejected | Maintenance Manager |
| Pending Engineering Assessment | Engineering Assessment Complete | Pending Engineering Supervisor Review | Engineering Team |
| Pending Engineering Supervisor Review | Supervisor Review Complete | Pending GM Final Approval | Engineering Supervisor |
| Pending GM Final Approval | GM Final Approve | Approved for Repair | Maintenance Manager |
| Pending GM Final Approval | GM Final Reject | Rejected | Maintenance Manager |
| Approved for Repair | Finish Repair | **Pending Supervisor Verification** | Engineering Supervisor |
| **Pending Supervisor Verification** | Supervisor Verify | Finished | Supervisor |
| **Pending Supervisor Verification** | Supervisor Reject | Rejected | Supervisor |

---

## 📝 Field Visibility Changes

### Section 1A: Issue Details (Draft state)
```javascript
depends_on: 'eval:doc.workflow_state=="Draft" && !doc.__islocal'
```
- Filled by: **Supervisor** (via portal)
- Fields: asset, failure_date, description, issue_photos, issue_severity

### Section 1B: Supervisor Initial Verification (Draft state)
```javascript
depends_on: 'eval:doc.workflow_state=="Draft" && !doc.__islocal'
```
- Filled by: **Supervisor** (via desk)
- Fields: supervisor_section1_notes, supervisor_section1_signature

### Section 3: Supervisor Final Verification (Pending Supervisor Verification)
```javascript
depends_on: 'eval:doc.workflow_state=="Pending Supervisor Verification"'
```
- Filled by: **Supervisor** (via portal)
- Fields: supervisor_verification_notes, supervisor_signature

**Remove these fields (operator-specific):**
- ❌ reporter_confirmation
- ❌ reporter_confirmed
- ❌ reporter_signature
- ❌ reporter_notes

---

## 🗑️ Fields to Delete

These fields are operator-specific and no longer needed:

1. `reporter_confirmation` (Checkbox)
2. `reporter_confirmed` (Int)
3. `reporter_signature` (Signature)
4. `reporter_notes` (Text)
5. Any section breaks for "Reporter Confirmation"

---

## ✅ Benefits of Supervisor-Only Workflow

1. **Simplified:** Only one person per department handles the workflow
2. **Accountable:** Supervisor is responsible for their team's issues
3. **Faster:** No waiting for operator to confirm (supervisor does it all)
4. **Cleaner:** Less role confusion, clearer responsibilities
5. **Realistic:** Reflects actual workflow (supervisors already do this)

---

## 🚀 Implementation Steps

1. ✅ Update workflow transitions (remove "Pending Reporter Confirmation")
2. ✅ Rename state "Pending Reporter Supervisor Verification" → "Pending Supervisor Verification"
3. ✅ Delete operator-specific fields
4. ✅ Update portal authentication (Supervisor only)
5. ✅ Update API validations
6. ✅ Update field visibility conditions
7. ✅ Test complete flow with Supervisor user

---

## 📊 Comparison

| Aspect | OLD (With Operators) | NEW (Supervisor Only) |
|--------|---------------------|----------------------|
| States | 10 | 9 (removed Pending Reporter Confirmation) |
| Portal Users | Maintenance User + Supervisor | Supervisor only |
| Issue Reporting | Operator | Supervisor (on behalf of team) |
| Completion Verification | Operator confirms → Supervisor verifies | Supervisor verifies directly |
| Hygiene Check | Supervisor | Supervisor |
| Complexity | High (2 roles, handoff) | Low (1 role, direct) |

---

**Document Version:** 1.0
**Author:** Claude AI
**Status:** PROPOSED - Awaiting approval
