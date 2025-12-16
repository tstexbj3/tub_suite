# TUB Maintenance Portal - System Workflows and Architecture

**Document Type:** Technical Reference
**Audience:** Administrators, Developers, System Integrators
**Version:** 1.0
**Last Updated:** December 16, 2024

---

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Complete Workflows](#complete-workflows)
3. [Asset Status Management](#asset-status-management)
4. [API Reference](#api-reference)
5. [Database Schema](#database-schema)
6. [Configuration Guide](#configuration-guide)
7. [Troubleshooting Guide](#troubleshooting-guide)

---

## System Architecture

### Technology Stack

```
┌─────────────────────────────────────────────┐
│           USER INTERFACES                    │
├─────────────────────────────────────────────┤
│  Mobile Portal (React 19 + Vite)            │
│  - Home, Checklist, Search, Verification     │
│                                             │
│  ERPNext Desk (Frappe Framework v15)        │
│  - Asset Management, Repair Workflow        │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│           APPLICATION LAYER                  │
├─────────────────────────────────────────────┤
│  Python APIs (tub_suite/api/)               │
│  - asset.py - Asset operations              │
│  - maintenance.py - Maintenance operations   │
│  - file_utils.py - Photo management         │
│                                             │
│  Custom DocType Overrides                   │
│  - asset_repair_override.py                 │
│  - Custom workflow logic                    │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│           DATA LAYER                         │
├─────────────────────────────────────────────┤
│  ERPNext DocTypes                           │
│  - Asset, Asset Repair, Asset Maintenance    │
│  - Asset Maintenance Log                     │
│                                             │
│  Custom DocTypes                            │
│  - Maintenance Portal Settings              │
│                                             │
│  MariaDB Database                           │
└─────────────────────────────────────────────┘
```

### Component Breakdown

**Frontend Components:**
- `Home.jsx` - Landing page with QR scanner and search
- `Checklist.jsx` - Asset inspection and issue reporting
- `AssetSearch.jsx` - Search function (manager access)
- `VerifyRepair.jsx` - Repair verification by reporter
- `PhotoUpload.jsx` - Reusable photo upload component
- `QRScanner.jsx` - QR code scanning component

**Backend APIs:**
- `search_assets()` - Asset search
- `get_asset_with_checklist()` - Fetch asset + maintenance tasks
- `submit_checklist()` - Submit inspection results
- `get_repairs_needing_verification()` - Pending verifications
- `verify_repair_completion()` - Submit verification
- `get_portal_settings()` - Configuration retrieval
- `get_user_roles()` - Role-based access control

**Custom Logic:**
- `CustomAssetRepair` class - Overrides ERPNext Asset Repair
- `update_asset_status_on_approval()` - Auto-change asset status
- `restore_asset_status_on_verification()` - Restore after verification
- `notify_reporter_to_verify()` - Send verification notifications

**Configuration:**
- `Maintenance Portal Settings` - Single DocType for settings
- `config.js` - Frontend settings cache (1-minute TTL)
- `hooks.py` - Frappe hooks registration

### Directory Structure

```
tub_suite/
├── api/
│   ├── asset.py                    # Asset operations
│   ├── maintenance.py               # Maintenance operations
│   ├── file_utils.py                # Photo management
│   └── qr_scanner.py                # QR routing
│
├── overrides/
│   └── asset_repair_override.py     # Custom repair logic
│
├── tub_suite/doctype/
│   └── maintenance_portal_settings/ # Portal configuration
│
├── public/
│   ├── js/
│   └── maintenance/                 # Built React app
│
├── maintenance-react-dev/
│   ├── src/
│   │   ├── pages/                   # React pages
│   │   ├── components/              # Reusable components
│   │   ├── services/                # API service layer
│   │   └── config.js                # Settings cache
│   ├── deploy.sh                    # Build + deploy script
│   └── update-hash.sh               # Asset hash updater
│
└── hooks.py                         # Frappe hooks
```

---

## Complete Workflows

### Workflow 1: Inspection and Issue Reporting

```
┌────────────────┐
│ Maintenance    │
│ User           │
└────────┬───────┘
         │
         ├─1─→ [Scan QR Code]
         │         │
         │         ↓
         ├─2─→ [View Asset Checklist]
         │     - Daily tasks
         │     - Weekly tasks
         │     - Monthly tasks
         │     - Badge indicators
         │         │
         │         ↓
         ├─3─→ [Complete Tasks]
         │     - Check boxes
         │     - Add notes
         │         │
         │         ↓
         ├─4─→ [Issue Found?] ──No──→ [Submit Checklist] ──→ [END]
         │         │
         │        Yes
         │         ↓
         ├─5─→ [Report Issue]
         │     - Description
         │     - Photos (min 2)
         │         │
         │         ↓
         ├─6─→ [Submit Checklist]
         │         │
         │         ↓
         │     [Asset Repair Created]
         │     - Status: Draft
         │     - Reported By: User email
         │         │
         │         ↓
         │     [Notifications Sent]
         │     - Engineering Team (ToDo + Email)
         │     - Maintenance Manager (ToDo + Email)
         │
         ↓
     [END - Wait for Verification]
```

**Key Points:**
- User identifies issue during inspection
- Photos mandatory if issue reported (min 2)
- Asset Repair automatically created
- Reporter tracked by email for future verification
- Notifications immediate

**API Calls:**
1. `GET /api/method/tub_suite.api.asset.get_asset_with_checklist`
2. `POST /api/method/tub_suite.api.asset.submit_checklist`
3. Backend creates Asset Repair document
4. Backend sends notifications

---

### Workflow 2: Repair Approval Process

```
┌────────────────┐         ┌────────────────┐         ┌────────────────┐
│  Engineering   │         │  Maintenance   │         │    System      │
│     Team       │         │    Manager     │         │   Automatic    │
└───────┬────────┘         └───────┬────────┘         └───────┬────────┘
        │                          │                          │
    ┌───┴───┐                      │                          │
    │ Draft │                      │                          │
    └───┬───┘                      │                          │
        │                          │                          │
   1. Fill Details                 │                          │
   - Issue Severity ★             │                          │
   - Repair Type                   │                          │
   - Estimated Cost                │                          │
   - Engineer Signature ★          │                          │
        │                          │                          │
   2. Submit                       │                          │
        │                          │                          │
        ├──────────────────────────┤                          │
        │                          │                          │
    ┌───┴──────────┐              │                          │
    │ Pending      │              │                          │
    │ Approval     │◄─────────────┤                          │
    └───┬──────────┘              │                          │
        │                          │                          │
        │                      3. Review                      │
        │                      - Check severity               │
        │                      - Verify cost                  │
        │                      - Business impact              │
        │                          │                          │
        │                      Decision?                      │
        │                          │                          │
        │            ┌─────────────┴─────────────┐            │
        │           APPROVE                   REJECT          │
        │            │                           │            │
        │            │                           │            │
    ┌───┴────────┐  │                      ┌────┴────┐       │
    │ Approved    │◄─┤                      │ Rejected│       │
    └───┬────────┘   │                      └────┬────┘       │
        │            │                           │            │
        │            │                      Returns to Draft   │
        │            │                      (Engineer edits)   │
        │            │                                         │
        │      Asset Status                                   │
        │      Change?                                        │
        │            │                                         │
        │            ├──────────────────────────────────►     │
        │            │                                         │
        │       Issue Severity                                │
        │       = "Major"?                                    │
        │            │                                         │
        │           Yes ──────► Asset Status = "Out of Order" │
        │            │                                         │
        │            No  ──────► Asset Status = Unchanged     │
        │                                                      │
   4. Perform Repair                                          │
   - Physical work                                            │
   - Take photos                                              │
   - Test equipment                                           │
        │                                                      │
   5. Mark "Job Finished"                                     │
        │                                                      │
        ├──────────────────────────────────────────────────────►
        │                                                      │
    ┌───┴────────┐                                            │
    │ Finished    │                                  Auto-fill │
    └───┬────────┘                                  - Completion Date
        │                                            - Notify Reporter
        │                                                      │
        └──────────────────────────────────────────────────────┘
                           │
                           ↓
                   [Reporter Verifies]
```

**Critical Decision Points:**

**Issue Severity Selection:**
- **Major - Asset Must Stop** → Asset status → "Out of Order" on approval
- **Minor - Asset Operational** → Asset stays operational

**Manager Approval:**
- Can override engineer's severity assessment
- Adds approval notes and signature
- Decision logged in audit trail

**Automatic Actions on Approval (Major):**
```python
if workflow_state == "Approved" and issue_severity == "Major":
    asset.status = "Out of Order"
    asset.add_comment("Asset marked Out of Order - Manager approved Major severity repair")
    asset.save()
```

**API Calls:**
1. Engineer: `GET /api/method/frappe.client.get` (Asset Repair document)
2. Engineer: `PUT /api/method/frappe.client.set_value` (fill fields)
3. Engineer: Submit document (triggers workflow)
4. System: `on_update_after_submit()` hook
5. System: `update_asset_status_on_approval()` if Major
6. Manager: Workflow action (Approve/Reject)
7. Engineer: Workflow action "Job Finished"
8. System: `notify_reporter_to_verify()`

---

### Workflow 3: Repair Verification

```
┌────────────────┐         ┌────────────────┐
│   Original     │         │     System     │
│   Reporter     │         │   Automatic    │
└───────┬────────┘         └───────┬────────┘
        │                          │
   [Receives Notification]         │
        │                          │
   From: Engineer marked           │
   "Job Finished"                  │
        │                          │
        ↓                          │
   [Login to Portal]               │
        │                          │
        ↓                          │
   [Home Page Alert]               │
   "⚠️ Pending Verifications: 1"   │
        │                          │
        ↓                          │
   [Click Repair Card]             │
        │                          │
        ↓                          │
   [Review Repair Details]         │
   - Original problem               │
   - Engineer's actions            │
   - Repair date                   │
        │                          │
        ↓                          │
   [GO TO ASSET ★]                 │
   Physical inspection required    │
        │                          │
        ↓                          │
   [Test Equipment]                │
   - Power on                      │
   - Check operation               │
   - Verify fix                    │
   - Observe 5-10 min             │
        │                          │
        ↓                          │
   [Is Fixed?] ──No──► [Contact Engineer/Manager]
        │                          │
       Yes                         │
        │                          │
        ↓                          │
   [Take Verification Photos]      │
   Minimum 2 photos required       │
   - Equipment running             │
   - Fixed area                    │
        │                          │
        ↓                          │
   [Read 7-Day Disclaimer]         │
   ⚠️ Responsibility clause         │
        │                          │
        ↓                          │
   [Check Confirmation Box]        │
   MANDATORY checkbox              │
        │                          │
        ↓                          │
   [Submit Verification]           │
        │                          │
        ├──────────────────────────►
        │                          │
        │                  verification_status =
        │                  "Verified - Passed"
        │                          │
        │                          ↓
        │                  Check for other
        │                  Major repairs
        │                  on this asset
        │                          │
        │                    ┌─────┴─────┐
        │                   Any?        None
        │                    │             │
        │              Keep "Out of   Restore
        │              Order" (safety) Asset Status
        │                    │             │
        │                    │             ↓
        │                    │        Asset Status =
        │                    │        "Submitted"
        │                    │             │
        │                    └──────┬──────┘
        │                           │
        ↓                           ↓
   [Confirmation Message]    [Asset Restored]
```

**7-Day Responsibility Rule:**
```
Reporter confirms:
✓ Personally inspected equipment
✓ Repair is complete and correct
✓ Equipment operates normally
★ If same problem returns within 7 days:
  - Reporter must report again
  - May be questioned about thoroughness
```

**Asset Restoration Logic:**
```python
def restore_asset_status_on_verification(doc):
    # Count OTHER open Major repairs
    other_major_repairs = frappe.db.count("Asset Repair", {
        "asset": doc.asset,
        "name": ["!=", doc.name],
        "issue_severity": "Major - Asset Must Stop",
        "workflow_state": ["not in", ["Finished", "Cancelled", "Rejected"]]
    })

    if other_major_repairs == 0:
        # Safe to restore
        asset.status = "Submitted"
        asset.save()
    else:
        # Keep out of order - other Major repairs exist
        pass
```

**Why Multiple Major Repairs Block Restoration:**
- Safety feature
- Asset may have multiple unrelated issues
- All Major issues must be resolved before returning to service
- Prevents premature restoration

**API Calls:**
1. `GET /api/method/tub_suite.api.maintenance.get_repairs_needing_verification`
2. `GET /api/method/tub_suite.api.maintenance.get_repair_for_verification`
3. `POST /api/method/tub_suite.api.maintenance.verify_repair_completion`
4. System: `on_update_after_submit()` hook
5. System: `restore_asset_status_on_verification()`

---

## Asset Status Management

### Status Lifecycle

```
┌────────────┐
│   Draft    │ ← New asset created
└─────┬──────┘
      │ Submit
      ↓
┌────────────┐
│ Submitted  │ ← Normal operational state
└─────┬──────┘   (Green badge)
      │
      │ Issue Reported + Manager Approves (Major Severity)
      │
      ↓
┌────────────┐
│ Out of     │ ← Asset offline for repair
│ Order      │   (Red badge)
└─────┬──────┘   Users cannot inspect
      │
      │ Repair Finished + Reporter Verified
      │ + No other Major repairs
      │
      ↓
┌────────────┐
│ Submitted  │ ← Restored to service
└────────────┘   (Green badge)
                 Ready for next inspection
```

### Status Triggers

**Submitted → Out of Order:**
```
TRIGGER: Manager approves repair
CONDITION: issue_severity = "Major - Asset Must Stop"
CODE LOCATION: asset_repair_override.py:234-295
FUNCTION: update_asset_status_on_approval()
```

**Out of Order → Submitted:**
```
TRIGGER: Reporter verifies repair completion
CONDITION: verification_status = "Verified - Passed"
         AND no other Major repairs open
CODE LOCATION: asset_repair_override.py:297-345
FUNCTION: restore_asset_status_on_verification()
```

### Status Badge Display

**In Search Results:**
```jsx
<span className={`status-badge status-${asset.status?.toLowerCase()}`}>
  {asset.status || 'Draft'}
</span>
```

**CSS Classes:**
- `.status-submitted` - Green background
- `.status-draft` - Yellow background
- `.status-cancelled` - Red background
- `.status-out-of-order` - Red background (mapped from "Out of Order")

**Badge Styling:**
```css
.status-badge {
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: bold;
  text-transform: uppercase;
}

.status-submitted {
  background: #4CAF50;
  color: white;
}
```

---

## API Reference

### Authentication

All APIs require authentication via Frappe session:
```
X-Frappe-CSRF-Token: <token>
Cookie: sid=<session_id>
```

### Asset Operations

#### 1. Search Assets
```http
POST /api/method/tub_suite.api.asset.search_assets
Content-Type: application/json

{
  "query": "u-ac"
}
```

**Response:**
```json
{
  "message": {
    "success": true,
    "assets": [
      {
        "name": "U-AC-01C",
        "asset_name": "Air Conditioner Room 1",
        "item_code": "AC-SPLIT-01",
        "location": "Meeting Room Floor 2",
        "status": "Submitted",
        "asset_category": "Air Conditioning"
      }
    ],
    "count": 1
  }
}
```

#### 2. Get Asset with Checklist
```http
POST /api/method/tub_suite.api.asset.get_asset_with_checklist
Content-Type: application/json

{
  "asset_name": "U-AC-01C"
}
```

**Response:**
```json
{
  "message": {
    "success": true,
    "asset": {
      "name": "U-AC-01C",
      "asset_name": "Air Conditioner Room 1",
      "status": "Submitted",
      "location": "Meeting Room Floor 2",
      "photo": "/files/asset_photo.jpg"
    },
    "checklist": [
      {
        "name": "TASK-001",
        "item_description": "Check air filter",
        "periodicity": "Daily",
        "is_overdue": true,
        "is_checkable": true,
        "status_badge": {
          "text": "เกินกำหนด",
          "color": "red",
          "type": "overdue"
        }
      }
    ],
    "unavailable": false,
    "active_repair": null
  }
}
```

#### 3. Submit Checklist
```http
POST /api/method/tub_suite.api.asset.submit_checklist
Content-Type: application/json

{
  "asset_name": "U-AC-01C",
  "checklist_data": [
    {
      "name": "TASK-001",
      "is_completed": true
    }
  ],
  "issue_description": "Air conditioner not cooling properly"
}
```

**Response:**
```json
{
  "message": {
    "success": true,
    "completed_tasks": ["LOG-001"],
    "total_completed": 1,
    "repair_name": "AR-001"
  }
}
```

### Maintenance Operations

#### 4. Get Repairs Needing Verification
```http
POST /api/method/tub_suite.api.maintenance.get_repairs_needing_verification
```

**Response:**
```json
{
  "message": [
    {
      "name": "AR-001",
      "asset": "U-AC-01C",
      "asset_name": "Air Conditioner Room 1",
      "description": "Not cooling",
      "workflow_state": "Finished",
      "verification_status": null,
      "completion_date": "2024-12-16",
      "location": "Meeting Room Floor 2"
    }
  ]
}
```

#### 5. Verify Repair Completion
```http
POST /api/method/tub_suite.api.maintenance.verify_repair_completion
Content-Type: application/json

{
  "repair_name": "AR-001",
  "verification_photos": [
    {
      "file_url": "/files/verify_1.jpg",
      "description": "Equipment running normally"
    }
  ],
  "verification_notes": "Tested for 10 minutes, working perfectly",
  "verification_status": "Verified - Passed"
}
```

#### 6. Get Portal Settings
```http
POST /api/method/tub_suite.api.maintenance.get_portal_settings
```

**Response:**
```json
{
  "message": {
    "enable_search_for_all": 0,
    "search_allowed_roles": [
      "Maintenance Manager",
      "System Manager",
      "Administrator"
    ]
  }
}
```

**Frontend Cache:**
```javascript
// config.js caches for 1 minute
const CACHE_DURATION = 60000

const fetchSettings = async () => {
  if (cachedSettings && (now - lastFetchTime) < CACHE_DURATION) {
    return cachedSettings
  }
  // ... fetch from API
}
```

### File Operations

#### 7. Upload Photo with Metadata
```http
POST /api/method/tub_suite.api.file_utils.attach_photo_with_metadata
Content-Type: multipart/form-data

{
  "file": <binary>,
  "doctype": "Asset Repair",
  "docname": "AR-001",
  "asset_name": "U-AC-01C",
  "activity_type": "VERIFY",
  "sequence": 1,
  "metadata": {
    "timestamp": "2024-12-16 10:30:00",
    "location": "Meeting Room Floor 2"
  }
}
```

---

## Database Schema

### Key DocTypes

#### Asset
```
Asset
├── name (PK)               # Asset ID (e.g., "U-AC-01C")
├── asset_name              # Display name
├── item_code               # Item reference
├── asset_category          # Category link
├── location                # Physical location
├── status                  # Submitted, Out of Order, Draft, etc.
├── image                   # Asset photo URL
└── [standard fields]
```

#### Asset Repair
```
Asset Repair
├── name (PK)               # Repair ID (e.g., "AR-001")
├── asset                   # Link to Asset
├── failure_date            # When problem occurred
├── description             # Problem description
├── issue_severity          # Major or Minor ★
├── repair_type             # Repair, Maintenance, etc.
├── workflow_state          # Draft, Pending Approval, Approved, etc.
├── reported_by             # Email of reporter ★
├── engineer_signature      # Digital signature
├── approval_notes          # Manager notes
├── approval_signature      # Manager signature
├── approval_timestamp      # Auto-filled
├── actions_performed       # What engineer did
├── completion_date         # When finished
├── verification_status     # Verified - Passed, etc. ★
└── [standard fields]
```

**Custom Fields Added:**
- `issue_severity` - Select (Major/Minor)
- `repair_type` - Select (Repair/Maintenance/etc.)
- `engineer_signature` - Signature
- `approval_notes` - Text
- `approval_signature` - Signature
- `approval_timestamp` - Datetime
- `verification_status` - Select
- `reported_by` - Link to User

#### Maintenance Portal Settings
```
Maintenance Portal Settings (Single DocType)
├── name = "Maintenance Portal Settings"
└── enable_search_for_all_users  # Check (0 or 1)
```

**Usage:**
```python
settings = frappe.get_single("Maintenance Portal Settings")
enable_all = settings.enable_search_for_all_users
```

### Workflow States

**Repair Approval WorkFlow:**
```
States:
- Draft                    # Engineer filling details
- Pending Approval         # Waiting for manager
- Approved                 # Manager approved, engineer working
- Finished                 # Engineer done, waiting verification
- Rejected                 # Manager rejected, back to engineer
- Cancelled                # Abandoned

Transitions:
Draft → Submit → Pending Approval
Pending Approval → Approve → Approved
Pending Approval → Reject → Rejected
Rejected → Submit → Pending Approval (re-cycle)
Approved → Job Finished → Finished
```

---

## Configuration Guide

### Initial Setup

**1. Create Portal Settings:**
```bash
bench console

>>> doc = frappe.get_doc({
...     "doctype": "Maintenance Portal Settings",
...     "enable_search_for_all_users": 0
... })
>>> doc.insert()
>>> frappe.db.commit()
```

**2. Assign Roles:**
```python
# Maintenance User
user = frappe.get_doc("User", "inspector@example.com")
user.add_roles("Maintenance User")

# Engineering Team
user = frappe.get_doc("User", "engineer@example.com")
user.add_roles("Engineering Team")

# Maintenance Manager
user = frappe.get_doc("User", "manager@example.com")
user.add_roles("Maintenance Manager")
```

**3. Configure Workflow:**
- Go to: Workflow → Repair Approval WorkFlow
- Verify states and transitions
- Assign to "Asset Repair" DocType
- Enable workflow

**4. Deploy React App:**
```bash
cd /home/user/frappe-bench/apps/tub_suite/maintenance-react-dev
npm run build
bash update-hash.sh
cd /home/user/frappe-bench
bench restart
```

### Environment-Specific Settings

**Development:**
```javascript
// config.js
ENABLE_SEARCH_FOR_ALL: true  // Easy testing
```

**Production:**
```javascript
// Via ERPNext Desk:
Maintenance Portal Settings
☐ Enable Search for All Users  // Unchecked
```

### Customization Points

**Custom Repair Types:**
Edit Asset Repair custom field "repair_type":
- Options: "Repair\nPreventive Maintenance\nBreakdown\nInspection\nReplacement\n[Your Custom Type]"

**Custom Status Badges:**
Add to CSS:
```css
.status-your-custom-status {
  background: #your-color;
  color: white;
}
```

**Custom Notifications:**
Edit `notify_reporter_to_verify()` in asset_repair_override.py

---

## Troubleshooting Guide

### Common Issues

#### Issue: Asset status not changing after approval

**Debug Steps:**
1. Check repair document:
   ```python
   doc = frappe.get_doc("Asset Repair", "AR-001")
   print(f"Workflow State: {doc.workflow_state}")
   print(f"Issue Severity: {doc.issue_severity}")
   ```

2. Check if hook is registered:
   ```python
   from tub_suite import hooks
   print(hooks.doc_events)
   # Should show Asset Repair hooks
   ```

3. Check override is loaded:
   ```python
   print(hooks.override_doctype_class)
   # Should show: {"Asset Repair": "tub_suite.overrides...CustomAssetRepair"}
   ```

4. Manual trigger:
   ```python
   from tub_suite.overrides.asset_repair_override import update_asset_status_on_approval
   doc = frappe.get_doc("Asset Repair", "AR-001")
   update_asset_status_on_approval(doc)
   ```

#### Issue: Verification not restoring asset

**Check:**
```python
# Count other Major repairs
other_repairs = frappe.db.count("Asset Repair", {
    "asset": "U-AC-01C",
    "issue_severity": "Major - Asset Must Stop",
    "workflow_state": ["not in", ["Finished", "Cancelled", "Rejected"]]
})
print(f"Other Major repairs: {other_repairs}")
# If > 0, asset correctly stays Out of Order
```

#### Issue: Portal settings not applying

**Debug:**
```python
settings = frappe.get_single("Maintenance Portal Settings")
print(f"Enable for all: {settings.enable_search_for_all_users}")

# Check API response
import requests
response = requests.post(
    "http://localhost:8000/api/method/tub_suite.api.maintenance.get_portal_settings",
    headers={"X-Frappe-CSRF-Token": "your-token"}
)
print(response.json())
```

**Clear Frontend Cache:**
```javascript
// In browser console
localStorage.clear()
location.reload()
```

### Log Locations

**Frappe Logs:**
```bash
tail -f /home/user/frappe-bench/sites/tub/logs/web.log
```

**Repair Workflow Debug:**
```python
# asset_repair_override.py has print statements
# Check console output:
print(f"🔧 ASSET STATUS UPDATE CALLED")
print(f"   Repair: {doc.name}")
```

**React Console:**
```javascript
// Browser DevTools → Console
// Check for errors and API responses
```

---

## Appendix: System Health Checks

### Daily Checks
- [ ] Pending approvals queue empty by EOD
- [ ] No assets stuck "Out of Order" unnecessarily
- [ ] All verifications processed within 24 hours
- [ ] Error logs clean

### Weekly Checks
- [ ] Database backup successful
- [ ] No orphaned repair documents
- [ ] Photo storage within limits
- [ ] Workflow states valid

### Monthly Checks
- [ ] Review system performance
- [ ] Audit trail integrity
- [ ] User role assignments current
- [ ] Asset status accuracy

---

**Document Version:** 1.0
**Last Updated:** December 16, 2024
**Prepared By:** TUB Suite Development Team

**For Support:** Contact system administrator or development team.
