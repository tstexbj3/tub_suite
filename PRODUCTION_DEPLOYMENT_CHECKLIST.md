# Production Deployment Checklist - v2.1.0

**Date:** 2026-01-21
**Feature:** Reporter Confirmation Workflow State

## Pre-Deployment Steps

### 1. Database Changes Required
Run these scripts IN ORDER on production:

```bash
cd ~/frappe-bench/apps/tub_suite

# 1. Add "Pending Reporter Confirmation" workflow state
../../env/bin/python3 ADD_PENDING_REPORTER_CONFIRMATION_STATE.py

# 2. Fix Section 3 visibility
../../env/bin/python3 FIX_SECTION3_VISIBILITY.py

# 3. Fix reporter confirmation section visibility
../../env/bin/python3 FIX_REPORTER_SECTION_VISIBILITY.py

# 4. Allow self-approval for Reporter Confirm transition
../../env/bin/python3 FIX_SELF_APPROVAL.py
```

### 2. Clear Cache
```bash
bench --site <your_site> clear-cache
```

### 3. Restart Services
```bash
sudo supervisorctl restart all
```

## Code Changes Summary

### Files Modified:
1. **tub_suite/overrides/asset_repair_override.py**
   - Added `check_repair_status()` override to bypass ERPNext validation
   - Fixed `before_workflow_action()` to handle "Pending Reporter Confirmation" state
   - Fixed validation to check OLD workflow state during transitions
   - Added permission checks for engineering workflow states

2. **tub_suite/api/maintenance.py**
   - Updated `get_repairs_for_confirmation()` to fetch "Pending Reporter Confirmation" state
   - Updated `submit_reporter_confirmation()` to apply workflow transition to "Finished"
   - Fixed confirmation photos parsing to extract first photo from JSON array

3. **maintenance-react-dev/src/pages/ConfirmRepair.jsx**
   - Added `maxPhotos={1}` to limit confirmation photo uploads to 1

4. **maintenance-react-dev/src/pages/Home.jsx**
   - Updated to fetch repairs in "Pending Reporter Confirmation" state
   - Display "Awaiting Confirmation" section

5. **maintenance-react-dev/src/App.jsx**
   - Added `/confirm/:repairName` route

## Portal Rebuild Required

```bash
cd ~/frappe-bench/apps/tub_suite/maintenance-react-dev
npm run build
```

## Testing Checklist

### Test Complete Workflow:
- [ ] Draft → GM Approval Section 1 (GM signs)
- [ ] GM Approval Section 1 → Pending Engineering Assessment (GM approves)
- [ ] Pending Engineering Assessment → Pending Eng Supervisor Review (Engineer fills assessment)
- [ ] Pending Eng Supervisor Review → Pending GM Final Approval (Eng Supervisor signs)
- [ ] Pending GM Final Approval → Approved for Repair (GM approves)
- [ ] Approved for Repair → Pending Supervisor Verification (Engineer fills repair_result_status and clicks "Finish Repair")
- [ ] Pending Supervisor Verification → **Pending Reporter Confirmation** (Supervisor verifies)
- [ ] **Pending Reporter Confirmation → Finished** (Reporter confirms via portal)

### Test Permission Checks:
- [ ] Engineering Assessment: Only Engineering Team can edit (not Supervisor/GM)
- [ ] Eng Supervisor Review: Only Eng Supervisor can edit (not Engineering Team/GM)
- [ ] GM Final Approval: Only GM can edit (not Engineer/Supervisor)
- [ ] Section 3 (Hygiene) only shows in "Pending Supervisor Verification" and "Finished"

### Test Portal:
- [ ] Create new repair from portal (Draft state creation works)
- [ ] Reporter confirmation shows in "Pending Reporter Confirmation" state
- [ ] Can attach 1 photo (not multiple)
- [ ] Can add notes
- [ ] Confirmation date auto-fills
- [ ] Transitions to "Finished" after confirmation
- [ ] Confirmation data visible in "Finished" state

### Test Edge Cases:
- [ ] "Please update Repair Status" error does NOT appear in any state
- [ ] Workflow transitions work without blocking
- [ ] Confirmation photo displays correctly (not JSON string)

## Rollback Plan

If issues occur:

1. **Revert workflow state:**
```bash
cd ~/frappe-bench/apps/tub_suite
git checkout HEAD~1 tub_suite/overrides/asset_repair_override.py
git checkout HEAD~1 tub_suite/api/maintenance.py
bench --site <your_site> clear-cache
```

2. **Remove workflow state from database:**
```sql
-- Remove the transition
DELETE FROM `tabWorkflow Transition`
WHERE state = 'Pending Reporter Confirmation';

-- Remove the state
DELETE FROM `tabWorkflow Document State`
WHERE state = 'Pending Reporter Confirmation'
AND parent = 'Asset Repair Workflow - Supervisor Only';
```

3. **Revert workflow action:**
```sql
DELETE FROM `tabWorkflow Action Master`
WHERE workflow_action_name = 'Reporter Confirm';
```

## Post-Deployment Verification

1. Check that all existing repairs still work
2. Create a test repair and complete full workflow
3. Monitor error logs for 24 hours
4. Verify portal confirmation works for end users

## Notes

- This update is BACKWARD COMPATIBLE - existing "Finished" repairs will still display correctly
- The "Pending Reporter Confirmation" state is NEW - no existing repairs will be in this state
- Reporter confirmation is OPTIONAL - if reporters don't confirm, repairs stay in "Pending Reporter Confirmation"
- Administrator can manually transition stuck repairs if needed
