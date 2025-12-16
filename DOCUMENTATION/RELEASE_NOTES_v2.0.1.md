# Release Notes - TUB Suite v2.0.1

**Release Date:** 2025-12-16
**Type:** Bug Fix Release
**Upgrade:** Required for production sites

---

## Critical Fixes

### 1. Badge System Fix ⚠️→✅

**Issue:** Orange "⚠ Issue Reported" badge turned green after page refresh

**Root Causes (3 bugs):**
1. Type mismatch: `datetime.date` vs `str` comparison always returned False
2. Query used `repair_status` field (empty until "Finished"), not `workflow_state`
3. Query showed badge on ALL tasks, not just the task with the issue

**Impact:** Users couldn't see which tasks had reported issues after refreshing the page

**Fixed:** `tub_suite/api/maintenance.py` lines 342-353
- Convert date to string for comparison
- Use `workflow_state` instead of `repair_status`
- Filter by specific `maintenance_task`

---

### 2. Field Locking - Engineer 🔒

**Issue:** Engineers could edit fields after submitting for approval

**Root Cause:** Python validation only blocked managers, not engineers

**Impact:** Engineers could change their documented work after submission (audit trail violation)

**Fixed:** `tub_suite/overrides/asset_repair_override.py` lines 58-78
- Block ALL field edits for engineers after Draft state
- Enforce in both Python (server) and Client Script (UI)

---

### 3. Field Locking - Manager 🔒

**Issue:** Managers could edit everything after approving repair

**Root Cause:** Validation only applied to "Pending Approval" state

**Impact:** Managers could alter records after approval (audit trail violation)

**Fixed:** `tub_suite/overrides/asset_repair_override.py` lines 80-127
- Extend validation to "Approved" and "Finished" states
- Lock all fields including approval fields after approval

---

### 4. Asset Status Timing ⏱️

**Issue:** Asset went "Out of Order" when engineer reported Major issue

**Business Requirement:** Asset should only go "Out of Order" when **manager approves** the repair

**Root Cause:** Code triggered on severity change (engineer action), not approval (manager action)

**Impact:** Assets marked down prematurely before manager confirmation

**Fixed:** `tub_suite/overrides/asset_repair_override.py` lines 146-150, 165-207
- Changed trigger from `severity_changed` to `workflow_state == "Approved"`
- Renamed function to `update_asset_status_on_approval()`
- Only Major repairs set asset "Out of Order", only after manager approval

---

## New Files

### Documentation

1. **TECHNICAL.md** - Comprehensive technical documentation
   - Architecture overview
   - Field locking implementation details
   - Badge system explained with all 3 bugs
   - Asset status business logic
   - API reference
   - Troubleshooting guide

2. **PRODUCTION_GUIDE.md** - Production deployment & debugging
   - Pre-deployment checklist
   - Step-by-step deployment
   - Post-deployment verification
   - Debug procedures for each issue
   - Common issues & solutions
   - Rollback procedures
   - Health check scripts

3. **CLEANUP_PLAN.md** - Code cleanup audit
   - Utility scripts to keep/delete
   - Database script cleanup
   - Git cleanup commands

### Utilities

4. **fix_existing_approved_repairs.py** - One-time migration utility
   - Fixes asset status for repairs approved before v2.0.1
   - Usage: `bench --site tub execute tub_suite.utils.fix_existing_approved_repairs.fix_approved_repairs`

---

## Breaking Changes

None. This is a bug fix release compatible with v2.0.0 data.

---

## Migration Required

### For Existing Production Sites

```bash
# 1. Backup first!
bench --site YOUR_SITE backup --with-files

# 2. Pull latest code
cd ~/frappe-bench/apps/tub_suite
git pull origin main

# 3. Check for old duplicate scripts
bench --site YOUR_SITE console
# (Run audit commands from PRODUCTION_GUIDE.md)

# 4. Run setup to update Client/Server Scripts
bench --site YOUR_SITE execute tub_suite.setup.asset_repair_setup.run_production_setup

# 5. Fix existing approved repairs (one-time)
bench --site YOUR_SITE execute tub_suite.utils.fix_existing_approved_repairs.fix_approved_repairs

# 6. Clear cache
bench --site YOUR_SITE clear-cache

# 7. Restart
bench restart  # or sudo supervisorctl restart all

# 8. Users must hard-refresh browsers: Ctrl+Shift+R
```

---

## Testing Checklist

After deployment, verify:

### Badge System
- [ ] Complete task without issue → Green badge "✓ Completed Today"
- [ ] Complete task WITH issue → Orange badge "⚠ Issue Reported"
- [ ] **Refresh page (F5)** → Badge stays orange ✅
- [ ] Complete different task without issue → Green badge (not orange)

### Field Locking - Engineer
- [ ] Create repair, fill fields, submit → Success
- [ ] Try to edit `actions_performed` → Fields locked (greyed out)
- [ ] Try to save anyway → Error message shown

### Field Locking - Manager
- [ ] Open repair in Pending Approval
- [ ] Try to edit engineer fields → Locked
- [ ] Can edit `approval_notes` and `approval_signature` → Yes
- [ ] Approve repair → Success
- [ ] Try to edit approval fields → Locked

### Asset Status
- [ ] Engineer reports Major issue → Asset stays "Submitted"
- [ ] Engineer submits for approval → Asset still "Submitted"
- [ ] Manager approves → Asset changes to "Out of Order" ✅
- [ ] Complete repair → Asset restored to "Submitted"

---

## Files Changed

### Modified

1. `tub_suite/api/maintenance.py`
   - Lines 279: Added API version debug
   - Lines 342-353: Fixed badge query (type + workflow_state + task filter)
   - Lines 357-366: Added debug output

2. `tub_suite/overrides/asset_repair_override.py`
   - Lines 58-78: Added engineer field locking
   - Lines 80-90: Extended manager restrictions to all states
   - Lines 136-137: Added workflow_state to old_doc query
   - Lines 146-150: Changed trigger to workflow_state change
   - Lines 165-207: Renamed and updated `update_asset_status_on_approval()`
   - Lines 163-168: Use workflow_state in Major repair check

3. `tub_suite/setup/asset_repair_setup.py`
   - Lines 152-209: Added workflow-based field locking in Client Script

### Added

4. `TECHNICAL.md` - Technical documentation
5. `PRODUCTION_GUIDE.md` - Production deployment guide
6. `CLEANUP_PLAN.md` - Cleanup plan
7. `RELEASE_NOTES_v2.0.1.md` - This file
8. `tub_suite/utils/fix_existing_approved_repairs.py` - Migration utility

### Deleted

9. Temporary debug files (to be removed):
   - `debug_badge_issue.py`
   - `check_repairs.py`
   - `check_task_timeline.py`

10. Temporary documentation (removed):
   - `BADGE_FIX.md`
   - `FIELD_LOCKING_FIX.md`
   - `DEPLOY_FIXES.md`
   - `ASSET_STATUS_FIX.md`
   - `FIXES_COMPLETED.md`
   - `REMAINING_ISSUES.md`

---

## Known Issues

None. All reported issues in v2.0.0 have been fixed.

---

## Performance Impact

- **Minimal** - Added one database query per completed task (only when `last_completion_date == today`)
- No impact on non-completed tasks
- No impact on tasks completed on previous days

---

## Security Improvements

- ✅ Enforced audit trail integrity
- ✅ Engineers cannot alter submitted work
- ✅ Managers cannot alter engineer work
- ✅ Managers cannot change approvals after giving them
- ✅ Clear separation of roles and responsibilities

---

## Upgrade Path

### From v2.0.0 → v2.0.1
- **Required:** Yes (critical bug fixes)
- **Database changes:** No schema changes
- **Data migration:** Yes (run `fix_existing_approved_repairs`)
- **Downtime:** < 1 minute (restart only)
- **Rollback:** Possible (see PRODUCTION_GUIDE.md)

### From v1.x → v2.0.1
- See MIGRATION_GUIDE.md
- Major version upgrade (jQuery → React)
- Database migration required
- Test on staging first

---

## Support

- **GitHub Issues:** https://github.com/tstexbj3/tub_suite/issues
- **Documentation:** See TECHNICAL.md and PRODUCTION_GUIDE.md
- **Email:** it@tipubon.com

---

## Credits

**Developed by:** Tipubon International Co., Ltd.
**Release Manager:** Claude (AI Assistant)
**Testing:** Tipubon IT Team

---

**Download:** https://github.com/tstexbj3/tub_suite/releases/tag/v2.0.1

**Changelog:** See CHANGELOG.md for detailed version history
