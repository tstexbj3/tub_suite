import frappe
from frappe import _
from datetime import datetime, timedelta

def get_maintenance_status(maintenance_doc):
    """
    Determine maintenance status based on due date and completion
    Returns: Draft, Pending, Overdue, Completed, Cancelled
    """
    if maintenance_doc.docstatus == 0:
        return "Draft"
    elif maintenance_doc.docstatus == 2:
        return "Cancelled"
    elif maintenance_doc.status == "Completed":
        return "Completed"
    elif maintenance_doc.due_date:
        due_date = frappe.utils.getdate(maintenance_doc.due_date)
        today = frappe.utils.today()
        if due_date < frappe.utils.getdate(today):
            return "Overdue"
        else:
            return "Pending"
    return "Pending"

def calculate_next_maintenance_date(last_date, frequency):
    """
    Calculate next maintenance date based on frequency
    frequency: Daily, Weekly, Monthly, Quarterly, Half-Yearly, Yearly
    """
    last_date = frappe.utils.getdate(last_date)
    
    frequency_map = {
        "Daily": 1,
        "Weekly": 7,
        "Monthly": 30,
        "Quarterly": 90,
        "Half-Yearly": 180,
        "Yearly": 365
    }
    
    days = frequency_map.get(frequency, 30)
    return frappe.utils.add_days(last_date, days)

def validate_checklist_completion(checklist_items):
    """
    Validate if all mandatory checklist items are completed
    Returns: (is_complete, missing_items)
    """
    missing_items = []
    
    for item in checklist_items:
        if item.is_mandatory and not item.is_completed:
            missing_items.append(item.item_description)
    
    return (len(missing_items) == 0, missing_items)

def get_user_role_profile():
    """
    Get current user's role profile for permission checks
    """
    user = frappe.session.user
    roles = frappe.get_roles(user)
    
    return {
        "user": user,
        "roles": roles,
        "is_inspector": "Maintenance Inspector" in roles,
        "is_manager": "Maintenance Manager" in roles,
        "is_admin": "System Manager" in roles or "Administrator" in roles
    }

def send_notification(recipients, subject, message, doctype=None, docname=None):
    """
    Send email and system notification to recipients
    """
    # System notification
    for recipient in recipients:
        notification = frappe.new_doc("Notification Log")
        notification.subject = subject
        notification.email_content = message
        notification.for_user = recipient
        notification.document_type = doctype
        notification.document_name = docname
        notification.insert(ignore_permissions=True)
    
    # Email notification
    frappe.sendmail(
        recipients=recipients,
        subject=subject,
        message=message,
        reference_doctype=doctype,
        reference_name=docname
    )

def format_checklist_for_print(checklist_items):
    """
    Format checklist items for print/PDF output
    """
    html = "<table class='table table-bordered'>"
    html += "<thead><tr><th>Item</th><th>Status</th><th>Remarks</th></tr></thead>"
    html += "<tbody>"
    
    for item in checklist_items:
        status = "✓ Completed" if item.is_completed else "○ Pending"
        html += f"<tr><td>{item.item_description}</td><td>{status}</td><td>{item.remarks or ''}</td></tr>"
    
    html += "</tbody></table>"
    return html
