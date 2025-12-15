# TUB Suite Maintenance Workflow

Complete workflow documentation for TUB Suite v2.0.0 maintenance management system.

---

## Table of Contents

1. [Workflow Overview](#workflow-overview)
2. [Role-Based Access](#role-based-access)
3. [Normal Maintenance Flow](#normal-maintenance-flow)
4. [Issue Reporting Flow](#issue-reporting-flow)
5. [Repair Workflow](#repair-workflow)
6. [Inspector Verification Flow](#inspector-verification-flow)
7. [Photo Requirements](#photo-requirements)
8. [Issue Severity System](#issue-severity-system)

---

## Workflow Overview

```
┌─────────────────┐
│  Asset Access   │
│  (QR/Search)    │
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │ Asset  │ ◄─── QR Code Scan (All Users)
    │  Page  │ ◄─── Manual Search (Managers Only)
    └────┬───┘
         │
         ▼
┌────────────────────┐
│ Maintenance Tasks  │
│   (TODO List)      │
└────────┬───────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────┐
│ Normal │ │  Issue   │
│  Flow  │ │  Report  │
└────┬───┘ └────┬─────┘
     │          │
     │          ▼
     │    ┌─────────────┐
     │    │ Repair      │
     │    │ Request     │
     │    └──────┬──────┘
     │           │
     │           ▼
     │    ┌──────────────┐
     │    │ Engineer     │
     │    │ Sets Severity│
     │    └──────┬───────┘
     │           │
     │      ┌────┴────┐
     │      │         │
     │      ▼         ▼
     │   ┌─────┐  ┌──────┐
     │   │Minor│  │Major │
     │   │Keep │  │Stop  │
     │   │Run  │  │Asset │
     │   └──┬──┘  └───┬──┘
     │      │         │
     │      │         ▼
     │      │    ┌─────────┐
     │      │    │ Out of  │
     │      │    │ Order   │
     │      │    └────┬────┘
     │      │         │
     │      ▼         ▼
     │    ┌────────────────┐
     │    │ Engineer Fixes │
     │    └────────┬───────┘
     │             │
     │             ▼
     │    ┌──────────────────┐
     │    │ Inspector Verify │
     │    │ (After Photos)   │
     │    └────────┬─────────┘
     │             │
     │             ▼
     │    ┌──────────────────┐
     │    │ Manager Approve  │
     │    └────────┬─────────┘
     │             │
     └─────────────┴──────────►
                   │
                   ▼
            ┌──────────┐
            │ Complete │
            └──────────┘
```

---

## Role-Based Access

### Maintenance User (Inspector)
**Access Method:**
- ✅ QR Code Scan ONLY
- ❌ Manual Search (Disabled in production)

**Permissions:**
- View assigned maintenance tasks
- Complete normal maintenance with inspection photos
- Report issues with issue photos
- Verify repair completion (only for issues they reported)

### Engineering Team (Inspector)
**Access Method:**
- ✅ QR Code Scan ONLY
- ❌ Manual Search (Disabled in production)

**Permissions:**
- Same as Maintenance User
- Additional technical maintenance tasks

### Maintenance Manager
**Access Method:**
- ✅ QR Code Scan
- ✅ Manual Search (Always enabled)

**Permissions:**
- All inspector permissions
- Upload maintenance schedules (Excel/CSV)
- Assign tasks to inspectors
- Approve completed repairs
- View all maintenance history
- Generate reports

---

## Normal Maintenance Flow

**Path A: No Issues Detected**

### 1. Task Assignment
- Manager uploads schedule OR
- Auto-assignment via ERPNext Assignment Rules
- Inspector sees tasks in TODO list

### 2. Asset Access
- Inspector scans QR code on asset
- System loads asset details and pending tasks

### 3. Task Completion
- Inspector performs maintenance checklist
- Takes **inspection photos** (minimum 1, maximum 5)
  - All photos have timestamps
  - Filename: `ASSET_ACTIVITY_TIMESTAMP_SEQ_USER.jpg`
  - Example: `PUMP001_INSP_20251215_143052_1_INSP001.jpg`
- Adds notes (optional)
- Submits task

### 4. Backend Processing
```python
# API: submit_maintenance_task()
# - has_issue = 0
# - inspection_photos required (min 1)
# - Creates Asset Maintenance Log
# - Updates task next_due_date
# - Asset status: UNCHANGED (stays In Service)
```

### 5. Result
- ✅ Task marked complete
- ✅ Next due date calculated
- ✅ Asset remains operational
- ✅ Log created with timestamped photos

---

## Issue Reporting Flow

**Path B: Issue Detected During Inspection**

### 1. Issue Detection
- Inspector finds problem during routine maintenance
- Examples:
  - Equipment malfunction
  - Safety hazard
  - Missing/damaged parts
  - Performance degradation

### 2. Issue Reporting
- Inspector selects "Report Issue"
- Takes **issue photos** (minimum 1, maximum 5)
  - **NO before photo required**
  - Only issue photos with timestamps
  - Filename: `PUMP001_ISSUE_20251215_143052_1_INSP001.jpg`
- Describes issue in detail
- Submits report

### 3. Backend Processing
```python
# API: submit_maintenance_task()
# - has_issue = 1
# - issue_photos required (min 1)
# - Creates Asset Repair request
# - Sets reported_by = current user
# - Sets verification_status = "Pending Verification"
# - Asset status: UNCHANGED (waits for engineer severity assessment)
```

### 4. Assignment
- Auto-assigned to engineer via Assignment Rules
- Engineer receives notification

---

## Repair Workflow

### 1. Engineer Assessment
- Engineer receives repair request
- Reviews issue photos and description
- **Sets Issue Severity:**
  - **Minor - Asset Operational**: Asset keeps running, low priority
  - **Major - Asset Must Stop**: Asset goes Out of Order immediately

### 2. Issue Severity Impact

#### Minor Issues
- Asset status: **In Service** (unchanged)
- Maintenance schedule: **Continues normally**
- Examples:
  - Cosmetic damage (stickers, labels)
  - Non-critical parts
  - Planned replacements
  - Performance optimization

#### Major Issues
- Asset status: **Out of Order** (automatic)
- Maintenance schedule: **Paused**
- Examples:
  - Safety hazards
  - Critical equipment failure
  - Legal/compliance violations
  - Production stoppage

### 3. Repair Execution
- Engineer performs repair work
- Sets expected completion date
- Updates repair notes
- Takes repair process photos (optional)

### 4. Repair Completion
- Engineer marks repair as "Ready for Verification"
- System notifies original inspector

---

## Inspector Verification Flow

**Critical Rule: Only the original reporter can verify repairs (unless Manager overrides)**

### 1. Verification Assignment
- Original inspector receives notification
- Repair appears in "Pending Verification" list
- Inspector must visit asset to verify

### 2. On-Site Verification
- Inspector goes to asset location
- Checks repair quality and completeness
- Takes **after-repair photos** (minimum 1, maximum 5)
  - Filename: `PUMP001_VERIFY_20251215_160000_1_INSP001.jpg`
  - Photos prove inspector physically present
  - Timestamps prove verification time

### 3. Verification Decision
Inspector selects one of:

#### ✅ Verified - Passed
- Repair is complete and satisfactory
- Issue is fully resolved
- Asset ready for return to service
- Forwards to manager for final approval

#### ❌ Verified - Failed
- Repair incomplete or unsatisfactory
- Issue still present or new issues found
- Returns to engineer with notes
- Requires re-work

### 4. Backend Processing
```python
# API: verify_repair_completion()
# - Requires original reporter OR manager role
# - verification_photos required (min 1)
# - Sets verified_by = current user
# - Sets verification_date = timestamp
# - Updates verification_status
```

### 5. Manager Approval
- Manager reviews verification
- Checks all photos (issue → repair → verification)
- Approves or requests changes
- If approved and Major severity:
  - Asset status: **In Service** (restored)
  - Maintenance schedule: **Resumed**

---

## Photo Requirements

### All Photos Must Have
- ✅ **Timestamp overlay** (proof of when taken)
- ✅ **Structured filename** (audit trail)
- ✅ **Minimum 1 photo** per activity
- ✅ **Maximum 5 photos** per activity

### Photo Types

| Activity Type | Photo Code | Purpose | Required |
|--------------|------------|---------|----------|
| Normal Inspection | `INSP` | Prove inspection completed | ✅ Yes |
| Issue Reporting | `ISSUE` | Document problem | ✅ Yes |
| Repair Verification | `VERIFY` | Prove repair verified | ✅ Yes |

### Filename Format
```
{ASSET}_{ACTIVITY}_{YYYYMMDD_HHMMSS}_{SEQ}_{USER}.jpg

Examples:
- PUMP001_INSP_20251215_143052_1_INSP001.jpg
- MOTOR05_ISSUE_20251215_150000_1_ENG002.jpg
- CONVEYOR3_VERIFY_20251215_160000_1_INSP001.jpg
```

### Photo Metadata (JSON in File.description)
```json
{
  "asset": "PUMP-001",
  "activity_type": "INSP",
  "timestamp": "2025-12-15 14:30:52",
  "user": "inspector1@example.com",
  "sequence": 1,
  "original_filename": "IMG_1234.jpg"
}
```

---

## Issue Severity System

### Purpose
Not all issues require stopping the asset. Severity allows engineers to prioritize and maintain operations when safe.

### Severity Levels

#### Minor - Asset Operational
**Definition:** Issue exists but asset can safely continue operating

**Examples:**
- ID sticker missing, torn, or faded
- Cosmetic damage (scratches, dents)
- Non-critical sensor offline
- Scheduled maintenance items
- Documentation updates needed
- Minor performance degradation
- Lubrication reminder

**Asset Impact:**
- Status: **In Service** ✅
- Maintenance: **Continues normally** ✅
- Production: **No interruption** ✅

**Workflow:**
1. Inspector reports issue
2. Engineer sets "Minor" severity
3. Asset keeps running
4. Engineer fixes during next scheduled downtime
5. Inspector verifies when complete
6. Manager approves

#### Major - Asset Must Stop
**Definition:** Issue requires immediate attention and asset shutdown

**Examples:**
- Safety hazards (exposed wiring, leaks)
- Critical equipment failure
- Regulatory compliance violations
- Quality defects affecting product
- Production stoppage
- Emergency repairs

**Asset Impact:**
- Status: **Out of Order** ⛔
- Maintenance: **Paused** ⛔
- Production: **Stopped** ⛔

**Workflow:**
1. Inspector reports issue
2. Engineer sets "Major" severity
3. **Asset automatically goes Out of Order**
4. Production notified
5. Engineer prioritizes repair
6. Inspector verifies when complete
7. Manager approves
8. **Asset status restored to In Service**

### Who Sets Severity?
- **Inspector:** Reports the issue (no severity set initially)
- **Engineer:** Assesses and sets severity based on technical evaluation
- **Manager:** Can override severity if needed

### Changing Severity
- Engineer can change severity during repair if assessment changes
- Example: Minor issue reveals Major underlying problem → upgrade to Major
- Status change happens automatically when severity saved

---

## System Integration

### ERPNext Native Features

#### Assignment Rules
- Auto-assign maintenance tasks to inspectors
- Auto-assign repairs to engineers
- Based on asset location, type, or custom logic

#### Email Alerts
- Task due soon (1 day before)
- Task overdue
- Issue reported → notify engineer
- Repair ready → notify original inspector
- Verification complete → notify manager

#### TODO Lists
- Inspector sees assigned tasks
- Engineer sees assigned repairs
- Manager sees pending approvals

### Data Flow
```
Mobile App (React)
      ↓
  REST API
      ↓
Python Backend (maintenance.py)
      ↓
ERPNext DocTypes
      ↓
MariaDB Database
```

---

## Key Differences from v1.0

| Feature | v1.0 | v2.0 |
|---------|------|------|
| Normal completion photos | Before + After | Inspection only ✅ |
| Issue reporting photos | Before + Issue | Issue only ✅ |
| Inspector verification | ❌ None | ✅ Required |
| Asset status on issue | ❌ Always Out of Order | ✅ Based on severity |
| Photo timestamps | ❌ None | ✅ All photos |
| Photo naming | Random | ✅ Structured audit trail |
| Search access | All users | ✅ Manager only |
| Schedule upload | Manual entry | ✅ Excel/CSV import |

---

## Workflow States

### Asset States
- **In Service**: Normal operation, maintenance continues
- **Out of Order**: Major issue, stopped for repair
- **Under Maintenance**: (Future) Scheduled downtime

### Repair States
- **Pending**: Reported, awaiting engineer
- **In Progress**: Engineer working on it
- **Ready for Verification**: Repair complete, needs inspector
- **Verified - Passed**: Inspector approved
- **Verified - Failed**: Inspector rejected, needs rework
- **Completed**: Manager approved, closed

### Verification States
- **Pending Verification**: Awaiting original inspector
- **Verified - Passed**: Inspector confirms repair OK
- **Verified - Failed**: Inspector rejects repair
- **Not Required**: Manager override, skip verification

---

## Best Practices

### For Inspectors
1. Always take clear, well-lit photos
2. Capture timestamps on all photos
3. Report issues immediately when found
4. Verify only repairs you originally reported
5. Be thorough in verification - reject if not satisfied

### For Engineers
1. Assess severity accurately
2. Use "Minor" when asset can safely continue
3. Use "Major" only when shutdown necessary
4. Set realistic completion dates
5. Document repair process in notes

### For Managers
1. Review all photos before approval
2. Trust inspector verification
3. Override severity only when necessary
4. Use Assignment Rules to balance workload
5. Monitor overdue tasks regularly

---

## API Reference

See [PHOTO_SYSTEM.md](PHOTO_SYSTEM.md) for photo utilities.

### Key Endpoints

```python
# Submit maintenance task
submit_maintenance_task(
    maintenance_name,
    task_name,
    asset_name,
    has_issue=0,
    issue_description="",
    notes="",
    inspection_photos=[],  # For normal completion
    issue_photos=[]        # For issue reporting
)

# Get repairs needing verification
get_repair_for_verification(repair_name)

# Verify repair completion
verify_repair_completion(
    repair_name,
    verification_photos=[],
    verification_notes="",
    verification_status="Verified - Passed"
)
```

---

## Troubleshooting

### Common Issues

**Q: Inspector can't verify a repair**
- A: Only the original reporter can verify. Check `reported_by` field.
- Manager can verify any repair.

**Q: Asset still Out of Order after Minor severity set**
- A: Only Major severity triggers Out of Order. Check severity field.

**Q: Photo upload fails**
- A: Check file size (<5MB), format (JPG/PNG), and timestamp overlay.

**Q: Task not showing in TODO list**
- A: Check Assignment Rules configuration and user roles.

---

## Version History

- **v2.0.0** (2025-12-15)
  - Issue severity system added
  - Inspector verification workflow
  - Photo timestamp system
  - Role-based search restrictions
  - Structured photo naming

- **v1.0.0** (Initial release)
  - Basic maintenance tracking
  - Before/after photos
  - QR code scanning

---

**Document Version:** 2.0.0
**Last Updated:** 2025-12-15
**Maintained By:** TUB Suite Development Team
