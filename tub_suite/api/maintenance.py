# Copyright (c) 2024, Tipubon International Co.,Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import date, timedelta


def send_overdue_notifications():
    """
    Scheduled task to send notifications for overdue maintenance tasks.
    Runs hourly via scheduler_events in hooks.py
    """
    try:
        today = date.today()

        # Get all active asset maintenance records
        maintenance_records = frappe.get_all("Asset Maintenance",
            filters={"docstatus": ["<", 2]},
            fields=["name", "asset_name"]
        )

        overdue_tasks = []

        for maintenance in maintenance_records:
            # Get tasks for this maintenance
            tasks = frappe.get_all("Asset Maintenance Task",
                filters={"parent": maintenance.name},
                fields=["name", "maintenance_task", "next_due_date", "assign_to"]
            )

            for task in tasks:
                if task.next_due_date and task.next_due_date < today:
                    overdue_tasks.append({
                        "maintenance": maintenance.name,
                        "asset": maintenance.asset_name,
                        "task": task.maintenance_task,
                        "due_date": task.next_due_date,
                        "assign_to": task.assign_to
                    })

        if not overdue_tasks:
            return {"success": True, "message": "No overdue tasks found"}

        # Group by assignee
        by_assignee = {}
        for task in overdue_tasks:
            assignee = task.get("assign_to") or "Maintenance Manager"
            if assignee not in by_assignee:
                by_assignee[assignee] = []
            by_assignee[assignee].append(task)

        # Send notifications
        notifications_sent = 0
        for assignee, tasks in by_assignee.items():
            try:
                # Get users with Maintenance Manager role if no specific assignee
                if assignee == "Maintenance Manager":
                    managers = frappe.get_all("Has Role",
                        filters={"role": "Maintenance Manager", "parenttype": "User"},
                        fields=["parent"],
                        distinct=True
                    )
                    recipients = [m.parent for m in managers if m.parent not in ["Administrator", "Guest"]]
                else:
                    recipients = [assignee]

                if not recipients:
                    continue

                # Build email content
                task_list = "<ul>"
                for t in tasks:
                    days_overdue = (today - t["due_date"]).days
                    task_list += f"<li><strong>{t['asset']}</strong>: {t['task']} (overdue by {days_overdue} days)</li>"
                task_list += "</ul>"

                subject = f"[TUB Suite] {len(tasks)} Overdue Maintenance Task(s)"
                message = f"""
                <h3>Overdue Maintenance Tasks</h3>
                <p>The following maintenance tasks are overdue and require attention:</p>
                {task_list}
                <p><a href="{frappe.utils.get_url()}/app/asset-maintenance">View Asset Maintenance</a></p>
                """

                frappe.sendmail(
                    recipients=recipients,
                    subject=subject,
                    message=message
                )
                notifications_sent += 1

            except Exception as e:
                frappe.log_error(f"Failed to send notification to {assignee}: {str(e)}",
                               "Overdue Notification Error")

        return {
            "success": True,
            "overdue_count": len(overdue_tasks),
            "notifications_sent": notifications_sent
        }

    except Exception as e:
        frappe.log_error(str(e), "Send Overdue Notifications Error")
        return {"success": False, "error": str(e)}
