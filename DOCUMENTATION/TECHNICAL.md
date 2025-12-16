# TUB Suite - Technical Documentation

**Version:** 2.0.0
**Last Updated:** 2025-12-16
**ERPNext:** v15
**Frappe:** v15

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Installation & Deployment](#installation--deployment)
3. [Workflow & Business Logic](#workflow--business-logic)
4. [Field Locking & Permissions](#field-locking--permissions)
5. [Badge System](#badge-system)
6. [Asset Status Management](#asset-status-management)
7. [API Reference](#api-reference)
8. [Troubleshooting](#troubleshooting)
9. [Migration from v1.x](#migration-from-v1x)

---

## Architecture Overview

### Tech Stack

**Frontend:**
- React 19.2.0
- Vite 6.0.3 (build tool)
- i18next (bilingual EN/TH)
- QR code scanner library

**Backend:**
- Python 3.12+
- Frappe Framework v15
- ERPNext v15

### Key Components

```
┌─────────────────────┐
│  Mobile Portal      │  React SPA @ /maintenance
│  (React 19)         │  QR Scanner @ /qr-scanner
└──────────┬──────────┘
           │
           │ HTTP API
           ▼
┌─────────────────────┐
│  Backend API        │  tub_suite/api/
│  (Python)           │  - maintenance.py
│                     │  - asset.py
│                     │  - qr_scanner.py
└──────────┬──────────┘
           │
           │ ORM
           ▼
┌─────────────────────┐
│  ERPNext Database   │  DocTypes:
│  (MariaDB)          │  - Asset
│                     │  - Asset Maintenance
│                     │  - Asset Repair
│                     │  - Asset Maintenance Log
└─────────────────────┘
```

### Files Structure

```
tub_suite/
├── tub_suite/
│   ├── api/                       # Backend API endpoints
│   │   ├── maintenance.py         # Main maintenance API (get_asset_tasks, submit_task)
│   │   ├── asset.py               # Asset search & security
│   │   └── qr_scanner.py          # QR code routing
│   │
│   ├── overrides/                 # DocType business logic overrides
│   │   └── asset_repair_override.py  # Validation, field locking, asset status
│   │
│   ├── setup/                     # Installation scripts
│   │   └── asset_repair_setup.py  # Client/Server script setup
│   │
│   ├── utils/                     # Utility scripts
│   │   ├── fix_orphaned_tasks.py  # Unlock tasks after log deletion
│   │   └── debug_*.py             # Debug utilities
│   │
│   ├── fixtures/                  # Auto-installed data
│   │   ├── custom_fields.json     # Custom field definitions
│   │   ├── workflow.json          # Repair approval workflow
│   │   └── client_script.json     # UI behavior scripts
│   │
│   ├── public/                    # Static files
│   │   └── maintenance-react/     # Built React app
│   │
│   └── www/                       # Web pages
│       ├── maintenance.html       # Portal entry point
│       └── maintenance.py         # Context provider
│
└── maintenance-react-dev/         # React source code
    ├── src/
    │   ├── pages/
    │   │   ├── QRScanner.jsx      # QR code scanner
    │   │   ├── AssetSearch.jsx    # Asset search
    │   │   └── Checklist.jsx      # Task checklist (BADGE LOGIC HERE)
    │   ├── services/
    │   │   └── api.js             # API client
    │   └── i18n/
    │       └── locales/           # EN/TH translations
    └── package.json
```

---

## Installation & Deployment

### Fresh Installation

```bash
cd ~/frappe-bench

# 1. Get app from GitHub
bench get-app https://github.com/tstexbj3/tub_suite.git

# 2. Install on site
bench --site YOUR_SITE install-app tub_suite

# 3. Run setup scripts (creates Client/Server scripts)
bench --site YOUR_SITE execute tub_suite.setup.asset_repair_setup.run_production_setup

# 4. Clear cache
bench --site YOUR_SITE clear-cache

# 5. Restart
bench restart
```

### Update Existing Installation

```bash
cd ~/frappe-bench/apps/tub_suite

# 1. Pull latest code
git pull origin main

# 2. Update fixtures (if custom fields changed)
bench --site YOUR_SITE migrate

# 3. Re-run setup (updates Client/Server scripts)
bench --site YOUR_SITE execute tub_suite.setup.asset_repair_setup.run_production_setup

# 4. Clear cache
bench --site YOUR_SITE clear-cache

# 5. Restart
bench restart
```

### Frontend Build (Development)

If modifying React code:

```bash
cd ~/frappe-bench/apps/tub_suite/maintenance-react-dev

# Install dependencies
npm install

# Build for production
npm run build

# Output automatically copied to:
# - tub_suite/public/maintenance-react/
```

**Important:** Production sites should use pre-built assets from GitHub. No need to run `npm` on production.

---

## Workflow & Business Logic

### Roles

| Role | Permissions |
|------|-------------|
| **Quality Inspector** | Mobile portal access, complete checklists, report issues |
| **Maintenance Engineer** | Handle repairs, fill actions_performed, sign off |
| **Manufacturing Manager** | Approve/reject repairs, view all data |
| **Quality Manager** | Same as Manufacturing Manager |

### Repair Workflow States

```
Draft → Pending Approval → Approved → Finished
                       ↓
                    Rejected
```

**Key Transitions:**

1. **Draft → Pending Approval**
   - Engineer completes `actions_performed` and `engineer_signature`
   - System validates signature exists (mandatory)
   - ALL engineer fields locked after this

2. **Pending Approval → Approved**
   - Manager reviews repair
   - Manager fills `approval_notes` and `approval_signature`
   - System sets `approval_timestamp`
   - **Asset status changes to "Out of Order"** (if Major severity)

3. **Approved → Finished**
   - Actual repair work completed
   - System sets `repair_status = "Completed"`
   - Asset restored to "Submitted" status

### Issue Severity

| Severity | Asset Status | Description |
|----------|--------------|-------------|
| **Major - Asset Must Stop** | Out of Order (after manager approval) | Asset cannot operate, immediate shutdown required |
| **Minor - Asset Operational** | Submitted (stays operational) | Asset can continue running, repair can wait |

---

## Field Locking & Permissions

### Engineer Restrictions

**Draft state:**
- ✅ Can edit: `actions_performed`, `engineer_signature`, `issue_severity`

**Pending Approval / Approved / Finished:**
- ❌ All fields LOCKED
- Cannot edit anything after submission

**Implementation:**
- Python validation: `asset_repair_override.py` lines 58-78
- UI locking: Client Script lines 161-177

### Manager Restrictions

**All states:**
- ❌ Cannot edit engineer fields: `actions_performed`, `engineer_signature`

**Pending Approval:**
- ✅ Can edit: `approval_notes`, `approval_signature` (before approving)

**Approved / Finished:**
- ❌ All fields LOCKED (including approval fields)

**Implementation:**
- Python validation: `asset_repair_override.py` lines 80-127
- UI locking: Client Script lines 179-209

### Why This Matters

**Audit Trail Integrity:**
- Engineer's documented work cannot be altered by managers
- Manager's approval cannot be changed after given
- Clear separation of responsibilities
- Compliance with ISO/quality standards

---

## Badge System

### Problems Solved (v2.0.1)

#### Problem 1: Badge Turned Green After Refresh

**Root Cause:** Backend query used `repair_status` field, but workflow doesn't update `repair_status` until repair reaches "Finished" state.

**Solution:** Changed query to use `workflow_state` instead.

#### Problem 2: Type Mismatch in Date Comparison

**Root Cause:** `last_completion_date` returns `datetime.date` object, but `nowdate()` returns `str`. So `date(2025,12,16) != "2025-12-16"` was always `False`!

**Solution:** Convert date object to string before comparison.

#### Problem 3: Badge Showing on ALL Tasks

**Root Cause:** Query found all repairs for the **asset**, but didn't filter by specific **task**. So if one task had an issue, ALL completed tasks showed orange badge.

**Solution:** Added `maintenance_task` filter to query.

### Final Implementation

**File:** `tub_suite/api/maintenance.py` lines 345-353

```python
# Convert last_completion_date to string for comparison (it's a date object)
last_completed = str(task.get("last_completion_date")) if task.get("last_completion_date") else None

if last_completed == today:
    # Check if there's a pending repair for THIS SPECIFIC TASK created today
    open_repairs = frappe.get_all("Asset Repair", filters={
        "asset": asset.name,
        "maintenance_task": task.get("maintenance_task"),  # ✅ Task-specific
        "failure_date": today,
        "workflow_state": ["not in", ["Finished", "Cancelled", "Rejected"]]  # ✅ Use workflow_state
    }, fields=["name", "workflow_state", "repair_status", "maintenance_task"])

    task["has_open_issue"] = 1 if len(open_repairs) > 0 else 0
```

**What was broken:**
```python
# ❌ Wrong: Type mismatch
if task.get("last_completion_date") == today:  # date != str

# ❌ Wrong: Missing task filter
"repair_status": ["in", ["Pending", "In Progress"]]  # Empty field, never matches

# ❌ Wrong: No maintenance_task filter
# Found all asset repairs, not just this task's repair
```

### Badge Logic (Frontend)

**File:** `maintenance-react-dev/src/pages/Checklist.jsx` lines 141-148

```javascript
{completedToday && hasOpenIssue ? (
  <span className="status-badge" style={{ background: '#FF9800', color: 'white' }}>
    ⚠ Issue Reported
  </span>
) : completedToday ? (
  <span className="status-badge" style={{ background: '#4CAF50', color: 'white' }}>
    ✓ Completed Today
  </span>
) : ...}
```

### Expected Behavior

| Scenario | Badge |
|----------|-------|
| Task completed, no issue | 🟢 ✓ Completed Today |
| Task completed, issue reported (Draft) | 🟠 ⚠ Issue Reported |
| Task completed, issue in Pending Approval | 🟠 ⚠ Issue Reported |
| Task completed, issue Approved | 🟠 ⚠ Issue Reported |
| Task completed, issue Finished | 🟢 ✓ Completed Today |
| Task completed, issue Rejected | 🟢 ✓ Completed Today |

---

## Asset Status Management

### Business Rule

**Asset goes "Out of Order" ONLY when:**
1. Major severity issue reported
2. **Manager APPROVES the repair**

**NOT when:** Engineer reports the issue (preliminary assessment)

### Implementation

**File:** `tub_suite/overrides/asset_repair_override.py` lines 146-150

```python
# Trigger on workflow state change to "Approved"
workflow_changed = str(old_doc.get("workflow_state") or "") != str(doc.get("workflow_state") or "")
if workflow_changed and doc.get("workflow_state") == "Approved":
    update_asset_status_on_approval(doc)
```

**Function:** `update_asset_status_on_approval(doc)` lines 165-207

```python
def update_asset_status_on_approval(doc):
    """Update asset status when manager APPROVES repair"""
    if not doc.asset:
        return

    severity = doc.get("issue_severity")
    workflow_state = doc.get("workflow_state")

    # Only update status if repair is approved
    if workflow_state != "Approved":
        return

    asset_doc = frappe.get_doc("Asset", doc.asset)

    if severity == "Major - Asset Must Stop":
        # Manager approved Major issue - mark asset Out of Order
        if asset_doc.status != "Out of Order":
            asset_doc.status = "Out of Order"
            asset_doc.add_comment("Comment",
                f"Asset marked Out of Order - Manager approved Major severity repair: {doc.description}")
            asset_doc.save(ignore_permissions=True)

    elif severity == "Minor - Asset Operational":
        # Check if there are OTHER open Major repairs
        other_major_repairs = frappe.db.count("Asset Repair", {
            "asset": doc.asset,
            "name": ["!=", doc.name],
            "issue_severity": "Major - Asset Must Stop",
            "workflow_state": ["not in", ["Finished", "Cancelled", "Rejected"]]
        })

        if other_major_repairs == 0 and asset_doc.status == "Out of Order":
            # Safe to restore - no other major issues
            asset_doc.status = "Submitted"
            asset_doc.save(ignore_permissions=True)
```

### State Transitions

```
┌─────────────────────────────────────────────────────────┐
│ MAJOR SEVERITY ISSUE                                     │
├─────────────────────────────────────────────────────────┤
│ 1. Inspector reports issue                              │
│    Asset Status: Submitted (In Service) ✅              │
│                                                          │
│ 2. Engineer sets severity="Major", submits for approval │
│    Asset Status: Submitted (STILL operational) ✅       │
│                                                          │
│ 3. Manager APPROVES repair                              │
│    Asset Status: Out of Order ✅ ← CHANGES HERE         │
│                                                          │
│ 4. Engineer completes repair (Finished)                 │
│    Asset Status: Submitted (Restored) ✅                │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ MINOR SEVERITY ISSUE                                     │
├─────────────────────────────────────────────────────────┤
│ Asset Status: Submitted throughout entire workflow ✅   │
│ Never goes Out of Order                                 │
└─────────────────────────────────────────────────────────┘
```

### Multiple Repairs on Same Asset

If asset has multiple repairs:
- Asset stays "Out of Order" until **ALL Major repairs are Finished**
- Minor repairs don't affect asset status

Example:
```
Asset ACC-001:
├─ Repair 1: Major (Approved) → Asset Out of Order
├─ Repair 2: Minor (Approved) → Asset stays Out of Order
└─ Repair 1: Finished → Asset restored to Submitted ✅
```

---

## API Reference

### Get Asset Tasks

```python
GET /api/method/tub_suite.api.maintenance.get_asset_tasks?asset_name=ACC-ASS-2025-00001
```

**Response:**
```json
[{
  "maintenance_task": "ทำความสะอาด Compressor",
  "last_completion_date": "2025-12-16",
  "has_open_issue": 1,  // 0 or 1
  "next_due_date": "2025-12-23",
  "periodicity": "Weekly",
  "badge_status": "issue_reported"  // or "completed" or "pending"
}]
```

### Submit Maintenance Task

```python
POST /api/method/tub_suite.api.maintenance.submit_maintenance_task
Content-Type: application/json

{
  "asset_name": "ACC-ASS-2025-00001",
  "task_name": "ทำความสะอาด Compressor",
  "notes": "Found leak",
  "has_issue": 1,
  "photos": ["base64..."]
}
```

### Get Repairs Needing Verification (NEW v2.0.1)

```python
POST /api/method/tub_suite.api.maintenance.get_repairs_needing_verification
Content-Type: application/json
X-Frappe-CSRF-Token: <token>

# No body required - returns repairs for logged-in user
```

**Response:**
```json
[{
  "name": "ACC-REP-2025-00001",
  "asset": "ACC-ASS-2025-00123",
  "asset_name": "เครื่องปรับอากาศห้องประชุม 1",
  "item_code": "AC-SPLIT-001",
  "item_name": "Air Conditioner Split Type",
  "location": "Meeting Room 1",
  "description": "Compressor not working",
  "failure_date": "2025-12-16",
  "workflow_state": "Finished",
  "verification_status": "Pending Verification",
  "reported_by": "inspector@test.com",
  "actions_performed": "Replaced compressor",
  "completion_date": "2025-12-16 15:30:00",
  "repair_status": "Completed"
}]
```

### Get Repair for Verification

```python
POST /api/method/tub_suite.api.maintenance.get_repair_for_verification
Content-Type: application/json

{
  "repair_name": "ACC-REP-2025-00001"
}
```

**Response:**
```json
{
  "repair": {
    "name": "ACC-REP-2025-00001",
    "asset": "ACC-ASS-2025-00123",
    "asset_name": "เครื่องปรับอากาศห้องประชุม 1",
    "item_code": "AC-SPLIT-001",
    "location": "Meeting Room 1",
    "description": "Compressor not working",
    "actions_performed": "Replaced compressor",
    "repair_status": "Completed",
    "verification_status": "Pending Verification",
    "reported_by": "inspector@test.com",
    "creation": "2025-12-16 10:00:00"
  },
  "issue_photos": [
    {
      "file_name": "ACCASS123_ISSUE_20251216_1.jpg",
      "file_url": "/files/photo.jpg",
      "sequence": 1,
      "user": "INSPECTOR",
      "timestamp": "20251216100000",
      "creation": "2025-12-16 10:00:00"
    }
  ]
}
```

### Verify Repair Completion

```python
POST /api/method/tub_suite.api.maintenance.verify_repair_completion
Content-Type: application/json

{
  "repair_name": "ACC-REP-2025-00001",
  "verification_photos": ["/files/verify_photo_1.jpg", "/files/verify_photo_2.jpg"],
  "verification_notes": "Verified working properly",
  "verification_status": "Verified - Passed"  // or "Verified - Failed"
}
```

**Response:**
```json
{
  "success": true,
  "repair_name": "ACC-REP-2025-00001",
  "verification_status": "Verified - Passed",
  "verified_by": "inspector@test.com",
  "verification_date": "2025-12-16 20:30:00",
  "message": "Repair verification submitted successfully. Waiting for manager approval."
}
```

**Side Effects:**
- If `verification_status = "Verified - Passed"`:
  - Checks for other open Major repairs on same asset
  - If none → Asset status automatically changes to "Submitted" (operational)
  - If other Major repairs exist → Asset stays "Out of Order"
- Asset Repair document updated with verification data
- Verification photos attached to Asset Repair document

### Debug Asset Repairs

```bash
# Check today's repairs and badge query
bench --site YOUR_SITE execute tub_suite.utils.debug_today_repairs.check_today

# Unlock orphaned tasks (after deleting logs)
bench --site YOUR_SITE execute tub_suite.utils.fix_orphaned_tasks.fix_orphaned_task_completions
```

---

## Troubleshooting

### Badge Still Turns Green After Refresh

**Symptoms:** Orange badge turns green after F5 refresh

**Cause:** Server not restarted, still running old code

**Fix:**
```bash
# Development mode: Bench auto-reloads Python, wait 5-10 seconds
# If still broken:
pkill -f "frappe"
bench start

# Production mode:
bench restart
```

### Engineer Can Edit After Submission

**Symptoms:** Engineer can edit `actions_performed` in Pending Approval state

**Cause:** Client Script not updated in database

**Fix:**
```bash
bench --site YOUR_SITE execute tub_suite.setup.asset_repair_setup.run_production_setup
bench --site YOUR_SITE clear-cache
bench restart

# Also clear browser cache: Ctrl+Shift+R
```

### Manager Can Edit Everything After Approval

**Symptoms:** Manager can edit engineer fields after approval

**Cause:** Python validation not running or old code

**Fix:**
```bash
# Check Python file has latest code
cat ~/frappe-bench/apps/tub_suite/tub_suite/overrides/asset_repair_override.py | grep "workflow_state"

# Should see: if workflow_state in ["Approved", "Finished"]:

# Restart server
bench restart
```

### Asset Status Wrong

**Symptoms:** Asset goes Out of Order when engineer reports Major issue (before manager approval)

**Cause:** Old code triggering on severity change, not approval

**Fix:**
```bash
# Verify fix is in place
cat ~/frappe-bench/apps/tub_suite/tub_suite/overrides/asset_repair_override.py | grep "update_asset_status_on_approval"

# Should see function call when workflow_state changes to "Approved"

# Restart
bench restart
```

### Task Card Stuck (Can't Resubmit)

**Symptoms:** Deleted Asset Repair/Log but task still shows "completed today"

**Cause:** Orphaned task completion record

**Fix:**
```bash
bench --site YOUR_SITE execute tub_suite.utils.fix_orphaned_tasks.fix_orphaned_task_completions
```

### 417 EXPECTATION FAILED Error

**Symptoms:** API calls return 417 error in browser console

**Cause:** CSRF token issue or session expired

**Fix:**
- Logout and login again
- Or restart browser
- Or clear cookies for site domain

---

## Migration from v1.x

### Breaking Changes in v2.0

1. **Frontend completely rewritten** from jQuery to React
2. **Client Scripts renamed** (old duplicate scripts must be deleted)
3. **Field locking logic changed** (now enforced in Python + UI)
4. **Asset status trigger changed** (now on manager approval, not engineer assessment)

### Migration Steps

```bash
cd ~/frappe-bench/apps/tub_suite

# 1. Backup production database first!
bench --site YOUR_SITE backup

# 2. Pull v2.0 code
git fetch origin
git checkout v2.0.0  # Or main branch

# 3. Check for old duplicate scripts
bench --site YOUR_SITE console
>>> import frappe
>>> scripts = frappe.get_all("Client Script", filters={"reference_doctype": "Asset Repair"}, fields=["name"])
>>> print(scripts)
# If you see old scripts like "Asset Repair - Field Locking" (without "UI"), delete them

# 4. Run migration
bench --site YOUR_SITE migrate

# 5. Run setup (creates new scripts)
bench --site YOUR_SITE execute tub_suite.setup.asset_repair_setup.run_production_setup

# 6. Clear cache
bench --site YOUR_SITE clear-cache

# 7. Restart
bench restart
```

### Post-Migration Checks

- [ ] Login as Engineer → Create Asset Repair → Submit for approval → Fields locked?
- [ ] Login as Manager → Open Pending Approval → Cannot edit engineer fields?
- [ ] Report issue from mobile → Badge shows orange → Refresh page → Still orange?
- [ ] Major issue → Engineer submits → Asset still In Service?
- [ ] Major issue → Manager approves → Asset now Out of Order?

---

## Version History

| Version | Date | Key Changes |
|---------|------|-------------|
| **2.0.1** | 2025-12-16 | Fixed badge refresh bug, field locking, asset status timing |
| **2.0.0** | 2025-12-15 | React migration, major rewrite from jQuery |
| 1.1.0 | 2024-12-04 | jQuery improvements |
| 1.0.0 | 2024-11-30 | Initial release |

---

## Support

- **GitHub Issues:** https://github.com/tstexbj3/tub_suite/issues
- **Email:** it@tipubon.com

---

**Last Updated:** 2025-12-16
**Maintained By:** Tipubon International Co., Ltd.
