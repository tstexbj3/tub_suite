# TUB Maintenance Portal - Engineering Team Manual

**Role:** Engineering Team
**Access:** ERPNext Desk + Mobile Portal (optional)
**Primary Duties:** Repair work, technical documentation, workflow management

---

## Table of Contents
1. [Getting Started](#getting-started)
2. [Receiving Repair Requests](#receiving-repair-requests)
3. [Working on Repairs](#working-on-repairs)
4. [Submitting for Approval](#submitting-for-approval)
5. [After Approval](#after-approval)
6. [Completing Repairs](#completing-repairs)
7. [Field Restrictions](#field-restrictions)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Accessing ERPNext Desk

1. Open browser (Chrome recommended)
2. Navigate to: `http://localhost:8000` (or your production URL)
3. Login with your credentials
   - Username: Your email address
   - Password: Your ERPNext password
4. You will see ERPNext desk interface

### Understanding Your Role

As **Engineering Team**, you have access to:
- ✅ Asset Repair documents (read/write)
- ✅ Repair workflow states
- ✅ Technical fields and engineering details
- ✅ ToDo notifications for new repairs
- ❌ Approval authority (Managers only)
- ❌ Editing after submission (locked fields)

**Key Principle:** You manage repairs from creation through completion, but Managers control approvals.

---

## Receiving Repair Requests

### How Repairs Are Created

Repair requests come from two sources:

1. **Mobile Portal Reports:**
   - Maintenance Users scan assets
   - Find issues during inspection
   - Submit with photos and description
   - Repair created automatically in "Draft" state

2. **Manual Creation:**
   - You can create repairs directly in desk
   - For urgent issues or manager requests
   - Start in "Draft" state

### Notification System

When new repair is created, you receive:

1. **ToDo Notification:**
   - Bell icon (🔔) in top right shows red badge
   - Click bell to see list
   - Shows: "New repair request for [Asset Name]"
   - Click to open repair document

2. **Email Notification (if enabled):**
   - Subject: "🔧 New Repair Request: [Asset Name]"
   - Contains:
     - Repair Request ID
     - Asset details
     - Problem description
     - Reporter name
     - Link to repair document

**Screenshot Location:** ToDo list with repair notification

### Viewing Repair Requests

**Method 1: From ToDo**
1. Click bell icon (🔔) top right
2. Find repair notification
3. Click "View" or repair name
4. Opens Asset Repair document

**Method 2: From DocType List**
1. Click search bar (⌘K or Ctrl+K)
2. Type "Asset Repair"
3. Press Enter
4. See list of all repairs
5. Filter by workflow state if needed

**Method 3: From Asset**
1. Open Asset document
2. Scroll to bottom
3. See "Asset Repair" section
4. Click repair to open

---

## Working on Repairs

### Draft State - Your Editing Phase

When repair is in **Draft** state, you have full editing access to fill in technical details.

### Required Fields

Before submission, you MUST fill:

| Field | Required | Description |
|-------|----------|-------------|
| **Asset** | ✅ REQUIRED | Asset being repaired (auto-filled from portal) |
| **Failure Date** | ✅ REQUIRED | Date problem occurred (auto-filled) |
| **Description** | ✅ REQUIRED | Problem description (from reporter) |
| **Issue Severity** | ✅ REQUIRED | Major or Minor (see below) |
| **Repair Type** | ✅ REQUIRED | Type of work (Repair/Maintenance/Breakdown/etc) |
| **Estimated Cost** | Recommended | Approximate repair cost |
| **Engineer Signature** | ✅ REQUIRED | Your digital signature before submission |

**Screenshot Location:** Asset Repair form in Draft state

### Issue Severity - CRITICAL Field

**This field controls asset status:**

**Major - Asset Must Stop:**
- Equipment is unsafe or unusable
- Must be taken out of service immediately
- Examples:
  - ⚠️ Complete failure (won't turn on)
  - ⚠️ Safety hazard (sparks, smoke, leaking)
  - ⚠️ Critical component broken
  - ⚠️ Cannot perform primary function
- **Effect:** When manager approves, asset status → "Out of Order"

**Minor - Asset Operational:**
- Equipment still works with limitations
- Can remain in service during repair
- Examples:
  - ✓ Cosmetic damage
  - ✓ Minor noise or vibration
  - ✓ Non-critical component worn
  - ✓ Reduced efficiency but still functional
- **Effect:** Asset remains operational during repair

**How to Choose:**
```
Ask yourself: "Can this asset safely continue operating?"

YES → Minor - Asset Operational
NO  → Major - Asset Must Stop
```

**Screenshot Location:** Issue Severity dropdown with options

### Engineering Details Section

Fill in technical information:

**Repair Type** (Select one):
- Repair - Fixing broken component
- Preventive Maintenance - Scheduled service
- Breakdown - Emergency failure
- Inspection - Diagnostic work
- Replacement - Component swap

**Root Cause** (Optional but recommended):
- What caused the failure?
- Examples:
  - "Worn bearing due to lack of lubrication"
  - "Filter clogged from extended use"
  - "Wiring damaged by vibration"

**Actions Performed** (Fill after repair):
- What you did to fix it
- Examples:
  - "Replaced compressor motor"
  - "Cleaned and lubricated moving parts"
  - "Rewired control panel"

**Stock Consumption** (If parts used):
- Click "Add Row"
- Select Item Code
- Enter Quantity
- System tracks inventory

**Repair Cost** (If applicable):
- Labor hours
- Parts cost
- External service fees

### Adding Engineer Signature

**MANDATORY before submission:**

1. Scroll to "Engineer Signature" field
2. Click in signature pad
3. Draw your signature with mouse/touch
4. Click "Clear" if need to redo
5. Signature must be present to submit

**Why Required:**
- Confirms you reviewed the repair
- Holds you accountable for assessment
- Required for workflow to proceed

**Screenshot Location:** Engineer signature field with drawn signature

### Saving Your Work

- Click blue "Save" button regularly
- Draft can be saved and returned to later
- All fields remain editable in Draft
- No notifications sent while in Draft

---

## Submitting for Approval

### When You're Ready

After filling all required fields and adding signature:

1. **Review Your Work:**
   - Double-check Issue Severity (Major vs Minor)
   - Verify all required fields complete
   - Check signature is present
   - Review problem description matches issue

2. **Click "Submit" Button:**
   - Located top-right of document
   - Blue button next to Save
   - Confirms "Submit this document?"
   - Click "Yes"

3. **Workflow Transition:**
   - Document status: Submitted (docstatus = 1)
   - Workflow state: "Draft" → "Pending Approval"
   - Document is now LOCKED for engineers
   - Manager receives notification

**Screenshot Location:** Submit button and confirmation dialog

### What Gets Locked

After submission, you **CANNOT** edit:
- ❌ Asset
- ❌ Failure Date
- ❌ Description
- ❌ Issue Severity
- ❌ Repair Type
- ❌ Engineering details
- ❌ Any technical fields

**Why Locked:**
- Prevents changes after manager reviewed
- Maintains audit trail
- Ensures approved work matches actual work

**If You Need Changes:**
- Contact Maintenance Manager
- Manager can reject (returns to Draft)
- You can then edit and resubmit
- Or manager approves as-is if minor mistake

---

## After Approval

### Manager Review Process

Manager sees your submitted repair and decides:

**Option 1: Approve**
- Workflow state: "Pending Approval" → "Approved"
- You receive notification to proceed
- For Major severity: Asset status → "Out of Order"
- For Minor severity: Asset stays operational

**Option 2: Reject**
- Workflow state: "Pending Approval" → "Rejected"
- Document returns to Draft
- You can edit all fields again
- Manager adds notes explaining why
- Resubmit after corrections

**Option 3: Request Changes**
- Manager contacts you directly
- May reject for edits
- Or approve with understanding you'll adjust

### When Approved - Your Next Steps

1. **Check Notification:**
   - ToDo: "Repair [ID] has been approved"
   - Email with approval details

2. **Review Manager Notes:**
   - Open repair document
   - Check "Approval Notes" field
   - Manager may add instructions
   - Follow any special requests

3. **Check Issue Severity Effect:**
   - If **Major**: Asset is now Out of Order
     - Users cannot inspect it
     - Asset tagged in system
     - Urgent priority
   - If **Minor**: Asset still operational
     - Can take time as needed
     - Schedule appropriately

4. **Perform Physical Repair:**
   - Go to asset location
   - Do actual repair work
   - Take photos (recommended)
   - Test thoroughly

**Screenshot Location:** Approved repair with manager notes

---

## Completing Repairs

### Marking Job as Finished

After physical repair is complete:

1. **Open Repair Document**
2. **Fill "Actions Performed":**
   - Describe what you did
   - Be specific for future reference
   - Example: "Replaced air filter, cleaned evaporator coils, tested cooling cycle - now operating at 18°C"

3. **Add Completion Date (Optional):**
   - System auto-fills when you click "Job Finished"
   - Shows date/time repair completed
   - If you manually set it, that's fine too

4. **Change Workflow State:**
   - Top ribbon shows current state
   - Click "Job Finished" button
   - Workflow: "Approved" → "Finished"
   - Completion date auto-filled
   - Reporter receives verification notification

**Screenshot Location:** Job Finished button in workflow ribbon

### What Happens Next

**Automatic Actions:**
1. **Completion Date Set:**
   - Auto-fills with current date/time
   - Marks when repair was completed
   - Used for tracking metrics

2. **Reporter Notified:**
   - Original reporter gets notification
   - Asked to verify repair
   - Must physically check equipment
   - Takes photos and confirms

3. **Asset Status:**
   - Still "Out of Order" if Major
   - Waits for reporter verification
   - Only restored after verification passed

### Verification by Reporter

**You DO NOT verify your own repairs.**

The original reporter must:
1. Go to asset location
2. Test equipment
3. Take verification photos
4. Confirm repair is satisfactory
5. System marks "Verified - Passed"
6. Asset status restored to "Submitted"

**If Reporter Finds Problem:**
- They will contact you
- May create new repair request
- Original repair stays "Finished" but unverified
- Your manager will discuss

**7-Day Rule:**
- Reporter is responsible for 7 days after verification
- If same problem returns within 7 days:
  - Reporter must report again
  - May indicate incomplete repair
  - Manager will investigate
  - Your work will be reviewed

---

## Field Restrictions

### What You Can Edit (By Workflow State)

**Draft State:**
- ✅ All fields editable
- ✅ Can save and return later
- ✅ Can add/remove items
- ✅ Can change everything

**Pending Approval State:**
- ❌ ALL fields locked
- ❌ Cannot edit anything
- ❌ Must wait for manager
- ✅ Can view only

**Approved State:**
- ❌ All locked EXCEPT:
- ✅ "Actions Performed" (describe your work)
- ✅ "Completion Date" (if needed)
- ✅ Workflow state ("Job Finished" button)
- ❌ Cannot change issue severity, description, etc.

**Finished State:**
- ❌ Completely locked
- ❌ Cannot edit anything
- ✅ Can view only
- Waiting for reporter verification

**Rejected State:**
- ✅ Returns to Draft
- ✅ All fields editable again
- ✅ Fix issues manager noted
- ✅ Resubmit when ready

### Why These Restrictions

**Audit Trail:**
- Maintains record of what was approved
- Prevents changing scope after approval
- Shows exactly what manager authorized

**Accountability:**
- Your submission represents your assessment
- Manager approves based on your information
- Changes after approval would invalidate approval

**Process Integrity:**
- Ensures everyone follows same workflow
- No shortcuts or bypasses
- Managers maintain control

---

## Troubleshooting

### Problem: Cannot submit - "Engineer Signature required"

**Solution:**
1. Scroll to Engineer Signature field
2. Draw signature in pad
3. Must be visible signature (not empty)
4. Save document
5. Try submit again

### Problem: "Cannot edit fields" error

**Cause:** Document is submitted (not in Draft)

**Solutions:**
1. Check workflow state (top of document)
2. If "Pending Approval": Wait for manager
3. If "Approved": You can only edit Actions Performed
4. If "Finished": Cannot edit (verification pending)
5. Contact manager to reject if need changes

### Problem: "Workflow action not found"

**Cause:** Missing workflow configuration

**Solution:**
1. Contact system administrator
2. Workflow "Repair Approval WorkFlow" may not be assigned
3. Admin needs to assign workflow to Asset Repair
4. Or check ERPNext system settings

### Problem: Asset not showing "Out of Order" after approval

**Cause:** May be Minor severity or workflow issue

**Check:**
1. Open repair document
2. Check "Issue Severity" field
3. If "Minor - Asset Operational" → Asset SHOULD NOT be Out of Order (correct behavior)
4. If "Major - Asset Must Stop" → Asset SHOULD be Out of Order
5. If Major but still operational → Bug, contact administrator

**Emergency Fix:**
1. Open Asset document directly
2. Check current status
3. Manually change to "Out of Order" if needed
4. Add comment explaining manual change

### Problem: Reporter not verifying repair

**Cause:** Reporter may not have received notification or cannot access portal

**Solutions:**
1. Check reporter email in repair document
2. Contact reporter directly by phone/email
3. Ask them to check mobile portal
4. Verify they can login and see verification alert
5. Manager can check if verification request was sent

### Problem: Cannot find my repairs in list

**Solution:**
1. Open Asset Repair list
2. Click "Filter" (funnel icon)
3. Add filter: "Workflow State" = "Approved"
4. Or: "Workflow State" = "Pending Approval"
5. Save filter as "My Repairs in Progress"
6. Use search by repair ID if known

### Problem: Stock items not deducting from inventory

**Cause:** Stock consumption table not properly filled

**Solution:**
1. Open repair document (must be Draft or Approved)
2. Scroll to "Stock Consumption" section
3. Click "Add Row"
4. Select correct Item Code from dropdown
5. Enter Quantity consumed
6. Save document
7. Stock will deduct when repair finalized

---

## Best Practices

### For Efficient Workflow

**✅ DO:**
- Review reporter's description and photos before starting
- Fill engineering details while working (not after)
- Take photos during repair for your records
- Test equipment thoroughly before marking finished
- Add detailed "Actions Performed" for future reference
- Respond to approvals within same day
- Contact manager if issue severity unclear

**❌ DON'T:**
- Submit repairs without signature
- Choose wrong issue severity (Major vs Minor is critical)
- Leave "Actions Performed" blank or vague
- Mark as finished without testing equipment
- Ignore manager rejection notes
- Try to edit submitted repairs (ask manager to reject)
- Verify your own repairs (reporter must verify)

### Documentation Tips

**Good "Actions Performed" Examples:**
- ✅ "Replaced faulty capacitor (100μF), tested motor rotation, verified cooling cycle operates at 20°C"
- ✅ "Disassembled pump, replaced worn seal and bearing, reassembled with new lubricant, tested 30 min - no leaks"
- ✅ "Rewired control panel according to schematic A-123, replaced damaged relay R5, tested all safety interlocks"

**Bad Examples:**
- ❌ "Fixed it"
- ❌ "Replaced part"
- ❌ "Done"

**Why Detailed Matters:**
- Future engineers reference your notes
- Manager understands what was done
- Helps diagnose recurring problems
- Creates valuable maintenance history

---

## Quick Reference

### Workflow States Summary

| State | Your Role | Can Edit? | Next Action |
|-------|-----------|-----------|-------------|
| **Draft** | Fill all details + sign | ✅ Everything | Submit |
| **Pending Approval** | Wait | ❌ Nothing | Manager decides |
| **Approved** | Do repair work | ✅ Actions only | Job Finished |
| **Finished** | Done | ❌ Nothing | Reporter verifies |
| **Rejected** | Fix issues | ✅ Everything | Resubmit |

### Critical Fields Checklist

Before submitting, verify:
- [  ] Asset selected
- [  ] Failure date set
- [  ] Description clear and detailed
- [  ] **Issue Severity chosen** (Major vs Minor)
- [  ] Repair Type selected
- [  ] **Engineer Signature drawn**
- [  ] All required fields have values
- [  ] Reviewed for accuracy

### Contact Information

- Maintenance Manager: [Add phone/email]
- System Administrator: [Add phone/email]
- Emergency Hotline: [Add number]

---

## Appendix: Screenshot Placeholders

The following screenshots should be taken and added to this manual:

1. **ToDo Notification** - Bell icon with red badge, list of repair notifications
2. **Asset Repair List** - List view with filters
3. **Draft Repair Form** - Full form with all editable fields
4. **Issue Severity Dropdown** - Major vs Minor options
5. **Engineer Signature** - Signature pad with drawn signature
6. **Submit Button** - Location and confirmation dialog
7. **Workflow Ribbon** - Showing current state and available actions
8. **Approved State** - Limited editable fields
9. **Actions Performed Field** - Filled with detailed notes
10. **Job Finished Button** - Workflow transition button
11. **Locked Fields** - Fields showing as read-only
12. **Manager Notes** - Approval notes section

---

**Document Version:** 1.0
**Last Updated:** December 16, 2024
**Prepared By:** TUB Suite Development Team
