# Cleanup Plan - Old Code Audit

## Utility Scripts Audit

### Keep (Production-Useful)

1. **`fix_orphaned_tasks.py`** ✅
   - **Purpose:** Unlock tasks after deleting repair/log
   - **Usage:** `bench --site tub execute tub_suite.utils.fix_orphaned_tasks.fix_orphaned_task_completions`
   - **Needed:** YES - Users will need this when cleaning up data

2. **`fix_existing_approved_repairs.py`** ✅
   - **Purpose:** One-time fix for v2.0.1 upgrade (asset status)
   - **Usage:** `bench --site tub execute tub_suite.utils.fix_existing_approved_repairs.fix_approved_repairs`
   - **Needed:** YES - For migration to v2.0.1

### Delete (Debug/Temporary)

3. **`debug_badge_issue.py`** ❌
   - **Purpose:** Debug badge issue (session work)
   - **Status:** Not complete, buggy
   - **Action:** DELETE

4. **`check_repairs.py`** ❌
   - **Purpose:** Check repair workflow states
   - **Status:** Debug utility, replaced by better tools
   - **Action:** DELETE

5. **`debug_today_repairs.py`** ⚠️
   - **Purpose:** Debug badge query
   - **Status:** Useful for troubleshooting badge issues
   - **Action:** KEEP but rename to `troubleshoot_badge.py`

6. **`check_task_timeline.py`** ❌
   - **Purpose:** Debug task completion timeline
   - **Status:** Incomplete, has bugs
   - **Action:** DELETE

7. **`audit_scripts.py`** ✅
   - **Purpose:** Audit all Client/Server Scripts
   - **Status:** Useful for production health checks
   - **Action:** KEEP

8. **`list_all_scripts.py`** ✅
   - **Purpose:** List all scripts in system
   - **Status:** Useful for debugging
   - **Action:** KEEP

9. **`cleanup_old_scripts.py`** ⚠️
   - **Purpose:** Delete v1.0 duplicate scripts
   - **Status:** One-time use for v2.0 migration
   - **Action:** KEEP (users might need during upgrade)

10. **`cleanup_duplicate_fields.py`** ⚠️
    - **Purpose:** Clean up duplicate custom fields
    - **Status:** One-time use for cleanup
    - **Action:** KEEP (might need for field cleanup)

## Client/Server Scripts Check

### Expected Scripts in Database (v2.0.1)

**Client Scripts:**
- ✅ "Asset Repair - Field Locking UI" (enabled=1)

**Server Scripts:**
- ✅ "Asset Repair - Validation and Status" (disabled=0)

### Old Scripts to Delete (if found)

**Old Client Scripts:**
- ❌ "Asset Repair - Field Locking" (old, no "UI")
- ❌ "Asset Repair - Lock All Fields Except Approval"
- ❌ "Asset Repair - Lock Fields After Submit"
- ❌ "Repair Approval"
- ❌ "Show Approval Fields - Asset Repair"

**Old Server Scripts:**
- ❌ "Asset repair approval" (lowercase, no doctype)

## Cleanup Commands

Run in your terminal:

```bash
cd ~/frappe-bench/apps/tub_suite/tub_suite/utils

# Delete debug scripts
rm -f debug_badge_issue.py check_repairs.py check_task_timeline.py

# Rename troubleshooting script
mv debug_today_repairs.py troubleshoot_badge.py

# List what's left
ls -1 *.py
```

Expected remaining files:
```
__init__.py
audit_scripts.py
cleanup_duplicate_fields.py
cleanup_old_scripts.py
fix_existing_approved_repairs.py
fix_orphaned_tasks.py
list_all_scripts.py
troubleshoot_badge.py
```

## Database Cleanup

Run this to check and clean old scripts:

```bash
bench --site tub console

import frappe

# Check Client Scripts
client_scripts = frappe.get_all("Client Script",
    filters={"reference_doctype": "Asset Repair"},
    fields=["name", "enabled", "modified"])

print(f"\\nClient Scripts found: {len(client_scripts)}")
for s in client_scripts:
    print(f"  - {s.name} (enabled={s.enabled})")

# Expected: 1 script
# If more than 1, delete old ones

old_client_names = [
    "Asset Repair - Field Locking",
    "Asset Repair - Lock All Fields Except Approval",
    "Asset Repair - Lock Fields After Submit",
    "Repair Approval",
    "Show Approval Fields - Asset Repair",
]

deleted = []
for name in old_client_names:
    if frappe.db.exists("Client Script", name):
        frappe.delete_doc("Client Script", name, force=1)
        deleted.append(name)
        print(f"✓ Deleted: {name}")

if deleted:
    frappe.db.commit()
    print(f"\\nDeleted {len(deleted)} old Client Scripts")
else:
    print("\\n✓ No old scripts to delete")

# Check Server Scripts
server_scripts = frappe.get_all("Server Script",
    filters={"reference_doctype": "Asset Repair"},
    fields=["name", "disabled", "modified"])

print(f"\\nServer Scripts found: {len(server_scripts)}")
for s in server_scripts:
    print(f"  - {s.name} (disabled={s.disabled})")

# Expected: 1 script

# Delete old server script if exists
old_server = "Asset repair approval"
if frappe.db.exists("Server Script", old_server):
    frappe.delete_doc("Server Script", old_server, force=1)
    frappe.db.commit()
    print(f"✓ Deleted: {old_server}")
```

## Git Cleanup

Check for uncommitted files:

```bash
cd ~/frappe-bench/apps/tub_suite

# Check status
git status

# If there are untracked utility files, add to .gitignore
echo "tub_suite/utils/debug_*.py" >> .gitignore
echo "tub_suite/utils/check_*.py" >> .gitignore

# Remove from git if accidentally committed
git rm --cached tub_suite/utils/debug_badge_issue.py
git rm --cached tub_suite/utils/check_repairs.py
git rm --cached tub_suite/utils/check_task_timeline.py
```

## Documentation Cleanup

Keep only essential docs:
- ✅ README.md
- ✅ CHANGELOG.md
- ✅ MIGRATION_GUIDE.md
- ✅ TECHNICAL.md (new comprehensive doc)
- ✅ PRODUCTION_GUIDE.md (new production/debugging guide)

All temporary session docs have been deleted.

## Final Checklist

- [ ] Delete debug utility scripts (3 files)
- [ ] Rename debug_today_repairs.py → troubleshoot_badge.py
- [ ] Run database cleanup to remove old Client/Server Scripts
- [ ] Verify only 1 Client Script and 1 Server Script remain
- [ ] Update .gitignore to exclude debug files
- [ ] Commit cleanup changes
- [ ] Tag version as v2.0.1

## Commit Message Template

```
chore: cleanup old debug scripts and duplicate Client/Server Scripts

- Removed temporary debug utilities (debug_badge_issue, check_repairs, check_task_timeline)
- Renamed debug_today_repairs.py to troubleshoot_badge.py
- Documented cleanup process in CLEANUP_PLAN.md
- Created PRODUCTION_GUIDE.md for deployment and debugging
- Updated TECHNICAL.md with v2.0.1 fixes

Fixes:
- Badge type mismatch (date vs str comparison)
- Badge showing on all tasks instead of specific task
- Asset status timing (now on manager approval, not engineer report)
- Field locking for engineers and managers

Ref: v2.0.1 release
```

---

**Next Steps:**
1. Run cleanup commands above
2. Test on staging
3. Deploy to production
4. Update version tag to v2.0.1
