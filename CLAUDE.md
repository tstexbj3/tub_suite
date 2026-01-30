# Claude AI Development Reference for TUB Suite

**IMPORTANT**: Read this file at the start of EVERY session to avoid repeating past mistakes.

---

## Critical ERPNext Skills Reference

Skills installed at: `~/.claude/skills/impl/erpnext-*/`

**ALWAYS read these before making changes:**
- `~/.claude/skills/impl/erpnext-impl-customapp/SKILL.md` - Custom app patterns
- `~/.claude/skills/impl/erpnext-impl-hooks/SKILL.md` - Hooks implementation
- `~/.claude/skills/impl/erpnext-impl-customapp/references/workflows.md` - Deployment workflows

---

## Project Structure

```
tub_suite/
├── hooks.py                    # App hooks configuration
├── patches.txt                 # Database migration patches registry
├── patches/                    # Patch scripts
│   └── v2_1/                   # Version 2.1 patches
├── tub_suite/                  # Main module
│   ├── doctype/                # DocType definitions
│   │   ├── repair_spare_part/
│   │   ├── parts_inserted_item/
│   │   └── ...
│   └── overrides/              # ERPNext DocType overrides
└── fixtures/                   # Configuration exports
    ├── custom_field.json
    ├── property_setter.json
    └── workflow.json
```

---

## CRITICAL LESSONS LEARNED

### 1. Frappe Fixtures DON'T Update Existing Records

**The Problem:**
- Fixtures use timestamp comparison: if DB `modified` >= fixture `modified`, import is SKIPPED
- This is BY DESIGN in Frappe core (`frappe/modules/import_file.py`)
- Deploying fixtures to production does NOT update existing Custom Fields, Property Setters, or Workflows

**The Solution:**
- Use fixtures for INITIAL deployment only
- Use **patches** for updating existing configuration
- See: `DEPLOYMENT_PROCEDURES.md` for detailed workflows

### 2. JSON Files vs Database Are NOT Auto-Synced

**Two Sources of Truth:**
1. JSON files in `tub_suite/doctype/*/` (version controlled)
2. Database tables (`tabDocType`, `tabDocField`, `tabCustom Field`, etc.)

**They sync ONLY when you run these commands:**

```bash
# JSON → Database
bench --site mysite reload-doctype "DocType Name"
bench --site mysite migrate

# Database → JSON
bench --site mysite export-doc "DocType" "DocType Name"
bench --site mysite export-fixtures --app tub_suite
```

**NEVER assume changes in one place appear in the other automatically!**

### 3. The Correct Deployment Workflow

See `DEPLOYMENT_PROCEDURES.md` for complete procedures. Summary:

**On DEV:**
1. Make changes via UI
2. Export to JSON/fixtures: `bench export-doc` or `bench export-fixtures`
3. Verify JSON files have correct values (not null!)
4. Commit to git
5. Push to branch

**On PRODUCTION:**
1. Pull code changes
2. For NEW records: `bench migrate` (fixtures auto-import)
3. For EXISTING records: Create a patch script
4. Clear cache and restart

### 4. Common Mistakes and Solutions

| Mistake | What Happens | Solution |
|---------|-------------|----------|
| Changed JSON, didn't reload | DEV doesn't reflect changes | `bench reload-doctype "DocType Name"` |
| Changed via UI, didn't export | PROD doesn't get updates | `bench export-doc` or `bench export-fixtures` |
| Deployed fixtures to PROD | Nothing changed | Create a patch instead |
| Forgot what changed 2 weeks ago | Can't find previous work | Export immediately, document in git commit |
| Edited database directly on PROD | Changes lost on next deploy | NEVER do this - use patches |

---

## Current State (as of v2.1.12)

### Known Issues Fixed in This Version

1. **Child Table Grid Columns** (v2.1.12)
   - **Problem**: Spare Parts table showing 4 columns instead of 2
   - **Root Cause**: DocType JSON had wrong `in_list_view` values, production DB never updated
   - **Fix**: Created patch `fix_child_table_grid_columns.py` to update all child tables
   - **Affected DocTypes**: Repair Spare Part, Parts Inserted Item, Parts Removed Item, Engineering Todo Item

2. **Custom Field Visibility** (v2.1.7-v2.1.11)
   - **Problem**: Fields visible in wrong workflow states
   - **Root Cause**: Fixture had `depends_on: null`, deployed to production, overwrote working values
   - **Fix**: Manual SQL updates + documentation of proper workflow
   - **Files**: `DEPLOYMENT_PROCEDURES.md` documents correct procedure

### Files to ALWAYS Check Before Deploying

- `tub_suite/patches.txt` - Are new patches registered?
- `tub_suite/fixtures/custom_field.json` - Do Custom Fields have correct `depends_on` values (not null)?
- `tub_suite/tub_suite/doctype/*/` - Are JSON files exported from latest UI changes?
- `DEPLOYMENT_PROCEDURES.md` - Following the correct procedure?

---

## Quick Reference Commands

### Development Workflow

```bash
# After UI changes - export to JSON
bench --site devsite export-doc "DocType" "Repair Spare Part"

# After Customize Form changes - export fixtures
bench --site devsite export-fixtures --app tub_suite

# Test migration
bench --site devsite migrate

# Check for errors
tail -f ~/frappe-bench/logs/web.error.log
```

### Production Deployment

```bash
# Backup first!
bench --site prodsite backup --with-files

# Pull changes
cd ~/frappe-bench/apps/tub_suite
git pull origin v2.1.0

# Migrate (runs patches)
bench --site prodsite migrate

# Clear cache
bench --site prodsite clear-cache

# Restart (if in production mode)
sudo supervisorctl restart frappe-bench-web:
sudo supervisorctl restart frappe-bench-workers:
```

### Emergency Rollback

```bash
# Restore database
bench --site prodsite restore /path/to/backup.sql.gz

# Rollback code
cd ~/frappe-bench/apps/tub_suite
git reset --hard <commit-hash>

# Restart
sudo supervisorctl restart frappe-bench-web:
```

---

## Key Principles

1. **ALWAYS** export after UI changes
2. **NEVER** manually edit production database
3. **TEST** on DEV first (`bench migrate` must run clean)
4. **DOCUMENT** everything (this file, git commits, DEPLOYMENT_PROCEDURES.md)
5. **BACKUP** before every deployment
6. **ONE CHANGE** at a time - don't bundle unrelated changes

---

## Asset Repair Workflow States

Document for reference when working on field visibility:

1. **Draft** - Initial state
2. **Pending Supervisor Verification** - After tech completes
3. **Rejected** - Supervisor rejects
4. **Pending Engineering Assessment** - After supervisor approves (for complex repairs)
5. **Finished** - Final state

### Field Visibility Rules

- `received_by`, `received_date`: Always hidden (signature auto-fills these)
- Section 5 (Final Remarks): Only visible in "Finished" state
- Engineering sections: Only visible in "Pending Engineering Assessment" and "Finished"

---

## Version History

- **v2.1.12** - Fix child table grid columns (CURRENT)
- **v2.1.11** - Fix photo field validation
- **v2.1.9** - Change fixtures format
- **v2.1.8** - Sync fixtures from DEV
- **v2.1.7** - Change repair_source from PM to PM Inspection

---

## References

- **ERPNext Skills**: `~/.claude/skills/impl/erpnext-*/`
- **Deployment Procedures**: `./DEPLOYMENT_PROCEDURES.md`
- **Frappe Docs**: https://frappeframework.com/docs
- **ERPNext Docs**: https://docs.erpnext.com/

---

**Last Updated**: 2026-01-30 (v2.1.12)
**Next Session TODO**: Read this file FIRST, then DEPLOYMENT_PROCEDURES.md BEFORE making ANY changes
