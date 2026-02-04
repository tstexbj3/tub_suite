"""
Asset Maintenance Override

Customizations for Asset Maintenance DocType to support Tub Suite workflows
"""

import frappe
from frappe import _


def validate_asset_maintenance(doc, method):
    """
    Override ERPNext's validation to allow submitting Asset Maintenance with Planned tasks.

    Standard ERPNext requires all tasks to be Completed/Cancelled before submission,
    which doesn't work for ongoing preventive maintenance schedules.

    This override allows submission with Planned tasks so the schedule becomes active
    and ERPNext's scheduled job can update maintenance_status from Planned -> Overdue.
    """
    # Allow submission with Planned tasks - no validation needed
    # The scheduled job will manage task status once submitted
    pass


def on_submit_asset_maintenance(doc, method):
    """
    After Asset Maintenance is submitted, ensure next_due_date is set for all tasks.
    """
    from frappe.utils import add_days, add_months, getdate, today

    for task in doc.get("asset_maintenance_tasks", []):
        # If task doesn't have next_due_date, calculate it based on periodicity
        if not task.next_due_date:
            start_date = getdate(doc.get("maintenance_start_date") or today())

            # Calculate next due date based on periodicity
            if task.periodicity == "Daily":
                task.next_due_date = add_days(start_date, 1)
            elif task.periodicity == "Weekly":
                task.next_due_date = add_days(start_date, 7)
            elif task.periodicity == "Monthly":
                task.next_due_date = add_months(start_date, 1)
            elif task.periodicity == "Quarterly":
                task.next_due_date = add_months(start_date, 3)
            elif task.periodicity == "Half-yearly":
                task.next_due_date = add_months(start_date, 6)
            elif task.periodicity == "Yearly":
                task.next_due_date = add_months(start_date, 12)
            elif task.periodicity == "2 Yearly":
                task.next_due_date = add_months(start_date, 24)
            elif task.periodicity == "3 Yearly":
                task.next_due_date = add_months(start_date, 36)
            else:
                # Default to 30 days if periodicity not recognized
                task.next_due_date = add_days(start_date, 30)

    # Save changes to child table
    doc.save()
