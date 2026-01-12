# Archive Folder

This folder contains **outdated and obsolete documentation** that is kept for historical reference only.

## ⚠️ DO NOT USE THESE FILES

All documentation in this folder is **OUT OF DATE** and does not reflect the current system.

## Current Documentation (Use These Instead)

Go to the project root and use these files:

1. **CLAUDE_RULES.md** - Rules for AI assistant to follow
2. **WORKFLOW_AND_FIELDS.md** - Single source of truth for Asset Repair workflow
3. **README.md** - Project overview
4. **CHANGELOG.md** - Version history
5. **DEPLOYMENT_GUIDE_v2.1.0.md** - How to deploy
6. **INSPECTOR_TODO_LIST_FEATURE.md** - Todo list feature (separate from Asset Repair)

---

## What's in Archive

### `/design/` - Old design documents
- DESIGN_ASSET_REPAIR_LOG.md
- DESIGN_UPDATES_APPEND.md
- DESIGN_ASSET_REPAIR_WORKFLOW_IMPROVEMENTS.md

**Why archived:** Design phase completed, workflow has changed significantly.

### `/analysis/` - Old analysis documents
- IMPACT_ANALYSIS_ASSET_REPAIR.md

**Why archived:** Analysis was for old workflow with operators.

### `/cleanup/` - Old cleanup plans
- CLEANUP_PLAN_OLD_VS_NEW.md
- SAFE_CLEANUP_EXECUTION.md

**Why archived:** Cleanup already completed.

### `/obsolete-plans/` - Obsolete technical docs
- WORKFLOW_CONFIG.md - Incomplete old workflow
- MASTER_PLAN_ASSET_REPAIR_FM_EN_04.md - Wrong workflow (had operators)
- FIXTURE_MANAGEMENT.md - Outdated field list (pre-supervisor-only)
- MIGRATION_GUIDE.md - v1→v2 migration (already done)

**Why archived:** Workflow changed to supervisor-only, field structure changed.

### Root of archive
- REDESIGNED_WORKFLOW_SUPERVISOR_ONLY.md - Initial supervisor-only redesign proposal

**Why archived:** Content merged into WORKFLOW_AND_FIELDS.md

---

## If You Need To Reference Old Workflow

The files here document the **operator-based workflow** that was used before 2026-01-10.

**Key change on 2026-01-10:**
- **Before:** Operators reported issues, supervisors verified
- **After:** Supervisors report issues on behalf of teams (no operators)

**Current workflow states:** 9 states (removed "Pending Reporter Confirmation")

**Current state name:** "Pending Supervisor Verification" (not "Pending Reporter Supervisor Verification")

---

**Last Updated:** 2026-01-11
**Status:** Archive folder - do not add new files here
