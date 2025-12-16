"""
Fix tasks that are locked due to deleted logs
When a maintenance log is deleted, the task's last_completion_date remains set,
causing the task to appear as completed even though there's no log.
"""

import frappe
from frappe.utils import nowdate

def fix_orphaned_task_completions():
    """
    Find tasks with last_completion_date = today but no corresponding log
    and clear the completion date
    """
    today = nowdate()

    # Get all tasks completed today
    tasks = frappe.db.sql("""
        SELECT
            amt.name,
            amt.maintenance_task,
            amt.last_completion_date,
            amt.parent as maintenance_doc
        FROM `tabAsset Maintenance Task` amt
        WHERE amt.last_completion_date = %s
    """, (today,), as_dict=True)

    fixed_count = 0

    for task in tasks:
        # Check if there's a log for this task today
        log_exists = frappe.db.exists("Asset Maintenance Log", {
            "task": task.name,
            "completion_date": today
        })

        if not log_exists:
            # No log exists - clear the completion date
            frappe.db.set_value(
                "Asset Maintenance Task",
                task.name,
                "last_completion_date",
                None,
                update_modified=False
            )
            fixed_count += 1
            print(f"✓ Cleared completion date for task: {task.maintenance_task} (No log found)")

    frappe.db.commit()

    return {
        "success": True,
        "tasks_checked": len(tasks),
        "tasks_fixed": fixed_count,
        "message": f"Fixed {fixed_count} orphaned task(s) out of {len(tasks)} checked"
    }
