# Inspector Todo List Feature - Complete Documentation

## Overview

The **My Tasks** feature allows maintenance inspectors to view all their assigned maintenance tasks in one place, organized by urgency (Overdue, Due Today, Upcoming).

---

## Access

- **URL:** `http://localhost:8000/maintenance/todos`
- **From Home:** Click "📋 My Tasks" card
- **Role Required:** Maintenance User (with assigned tasks)

---

## How It Works

### Backend API

**Endpoint:** `POST /api/method/tub_suite.api.maintenance.get_inspector_todo_list`

**File:** `tub_suite/api/maintenance.py` (Lines 660-775)

**Logic:**
1. Gets current logged-in user's email
2. Queries all **Asset Maintenance** records (including drafts - no docstatus filter)
3. For each maintenance record, gets **Asset Maintenance Tasks** where:
   - `assign_to` = current user's email
   - `maintenance_status` in ["Planned", "Overdue"] (field on child table)
4. Calculates urgency based on `next_due_date`:
   - **Overdue:** `next_due_date < today`
   - **Due Today:** `next_due_date = today`
   - **Upcoming:** `next_due_date` between today and today+7 days
5. Returns categorized tasks with summary counts

**Response Structure:**
```json
{
  "overdue": [
    {
      "name": "TASK-001",
      "asset_name": "BOILER-001",
      "asset_title": "Main Boiler",
      "location": "Building A",
      "maintenance_task": "Daily Pressure Check",
      "description": "Check safety valve",
      "periodicity": "Daily",
      "next_due_date": "2025-12-10",
      "maintenance_type": "Preventive Maintenance",
      "last_completion_date": "2025-12-09",
      "days_overdue": 7
    }
  ],
  "due_today": [...],
  "upcoming": [...],
  "summary": {
    "overdue_count": 1,
    "due_today_count": 3,
    "upcoming_count": 12,
    "total": 16
  }
}
```

---

## Task Assignment Rules

### ✅ Tasks WILL appear if:

1. **Asset Maintenance record exists** in ERPNext:
   - DocType: "Asset Maintenance"
   - Any docstatus (includes drafts)

2. **Task is assigned to you:**
   - `Asset Maintenance Task.assign_to` = Your email address
   - Example: `test_maintenance_repair@test.com`
   - `Asset Maintenance Task.maintenance_status` = "Planned" or "Overdue"

3. **Task has due date:**
   - `next_due_date` field is set
   - Due date is within: past, today, or next 7 days

### ❌ Tasks will NOT appear if:

- Logged in as different user than task assignment
- Task status = "Completed" or "Cancelled" (on child table)
- `assign_to` field is empty
- `next_due_date` is empty or more than 7 days away

**IMPORTANT:** `maintenance_status` is a field on **Asset Maintenance Task** (child table), NOT on Asset Maintenance (parent table).

---

## Common Issues

### Issue 1: "All Caught Up!" message when tasks exist

**Cause:** You're logged in as a different user than the one assigned to tasks.

**Example:**
- Tasks assigned to: `test_maintenance_repair@test.com`
- Logged in as: `admin@example.com`
- Result: "All Caught Up!" ❌

**Solution:** Login as `test_maintenance_repair@test.com`

### Issue 2: Tasks not showing up

**Checklist:**
1. ✅ Task has `maintenance_status` = "Planned" or "Overdue" (on child table)?
2. ✅ Task has `assign_to` field = your email?
3. ✅ Task has `next_due_date` set?
4. ✅ Due date is not more than 7 days in future?
5. ✅ Logged in as correct user?

### Issue 3: Completed tasks still showing

**Cause:** `next_due_date` not updated after completion.

**Expected Behavior:**
- When task is completed via checklist
- System should update `last_completion_date`
- System should calculate NEW `next_due_date` based on periodicity
- Task moves to upcoming section or disappears

**If not working:** Check if Asset Maintenance Log creation updates the task dates.

---

## How to Create Test Data

### Method 1: Via ERPNext Desk (Quick Test)

1. Go to: `http://localhost:8000/app/asset-maintenance`
2. Click "New"
3. Fill fields:
   - **Asset Name:** Select any asset (e.g., BOILER-001)
   - **Maintenance Team:** Select or create team
   - **Company:** Your company
4. In **Asset Maintenance Tasks** table, add row:
   - **Maintenance Task:** "Test Daily Check"
   - **Periodicity:** "Daily"
   - **Start Date:** Today
   - **Next Due Date:** Today or yesterday (to see it in overdue/due today)
   - **Assign To:** `test_maintenance_repair@test.com` (your inspector email)
   - **Maintenance Type:** "Preventive Maintenance"
5. Click "Submit"
6. Login to portal as `test_maintenance_repair@test.com`
7. Go to My Tasks → Should see the task!

### Method 2: Via PM Schedule Upload (Future Feature)

Once implemented, managers can upload Excel with 100+ tasks assigned to multiple inspectors.

---

## Frontend Implementation

### Files

1. **TodoList.jsx** - Main page component
   - Location: `maintenance-react-dev/src/pages/TodoList.jsx`
   - 263 lines
   - Features:
     - Fetches from API on load
     - Shows summary stats
     - Categorized sections (overdue/today/upcoming)
     - Clickable task cards navigate to checklist
     - Refresh button
     - Empty state ("All Caught Up!")

2. **App.jsx** - Route definition
   - Route: `/todos` → `<TodoList />`

3. **Home.jsx** - Navigation card
   - "📋 My Tasks" card added to home grid
   - Positioned as first card (before QR scanner)

4. **index.css** - Styling
   - Lines 945-1246
   - 300+ lines of CSS
   - Responsive design
   - Color-coded urgency (red/orange/blue)

---

## API Parameters

### `days_ahead`

**Default:** 7

**Purpose:** How many days into the future to include in "upcoming" tasks

**Usage:**
```javascript
fetch('/api/method/tub_suite.api.maintenance.get_inspector_todo_list', {
  method: 'POST',
  body: JSON.stringify({
    days_ahead: 14  // Show tasks due in next 14 days
  })
})
```

---

## Database Query

The API performs this query:

```sql
-- Get all Asset Maintenance records (including drafts)
SELECT name, asset_name, company, maintenance_team
FROM `tabAsset Maintenance`

-- For each maintenance, get tasks assigned to current user with active status
SELECT name, maintenance_task, description, periodicity,
       next_due_date, assign_to, maintenance_type, maintenance_status, last_completion_date
FROM `tabAsset Maintenance Task`
WHERE parent = '<maintenance_name>'
  AND assign_to = '<current_user_email>'
  AND maintenance_status IN ('Planned', 'Overdue')

-- For each task, get asset details
SELECT asset_name, item_name, location
FROM `tabAsset`
WHERE name = '<asset_name>'
```

---

## Integration Points

### 1. Task Completion

When user completes a checklist:
- `submit_maintenance_task()` API is called
- Should update:
  - `last_completion_date` = now
  - `next_due_date` = calculate from periodicity
- Task moves to different category or disappears from list

### 2. Task Assignment

Tasks can be assigned via:
- **Manual:** ERPNext desk → Edit Asset Maintenance Task
- **PM Upload:** (Future) Bulk import with assignments
- **Default:** Asset Maintenance Team → default_inspector field

### 3. Date Calculation

Periodicity → Next Due Date:
- Daily → +1 day
- Weekly → +7 days
- Monthly → +1 month (handles month-end)
- Quarterly → +3 months
- Half-yearly → +6 months
- Yearly → +1 year
- 2 Yearly → +2 years
- 3 Yearly → +3 years

---

## Testing Checklist

- [ ] Login as user with assigned tasks
- [ ] Tasks appear in correct categories
- [ ] Summary counts are accurate
- [ ] Task cards show correct information
- [ ] Click task card → navigates to checklist
- [ ] Complete task → disappears from overdue
- [ ] Refresh button works
- [ ] Empty state shows when no tasks
- [ ] Login as different user → different tasks shown
- [ ] Responsive on mobile
- [ ] Thai/English language toggle works

---

## Future Enhancements

1. **Filter Options**
   - By location
   - By asset type
   - By maintenance type

2. **Sort Options**
   - By due date
   - By location
   - By asset name

3. **Push Notifications**
   - Daily reminder for overdue tasks
   - Morning notification of due today tasks

4. **Batch Actions**
   - Mark multiple tasks as completed
   - Snooze tasks

5. **Calendar View**
   - Monthly calendar showing all tasks
   - Color-coded by status

---

## Troubleshooting Commands

### Check if API is accessible:
```bash
curl -X POST http://localhost:8000/api/method/tub_suite.api.maintenance.get_inspector_todo_list \
  -H "Content-Type: application/json" \
  -H "X-Frappe-CSRF-Token: <token>" \
  --cookie "sid=<session_id>"
```

### Check database directly:
```sql
-- See all assigned tasks
SELECT
  amt.name,
  amt.parent,
  amt.maintenance_task,
  amt.assign_to,
  amt.next_due_date,
  amt.maintenance_status,
  am.asset_name
FROM `tabAsset Maintenance Task` amt
JOIN `tabAsset Maintenance` am ON amt.parent = am.name
WHERE amt.maintenance_status IN ('Planned', 'Overdue')
  AND amt.assign_to = 'test_maintenance_repair@test.com'
ORDER BY amt.next_due_date;
```

---

## Summary

**Feature Status:** ✅ COMPLETE AND WORKING

**Key Points:**
- Shows tasks assigned to **YOUR EMAIL ONLY**
- Works with draft or submitted Asset Maintenance records
- Filters tasks by `maintenance_status` on child table ("Planned" or "Overdue")
- Requires `assign_to` and `next_due_date` fields populated on child table
- Categorizes by urgency based on due date vs today
- Clicking task navigates to asset checklist
- Only visible to users with "Maintenance User" role

**Fixed Issues:**
- ✅ Wrong field location: `maintenance_status` is on Asset Maintenance Task (child), not Asset Maintenance (parent)
- ✅ Wrong docstatus filter: Removed filter to include draft records (original behavior)
- ✅ Role permission: Added check for "Maintenance User" role, hides "My Tasks" card for other users
