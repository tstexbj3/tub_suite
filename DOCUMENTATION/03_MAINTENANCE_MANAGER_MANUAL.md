# TUB Maintenance Portal - Maintenance Manager Manual

**Role:** Maintenance Manager
**Access:** Full System Access (ERPNext Desk + Mobile Portal)
**Primary Duties:** Workflow approval, team oversight, system configuration, reporting

---

## Table of Contents
1. [Getting Started](#getting-started)
2. [Approval Workflow](#approval-workflow)
3. [Portal Settings Management](#portal-settings-management)
4. [Search Function](#search-function)
5. [Team Oversight](#team-oversight)
6. [Reports and Analytics](#reports-and-analytics)
7. [System Administration](#system-administration)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Understanding Your Authority

As **Maintenance Manager**, you are the central authority for:

**Approval Powers:**
- ✅ Approve or Reject repair requests
- ✅ Determine repair priority and scheduling
- ✅ Override engineering assessments
- ✅ Add approval notes and signatures

**System Configuration:**
- ✅ Manage Portal Settings
- ✅ Control search function visibility
- ✅ Configure user roles and permissions
- ✅ Manage workflows

**Oversight:**
- ✅ Monitor all maintenance activities
- ✅ Track team performance
- ✅ Review asset status
- ✅ Generate reports

**Access:**
- ✅ Full ERPNext Desk access
- ✅ Mobile Portal access
- ✅ All DocTypes (Assets, Repairs, Maintenance, etc.)
- ✅ System Settings

### Your Daily Responsibilities

**Morning:**
1. Check pending approval queue
2. Review overnight emergency repairs
3. Check asset status dashboard
4. Review team workload

**Throughout Day:**
5. Approve/reject repair requests as they arrive
6. Monitor high-priority issues
7. Respond to escalations
8. Coordinate with engineers and users

**End of Day:**
9. Review completion statistics
10. Plan next day priorities
11. Update management reports

---

## Approval Workflow

### Understanding the Repair Workflow

```
[Reporter] → [Engineer] → [YOU] → [Engineer] → [Reporter]
   Creates      Fills       Approves   Performs    Verifies
   Issue       Details       /Rejects    Repair      Result
```

**Your Role:** Gate keeper between assessment and action

### Receiving Approval Requests

**Notification Methods:**

1. **ToDo List:**
   - Bell icon (🔔) in top right
   - Shows: "Repair [ID] requires approval"
   - Click to open document

2. **Email Notification:**
   - Subject: "Repair Request Requires Approval: [Asset]"
   - Contains full repair details
   - Link to document

3. **Dashboard Widget:**
   - "Pending Approvals" count
   - Click to see list
   - Filter by priority/severity

**Screenshot Location:** Approval queue and notifications

### Reviewing Repair Requests

When opening repair for review, check:

1. **Reporter Information:**
   - Who reported the issue?
   - Are they the regular inspector for this asset?
   - Have they reported similar issues before?

2. **Problem Description:**
   - Is description clear and specific?
   - Review photos from reporter
   - Does severity match description?

3. **Engineer Assessment:**
   - Issue Severity: Major vs Minor
   - Estimated cost
   - Proposed actions
   - Root cause analysis

4. **Asset History:**
   - Click "Asset" link to view asset document
   - Check repair history
   - Look for patterns (recurring issues)
   - Review last maintenance date

5. **Business Impact:**
   - Is asset critical to operations?
   - Can we afford downtime?
   - Budget implications?

**Screenshot Location:** Repair document with all review sections highlighted

### Issue Severity - YOUR DECISION

**Engineer recommends, but YOU decide:**

**Major - Asset Must Stop:**
- ⚠️ Use when asset MUST be taken offline
- Asset status → "Out of Order" immediately
- Users cannot inspect it
- Urgent priority
- Examples:
  - Safety hazard
  - Complete failure
  - Blocking critical operations
  - Risk of further damage if used

**Minor - Asset Operational:**
- ✓ Asset continues operating during repair
- Can schedule at convenience
- Lower priority
- Examples:
  - Cosmetic issues
  - Reduced efficiency
  - Warning signs but still functional
  - Preventive maintenance

**How to Override:**
1. If you disagree with engineer's severity assessment
2. Edit "Issue Severity" dropdown
3. Select correct severity
4. Add note explaining your decision
5. Engineer's original assessment is NOT locked

### Making Approval Decision

**Option 1: APPROVE**

1. Review all information (checklist above)
2. Scroll to "Approval Details" section
3. Add "Approval Notes" (optional but recommended)
   - Why approved
   - Any special instructions
   - Priority level
   - Example: "Approved - High priority. Complete by end of week. Notify me when finished."

4. Add "Manager Signature" (optional)
   - Click in signature pad
   - Draw signature
   - Professional confirmation

5. Click workflow button: **"Approve"**
   - Workflow: "Pending Approval" → "Approved"
   - Engineer receives notification
   - For Major: Asset status → "Out of Order" automatically
   - For Minor: Asset remains operational

**Screenshot Location:** Approval section with notes and signature

**Option 2: REJECT**

**When to Reject:**
- Incomplete information
- Wrong issue severity
- Needs more investigation
- Cost too high without justification
- Safety concerns not addressed
- Missing required fields

**How to Reject:**
1. Scroll to "Approval Notes"
2. **MUST explain why rejected**
   - Be specific
   - Tell engineer what to fix
   - Example: "Rejected - Need detailed cost breakdown for parts. Also investigate if this is covered under warranty. Resubmit with documentation."

3. Click workflow button: **"Reject"**
   - Workflow: "Pending Approval" → "Rejected"
   - Document returns to Draft
   - Engineer can edit all fields
   - Engineer must resubmit after fixes

4. Optional: Contact engineer directly
   - Explain verbally if complex
   - Provide guidance
   - Set expectations

**Screenshot Location:** Rejection with detailed notes

**Option 3: REQUEST MORE INFORMATION**

**Process:**
1. Add note: "Need more information before approval"
2. Contact engineer by phone/email/chat
3. DO NOT approve or reject yet
4. Wait for response
5. Then make decision

### After Approval - Monitoring Progress

**Track Repair Status:**
1. Repair moves to "Approved" state
2. Engineer performs work
3. Engineer clicks "Job Finished"
4. Reporter must verify
5. After verification: Complete

**Your Checkpoints:**
- Check "Completion Date" filled
- Verify "Actions Performed" is detailed
- Monitor reporter verification
- If verification delayed → contact reporter
- Review final outcome

**Asset Status Changes:**
- **Major Approved** → Asset = "Out of Order"
- **Job Finished** → Still "Out of Order" (waiting verification)
- **Verified** → Asset = "Submitted" (back in service)

**If Asset Not Restored:**
- Check for other open Major repairs
- System only restores when ALL major repairs verified
- Intentional safety feature

---

## Portal Settings Management

### Accessing Portal Settings

1. Press `⌘K` or `Ctrl+K` (quick search)
2. Type: "Maintenance Portal Settings"
3. Press Enter
4. Settings document opens

**OR:**

1. Click search bar
2. Type "Maintenance Portal Settings"
3. Select from dropdown

**Screenshot Location:** Portal Settings document

### Understanding Settings

**Current Setting:**

```
┌───────────────────────────────────────┐
│ Portal Settings                       │
│                                       │
│ ☐ Enable Search for All Users        │
│                                       │
│ When enabled, all users can access   │
│ the search function. When disabled,   │
│ only users with Maintenance Manager   │
│ role can search.                      │
└───────────────────────────────────────┘
```

**Checkbox States:**

**☐ UNCHECKED** (Recommended for Production)
- Only Maintenance Managers see search function
- Maintenance Users: QR Scanner only
- Engineering Team: QR Scanner only
- Tighter access control
- Encourages proper QR code usage

**☑ CHECKED** (Testing/Training Mode)
- ALL users see search function
- Good for testing
- Good for training
- Easier access during setup
- Set to unchecked for production

### Changing Settings

**To Enable Search for All Users:**
1. Check the box: ☑ "Enable Search for All Users"
2. Click "Save" button
3. Settings take effect immediately (within 1 minute cache)
4. All users can now see search card on home page

**To Restrict Search to Managers Only:**
1. Uncheck the box: ☐ "Enable Search for All Users"
2. Click "Save" button
3. Non-managers lose search access immediately
4. Search card disappears from their home page
5. Direct URL access also blocked

**Testing the Change:**
1. Save setting
2. Open mobile portal in incognito/private window
3. Login as Maintenance User (non-manager)
4. Check if search card appears/disappears
5. Try accessing /maintenance/search directly
6. Should see "Access Denied" if restricted

**Screenshot Location:** Settings with checkbox in both states

### When to Use Each Setting

**Unchecked (Restricted) - Use When:**
- ✅ System in production
- ✅ Users trained on QR codes
- ✅ QR labels printed and installed
- ✅ Want to enforce process
- ✅ Security requirements

**Checked (Open) - Use When:**
- ✅ Testing new features
- ✅ Training new users
- ✅ QR labels not yet installed
- ✅ Need flexibility
- ✅ Development environment

---

## Search Function

### Your Exclusive Access

As manager, you ALWAYS have search access regardless of settings.

### Using Search Function

**From Mobile Portal:**
1. Open mobile portal home page
2. See two cards:
   - 📷 Scan QR Code
   - 🔍 Search Asset
3. Click "Search Asset" card

**OR from Search Page:**
- Direct URL: `http://localhost:8000/maintenance/search`

**Screenshot Location:** Home page with both cards visible

### Performing Searches

**Search Interface:**
```
┌───────────────────────────────────────┐
│ Search Asset                          │
│                                       │
│ ┌─────────────────────┐  [Search]    │
│ │ u-ac                │              │
│ └─────────────────────┘              │
└───────────────────────────────────────┘
```

**How to Search:**
1. Type search term in box
2. Can search by:
   - Asset name (e.g., "Air Conditioner")
   - Asset code (e.g., "U-AC-01")
   - Item code (e.g., "AC-SPLIT-01")
   - Location (e.g., "Meeting Room")
3. Press Enter or click "Search" button
4. Results appear as cards below

**Search Results:**

Each card shows:
- Asset name (large text)
- Status badge (colored)
- Item code
- Location (with 📍 icon)

**Status Badges:**
- 🟢 **Submitted** - Normal, operational
- 🔴 **Out of Order** - Under repair
- 🟡 **Draft** - Not yet active
- ⚫ **Cancelled** - Decommissioned

**Clicking Results:**
- Click any card
- Opens checklist for that asset
- Same as scanning QR code
- Can inspect or report issue

**Screenshot Location:** Search results with multiple assets

### Search Use Cases

**When You Should Use Search:**
1. **Finding Specific Asset:**
   - Know asset code, want quick access
   - Faster than scanning QR

2. **Mobile QR Inspection:**
   - QR code damaged or missing
   - Can search and inspect anyway

3. **Checking Asset Status:**
   - Want to see current status
   - Check if out of order
   - Review location

4. **Historical Review:**
   - Looking for assets by name
   - Comparing similar equipment
   - Inventory checks

**When to Use QR Instead:**
- Regular daily inspections
- Physical asset verification needed
- Training users on process
- Ensuring correct asset identified

---

## Team Oversight

### Monitoring Maintenance Users

**View All Inspections:**
1. Open "Asset Maintenance Log" list
2. Filter by date range
3. Filter by user (owner field)
4. See completion statistics

**Check for Issues:**
- Missing inspections (overdue tasks)
- Low completion rates
- Quality of documentation
- Photo compliance

**Performance Metrics:**
1. Open "Asset Maintenance" list
2. Use built-in reports
3. Check completion percentages
4. Identify training needs

**Screenshot Location:** Maintenance Log list with filters

### Monitoring Engineers

**Repair Queue Status:**
1. Open "Asset Repair" list
2. Filter by workflow state:
   - "Draft" - Engineer working
   - "Pending Approval" - Waiting for you
   - "Approved" - Engineer should be working
   - "Finished" - Waiting verification

**Red Flags:**
- Repairs stuck in Draft too long
- Approved repairs not finished
- Incomplete documentation
- Frequent rejections

**Engineer Performance:**
- Average time from approval to completion
- Quality of "Actions Performed" notes
- Recurring issues on same assets
- Stock consumption accuracy

**Response Times:**
1. Check "Notification Log"
2. See when engineers were notified
3. Compare to when they opened document
4. Track responsiveness

### Verification Compliance

**Checking Reporter Verification:**
1. Open "Asset Repair" list
2. Filter: Workflow State = "Finished"
3. Check "Verification Status" column
4. Look for:
   - "Verified - Passed" - Good
   - Empty/Null - Need to follow up

**If Verification Delayed:**
1. Check who is reporter (Reported By field)
2. Contact them directly
3. Remind of 7-day responsibility
4. Escalate if no response

**Verification Photos:**
1. Open repair document
2. Scroll to attachments section
3. Check for verification photos
4. Should have minimum 2 photos
5. Review quality and relevance

---

## Reports and Analytics

### Built-in Reports

**Asset Maintenance Report:**
1. Go to: Reports → Asset Maintenance
2. Shows all active maintenance schedules
3. Filter by asset, date, status
4. Export to Excel if needed

**Asset Repair Analysis:**
1. Go to: Reports → Asset Repair Analysis
2. Group by:
   - Issue Severity
   - Repair Type
   - Asset
   - Time period
3. Identify trends

**Custom Reports:**
1. Click "Create New Report"
2. Select "Asset Repair"
3. Choose fields to display
4. Add filters
5. Save as custom report
6. Share with management

**Screenshot Location:** Report builder interface

### Key Metrics to Track

**Daily:**
- Pending approvals count
- Assets out of order
- Overdue inspections
- Emergency repairs

**Weekly:**
- Repairs completed
- Average completion time
- Verification compliance rate
- Major vs Minor ratio

**Monthly:**
- Total maintenance activities
- Cost per asset
- Recurring issues
- Asset reliability trends

### Exporting Data

**For Management Reports:**
1. Open any list view
2. Select desired filters
3. Click "Export" button (top right)
4. Choose format:
   - Excel (.xlsx)
   - CSV
   - PDF
5. Download and share

**Dashboard Creation:**
1. Go to: Dashboard → New Dashboard
2. Add widgets:
   - Number cards (KPIs)
   - Charts (trends)
   - Lists (quick views)
3. Save dashboard
4. Share with executives

---

## System Administration

### User Management

**Adding New Users:**
1. Go to: User → New User
2. Fill email, name
3. Set role:
   - Maintenance User
   - Engineering Team
   - Maintenance Manager
4. Save and send invitation

**Assigning Roles:**
1. Open existing user
2. Scroll to "Roles" section
3. Check appropriate roles
4. Remember:
   - Maintenance User = Mobile portal only
   - Engineering Team = Desk access
   - Maintenance Manager = Full access

**Role Permissions:**
- Roles control what users can see/do
- Pre-configured in system
- Do not modify without admin knowledge

### Workflow Management

**Viewing Workflow:**
1. Search: "Repair Approval WorkFlow"
2. See states:
   - Draft
   - Pending Approval
   - Approved
   - Finished
   - Rejected
   - Cancelled

**Workflow States:**
- Each state has specific permissions
- Controls what users can edit
- DO NOT modify unless trained

**If Workflow Broken:**
- Contact system administrator
- Do not attempt to fix yourself
- Can cause data integrity issues

### Asset Management

**Creating New Assets:**
1. Go to: Asset → New Asset
2. Fill required fields
3. Set initial status (usually "Draft")
4. Submit when ready
5. Generate QR code (see next section)

**Printing QR Codes:**
1. Open asset document
2. Use QR code button/menu option
3. Print label
4. Affix to physical asset
5. Test scan with mobile portal

**Asset Categories:**
- Group assets by type
- Inherit maintenance schedules
- Standard templates
- Manage in: Asset Category list

### Backup and Maintenance

**Regular Backups:**
- System administrator handles
- Ensure daily backups configured
- Test restore procedures
- Keep offsite copies

**System Updates:**
- Coordinate with IT
- Test in development first
- Plan downtime
- Notify users in advance

---

## Troubleshooting

### Problem: Cannot approve repairs

**Symptoms:** No "Approve" button visible

**Solutions:**
1. Check workflow state - must be "Pending Approval"
2. Verify you have Maintenance Manager role
3. Check if workflow assigned to Asset Repair
4. Contact system administrator

### Problem: Asset not changing to Out of Order

**Symptoms:** Approved Major repair but asset still "Submitted"

**Investigation:**
1. Open repair document
2. Verify Issue Severity = "Major - Asset Must Stop"
3. Check workflow state = "Approved"
4. Open Asset document
5. Check status field

**Manual Override:**
1. Open Asset document
2. Click Edit (if not submitted, submit first)
3. Click workflow action if available
4. Or manually set status to "Out of Order"
5. Add comment explaining manual change
6. Save
7. Report bug to administrator

### Problem: Search not working for managers

**Symptoms:** Search card not appearing even for manager

**Solutions:**
1. Check Portal Settings
2. Verify setting saved correctly
3. Clear browser cache (Ctrl+Shift+R)
4. Try incognito/private window
5. Check user has Maintenance Manager role
6. Verify /api/method/tub_suite.api.maintenance.get_portal_settings returns correct data

### Problem: Users not receiving notifications

**Symptoms:** ToDo not appearing, no emails

**Check:**
1. Email settings configured (Admin → Email Account)
2. User email address correct
3. User has permission to receive notifications
4. Check "Notification Log" for sent messages
5. Check spam/junk folders

**Fix:**
1. Test email with "Send Test Email"
2. Verify SMTP settings
3. Check user notification preferences
4. Contact system administrator if still failing

### Problem: Verification not updating asset status

**Symptoms:** Reporter verified but asset still "Out of Order"

**Investigation:**
1. Open repair document
2. Check "Verification Status" = "Verified - Passed"
3. Open "Asset Repair" list
4. Filter by asset name
5. Check for OTHER Major repairs still open

**Explanation:**
- Asset only restores when ALL Major repairs verified
- System checks for other open Major repairs
- If found, asset stays "Out of Order"
- This is correct behavior (safety feature)

**Resolution:**
1. Review all Major repairs for asset
2. Complete and verify each one
3. After last verification, asset auto-restores
4. If should restore early, manually change asset status

### Problem: Engineer cannot edit approved repair

**Symptoms:** "Cannot edit field" errors

**Explanation:**
- This is correct behavior
- Only "Actions Performed" editable after approval
- Prevents scope creep

**If Engineer Needs to Edit:**
1. Reject the repair
2. Engineer can edit in Draft
3. Engineer resubmits
4. You re-approve

---

## Best Practices

### Approval Guidelines

**✅ DO:**
- Review within 2 hours of submission
- Add meaningful approval notes
- Contact engineer if questions
- Consider business impact
- Check asset history
- Verify cost reasonableness
- Override severity if needed

**❌ DON'T:**
- Rubber-stamp approvals
- Approve without reading
- Ignore cost implications
- Let approvals pile up
- Approve unclear descriptions
- Skip business impact assessment

### Team Communication

**Effective Feedback:**
- Be specific in rejection notes
- Provide actionable guidance
- Recognize good work
- Address issues promptly
- Maintain professional tone

**Escalation Protocol:**
1. Emergency repairs: Immediate approval
2. High-cost repairs: Discuss with finance
3. Recurring issues: Investigate root cause
4. Safety concerns: Prioritize immediately

### System Hygiene

**Weekly Tasks:**
- Review pending verifications
- Check overdue inspections
- Clean up old Draft repairs
- Update dashboard
- Export weekly metrics

**Monthly Tasks:**
- Generate management reports
- Review asset status
- Analyze cost trends
- Identify recurring issues
- Plan preventive actions

---

## Quick Reference

### Approval Decision Matrix

| Scenario | Recommend | Notes |
|----------|-----------|-------|
| Safety hazard | APPROVE (Major) | Immediate priority |
| Complete failure | APPROVE (Major) | Take offline |
| Minor wear | APPROVE (Minor) | Schedule flexibly |
| High cost (>$X) | REVIEW | Discuss with management |
| Unclear description | REJECT | Request details |
| Recurring issue | INVESTIGATE | Root cause analysis |
| Cosmetic only | DEFER | Low priority |

### Workflow Quick Guide

```
Draft → Submit → Pending Approval → [YOU] Approve/Reject

If Approve:
  → Approved → Engineer works → Job Finished → Reporter Verifies → Complete

If Reject:
  → Returns to Draft → Engineer edits → Resubmit → Pending Approval
```

### Contact Information

- System Administrator: [Add contact]
- IT Support: [Add contact]
- Management: [Add contact]
- Emergency: [Add number]

---

## Appendix: Screenshot Placeholders

The following screenshots should be taken and added to this manual:

1. **Approval Queue** - List of repairs pending approval with priority indicators
2. **Repair Review Screen** - Full form showing all fields to review
3. **Approval Section** - Notes, signature, and approve/reject buttons
4. **Portal Settings** - Settings document with checkbox states
5. **Manager Home Page** - Both QR and Search cards visible
6. **Search Interface** - Search box and results grid
7. **Status Badges** - Different colored badges (Submitted, Out of Order, etc.)
8. **Asset Repair List** - Filtered by workflow state
9. **Reports Dashboard** - Custom dashboard with widgets
10. **Workflow Diagram** - Visual representation of states
11. **Notification Log** - List of sent notifications
12. **User Management** - User list with roles

---

**Document Version:** 1.0
**Last Updated:** December 16, 2024
**Prepared By:** TUB Suite Development Team

**For Technical Support:** Contact system administrator or refer to technical documentation.
