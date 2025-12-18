# 👔 Maintenance Manager User Manual
**Role:** Maintenance Manager / Quality Manager
**Platform:** ERPNext Desktop (Web Browser)
**Version:** v2.1.0

---

## Table of Contents
1. [Overview](#overview)
2. [Accessing the System](#accessing-the-system)
3. [Reviewing Repair Requests](#reviewing-repair-requests)
4. [Approving Repairs](#approving-repairs)
5. [Rejecting Repairs](#rejecting-repairs)
6. [Monitoring System](#monitoring-system)
7. [Reports and Analytics](#reports-and-analytics)
8. [Troubleshooting](#troubleshooting)

---

## Overview

### What You Do
As a **Maintenance Manager**, you are responsible for:
- ✅ Reviewing engineer-submitted repair work
- ✅ Approving quality repairs with proper documentation
- ✅ Rejecting incomplete or unsafe repairs
- ✅ Providing feedback to engineers
- ✅ Monitoring overall maintenance performance
- ✅ Ensuring audit trail compliance

### What You DON'T Do
- ❌ You do NOT perform the actual repairs (engineers do this)
- ❌ You do NOT verify completed repairs (inspectors do this)
- ❌ You do NOT override inspector reports

### Your Authority
You have **full access** to:
- View all repairs (Draft, Pending, Approved, Finished, Rejected)
- Approve or reject engineer work
- Edit approval notes and signatures
- View all system reports
- Lock/unlock protected fields

You **cannot edit** (for audit compliance):
- Inspector's original issue report
- Engineer's work documentation
- Failure date/time
- Reported by field

### Your Workflow
```
1. Receive notification → Engineer submitted for approval
2. Review documentation → Check photos, notes, parts used
3. Evaluate quality → Is work complete and safe?
4. Make decision:
   ├─ Approve → Add signature + notes → Engineer marks Finished
   └─ Reject → Add reason → Engineer reworks or abandons
5. Monitor verification → Inspector tests the repair
```

---

## Accessing the System

### Step 1: Open ERPNext
1. Open web browser (Chrome, Edge, Firefox)
2. Navigate to: `https://tub.x-desk.tech`
3. **Do NOT use** the mobile portal

**[SCREENSHOT 1: ERPNext login page]**

### Step 2: Log In
1. Enter your manager credentials
2. Click **Login**

**[SCREENSHOT 2: Manager login]**

### Step 3: Navigate to Asset Repair
**Method 1: Workspace**
1. Click **Workspace** menu
2. Select **Asset**
3. Click **Asset Repair**

**[SCREENSHOT 3: Workspace navigation]**

**Method 2: Notifications**
1. Click **🔔 Bell icon** (top right)
2. View pending approval notifications
3. Click to open repair directly

**[SCREENSHOT 4: Manager notifications with pending approvals]**

---

## Reviewing Repair Requests

### Step 1: Find Pending Repairs
1. Open **Asset Repair** list
2. Apply filter: **Workflow State = Pending Approval**
3. View all repairs awaiting your decision

**[SCREENSHOT 5: Asset Repair list filtered - Pending Approval]**

**Tip:** Set this as your default filter to see pending work first.

### Step 2: Understand Priority
Check **Issue Severity** column:
- 🔴 **Major - Asset Must Stop** → URGENT (asset out of order)
- 🟡 **Minor - Asset Operational** → Normal priority

**[SCREENSHOT 6: Repair list with severity indicators]**

### Step 3: Open Repair Document
Click on the repair name (e.g., "MAT-REP-2025-00123")

**[SCREENSHOT 7: Opening repair document]**

### Step 4: Review Header Information
Check these critical fields:

| Field | What to Check |
|---|---|
| **Asset** | Which equipment |
| **Failure Date** | When issue occurred (with exact time) |
| **Description** | Inspector's original problem report |
| **Issue Severity** | Minor or Major |
| **Reported By** | Inspector who found the issue |
| **Maintenance Task** | Which checklist item failed |
| **Workflow State** | Should be "Pending Approval" |

**[SCREENSHOT 8: Repair header section]**

### Step 5: Review Issue Photos (Original Report)
1. Scroll to **Attachments** section
2. Identify photos taken by inspector when reporting
3. Look for files named "Issue Photo 1", "Issue Photo 2", etc.
4. Click to view full size

**Questions to ask:**
- Is the reported problem visible in photos?
- Is it a real issue or false alarm?
- Does severity match the problem?

**[SCREENSHOT 9: Issue photos from inspector]**

### Step 6: Review Engineering Plan
1. Scroll to **Engineering Details** table
2. Check each row:

| Column | What to Verify |
|---|---|
| **Action** | Is the planned action appropriate? |
| **Parts Required** | Are parts correct and sufficient? |
| **Estimated Time** | Is time estimate reasonable? |

**Red flags:**
- ❌ Empty or vague actions ("Fix it")
- ❌ Missing parts list
- ❌ Unrealistic time estimates

**[SCREENSHOT 10: Engineering Details table - good example]**

**[SCREENSHOT 11: Engineering Details table - poor example]**

### Step 7: Review Actions Performed
1. Scroll to **Actions Performed** field
2. Read the engineer's work log

**Good documentation includes:**
- Step-by-step what was done
- Parts used with part numbers
- Measurements/readings taken
- Testing performed
- Results of testing

**Poor documentation:**
- Vague ("Fixed problem")
- Missing details
- No testing mentioned
- No measurements

**[SCREENSHOT 12: Actions Performed - good example]**

**[SCREENSHOT 13: Actions Performed - poor example]**

### Step 8: Review Completion Photos
1. Scroll to **Attachments** section
2. Look for photos added by engineer (not issue photos)
3. Verify photos show:
   - Completed repair
   - New parts installed
   - Asset in working condition
   - Measurement readings if applicable

**[SCREENSHOT 14: Completion photos from engineer]**

### Step 9: Verify Engineer Signature
1. Scroll to **Engineer Signature** field
2. Confirm engineer has signed
3. Check signature matches the engineer who did the work

**[SCREENSHOT 15: Engineer Signature field - signed]**

---

## Approving Repairs

### When to Approve
Approve when ALL criteria met:
- ✅ Documentation is complete and detailed
- ✅ Appropriate parts used
- ✅ Work was tested
- ✅ Photos show completed repair
- ✅ Engineer signature present
- ✅ No safety concerns
- ✅ Work matches the original issue

### Step 1: Scroll to Manager Approval Section
This section is **visible only to managers**.

**[SCREENSHOT 16: Manager Approval section location]**

### Step 2: Add Approval Notes
Click in **Approval Notes** field and write:
- What you verified
- Any observations
- Commendations (if exceptional work)

**Example:**
```
Repair approved. Engineer correctly diagnosed hydraulic
seal failure, replaced with appropriate part (HS-2245-A),
and performed pressure testing. Documentation is thorough.
Photos clearly show completed work. Good job.
```

**[SCREENSHOT 17: Approval Notes field - filled]**

### Step 3: Add Your Signature
1. Click in **Approval Signature** field
2. Type your full name or draw signature

**[SCREENSHOT 18: Approval Signature field]**

### Step 4: Save Document
Click **Save** button (top right)

**[SCREENSHOT 19: Save button]**

**Note:** Approval timestamp is auto-filled when you save.

### Step 5: Change Workflow to Approved
1. Locate **Workflow** section (top right)
2. Click **Approve** button
3. Confirm in dialog

**[SCREENSHOT 20: Workflow - Approve button]**

**[SCREENSHOT 21: Approval confirmation dialog]**

### Step 6: Verify Approval Success
After approval:
- Workflow State changes to **Approved**
- Engineer receives notification
- Engineer can now mark as Finished
- Most fields become read-only

**[SCREENSHOT 22: Repair in Approved state]**

### What Happens Next?
1. **Engineer is notified** automatically
2. **Engineer marks as Finished** when ready
3. **Inspector verifies** the repair quality
4. **Asset returns to service** (if verification passes)

---

## Rejecting Repairs

### When to Reject
Reject when:
- ❌ Documentation insufficient
- ❌ Photos missing or unclear
- ❌ Wrong parts used
- ❌ Work not tested
- ❌ Safety concerns
- ❌ Work doesn't match the issue
- ❌ False alarm (issue doesn't exist)

### Step 1: Add Rejection Notes
Click in **Approval Notes** field and write:
- **WHY** you're rejecting
- **WHAT** needs to be fixed
- **HOW** engineer should correct it

**Example for insufficient documentation:**
```
Rejected - Documentation insufficient.

ISSUES:
1. Actions Performed too vague - need step-by-step details
2. No completion photos showing installed part
3. No testing described - how do you know it's fixed?

REQUIRED FOR RESUBMISSION:
- Add detailed step-by-step work log
- Attach photos of new seal installed
- Describe pressure testing performed and results

Resubmit after addressing these items.
```

**[SCREENSHOT 23: Rejection Notes - detailed feedback]**

**Example for false alarm:**
```
Rejected - False alarm.

Inspected asset personally. The reported "hydraulic leak"
is normal condensation from temperature differential.
No actual leak present. Asset is fully operational.

No repair needed. Closing this request.
```

**[SCREENSHOT 24: Rejection Notes - false alarm]**

### Step 2: Add Your Signature
Sign in the **Approval Signature** field.

**Note:** Signature required for both approval AND rejection.

### Step 3: Save Document
Click **Save** button.

### Step 4: Change Workflow to Rejected
1. Click **Reject** button in workflow section
2. Confirm rejection

**[SCREENSHOT 25: Workflow - Reject button]**

**[SCREENSHOT 26: Rejection confirmation dialog]**

### Step 5: Verify Rejection Success
After rejection:
- Workflow State changes to **Rejected**
- Engineer receives notification with your notes
- Engineer can edit and resubmit
- Maintenance Log returns to "Completed" (issue closed)

**[SCREENSHOT 27: Repair in Rejected state]**

### What Happens Next?
**Option 1: Engineer Reworks**
- Engineer makes corrections
- Engineer resubmits for approval
- You review again

**Option 2: Engineer Abandons**
- Issue was false alarm or no longer relevant
- Repair stays in Rejected status
- No further action needed

---

## Monitoring System

### Dashboard Overview
**Method 1: Asset Repair List**
1. Go to Asset Repair list
2. Use these filter combinations:

**[SCREENSHOT 28: Asset Repair list with multiple filters]**

| View | Filter | Purpose |
|---|---|---|
| **Pending My Review** | Workflow State = Pending Approval | Your action needed |
| **Recently Approved** | Workflow State = Approved + Modified Last Week | Track recent approvals |
| **Rejected Items** | Workflow State = Rejected | Follow up on rework |
| **Completed This Month** | Workflow State = Finished + Modified This Month | Performance tracking |
| **Major Issues** | Issue Severity = Major | Critical repairs |

### Active Repairs Report
1. Click **Reports** menu
2. Select **Asset Repair Report** (if configured)
3. Filter by date range, workflow state, severity

**[SCREENSHOT 29: Asset Repair Report]**

### Engineer Performance
Track by:
1. Filter: **Engineer** field (if customized to show engineer name)
2. Count repairs per engineer
3. Check approval/rejection ratio
4. Review average time to completion

**[SCREENSHOT 30: Repairs filtered by engineer]**

### Asset Status Overview
1. Go to **Asset** list
2. Filter by Status:
   - Out of Order (needs attention)
   - In Maintenance (minor issues)
   - Submitted (operational)

**[SCREENSHOT 31: Asset list filtered by status]**

---

## Reports and Analytics

### Monthly Maintenance Summary
**Data to track:**
- Total repairs submitted
- Approvals vs Rejections
- Average time from report to finished
- Most common failure types
- Assets with repeat issues

**[SCREENSHOT 32: Monthly summary dashboard (if available)]**

### Asset Downtime Report
**Track:**
- How long assets stayed "Out of Order"
- Which assets have longest downtime
- Downtime cost impact

**[SCREENSHOT 33: Asset downtime tracking]**

### Inspector Performance
**Metrics:**
- Issues reported (true issues vs false alarms)
- Photo quality
- Description completeness
- Verification accuracy

**[SCREENSHOT 34: Inspector metrics]**

### Engineer Quality Metrics
**Track:**
- First-time approval rate
- Rejection reasons
- Rework frequency
- Documentation quality trends

**[SCREENSHOT 35: Engineer quality dashboard]**

---

## Advanced Functions

### Editing Repairs After Approval
**Scenario:** You approved but found error in your notes.

**Solution:**
1. Open the repair document
2. You CAN edit **Approval Notes** field (manager-only)
3. You CANNOT change workflow state back
4. Save changes
5. Notes are updated for record

**[SCREENSHOT 36: Editing approval notes after approval]**

### Handling Special Cases

#### Case 1: Engineer Forgot to Add Photo
**Option A: Reject**
- Standard approach
- Enforces documentation standards

**Option B: Request via Comment**
- Add comment asking for photo
- Engineer can attach without resubmitting (if you allow)
- Use for minor issues only

**[SCREENSHOT 37: Using comments for clarification]**

#### Case 2: Urgent Approval Needed
**Steps:**
1. Review quickly but thoroughly
2. Approve if minimally acceptable
3. Add note: "Approved for urgency. Follow up on [specific item] for future repairs."
4. Email engineer separately with detailed feedback

#### Case 3: Partial Approval
**Problem:** Repair is 80% good but has minor issue.

**Solution:**
- Approve with detailed notes on improvement needed
- OR Reject with clear guidance for quick fix
- Choose based on urgency and severity of documentation gap

**[SCREENSHOT 38: Conditional approval notes]**

---

## Field Reference

### Fields You Can Edit (Manager Only)
| Field | When | Purpose |
|---|---|---|
| Approval Notes | Always | Document your decision |
| Approval Signature | Always | Authenticate approval/rejection |
| Approval Timestamp | Auto-filled | Records when you signed |

### Fields You Can View (But Not Edit)
| Field | Owner | Locked Reason |
|---|---|---|
| Failure Date | System | Audit trail |
| Description | Inspector | Original report preservation |
| Reported By | Inspector | Audit trail |
| Maintenance Task | Inspector | Original context |
| Actions Performed | Engineer | Work documentation |
| Engineer Signature | Engineer | Work authentication |
| Engineering Details | Engineer | Work plan |

### Workflow States and Meanings
| State | Meaning | Who Acts Next |
|---|---|---|
| Draft | New issue, engineer hasn't started | Engineer |
| Pending Approval | Engineer submitted, awaiting review | **YOU** |
| Approved | You approved, awaiting finish | Engineer |
| Rejected | You rejected, needs rework | Engineer (optional) |
| Finished | Engineer marked done, awaiting verification | Inspector |
| Cancelled | Abandoned/invalid | None |

**[SCREENSHOT 39: Workflow state diagram]**

---

## Troubleshooting

### Problem: "Cannot Edit Approval Fields"
**Possible Causes:**

1. **Wrong Role**
   - Check: Settings → Users → Your Profile → Roles
   - Required: "Maintenance Manager" or "Quality Manager"

2. **Document in Draft State**
   - Approval section only appears in Pending Approval state
   - Wait for engineer to submit

**[SCREENSHOT 40: Role verification in user profile]**

---

### Problem: Notification Not Received
**Check:**
1. Bell icon (🔔) → Check all notifications
2. Notification settings → Email notifications enabled?
3. Go to Asset Repair list → Filter Pending Approval manually

**[SCREENSHOT 41: Notification settings]**

---

### Problem: Can't Change Workflow State
**Error:** "This document must be submitted"

**Solution:**
Document is still in Draft. Engineer needs to:
1. Add engineer signature
2. Click "Submit for Approval" button

**[SCREENSHOT 42: Document not submitted error]**

---

### Problem: Approval Timestamp Not Showing
**Cause:** You haven't saved after adding signature.

**Solution:**
1. Fill Approval Notes
2. Fill Approval Signature
3. Click **Save** (timestamp auto-fills)
4. Then change workflow state

---

### Problem: Want to "Un-Approve" a Repair
**Challenge:** ERPNext workflow doesn't allow state reversal.

**Options:**

**Option 1: Edit Approval Notes**
- Add correction to notes
- Notes are visible to engineer
- Workflow stays Approved

**Option 2: Ask Engineer Not to Mark Finished**
- Contact engineer directly
- Explain the issue
- Engineer can leave in Approved state

**Option 3: Cancel Document**
- Change workflow to Cancelled (if option available)
- Create new repair document

**[SCREENSHOT 43: Workflow state transitions]**

---

## Best Practices

### Quality Review Checklist
Before approving, verify:
- [ ] Issue description matches work performed
- [ ] Parts used are appropriate
- [ ] Work is clearly documented step-by-step
- [ ] Testing/verification performed
- [ ] Safety procedures followed
- [ ] Photos show completed work clearly
- [ ] Engineer signature present
- [ ] No shortcuts taken on critical repairs

### Documentation Standards
**Enforce these in your approval notes:**
- Engineers must describe testing performed
- Photos must show before AND after (when applicable)
- Part numbers must be included
- Measurements/readings must be documented
- Safety checks must be mentioned

### Feedback Quality
**Good feedback (approval):**
```
Approved. Excellent documentation. Clear photos showing
the broken belt and new belt installed. Good inclusion
of tension measurements before/after. Testing procedure
is appropriate. This is the standard we want to see.
```

**Good feedback (rejection):**
```
Rejected - Need more detail.

Your work may be fine, but documentation is insufficient:
1. "Replaced belt" - which belt? Part number?
2. No photo of new belt installed
3. No mention of tensioning or alignment check
4. No testing described

Please update Actions Performed with step-by-step details,
add completion photo, and describe testing. Resubmit.
```

**Poor feedback:**
```
Approved
```
or
```
Rejected - not good enough
```

### Time Management
**Prioritize reviews:**
1. 🔴 Major severity (assets down) - Review within 2 hours
2. 🟡 Minor severity - Review same day
3. 📊 Batch review end of day if many pending

**Set expectations:**
- Engineers should expect feedback within 4-24 hours
- Communicate if you'll be unavailable

---

## Security and Compliance

### Audit Trail Protection
**What's Protected:**
- You CANNOT edit inspector's original report
- You CANNOT edit engineer's work documentation
- You CANNOT edit failure date/time
- System logs all your approvals/rejections

**Why:** Ensures integrity for:
- Safety investigations
- Warranty claims
- Regulatory compliance
- Performance reviews

### Your Signature Authority
Your approval signature means:
- You verified work was completed
- You verified documentation is adequate
- You take responsibility for quality
- Work meets company standards

**Take it seriously.**

### Data Access
As manager, you can see:
- All repairs across all assets
- All inspector reports
- All engineer work
- All approvals/rejections

**Use responsibly:**
- Don't share sensitive info inappropriately
- Don't approve work you haven't reviewed
- Don't sign on behalf of others

---

## Quick Reference Card

### Approval Workflow
```
1. Open Pending Approval repair
2. Review issue photos (inspector)
3. Review engineering plan
4. Review actions performed
5. Review completion photos
6. Verify engineer signature
7. Decide: Approve or Reject
8. Add approval notes (detailed)
9. Add approval signature
10. Save document
11. Click Approve/Reject button
```

### Rejection Checklist
```
In Approval Notes, include:
- WHY rejecting
- WHAT is insufficient
- HOW to correct
- WHAT to include in resubmission
```

### Daily Manager Tasks
```
Morning:
- Check pending approvals
- Prioritize by severity
- Review urgent (Major) first

Throughout Day:
- Respond to pending reviews
- Provide feedback to engineers
- Monitor asset status

End of Day:
- Clear all pending approvals
- Check rejection follow-ups
- Review daily summary
```

---

## Contact Support

### When to Escalate
- Safety-critical repairs
- Repeat quality issues with engineer
- System access problems
- Compliance concerns

### Contacts
- **IT Support:** it@tipubon.com
- **Operations Manager:** [MANAGER EMAIL]
- **Safety Officer:** [SAFETY EMAIL]

---

## Appendix: Screenshot Checklist

**For IT/Documentation Team:** Add screenshots at these locations:

| # | Screenshot Needed | Status |
|---|---|---|
| 1 | ERPNext login page | ⬜ Pending |
| 2 | Manager login | ⬜ Pending |
| 3 | Workspace navigation | ⬜ Pending |
| 4 | Manager notifications | ⬜ Pending |
| 5 | List filtered Pending Approval | ⬜ Pending |
| 6 | Severity indicators | ⬜ Pending |
| 7 | Opening repair document | ⬜ Pending |
| 8 | Repair header section | ⬜ Pending |
| 9 | Issue photos from inspector | ⬜ Pending |
| 10 | Engineering Details - good | ⬜ Pending |
| 11 | Engineering Details - poor | ⬜ Pending |
| 12 | Actions Performed - good | ⬜ Pending |
| 13 | Actions Performed - poor | ⬜ Pending |
| 14 | Completion photos | ⬜ Pending |
| 15 | Engineer Signature signed | ⬜ Pending |
| 16 | Manager Approval section | ⬜ Pending |
| 17 | Approval Notes filled | ⬜ Pending |
| 18 | Approval Signature field | ⬜ Pending |
| 19 | Save button | ⬜ Pending |
| 20 | Approve button | ⬜ Pending |
| 21 | Approval confirmation | ⬜ Pending |
| 22 | Approved state | ⬜ Pending |
| 23 | Rejection Notes - detailed | ⬜ Pending |
| 24 | Rejection Notes - false alarm | ⬜ Pending |
| 25 | Reject button | ⬜ Pending |
| 26 | Rejection confirmation | ⬜ Pending |
| 27 | Rejected state | ⬜ Pending |
| 28 | List with multiple filters | ⬜ Pending |
| 29 | Asset Repair Report | ⬜ Pending |
| 30 | Repairs by engineer | ⬜ Pending |
| 31 | Asset list by status | ⬜ Pending |
| 32 | Monthly summary dashboard | ⬜ Pending |
| 33 | Asset downtime tracking | ⬜ Pending |
| 34 | Inspector metrics | ⬜ Pending |
| 35 | Engineer quality dashboard | ⬜ Pending |
| 36 | Edit notes after approval | ⬜ Pending |
| 37 | Using comments | ⬜ Pending |
| 38 | Conditional approval notes | ⬜ Pending |
| 39 | Workflow state diagram | ⬜ Pending |
| 40 | Role verification | ⬜ Pending |
| 41 | Notification settings | ⬜ Pending |
| 42 | Not submitted error | ⬜ Pending |
| 43 | Workflow transitions | ⬜ Pending |

---

**Document Version:** 1.0
**Last Updated:** 2025-12-18
**Next Review:** 2026-01-18
