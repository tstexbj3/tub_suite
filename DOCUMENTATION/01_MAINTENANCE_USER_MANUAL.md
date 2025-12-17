# TUB Maintenance Portal - Maintenance User Manual

**Role:** Maintenance User
**Access:** Mobile Portal Only (http://localhost:8000/maintenance)
**Primary Duties:** Asset inspections, issue reporting, repair verification

---

## Table of Contents
1. [Getting Started](#getting-started)
2. [Daily Workflow](#daily-workflow)
3. [Scanning Assets](#scanning-assets)
4. [Completing Checklists](#completing-checklists)
5. [Reporting Issues](#reporting-issues)
6. [Verifying Repairs](#verifying-repairs)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Accessing the Portal

1. Open your mobile browser (Chrome, Safari, Edge)
2. Navigate to: `http://localhost:8000/maintenance` (or your production URL)
3. Login with your ERPNext credentials
   - Username: Your email address
   - Password: Your ERPNext password
4. You will see the TUB Maintenance Portal home page

**Screenshot Location:** Home page with QR scanner

### Understanding Your Role

As a **Maintenance User**, you have access to:
- ✅ **My Tasks** - View your assigned maintenance tasks (overdue, due today, upcoming)
- ✅ QR Code Scanner - Scan assets for inspection
- ✅ Maintenance Checklists - Complete daily/weekly/monthly tasks
- ✅ Issue Reporting - Report problems with photos
- ✅ Repair Verification - Verify completed repairs
- ❌ Search Function - Not available (Managers only)
- ❌ ERPNext Desk - Should not be used

**IMPORTANT:** You should work entirely from the mobile portal. Do NOT use the ERPNext desk interface.

---

## Daily Workflow

### Typical Day Routine

**RECOMMENDED WORKFLOW:**

1. **Check My Tasks** (📋)
   - Open the portal: `http://localhost:8000/maintenance`
   - Click "My Tasks" card on home page
   - View your assigned maintenance tasks:
     - 🔥 **Overdue** (Red) - Complete these first!
     - ⚠️ **Due Today** (Orange) - Complete today
     - 📅 **Upcoming** (Blue) - Tasks due in next 7 days
   - Click any task card to go directly to that asset's checklist

2. **Scan QR Codes**
   - Alternative to My Tasks
   - Scan QR code on physical asset
   - Complete the checklist

3. **Report Issues**
   - If you find problems during inspection
   - Take photos (minimum 2 required)
   - Describe the issue

4. **Verify Repairs**
   - Check "Pending Verifications" alert (if any)
   - Verify completed repairs with photos
   - Sign off on repair quality

---

## My Tasks Feature

### Overview

The **My Tasks** page shows all maintenance tasks assigned to you, organized by urgency. This is your daily todo list.

### Accessing My Tasks

1. From **Home Page:**
   - Click the "📋 My Tasks" card
   - OR navigate to: `http://localhost:8000/maintenance/todos`

2. You will see:
   - **Summary Stats** at top:
     - Overdue count (red)
     - Due Today count (orange)
     - Upcoming count (blue)
   - **Task Sections:**
     - Overdue tasks (if any)
     - Due Today tasks
     - Upcoming tasks (next 7 days)

### Task Assignment Rules

**CRITICAL: You only see tasks where:**
- `Asset Maintenance Task.assign_to` field = **Your email address**
- Asset Maintenance is Submitted (docstatus = 1)
- Maintenance Status = "Planned" (active schedules)
- `next_due_date` is set

**Example:**
- If you're logged in as `test_maintenance_repair@test.com`
- You will ONLY see tasks assigned to `test_maintenance_repair@test.com`
- If logged in as `admin@example.com`, you see tasks assigned to `admin@example.com`

**If you see "All Caught Up!":**
- Either no tasks are assigned to your email, OR
- No tasks are due within the next 7 days, OR
- No Asset Maintenance records exist

### Task Card Information

Each task card shows:
- **Asset Name** - Which equipment to inspect
- **Asset Code** - Asset identifier (e.g., ACC-ASS-2025-00019)
- **Task Name** - What to do (e.g., "Daily Pressure Check")
- **Due Status Badge:**
  - Red = X days late
  - Orange = Due Today
  - Blue = Due on [date]
- **Location** 📍 - Where to find the asset
- **Periodicity** 🔄 - How often (Daily, Weekly, Monthly, etc.)
- **Maintenance Type** 🔧 - Type of maintenance

### Using My Tasks

1. **Click any task card** to go directly to that asset's checklist
2. **Complete the inspection** as normal
3. **Task automatically updates** after completion:
   - `last_completion_date` is set
   - `next_due_date` is calculated based on periodicity
   - Task moves to upcoming or disappears from overdue

### Priority Order

Always complete tasks in this order:
1. 🔥 **Overdue** (highest priority)
2. ⚠️ **Due Today** (medium priority)
3. 📅 **Upcoming** (plan ahead)

---

## Scanning Assets

```
Morning:
1. Login to maintenance portal
2. Check for pending verification alerts (red banner at top)
3. Verify any completed repairs from previous days
4. Start daily inspections

During Day:
5. Scan QR code on each asset
6. Complete maintenance checklist
7. Report any issues immediately with photos
8. Continue to next asset

End of Day:
9. Review all completed tasks
10. Ensure all issues were properly reported
```

---

## Scanning Assets

### How to Scan QR Codes

1. **From Home Page:**
   - Click inside the QR scanner box (📷 icon)
   - Allow camera access when prompted
   - Point camera at asset QR code
   - Wait for automatic scan

2. **QR Code Location:**
   - Look for white label with black QR code
   - Usually located on front/side of equipment
   - Clean QR code if dirty or damaged

3. **After Successful Scan:**
   - Screen will automatically navigate to checklist
   - Asset name and details will appear at top
   - Maintenance tasks will load automatically

**Screenshot Location:** QR scanner interface

### If QR Code Won't Scan

**Problem:** Camera not working
- Solution: Check browser permissions (Settings → Privacy → Camera)
- Solution: Try different browser (Chrome recommended)

**Problem:** QR code damaged/unreadable
- Solution: Contact Maintenance Manager to print new QR label
- Solution: Use search function (if you have manager role)

**Problem:** "Asset not found" error
- Solution: Asset may not be registered in system
- Solution: Contact Maintenance Manager with asset details

---

## Completing Checklists

### Understanding the Checklist Screen

After scanning, you'll see:

```
┌─────────────────────────────────────┐
│ ASSET INFO                          │
│ Name: Air Conditioner Room 1        │
│ Code: U-AC-01C                      │
│ Location: Meeting Room Floor 2      │
│ Status: Submitted (green badge)     │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ MAINTENANCE CHECKLIST               │
│                                     │
│ ☐ Check filter cleanliness          │
│   Daily | Overdue (red badge)       │
│                                     │
│ ☐ Check temperature display         │
│   Daily | Due Today (orange badge)  │
│                                     │
│ ☐ Check remote control battery      │
│   Weekly | Due Soon (orange badge)  │
│                                     │
│ ☐ Inspect drainage pipe             │
│   Monthly | Next: 25/12/2025 (gray) │
└─────────────────────────────────────┘
```

### Badge Colors Explained

| Badge | Meaning | Action Required |
|-------|---------|----------------|
| **Red** "เกินกำหนด" | Overdue | Complete immediately |
| **Orange** "ถึงกำหนดวันนี้" | Due Today | Complete today |
| **Orange** "ใกล้ถึงกำหนด" | Due Soon (within 7 days) | Can complete now |
| **Blue** "เสร็จวันนี้" | Completed Today | Cannot check again today |
| **Gray** "ครั้งถัดไป..." | Not Due Yet | Cannot check yet |

### How to Complete Tasks

1. **Check the Checkbox:**
   - Tap the checkbox next to each task
   - Checked tasks turn green
   - Only check after actually performing the task

2. **Add Notes (Optional):**
   - Scroll down to "Maintenance Notes" field
   - Add any observations or comments
   - Example: "Filter was very dirty, cleaned thoroughly"

3. **Take Photos (Optional for normal inspection):**
   - Scroll to photo upload section
   - Tap "Choose Files" or use camera
   - Take clear, well-lit photos
   - Minimum 1 photo required if issue reported

4. **Report Issue (If Found):**
   - See next section: [Reporting Issues](#reporting-issues)

5. **Submit Checklist:**
   - Scroll to bottom
   - Tap blue "Submit Checklist" button
   - Wait for confirmation message

**Screenshot Location:** Checklist with tasks checked

### Task Completion Rules

**Same-Day Limit:**
- Each task can only be checked ONCE per day
- If completed today, badge shows blue "เสร็จวันนี้"
- You cannot check again until tomorrow

**Future Tasks:**
- Gray badge "ครั้งถัดไป..." means not due yet
- You cannot check these tasks early
- Wait until due date arrives

**Overdue Tasks:**
- Red badge "เกินกำหนด" means missed deadline
- Complete these FIRST before other tasks
- Your manager can see overdue tasks in reports

---

## Reporting Issues

### When to Report an Issue

Report immediately if you notice:
- ❌ Equipment not working
- ❌ Strange noises or smells
- ❌ Visible damage or wear
- ❌ Safety hazards
- ❌ Any abnormal operation

### How to Report an Issue

1. **Complete Checklist First:**
   - Check all applicable tasks
   - Even if equipment is broken, complete what you can

2. **Enable "Report Issue":**
   - Scroll to "Report an Issue" section
   - Check the box: ☑ "Report an Issue"
   - New fields will appear

3. **Describe the Problem:**
   - Type clear description in "Issue Description" field
   - Be specific: What happened? When? How bad?
   - Examples:
     - ✅ "Air conditioner not cooling. Temperature stays at 28°C even when set to 20°C. Started this morning around 9 AM."
     - ❌ "AC broken" (too vague)

4. **Take Issue Photos (REQUIRED):**
   - Minimum 2 photos required
   - Take photos showing:
     - Overall view of equipment
     - Close-up of problem area
     - Any error messages or displays
   - Photos must be clear and well-lit

5. **Submit:**
   - Tap blue "Submit Checklist" button
   - System creates Asset Repair request automatically
   - Engineering Team receives notification

**Screenshot Location:** Issue reporting section with photos

### After Reporting

**What Happens Next:**
1. Engineering Team receives notification immediately
2. Maintenance Manager reviews and approves repair
3. Engineer performs repair work
4. You receive notification to verify repair (see next section)

**Your Responsibility:**
- Keep your phone/email accessible for verification notification
- Respond to verification requests within 24 hours
- If problem persists after repair, report again

---

## Verifying Repairs

### Understanding Verification Workflow

**Why Verification is Required:**
- You reported the problem, so you must verify the fix
- Ensures repairs are actually completed correctly
- Holds both you and engineer accountable

**When You Get Notification:**
- After engineer marks repair as "Job Finished"
- You receive alert on portal home page
- Red banner shows pending verifications count

### How to Verify a Repair

1. **Check Home Page:**
   - Red alert banner appears at top
   - Shows: "⚠️ รอการตรวจสอบ - You have X repair(s) waiting for your verification"
   - Lists all repairs needing verification

**Screenshot Location:** Home page with verification alert

2. **Click on Repair:**
   - Tap the repair card to open verification page
   - Review repair details:
     - Asset name and location
     - Original problem description
     - Engineer's repair notes
     - Actions performed
     - Repair date

3. **GO TO ASSET:**
   - **IMPORTANT:** You must physically go to the asset location
   - Do NOT verify from your desk
   - Scan the asset QR code if possible
   - Test the equipment thoroughly

4. **Test the Repair:**
   - Turn on equipment
   - Check that problem is fixed
   - Test all functions
   - Observe for 5-10 minutes minimum

5. **Take Verification Photos (REQUIRED):**
   - Minimum 2 photos required
   - Take photos showing:
     - Equipment running normally
     - Fixed component/area
     - Display showing normal operation
   - Photos must be clear and recent (not old photos)

**Screenshot Location:** Photo upload in verification

6. **Read the Disclaimer:**
   - Important notice about 7-day responsibility
   - You are responsible if problem returns within 7 days
   - Read carefully before checking

**Disclaimer Text:**
```
⚠️ ประกาศสำคัญ / Important Notice

การยืนยันการตรวจสอบนี้ คุณรับทราบและยอมรับว่า:
By confirming this verification, you acknowledge and accept that:

• คุณได้ตรวจสอบอุปกรณ์ด้วยตนเอง
  You have personally inspected the equipment

• งานซ่อมแซมเสร็จสมบูรณ์และถูกต้อง
  The repair work is complete and correct

• อุปกรณ์ทำงานได้ตามปกติ
  The equipment operates normally

• หากปัญหาเดิมเกิดขึ้นอีกภายใน 7 วัน คุณจะต้องรับผิดชอบ
  ในการรายงานปัญหาอีกครั้ง และอาจถูกตั้งคำถามถึงความรอบคอบ
  ในการตรวจสอบครั้งนี้
  If the same problem reoccurs within 7 days, you will be responsible
  for reporting it again and may be questioned about the thoroughness
  of this verification
```

7. **Check Confirmation Box:**
   - Check: ☑ "ฉันยืนยันว่าได้ตรวจสอบอุปกรณ์แล้วและทำงานได้ตามปกติ"
   - This is MANDATORY - cannot submit without checking
   - Only check if you truly verified the equipment

8. **Submit Verification:**
   - Tap blue "Submit Verification" button
   - System marks repair as "Verified - Passed"
   - Asset returns to service automatically
   - Confirmation message appears

**Screenshot Location:** Confirmation checkbox and submit button

### Verification Requirements

| Requirement | Status | Details |
|------------|--------|---------|
| Physical Inspection | MANDATORY | Must go to asset location |
| Equipment Testing | MANDATORY | Must test equipment operation |
| Verification Photos | MANDATORY | Minimum 2 photos |
| Read Disclaimer | MANDATORY | Must understand 7-day rule |
| Confirmation Checkbox | MANDATORY | Must check to submit |
| Verification Notes | Optional | Can add comments |

### What If Problem Not Fixed?

**If equipment still broken:**
1. DO NOT verify the repair
2. Contact the engineer immediately
3. Contact Maintenance Manager
4. Report new issue through normal process
5. Original repair will remain "Finished" but unverified

**If problem partially fixed:**
1. DO NOT verify
2. Contact engineer and manager
3. Engineer must complete work properly
4. Wait for proper completion before verifying

**Remember:**
- Your verification means "I confirm this is 100% fixed"
- Do NOT verify if you have any doubts
- You are responsible for 7 days after verification

---

## Troubleshooting

### Common Problems and Solutions

#### Problem: Cannot login to portal

**Symptoms:** "Invalid credentials" or "Access denied"

**Solutions:**
1. Check you're using correct URL (http://localhost:8000/maintenance)
2. Use your ERPNext email and password (same as desk login)
3. Clear browser cache and cookies
4. Try incognito/private browser window
5. Contact IT if password forgotten

#### Problem: QR scanner not opening

**Symptoms:** Black screen or "Camera access denied"

**Solutions:**
1. Allow camera permission in browser settings
2. Check camera is not used by another app
3. Try different browser (Chrome recommended)
4. Restart browser
5. Check phone camera hardware works in camera app

#### Problem: Photos won't upload

**Symptoms:** "Upload failed" or stuck uploading

**Solutions:**
1. Check internet connection (WiFi or mobile data)
2. Check file size (max 5MB per photo recommended)
3. Take new photo instead of selecting old one
4. Try uploading one photo at a time
5. Clear browser cache and retry

#### Problem: Asset shows "Out of Order" - cannot check

**Symptoms:** Red "Out of Order" badge, checklist hidden

**Solutions:**
1. This is CORRECT behavior - asset is broken
2. Do NOT attempt inspection when out of order
3. Check if there's an active repair for this asset
4. Contact Maintenance Manager for status
5. Move to next asset on your route

#### Problem: Cannot verify repair - not in list

**Symptoms:** Verification alert shows 0 repairs

**Solutions:**
1. Check you're logged in with correct account
2. Verification only shows repairs YOU reported
3. Engineer may not have finished yet (status must be "Finished")
4. Check your email for notification
5. Contact Maintenance Manager to check repair status

#### Problem: Completed task still shows red "Overdue"

**Symptoms:** Badge doesn't change after checking

**Solutions:**
1. Make sure you clicked "Submit Checklist" button
2. Check for success message after submission
3. Refresh page (pull down on mobile)
4. If still red after refresh, task was not saved - redo it
5. Check internet connection during submission

#### Problem: "You have already completed this task today"

**Symptoms:** Blue "เสร็จวันนี้" badge, cannot check

**Solutions:**
1. This is CORRECT behavior - one check per day limit
2. Task was completed earlier today (check time stamp)
3. If you believe this is error, contact Maintenance Manager
4. Otherwise, return tomorrow to check again

---

## Quick Reference

### Dos and Don'ts

**✅ DO:**
- Check equipment thoroughly before completing checklist
- Take clear, well-lit photos
- Report issues immediately when found
- Verify repairs in person at equipment location
- Read disclaimers before confirming
- Contact manager if unsure about anything

**❌ DON'T:**
- Check tasks you didn't actually perform
- Submit fake or old photos
- Verify repairs without testing equipment
- Use ERPNext desk interface (mobile portal only)
- Check confirmation box if you didn't verify
- Ignore verification notifications

### Important Phone Numbers

- Maintenance Manager: [Add phone number]
- Engineering Team: [Add phone number]
- IT Support: [Add phone number]
- Emergency: [Add emergency number]

### Portal URL

- Production: [Add your production URL]
- Local/Testing: http://localhost:8000/maintenance

---

## Appendix: Screenshot Placeholders

The following screenshots should be taken and added to this manual:

1. **Home Page** - Login screen and portal home with QR scanner
2. **QR Scanner** - Camera interface scanning QR code
3. **Checklist View** - Asset details and maintenance tasks with various badge colors
4. **Task Checked** - Green checkmarks on completed tasks
5. **Issue Reporting** - Report issue section with description and photos
6. **Photo Upload** - Interface for uploading multiple photos
7. **Verification Alert** - Red banner at top of home page
8. **Verification Page** - Repair details and verification form
9. **Disclaimer** - Important notice text with confirmation checkbox
10. **Success Message** - Confirmation after successful submission

**Note:** Screenshots should be taken on actual mobile device in portrait orientation for accuracy.

---

**Document Version:** 1.0
**Last Updated:** December 16, 2024
**Prepared By:** TUB Suite Development Team
