#!/bin/bash
# Cleanup outdated scripts and temporary files after v2.1.3 deployment

echo "=========================================="
echo "TUB Suite v2.1.3 - Cleanup Script"
echo "=========================================="

# List of files to delete (temporary/outdated scripts)
files_to_delete=(
    "ADD_CUSTOM_DOCPERM_TO_FIXTURES.py"
    "CHANGELOG_v2.1.0_ENTRY.md"
    "CLEANUP_TEMP_FILES.sh"
    "CONDITIONAL_WORKFLOW_IMPLEMENTATION_SUMMARY.md"
    "DEPLOYMENT_READY_CHECKLIST.md"
    "EXPORT_FIXTURES.sh"
    "EXPORT_PRINT_FORMAT.sh"
    "FIX_EVERYTHING.sql"
    "FIX_HOOKS.py"
    "HIDE_FIELDS_SQL.sql"
    "PM_WORKFLOW_NEW_STATES_DESIGN.md"
    "UPDATE_HOOKS_DOCPERM.py"
    "UPDATE_REPAIR_TYPE_DB.sql"
    "UPDATE_WORKFLOW_ADD_MAINTENANCE_SUPERVISOR.py"
    "WORKFLOW_BACKUP_20260127_144940.json"
    "run_workflow_update.sh"
    "check_signatures.py"
    "fix_letterhead.py"
    "fix_submit_task.sh"
    "update_workflow.sh"
    "maintenance-react-dev/src/pages/Checklist.jsx.backup"
    "maintenance-react-dev/src/pages/Checklist_UPDATED.jsx"
    "tub_suite/api/maintenance.py.backup"
    "tub_suite/api/maintenance.py.backup_20260122_161934"
    "tub_suite/fixtures/workflow.json.backup_workflow"
    "tub_suite/tub_suite/doctype/repair_spare_part/repair_spare_part.json.backup"
    "tub_suite/fix_reporter_photos_field.py"
    "tub_suite/force_fix.py"
    "tub_suite/update_client_script.py"
)

# Files to keep (important documentation)
echo -e "\n✅ Files to KEEP (important docs):"
echo "  - README.md"
echo "  - CHANGELOG.md"
echo "  - CLEANUP_AND_DEPLOY.md"
echo "  - DEPLOYMENT_ISSUES_AND_FIXES.md"
echo "  - PERMISSION_REVIEW.md"
echo "  - CUSTOM_DOCPERM_DEPLOYMENT_GUIDE.md"
echo "  - ASSET_REPAIR_CLIENT_SCRIPTS.md"
echo "  - ASSET_REPAIR_SIGNATURE_AUTOFILL.md"
echo "  - PM_WORKFLOW_IMPLEMENTATION.md"
echo "  - WORKFLOW_DOCUMENTATION.md"
echo "  - PRINT_FORMAT_UPDATES.md"
echo "  - CLAUDE_RULES.md"

echo -e "\n🗑️  Files to DELETE:"
deleted_count=0
for file in "${files_to_delete[@]}"; do
    if [ -f "$file" ]; then
        echo "  - $file"
        rm "$file"
        deleted_count=$((deleted_count + 1))
    elif [ -d "$file" ]; then
        echo "  - $file/ (directory)"
        rm -rf "$file"
        deleted_count=$((deleted_count + 1))
    fi
done

echo -e "\n=========================================="
echo "✅ Cleanup complete!"
echo "   Deleted: $deleted_count files"
echo "=========================================="

# Show remaining temporary files (if any)
remaining=$(ls -1 *.py *.sh *.sql *.html 2>/dev/null | grep -E "^[A-Z_]" | wc -l)
if [ "$remaining" -gt 0 ]; then
    echo -e "\n⚠️  Remaining temporary files:"
    ls -1 *.py *.sh *.sql *.html 2>/dev/null | grep -E "^[A-Z_]"
    echo ""
    echo "Review these files manually to determine if they should be deleted."
fi

echo -e "\n📚 Documentation files are preserved."
echo "Next: Commit cleanup changes and test on production."
