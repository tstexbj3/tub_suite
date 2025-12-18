# 📱 Maintenance Inspector User Manual
**Role:** Maintenance User (Inspector)
**Platform:** Mobile Portal
**Version:** v2.1.0

---

## Table of Contents
1. [Overview](#overview)
2. [Accessing the Portal](#accessing-the-portal)
3. [Daily Tasks](#daily-tasks)
4. [Reporting Issues](#reporting-issues)
5. [Verifying Repairs](#verifying-repairs)
6. [Troubleshooting](#troubleshooting)

---

## Overview

### What You Do
As a **Maintenance Inspector**, you are responsible for:
- ✅ Performing daily maintenance inspections using mobile devices
- ✅ Scanning asset QR codes to access maintenance checklists
- ✅ Taking timestamped photos during inspections
- ✅ Reporting equipment issues with photos
- ✅ Verifying completed repairs

### What You DON'T Do
- ❌ You do NOT use the ERPNext desktop interface
- ❌ You do NOT approve or assign repairs
- ❌ You do NOT perform the actual repairs

---

## Accessing the Portal

### Step 1: Open Your Browser
1. Open your mobile device browser (Chrome, Safari, Edge, etc.)
2. Navigate to: `https://tub.x-desk.tech/maintenance`

**[SCREENSHOT 1: Mobile browser with portal URL]**

### Step 2: Log In
1. Enter your username (provided by IT)
2. Enter your password
3. Tap **Login**

**[SCREENSHOT 2: Login screen]**

### Step 3: View Dashboard
After login, you'll see:
- 🔢 **Badge count** - Number of tasks requiring verification today
- 📋 **Asset list** - All assets assigned to you
- 🔍 **Search bar** - Quick asset lookup

**[SCREENSHOT 3: Dashboard with badge count]**

---

## Daily Tasks

### Step 1: Scan Asset QR Code
1. Tap the **Scan QR** button at the top
2. Point your camera at the asset's QR code sticker
3. Wait for automatic recognition

**[SCREENSHOT 4: QR scanner screen]**

**Tip:** If QR scan doesn't work, use the search bar to type the asset code manually.

### Step 2: View Asset Details
After scanning, you'll see:
- 📷 **Asset photo**
- 📝 **Asset name and code**
- ✅ **Maintenance checklist** (if asset is available)
- ⚠️ **Issue warning** (if asset is Out of Order)

**[SCREENSHOT 5: Asset detail page - healthy asset]**

**[SCREENSHOT 6: Asset detail page - asset with active repair]**

### Step 3: Perform Inspection (No Issues)
If everything is working normally:

1. Review each checklist item:
   - Check engine oil level
   - Check tire pressure
   - Check brake fluid
   - etc.

2. Tap **📷 Take Photo** button
3. Take **BEFORE photo** (starting condition)
4. Perform the maintenance tasks
5. Tap **📷 Take Photo** button again
6. Take **AFTER photo** (completed condition)

**[SCREENSHOT 7: Checklist with photo buttons]**

**[SCREENSHOT 8: Camera capture screen]**

**Important:** Photos are automatically timestamped and geotagged.

### Step 4: Add Inspection Notes
1. Scroll to **Notes** field
2. Enter any observations:
   - "All systems normal"
   - "Minor oil leak observed but operational"
   - "Tires replaced during inspection"

**[SCREENSHOT 9: Notes field]**

### Step 5: Submit Task
1. Tap **Submit Task** button at the bottom
2. Wait for confirmation message: "✅ Task submitted successfully"
3. Task card will be **locked** until tomorrow

**[SCREENSHOT 10: Submit button and success message]**

---

## Reporting Issues

### When to Report an Issue
Report an issue if you find:
- ❌ Equipment not functioning
- ⚠️ Safety hazards
- 🔧 Parts broken or missing
- 🛑 Asset cannot operate safely

### Step 1: Select "Has Issue"
1. Tap the toggle: **This task has an issue**
2. The form will change to show issue fields

**[SCREENSHOT 11: Toggle issue button - OFF state]**

**[SCREENSHOT 12: Toggle issue button - ON state with issue fields]**

### Step 2: Take Issue Photos
1. Tap **📷 Take Photo** button in the **Issue Photos** section
2. Take clear photos showing:
   - The broken part
   - The error message (if applicable)
   - The overall condition

**Minimum:** 1 photo required
**Recommended:** 2-3 photos from different angles

**[SCREENSHOT 13: Issue photo section]**

**[SCREENSHOT 14: Example issue photos - broken part]**

### Step 3: Describe the Problem
In the **Issue Description** field, write:
- **What's broken:** "Front tire is flat"
- **What you observed:** "Heard hissing sound, tire completely deflated"
- **When it happened:** "Discovered during morning inspection"

**Example:**
```
Front left tire is completely flat. Discovered during
morning inspection. Tire appears to have a puncture.
Vehicle cannot be operated safely.
```

**[SCREENSHOT 15: Issue description field filled]**

### Step 4: Add Inspection Notes (Optional)
Use the **Notes** field for additional context:
- "Asset was working fine yesterday"
- "Operator reported strange noise yesterday"

**[SCREENSHOT 16: Notes field for issue reporting]**

### Step 5: Submit Issue Report
1. Tap **Submit Task** button
2. Wait for confirmation
3. You'll see:
   - ✅ "Issue reported successfully"
   - 🔔 "Engineers have been notified"

**[SCREENSHOT 17: Issue submission success message]**

### What Happens Next?
1. **Asset status** changes to "Out of Order"
2. **Engineering Team** receives notification
3. **Repair request** is created automatically
4. **You will be notified** when repair is finished for verification

---

## Verifying Repairs

### When Do You Verify?
After engineers finish a repair, you'll receive a notification:
- 🔔 "Repair finished - Please verify"
- 📱 Badge count will increase

**[SCREENSHOT 18: Notification badge for verification]**

### Step 1: Scan Asset Again
1. Return to the asset location
2. Scan the QR code
3. You'll see the repair information

**[SCREENSHOT 19: Asset page showing finished repair]**

### Step 2: Test the Asset
1. Check if the issue is truly fixed
2. Test the asset functionality
3. Verify the repair quality

### Step 3: Choose Verification Result

#### Option A: Repair Passed ✅
If the repair is good:
1. Tap **Verified - Passed** button
2. Asset status returns to "Submitted" (operational)
3. Task card unlocks for normal inspections

**[SCREENSHOT 20: Verification buttons - Passed selected]**

#### Option B: Repair Failed ❌
If the issue is NOT fixed:
1. Tap **Verified - Failed** button
2. Take photos showing the remaining problem
3. Add notes explaining what's still wrong
4. Engineers will be re-notified

**[SCREENSHOT 21: Verification buttons - Failed selected]**

**[SCREENSHOT 22: Failed verification with notes]**

---

## Troubleshooting

### Problem: QR Code Won't Scan
**Solutions:**
1. Clean the QR code sticker
2. Ensure good lighting
3. Hold phone steady, 6-12 inches away
4. Use the **Search** function instead:
   - Tap search bar
   - Type asset code (e.g., "PUMP-001")
   - Select from results

**[SCREENSHOT 23: Search function as QR alternative]**

### Problem: Camera Not Working
**Solutions:**
1. Check browser permissions:
   - Settings → Safari/Chrome → Camera → Allow
2. Close and reopen browser
3. Try different browser
4. Restart phone

**[SCREENSHOT 24: Browser camera permission settings]**

### Problem: "Photo Required" Error
**Solution:**
- Normal inspection: Take **2 photos minimum** (before/after)
- Issue reporting: Take **1 photo minimum** (issue photo)

**[SCREENSHOT 25: Photo required error message]**

### Problem: Task Card Won't Unlock
**Why:** Tasks lock after completion until next scheduled date.

**Check:**
1. View task frequency (Daily, Weekly, Monthly)
2. Last completion date
3. Next due date

**Contact IT** if task should be available but isn't.

**[SCREENSHOT 26: Locked task card with schedule info]**

### Problem: "Asset Out of Order" Message
**Meaning:** Asset has an active repair in progress.

**What to do:**
1. Do NOT perform maintenance
2. Check repair status
3. Wait for engineer to finish
4. You'll be notified when ready for verification

**[SCREENSHOT 27: Out of Order warning screen]**

### Problem: Can't Submit Task
**Common Causes:**
1. ❌ Missing required photos
2. ❌ Empty description (if reporting issue)
3. ❌ Network connection lost
4. ❌ Session expired

**Solutions:**
1. Check all fields are filled
2. Check WiFi/mobile data connection
3. Refresh page and try again
4. Log out and log back in

**[SCREENSHOT 28: Network error message]**

---

## Quick Reference Card

### Normal Inspection Workflow
```
1. Scan QR Code
2. Review Checklist
3. Take Before Photo
4. Perform Tasks
5. Take After Photo
6. Add Notes
7. Submit Task
```

### Issue Reporting Workflow
```
1. Scan QR Code
2. Toggle "Has Issue" ON
3. Take Issue Photos (1-3)
4. Describe Problem
5. Add Notes
6. Submit Task
```

### Verification Workflow
```
1. Receive Notification
2. Scan QR Code
3. Test Asset
4. Choose: Passed or Failed
5. Submit Verification
```

---

## Contact Support

### When to Contact IT
- Login problems
- Portal not loading
- Asset missing from list
- QR code damaged/missing
- Account access issues

### How to Contact
- **Email:** it@tipubon.com
- **Phone:** [PHONE NUMBER]
- **Urgent Issues:** Contact your supervisor

---

## Appendix: Screenshot Checklist

**For IT/Documentation Team:** Add screenshots at these locations:

| # | Screenshot Needed | Status |
|---|---|---|
| 1 | Mobile browser with portal URL | ⬜ Pending |
| 2 | Login screen | ⬜ Pending |
| 3 | Dashboard with badge count | ⬜ Pending |
| 4 | QR scanner screen | ⬜ Pending |
| 5 | Asset detail page - healthy asset | ⬜ Pending |
| 6 | Asset detail page - asset with repair | ⬜ Pending |
| 7 | Checklist with photo buttons | ⬜ Pending |
| 8 | Camera capture screen | ⬜ Pending |
| 9 | Notes field | ⬜ Pending |
| 10 | Submit button and success message | ⬜ Pending |
| 11 | Toggle issue button - OFF | ⬜ Pending |
| 12 | Toggle issue button - ON | ⬜ Pending |
| 13 | Issue photo section | ⬜ Pending |
| 14 | Example issue photos | ⬜ Pending |
| 15 | Issue description filled | ⬜ Pending |
| 16 | Notes field for issues | ⬜ Pending |
| 17 | Issue submission success | ⬜ Pending |
| 18 | Notification badge | ⬜ Pending |
| 19 | Asset with finished repair | ⬜ Pending |
| 20 | Verification - Passed | ⬜ Pending |
| 21 | Verification - Failed | ⬜ Pending |
| 22 | Failed verification notes | ⬜ Pending |
| 23 | Search function | ⬜ Pending |
| 24 | Camera permissions | ⬜ Pending |
| 25 | Photo required error | ⬜ Pending |
| 26 | Locked task card | ⬜ Pending |
| 27 | Out of Order warning | ⬜ Pending |
| 28 | Network error | ⬜ Pending |

---

**Document Version:** 1.0
**Last Updated:** 2025-12-18
**Next Review:** 2026-01-18
