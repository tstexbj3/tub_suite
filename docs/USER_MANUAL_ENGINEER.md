# 🔧 Engineering Team User Manual
**Role:** Engineering Team
**Platform:** ERPNext Desktop (Web Browser)
**Version:** v2.1.0

---

## Table of Contents
1. [Overview](#overview)
2. [Accessing the System](#accessing-the-system)
3. [Receiving Repair Requests](#receiving-repair-requests)
4. [Working on Repairs](#working-on-repairs)
5. [Submitting for Approval](#submitting-for-approval)
6. [After Manager Decision](#after-manager-decision)
7. [Troubleshooting](#troubleshooting)

---

## Overview

### What You Do
As an **Engineering Team Member**, you are responsible for:
- ✅ Receiving and reviewing repair requests from inspectors
- ✅ Investigating reported issues
- ✅ Performing actual repairs and maintenance work
- ✅ Documenting work performed with photos and notes
- ✅ Submitting completed work for manager approval

### What You DON'T Do
- ❌ You do NOT approve your own repairs
- ❌ You do NOT verify completed repairs (inspectors do this)
- ❌ You do NOT edit manager approval decisions

### Your Workflow
```
1. Receive notification → New issue reported
2. Review issue details → Check photos, description
3. Draft repair plan → Document actions needed
4. Perform repair work → Fix the issue
5. Document completion → Photos, signature, notes
6. Submit for approval → Manager reviews
7. Wait for decision → Approved/Rejected
   ├─ If Approved → Mark as Finished
   └─ If Rejected → Review feedback, resubmit or abandon
```

---

## Accessing the System

### Step 1: Open ERPNext
1. Open your web browser (Chrome, Edge, Firefox)
2. Navigate to: `https://tub.x-desk.tech`
3. **Do NOT use** the mobile portal at `/maintenance`

**[SCREENSHOT 1: ERPNext login page]**

### Step 2: Log In
1. Enter your username (provided by IT)
2. Enter your password
3. Click **Login**

**[SCREENSHOT 2: ERPNext login form]**

### Step 3: Navigate to Asset Repair
1. Click **Workspace** menu (top left)
2. Select **Asset**
3. Click **Asset Repair**

**[SCREENSHOT 3: Workspace menu with Asset section]**

**[SCREENSHOT 4: Asset Repair list view]**

### Alternative: Use Notifications
1. Click the **🔔 Bell icon** (top right)
2. View new repair notifications
3. Click notification to open repair directly

**[SCREENSHOT 5: Notification bell with badge]**

**[SCREENSHOT 6: Notification dropdown with repair alerts]**

---

## Receiving Repair Requests

### Step 1: Check Notifications
When an inspector reports an issue, you'll receive:
- 🔔 In-app notification
- 📧 Email notification (if enabled)

Notification content:
```
🚨 NEW REPAIR REQUEST
Asset: [Asset Name]
Reported by: [Inspector Name]
Issue: [Brief description]
```

**[SCREENSHOT 7: New repair notification]**

### Step 2: Open Repair Document
1. Click the notification OR
2. Go to Asset Repair list
3. Filter by **Workflow State = Draft**
4. Click on the repair name (e.g., "MAT-REP-2025-00123")

**[SCREENSHOT 8: Asset Repair list filtered by Draft]**

### Step 3: Review Issue Details
Check these fields:
- **Asset:** Which equipment needs repair
- **Failure Date:** When issue was reported (with time)
- **Description:** Inspector's problem description
- **Issue Severity:**
  - Minor - Asset Operational
  - Major - Asset Must Stop
- **Reported By:** Who found the issue
- **Maintenance Task:** Which checklist item failed

**[SCREENSHOT 9: Repair document - header section]**

### Step 4: View Issue Photos
1. Scroll to **Attachments** section at bottom
2. Click photos to view full size
3. Download if needed for reference

**[SCREENSHOT 10: Attachments section with issue photos]**

**[SCREENSHOT 11: Full-size issue photo viewer]**

### Step 5: Check Asset Status
The asset's status will be:
- **Out of Order** - Major severity (asset stopped)
- **In Maintenance** - Minor severity (asset operational but needs attention)

**[SCREENSHOT 12: Asset status indicator]**

---

## Working on Repairs

### Step 1: Plan Your Work
Before starting repairs, document your plan:

1. Scroll to **Engineering Details** section
2. Click **Add Row** in the table
3. Fill in each row:

| Field | What to Enter |
|---|---|
| **Action** | What you will do (e.g., "Replace front tire") |
| **Parts Required** | Parts needed (e.g., "1x Tire 205/55R16") |
| **Estimated Time** | How long (e.g., "2 hours") |

**[SCREENSHOT 13: Engineering Details table - empty]**

**[SCREENSHOT 14: Engineering Details table - filled with plan]**

### Step 2: Obtain Parts
1. Use the **Parts Required** column to create parts list
2. Get parts from warehouse/procurement
3. Update the table if actual parts differ from estimate

### Step 3: Perform the Repair
1. Go to the asset location
2. Perform the repair work
3. **Take photos** during/after repair:
   - Before repair (if not in issue photos)
   - During work
   - After completion

**[SCREENSHOT 15: Engineer performing repair work - example photo]**

### Step 4: Document Work Completed
1. Scroll to **Actions Performed** field
2. Write detailed notes of what you did:

**Good Example:**
```
1. Removed flat front left tire
2. Inspected rim - no damage found
3. Mounted new tire (205/55R16)
4. Inflated to 32 PSI
5. Balanced wheel
6. Test drove - no vibration, working normally
```

**Bad Example:**
```
Fixed tire
```

**[SCREENSHOT 16: Actions Performed field - good example]**

### Step 5: Attach Completion Photos
1. Scroll to **Attachments** section
2. Click **Attach** button
3. Select photos from your device
4. Add descriptive file names:
   - "After_Repair_New_Tire.jpg"
   - "Tire_Pressure_Reading.jpg"

**[SCREENSHOT 17: Attach file button and dialog]**

**Tip:** Photos should show:
- The completed repair
- New parts installed
- Any measurements/readings
- Asset in working condition

### Step 6: Add Your Signature
1. Scroll to **Engineer Signature** field
2. Click in the field
3. Type your full name or draw signature (if signature pad enabled)

**[SCREENSHOT 18: Engineer Signature field]**

**IMPORTANT:** Signature is **REQUIRED** before submitting for approval.

### Step 7: Save Your Progress
Click **Save** button (top right) frequently to avoid losing work.

**[SCREENSHOT 19: Save button location]**

---

## Submitting for Approval

### Step 1: Review Checklist
Before submitting, ensure:
- ✅ Engineering Details table filled
- ✅ Actions Performed documented
- ✅ Completion photos attached
- ✅ Engineer Signature added
- ✅ Repair actually tested and working

### Step 2: Change Workflow State
1. Locate the **Workflow** section (top right of form)
2. Current state should be **Draft**
3. Click **Submit for Approval** button

**[SCREENSHOT 20: Workflow section - Draft state]**

**[SCREENSHOT 21: Submit for Approval button]**

### Step 3: Confirm Submission
1. A dialog will appear asking for confirmation
2. Click **Yes** to proceed
3. The document will be submitted

**[SCREENSHOT 22: Submission confirmation dialog]**

### Step 4: Verify Submission Success
After submission:
- Workflow State changes to **Pending Approval**
- Form fields become **read-only** (locked)
- Manager Approval section appears (but you can't edit it)
- Managers receive notification

**[SCREENSHOT 23: Repair in Pending Approval state]**

**[SCREENSHOT 24: Manager Approval section - locked for engineers]**

### What Happens Next?
1. **Managers are notified** automatically
2. **Manager reviews** your work and documentation
3. **Manager decides:**
   - ✅ **Approve** → You can mark as Finished
   - ❌ **Reject** → You receive feedback

**You cannot edit anything while waiting for approval.**

---

## After Manager Decision

### Scenario A: Repair Approved ✅

#### Step 1: Receive Approval Notification
You'll get notification:
```
✅ REPAIR APPROVED
Asset: [Asset Name]
Manager: [Manager Name]
Notes: [Manager's comments]
```

**[SCREENSHOT 25: Approval notification]**

#### Step 2: Mark Repair as Finished
1. Open the repair document
2. Workflow state is now **Approved**
3. Click **Mark as Finished** button

**[SCREENSHOT 26: Mark as Finished button]**

#### Step 3: Confirm Completion
The workflow changes to **Finished**:
- Asset status updates (if applicable)
- Inspector receives verification notification
- Your work is complete

**[SCREENSHOT 27: Repair in Finished state]**

#### What Happens Next?
- **Inspector verifies** the repair quality
- If inspector marks "Verified - Passed", asset returns to service
- If inspector marks "Verified - Failed", you may need to rework

---

### Scenario B: Repair Rejected ❌

#### Step 1: Receive Rejection Notification
You'll get notification:
```
❌ REPAIR REJECTED
Asset: [Asset Name]
Manager: [Manager Name]
Reason: [Manager's explanation]
```

**[SCREENSHOT 28: Rejection notification]**

#### Step 2: Review Manager's Feedback
1. Open the repair document
2. Workflow state is now **Rejected**
3. Read the **Approval Notes** field (manager's reason)

**[SCREENSHOT 29: Rejected repair with manager notes]**

Common rejection reasons:
- Insufficient documentation
- Photos unclear or missing
- Work not completed properly
- Wrong parts used
- Safety concerns

#### Step 3: Decide Next Steps

**Option A: Rework and Resubmit**
If the issue is fixable:
1. Workflow state **Rejected** allows editing again
2. Make corrections based on manager feedback
3. Update Actions Performed
4. Add new photos if needed
5. Click **Submit for Approval** again

**[SCREENSHOT 30: Editing rejected repair]**

**Option B: Abandon Repair**
If the repair is no longer needed:
1. Ask manager to change workflow to **Cancelled**
2. Do not resubmit

#### Important Notes
- ❌ **You CANNOT edit manager's approval fields** (notes, signature)
- ✅ **You CAN edit all engineering fields** in Rejected state
- 🔄 **You CAN resubmit** after making corrections

---

## Field Restrictions

### Fields You CAN Edit (in Draft/Rejected)
- ✅ Engineering Details table
- ✅ Actions Performed
- ✅ Engineer Signature
- ✅ Attachments

### Fields You CANNOT Edit (Always Locked)
- 🔒 Failure Date (set when inspector reported)
- 🔒 Description (inspector's report)
- 🔒 Reported By
- 🔒 Maintenance Task

### Fields You CANNOT Edit (Manager Only)
- 🔒 Approval Notes
- 🔒 Approval Signature
- 🔒 Approval Timestamp

**If you try to edit manager fields, you'll get error:**
```
Engineers cannot edit Manager Approval fields.
This is restricted to Maintenance Managers only.
```

**[SCREENSHOT 31: Permission error when editing manager fields]**

---

## Troubleshooting

### Problem: "Engineer Signature Required" Error
**Cause:** You tried to submit without signing.

**Solution:**
1. Scroll to **Engineer Signature** field
2. Type your full name
3. Click **Save**
4. Try submitting again

**[SCREENSHOT 32: Engineer signature required error]**

---

### Problem: Can't Edit Repair Document
**Possible Causes:**

1. **Workflow State = Pending Approval**
   - **Why:** Waiting for manager decision
   - **Solution:** Wait for approval/rejection

2. **Workflow State = Approved**
   - **Why:** Manager already approved
   - **Solution:** Mark as Finished (you can't edit approved work)

3. **Workflow State = Finished**
   - **Why:** Repair is complete
   - **Solution:** Cannot edit finished repairs

**[SCREENSHOT 33: Read-only form in Pending Approval]**

---

### Problem: "Cannot Edit Manager Approval Fields"
**Cause:** You tried to edit Approval Notes or Approval Signature.

**Solution:**
- These fields are **manager-only**
- You cannot edit them in any state
- This is intentional for audit trail

---

### Problem: Notification Not Received
**Check:**
1. Click 🔔 bell icon (top right)
2. Check "All" tab in notifications
3. Check your email (if email notifications enabled)

**If still missing:**
1. Go to Asset Repair list
2. Filter: **Workflow State = Draft**
3. Check **Modified** date for new entries

**[SCREENSHOT 34: Notification settings and filters]**

---

### Problem: Can't Find Asset Repair
**Navigation Help:**
1. Click **Workspace** menu (top left)
2. Scroll to **Asset** section
3. Click **Asset Repair**

**Alternative:**
1. Use **Global Search** (press Ctrl+K or Cmd+K)
2. Type "Asset Repair"
3. Select from results

**[SCREENSHOT 35: Global search for Asset Repair]**

---

### Problem: Photos Won't Upload
**Solutions:**
1. **Check file size:** Max 10MB per photo
2. **Check file type:** JPG, PNG only
3. **Check connection:** Ensure stable internet
4. **Try smaller photos:** Compress before uploading

**[SCREENSHOT 36: File upload error messages]**

---

### Problem: Lost Work (Didn't Save)
**Prevention:**
- Click **Save** button frequently
- Don't rely on auto-save
- Don't close browser until saved

**Recovery:**
- Unfortunately, unsaved work cannot be recovered
- Always save after adding each section

---

## Best Practices

### Documentation Quality
**Good Documentation:**
```
ACTIONS PERFORMED:
1. Diagnosed hydraulic leak - found damaged seal on cylinder #3
2. Drained hydraulic fluid (2.5L recovered)
3. Removed cylinder #3 from mounting bracket
4. Replaced seal (Part #: HS-2245-A)
5. Reinstalled cylinder and reconnected hydraulic lines
6. Refilled hydraulic fluid (3L fresh Mobil DTE 25)
7. Pressure tested - no leaks at 2500 PSI
8. Cycled mechanism 10 times - operating smoothly

PARTS USED:
- 1x Hydraulic seal HS-2245-A
- 3L Hydraulic oil Mobil DTE 25

TEST RESULTS:
- Pressure: 2500 PSI (normal range 2400-2600)
- Temperature: 45°C under load (normal)
- No leaks after 30 minutes operation
```

**Bad Documentation:**
```
Fixed hydraulic leak
```

### Photo Quality
**Take photos that show:**
- ✅ Clear, well-lit images
- ✅ Close-up of repaired area
- ✅ New parts installed
- ✅ Measurement readings
- ✅ Before AND after

**Avoid:**
- ❌ Blurry photos
- ❌ Too dark to see details
- ❌ Photos of unrelated things
- ❌ Only "before" photos without "after"

**[SCREENSHOT 37: Example good repair photos]**

**[SCREENSHOT 38: Example bad repair photos]**

### Communication
**When to contact manager BEFORE submitting:**
- Major repairs requiring expensive parts
- Safety-critical repairs
- Repairs affecting production schedule
- Uncertain about correct fix

**When to add detailed notes:**
- Used non-standard parts (explain why)
- Found additional problems
- Temporary fix applied (permanent fix needed later)
- Special testing performed

---

## Quick Reference Card

### New Repair Workflow
```
1. Check notifications (🔔 bell icon)
2. Open repair document
3. Review issue photos and description
4. Add engineering plan to table
5. Perform repair work
6. Document in Actions Performed
7. Attach completion photos
8. Add engineer signature
9. Save document
10. Submit for Approval
11. Wait for manager decision
```

### Keyboard Shortcuts
| Shortcut | Action |
|---|---|
| Ctrl+S / Cmd+S | Save document |
| Ctrl+K / Cmd+K | Global search |
| Escape | Close dialog |

---

## Contact Support

### When to Contact IT
- Login problems
- Cannot access Asset Repair
- Permissions errors
- System errors/crashes

### When to Contact Your Manager
- Unclear repair requirements
- Need approval for expensive parts
- Safety concerns
- Workload issues

### How to Contact
- **IT Email:** it@tipubon.com
- **Manager:** [MANAGER EMAIL]
- **Urgent:** [PHONE NUMBER]

---

## Appendix: Screenshot Checklist

**For IT/Documentation Team:** Add screenshots at these locations:

| # | Screenshot Needed | Status |
|---|---|---|
| 1 | ERPNext login page | ⬜ Pending |
| 2 | ERPNext login form | ⬜ Pending |
| 3 | Workspace menu - Asset section | ⬜ Pending |
| 4 | Asset Repair list view | ⬜ Pending |
| 5 | Notification bell with badge | ⬜ Pending |
| 6 | Notification dropdown | ⬜ Pending |
| 7 | New repair notification detail | ⬜ Pending |
| 8 | Asset Repair list filtered | ⬜ Pending |
| 9 | Repair document header | ⬜ Pending |
| 10 | Attachments with issue photos | ⬜ Pending |
| 11 | Full-size photo viewer | ⬜ Pending |
| 12 | Asset status indicator | ⬜ Pending |
| 13 | Engineering Details - empty | ⬜ Pending |
| 14 | Engineering Details - filled | ⬜ Pending |
| 15 | Repair work example photo | ⬜ Pending |
| 16 | Actions Performed - good example | ⬜ Pending |
| 17 | Attach file dialog | ⬜ Pending |
| 18 | Engineer Signature field | ⬜ Pending |
| 19 | Save button location | ⬜ Pending |
| 20 | Workflow - Draft state | ⬜ Pending |
| 21 | Submit for Approval button | ⬜ Pending |
| 22 | Submission confirmation | ⬜ Pending |
| 23 | Pending Approval state | ⬜ Pending |
| 24 | Manager section locked | ⬜ Pending |
| 25 | Approval notification | ⬜ Pending |
| 26 | Mark as Finished button | ⬜ Pending |
| 27 | Finished state | ⬜ Pending |
| 28 | Rejection notification | ⬜ Pending |
| 29 | Rejected with manager notes | ⬜ Pending |
| 30 | Editing rejected repair | ⬜ Pending |
| 31 | Permission error - manager fields | ⬜ Pending |
| 32 | Signature required error | ⬜ Pending |
| 33 | Read-only pending approval | ⬜ Pending |
| 34 | Notification settings | ⬜ Pending |
| 35 | Global search | ⬜ Pending |
| 36 | File upload errors | ⬜ Pending |
| 37 | Good repair photos example | ⬜ Pending |
| 38 | Bad repair photos example | ⬜ Pending |

---

**Document Version:** 1.0
**Last Updated:** 2025-12-18
**Next Review:** 2026-01-18
