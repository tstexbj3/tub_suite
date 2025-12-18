# Complete Workflow Logic Documentation

**TUB Suite Maintenance System**
**Version:** 2.0.1+
**Last Updated:** 2025-12-18

---

## Table of Contents

1. [Workflow Overview](#workflow-overview)
2. [Task Locking Logic](#task-locking-logic)
3. [Repair Workflow States](#repair-workflow-states)
4. [Field Validation & Permissions](#field-validation--permissions)
5. [Task Completion Logic](#task-completion-logic)
6. [Verification & Completion](#verification--completion)
7. [Asset Maintenance Log Lifecycle](#asset-maintenance-log-lifecycle)
8. [Technical Implementation](#technical-implementation)

---

## Workflow Overview

### Complete Maintenance Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                     MAINTENANCE TASK WORKFLOW                    │
└─────────────────────────────────────────────────────────────────┘

1. INSPECTOR SUBMITS TASK
   ├─ No Issue Reported
   │  ├─ Task marked "Completed Today"
   │  ├─ Task locked until next day
   │  ├─ Maintenance Log: "Completed"
   │  └─ next_due_date calculated
   │
   └─ Issue Reported
      ├─ Task stays OPEN (no completion date)
      ├─ Task LOCKED (pending_repair = 1)
      ├─ Asset Repair created (Draft)
      ├─ Maintenance Log: "Planned"
      └─ Engineer notified 🔧

2. ENGINEER WORKS ON REPAIR
   ├─ Engineer fills repair details
   ├─ Engineer signs document
   ├─ Engineer submits for approval
   ├─ Workflow: Draft → Pending Approval
   ├─ Task STAYS LOCKED (pending_repair = 1)
   ├─ Engineer email stored in cache (24h)
   └─ Manager notified ⏳

3. MANAGER REVIEWS
   ├─ APPROVED
   │  ├─ Manager MUST sign + add notes
   │  ├─ Workflow: Pending Approval → Approved
   │  ├─ Task STAYS LOCKED (pending_repair = 1)
   │  ├─ Asset status updated
   │  └─ Engineer notified ✅
   │
   └─ REJECTED
      ├─ Manager MUST sign + add notes
      ├─ Workflow: Pending Approval → Rejected
      ├─ Task UNLOCKED (pending_repair = 0)
      ├─ Engineer CANNOT edit rejected repair
      ├─ Engineer MUST create NEW repair document
      └─ Engineer notified ❌

4. ENGINEER FINISHES REPAIR (After Approval)
   ├─ Engineer completes physical repair
   ├─ Engineer marks: Approved → Finished
   ├─ Task STAYS LOCKED (pending_repair = 1)
   ├─ Asset status restored
   └─ Reporter notified to verify 📋

5. REPORTER VERIFIES COMPLETION
   ├─ VERIFIED - PASSED
   │  ├─ Task UNLOCKED
   │  ├─ Task completion date set
   │  ├─ next_due_date calculated
   │  ├─ Maintenance Log: "Planned" → "Completed"
   │  └─ Workflow complete ✓
   │
   └─ VERIFIED - FAILED
      ├─ Task STAYS LOCKED
      ├─ New repair cycle begins
      └─ Engineer notified of failure
```

---

## Task Locking Logic

### When Tasks Are Locked

**Location:** `tub_suite/api/maintenance.py:354-384`

Tasks are locked (not clickable, grayed out) when:

1. **Completed Today** - `last_completion_date == today`
2. **Pending Repair** - `pending_repair == 1`

```python
# Check for pending repairs (not finished/cancelled/rejected)
pending_repairs = frappe.get_all("Asset Repair", filters={
    "asset": asset.name,
    "maintenance_task": task.get("maintenance_task"),
    "workflow_state": ["not in", ["Cancelled", "Rejected"]]
}, fields=["name", "workflow_state", "repair_status", "maintenance_task", "failure_date", "verification_status"])

# Task is locked if repair is:
# - Draft, Pending Approval, Approved (any verification_status)
# - Finished but NOT verified as passed
unverified_repairs = [
    r for r in pending_repairs
    if r.workflow_state != "Finished" or r.verification_status != "Verified - Passed"
]

task["pending_repair"] = 1 if len(unverified_repairs) > 0 else 0
```

### When Tasks Are Unlocked

Tasks unlock when:

1. **Next Day** - After midnight, `last_completion_date != today`
2. **Repair Rejected** - Manager rejects, `workflow_state = "Rejected"`
3. **Repair Verified** - Reporter verifies as passed, `verification_status = "Verified - Passed"`

### Frontend Display

**Location:** `maintenance-react-dev/src/pages/Checklist.jsx:125-170`

```javascript
// Check if task was completed today or has a pending repair
const today = new Date().toISOString().split('T')[0]
const lastCompleted = task.last_completion_date
const completedToday = lastCompleted === today
const hasOpenIssue = task.has_open_issue === 1
const hasPendingRepair = task.pending_repair === 1

// Lock task if: completed today OR has pending repair
const isLocked = completedToday || hasPendingRepair
```

**Badge Display Priority:**

1. 🔧 **Repair In Progress** - `hasPendingRepair && !completedToday`
2. ⚠ **Issue Reported** - `completedToday && hasOpenIssue`
3. ✓ **Completed Today** - `completedToday`
4. Type badge - `task.maintenance_type`

---

## Repair Workflow States

### Available States

| State | Description | Who Can Set | Next States |
|-------|-------------|-------------|-------------|
| **Draft** | Initial state, engineer filling details | Engineer | Pending Approval |
| **Pending Approval** | Awaiting manager review | Engineer | Approved, Rejected |
| **Approved** | Manager approved repair | Manager | Finished |
| **Rejected** | Manager rejected repair | Manager | *(Creates new repair)* |
| **Finished** | Engineer completed repair | Engineer | *(Awaits verification)* |
| **Cancelled** | Repair cancelled | Manager | *(End state)* |

### State Transition Rules

**Location:** `tub_suite/overrides/asset_repair_override.py:230-276`

```python
# Workflow change detection
old_workflow = old_doc.get("workflow_state")
new_workflow = doc.get("workflow_state")
workflow_changed = str(old_workflow or "") != str(new_workflow or "")

if workflow_changed:
    # Validate manager signature for approval/rejection
    if new_workflow in ["Approved", "Rejected"] and old_workflow == "Pending Approval":
        if not doc.get("approval_signature"):
            frappe.throw("Manager Signature is required for approval or rejection")
        if not doc.get("approval_notes"):
            frappe.throw("Approval Notes are required for approval or rejection")
```

---

## Field Validation & Permissions

### Edit Permissions by Workflow State

**Location:** `tub_suite/overrides/asset_repair_override.py:135-162`

#### Draft State

- **Who:** Engineers and Managers
- **Can Edit:** ALL fields
- **Validation:** None

```python
# Allow free editing ONLY in Draft state for engineers and managers
if not workflow_state or workflow_state == "Draft":
    # Engineers can only edit in Draft state
    # Rejected repairs require creating NEW repair document
    return
```

#### After Submission (Pending Approval, Approved, Finished)

- **Engineers:** CANNOT edit any field
- **Managers:** CAN ONLY edit approval fields

```python
# After Draft: Lock ALL fields for engineers
if not is_manager:
    # Engineers cannot edit anything after submitting for approval
    if not doc.is_new():
        old_doc = frappe.db.get_value("Asset Repair", doc.name, "*", as_dict=True)
        if old_doc:
            # Check if any field changed (except system fields)
            ignored_fields = ["_user_tags", "_comments", "_assign", "_liked_by", "modified", "modified_by",
                             "docstatus", "workflow_state", "repair_status", "completion_date"]
            meta = frappe.get_meta("Asset Repair")
            for field in meta.fields:
                if field.fieldname in ignored_fields:
                    continue
                if field.fieldtype in ["Table", "Table MultiSelect", "Attach", "Attach Image"]:
                    continue
                if doc.get(field.fieldname) != old_doc.get(field.fieldname):
                    frappe.throw(
                        f"Engineers cannot edit fields after submitting for approval. Changed field: {field.label or field.fieldname}"
                    )
```

#### Rejected State

- **Engineers:** CANNOT edit rejected document
- **Must:** Create NEW Asset Repair document
- **Reason:** Maintain audit trail of rejected repairs

#### Manager Editable Fields

**Location:** `tub_suite/overrides/asset_repair_override.py:184-210`

Managers can ONLY edit these fields after submission:

- `approval_notes`
- `approval_signature`
- `approval_timestamp`

### Required Signatures

**Location:** `tub_suite/overrides/asset_repair_override.py:272-275`

#### Engineer Signature

- **When:** Before submitting (Draft → Pending Approval)
- **Required:** Yes
- **Field:** `engineer_signature`

```python
def before_submit_asset_repair(doc, method):
    """Validate engineer signature before submission"""
    if not doc.get("engineer_signature"):
        frappe.throw("Engineer Signature is required before submission")
```

#### Manager Signature

- **When:** Approving or Rejecting
- **Required:** Yes
- **Field:** `approval_signature`
- **Also Required:** `approval_notes`

```python
# Validate manager signature for approval/rejection
if new_workflow in ["Approved", "Rejected"] and old_workflow == "Pending Approval":
    if not doc.get("approval_signature"):
        frappe.throw("Manager Signature is required for approval or rejection")
    if not doc.get("approval_notes"):
        frappe.throw("Approval Notes are required for approval or rejection")
```

---

## Task Completion Logic

### Scenario 1: No Issue Reported

**Location:** `tub_suite/api/maintenance.py:153-187`

When inspector submits task with NO issue:

```python
if not has_issue:
    task_doc.last_completion_date = nowdate()

    # Calculate next due date based on periodicity
    completion_date = frappe.utils.getdate(nowdate())
    periodicity = task_doc.periodicity

    if periodicity == "Daily":
        next_due = add_days(completion_date, 1)
    elif periodicity == "Weekly":
        next_due = add_days(completion_date, 7)
    elif periodicity == "Monthly":
        next_due = add_months(completion_date, 1)
    elif periodicity == "Quarterly":
        next_due = add_months(completion_date, 3)
    elif periodicity == "Half-yearly":
        next_due = add_months(completion_date, 6)
    elif periodicity == "Yearly":
        next_due = add_months(completion_date, 12)
    elif periodicity == "2 Yearly":
        next_due = add_months(completion_date, 24)
    elif periodicity == "3 Yearly":
        next_due = add_months(completion_date, 36)
    else:
        next_due = add_months(completion_date, 1)

    task_doc.next_due_date = next_due
    task_doc.save(ignore_permissions=True)
```

**Result:**
- Task shows "✓ Completed Today" badge
- Task locked until tomorrow
- Maintenance Log status: "Completed"
- `completion_date` set to today

### Scenario 2: Issue Reported

**Location:** `tub_suite/api/maintenance.py:185-187`

When inspector submits task WITH issue:

```python
else:
    # Issue reported - task remains open until repair is verified
    frappe.logger().info(f"Task {task_name}: Issue reported, task stays open until repair verified")
```

**Result:**
- Task has NO `last_completion_date`
- Task shows "🔧 Repair In Progress" badge
- Task locked until repair verified
- Maintenance Log status: "Planned"
- NO `completion_date`

---

## Verification & Completion

### Verification Process

**Location:** `tub_suite/api/maintenance.py:520-656`

When reporter verifies repair completion:

```python
@frappe.whitelist(methods=["POST"])
def verify_repair_completion(repair_name, verification_status, verification_notes, verification_photos):
    """
    Inspector verifies repair completion with photos

    Args:
        repair_name: Name of Asset Repair document
        verification_status: "Verified - Passed" or "Verified - Failed"
        verification_notes: Inspector's notes about verification
        verification_photos: List of photo URLs (3 required)
    """
```

### Passed Verification

**Location:** `tub_suite/api/maintenance.py:579-656`

When `verification_status == "Verified - Passed"`:

1. **Find Correct Asset Maintenance**
   ```python
   # Find the Asset Maintenance document for this asset
   maintenance_docs = frappe.get_all("Asset Maintenance",
       filters={"asset_name": asset_name},
       fields=["name"],
       limit=1
   )
   ```

2. **Find Correct Task**
   ```python
   # Find the specific task within this Asset Maintenance
   tasks = frappe.get_all("Asset Maintenance Task",
       filters={
           "maintenance_task": task_label,
           "parent": maintenance_docs[0].name  # ✅ Filter by asset's maintenance doc
       },
       fields=["name", "parent", "periodicity"],
       limit=1
   )
   ```

3. **Complete Task**
   ```python
   task_doc.last_completion_date = nowdate()
   task_doc.next_due_date = next_due  # Calculated based on periodicity
   task_doc.save(ignore_permissions=True)
   ```

4. **Update Maintenance Log**
   ```python
   # Filter by task, asset_maintenance, and status = "Planned"
   logs = frappe.get_all("Asset Maintenance Log",
       filters={
           "task": task.name,
           "asset_maintenance": maintenance_docs[0].name,  # ✅ Filter by asset
           "maintenance_status": "Planned"
       },
       fields=["name"],
       limit=1
   )

   if logs:
       log_doc = frappe.get_doc("Asset Maintenance Log", logs[0].name)
       log_doc.maintenance_status = "Completed"
       log_doc.completion_date = nowdate()
       log_doc.save(ignore_permissions=True)
   ```

**Result:**
- Task unlocked
- Task shows "✓ Completed Today"
- Maintenance Log: "Planned" → "Completed"
- `completion_date` set
- `next_due_date` calculated

### Failed Verification

When `verification_status == "Verified - Failed"`:

**Result:**
- Task stays locked
- Repair workflow may restart
- Maintenance Log stays "Planned"
- Engineer notified of failure

---

## Asset Maintenance Log Lifecycle

### Log Creation

**Location:** `tub_suite/api/maintenance.py:95-130`

Created when inspector reports issue:

```python
log = frappe.new_doc("Asset Maintenance Log")
log.asset_maintenance = task.parent
log.asset_name = asset_name
log.task = task_name
log.task_name = task.maintenance_task
log.maintenance_type = task.maintenance_type
log.periodicity = task.periodicity
log.maintenance_status = "Planned"  # ✅ Initially "Planned"
log.due_date = frappe.utils.add_days(frappe.utils.nowdate(), 7)
log.assign_to_name = frappe.session.user
log.insert(ignore_permissions=True)
```

### Log States

| State | When Set | Meaning |
|-------|----------|---------|
| **Planned** | Issue reported | Maintenance work scheduled but not completed |
| **Completed** | No issue OR verification passed | Maintenance work finished |
| **Overdue** | Past due_date | (System-managed) |
| **Cancelled** | Log cancelled | (Manual) |

### Log Completion

#### Path 1: No Issue Reported

**Location:** `tub_suite/api/maintenance.py:153-187`

```python
# When task submitted with no issue
if not has_issue:
    # Maintenance Log is created as "Completed" with completion_date
```

#### Path 2: Issue → Repair → Verification

**Location:** `tub_suite/api/maintenance.py:639-656`

```python
# When reporter verifies repair as passed
if verification_status == "Verified - Passed":
    logs = frappe.get_all("Asset Maintenance Log",
        filters={
            "task": task.name,
            "asset_maintenance": maintenance_docs[0].name,
            "maintenance_status": "Planned"  # ✅ Find the "Planned" log
        },
        fields=["name"],
        limit=1
    )

    if logs:
        log_doc = frappe.get_doc("Asset Maintenance Log", logs[0].name)
        log_doc.maintenance_status = "Completed"  # ✅ Change to "Completed"
        log_doc.completion_date = nowdate()  # ✅ Set completion date
        log_doc.save(ignore_permissions=True)
```

---

## Technical Implementation

### File Structure

```
tub_suite/
├── api/
│   └── maintenance.py              # API endpoints, task logic
├── overrides/
│   └── asset_repair_override.py   # Workflow hooks, validation
├── www/
│   └── maintenance/                # Portal frontend
└── public/
    └── maintenance/                # Built frontend assets

maintenance-react-dev/
└── src/
    └── pages/
        └── Checklist.jsx           # Task card UI
```

### Key Functions

#### `submit_maintenance_task()`
**Location:** `tub_suite/api/maintenance.py:41-194`
- Creates Asset Repair if issue reported
- Creates Maintenance Log
- Sets task completion (if no issue)
- Notifies engineers

#### `verify_repair_completion()`
**Location:** `tub_suite/api/maintenance.py:520-670`
- Updates repair with verification info
- Completes task (if passed)
- Updates maintenance log (if passed)
- Unlocks task (if passed)

#### `validate_asset_repair()`
**Location:** `tub_suite/overrides/asset_repair_override.py:115-213`
- Field edit validation
- Role-based permissions
- Workflow state restrictions

#### `before_save_asset_repair()`
**Location:** `tub_suite/overrides/asset_repair_override.py:217-276`
- Auto-fill approval timestamp
- Validate manager signature
- Handle workflow transitions
- Send notifications
- Update asset status

### Hooks Configuration

**Location:** `tub_suite/hooks.py`

```python
doc_events = {
    "Asset Repair": {
        "validate": "tub_suite.overrides.asset_repair_override.validate_asset_repair",
        "before_save": "tub_suite.overrides.asset_repair_override.before_save_asset_repair",
        "before_submit": "tub_suite.overrides.asset_repair_override.before_submit_asset_repair",
        "on_update_after_submit": "tub_suite.overrides.asset_repair_override.on_update_after_submit_asset_repair"
    }
}
```

### Database Schema

#### Asset Maintenance Task (Child Table)

| Field | Type | Description |
|-------|------|-------------|
| `maintenance_task` | Data | Task label/name |
| `last_completion_date` | Date | When task was last completed |
| `next_due_date` | Date | When task is next due |
| `periodicity` | Select | Daily, Weekly, Monthly, etc. |

#### Asset Repair

| Field | Type | Description |
|-------|------|-------------|
| `workflow_state` | Link | Draft, Pending Approval, Approved, etc. |
| `verification_status` | Select | Pending/Verified - Passed/Failed |
| `maintenance_task` | Data | Links to original task |
| `engineer_signature` | Signature | Engineer's signature |
| `approval_signature` | Signature | Manager's signature |
| `approval_notes` | Text | Manager's approval notes |

#### Asset Maintenance Log

| Field | Type | Description |
|-------|------|-------------|
| `asset_maintenance` | Link | Parent Asset Maintenance doc |
| `task` | Data | Task internal ID |
| `maintenance_status` | Select | Planned, Completed, Overdue |
| `completion_date` | Date | When maintenance was completed |
| `due_date` | Date | When maintenance is due |

---

## Customizations Summary

### Backend Customizations

1. **Task Locking System**
   - Added `pending_repair` flag to tasks
   - Locks tasks during entire repair workflow
   - Unlocks only on rejection or verification

2. **Workflow Validation**
   - Engineer signature required before submission
   - Manager signature + notes required for approval/rejection
   - Engineers cannot edit after submission
   - Engineers cannot edit rejected repairs

3. **Asset-Specific Log Completion**
   - Fixed bug where wrong asset's log was updated
   - Now filters by both task AND asset_maintenance
   - Ensures correct log completion on verification

4. **Task Completion Logic**
   - No completion if issue reported
   - Completion only on verification passed
   - Proper next_due_date calculation

### Frontend Customizations

1. **Task Card Locking**
   - Visual feedback (opacity, cursor)
   - Multiple lock states
   - Badge priority system

2. **Badge Display**
   - 🔧 Repair In Progress
   - ⚠ Issue Reported
   - ✓ Completed Today
   - Type badges

---

## Testing Scenarios

### Scenario 1: Complete Success Path

1. Inspector reports issue → Task locked, shows "🔧 Repair In Progress"
2. Engineer fills details, signs, submits → Task stays locked
3. Manager signs, adds notes, approves → Task stays locked
4. Engineer marks finished → Task stays locked
5. Reporter verifies passed → Task unlocks, shows "✓ Completed Today"

### Scenario 2: Rejection Path

1. Inspector reports issue → Task locked
2. Engineer submits for approval → Task stays locked
3. Manager signs, adds notes, rejects → Task unlocks
4. Engineer cannot edit rejected repair
5. Engineer creates NEW repair document
6. Repeat from step 2

### Scenario 3: No Issue Path

1. Inspector submits with no issue → Task shows "✓ Completed Today"
2. Task locked until tomorrow
3. No repair workflow needed
4. Maintenance log already "Completed"

---

## Known Issues & Limitations

### 1. 24-Hour Cache for Engineer Tracking

**Issue:** Engineer email stored in Redis cache for 24 hours
**Impact:** If cache cleared, approval notification may fail
**Workaround:** Approval flow should complete within 24 hours

### 2. Multiple Assets with Same Task Name

**Issue:** Task internal IDs can be same across different assets
**Fix:** Now filters by both task ID and asset_maintenance parent
**Status:** Fixed in v2.0.1+

### 3. Rejected Repairs Cannot Be Edited

**Behavior:** Engineers must create new repair document
**Reason:** Maintain audit trail of rejected repairs
**Status:** Working as designed

---

## Future Enhancements

1. **Repair History Panel** - Show all repairs for a task
2. **Task Comments** - Allow inspectors to add notes during checks
3. **Auto-Assignment** - Auto-assign repairs to specific engineers
4. **SLA Tracking** - Track time from report to completion
5. **Analytics Dashboard** - Repair statistics and trends

---

## Support & Maintenance

### Debugging Tools

1. **Check Task Locking:**
   ```python
   frappe.get_doc("Asset Maintenance Task", "task_id").as_dict()
   ```

2. **Check Repair Status:**
   ```python
   frappe.get_all("Asset Repair",
       filters={"maintenance_task": "task_label"},
       fields=["name", "workflow_state", "verification_status"])
   ```

3. **Check Maintenance Log:**
   ```python
   frappe.get_all("Asset Maintenance Log",
       filters={"task": "task_id"},
       fields=["name", "maintenance_status", "completion_date"])
   ```

### Common Commands

```bash
# Restart bench
cd ~/frappe-bench && bench restart

# Clear cache
bench --site YOUR_SITE clear-cache

# View logs
tail -f ~/frappe-bench/logs/bench-start.log

# Rebuild frontend
cd apps/tub_suite/maintenance-react-dev && npm run build
```

---

**Document Version:** 1.0
**Last Updated:** 2025-12-18
**Author:** Claude (AI Assistant) + Tipubon IT Team
