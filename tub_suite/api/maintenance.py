# Copyright (c) 2024, Tipubon International Co.,Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from tub_suite.utils import send_notification

@frappe.whitelist()
def get_pending_inspections(user=None):
    """
    Get pending maintenance inspections assigned to user
    """
    if not user:
        user = frappe.session.user
    
    logs = frappe.get_all("Maintenance Log",
        filters={
            "performed_by": user,
            "status": ["in", ["Draft", "Pending", "In Progress"]],
            "docstatus": 0
        },
        fields=["name", "asset", "asset_name", "due_date", "status", 
                "completion_percentage", "maintenance_type"],
        order_by="due_date asc"
    )
    
    return logs

@frappe.whitelist()
def create_repair_request(asset_name, repair_type, description, priority="Medium"):
    """
    Create Asset Repair request from inspector
    Simplified interface for inspectors
    """
    user_roles = frappe.get_roles()
    
    if "Maintenance Inspector" not in user_roles:
        frappe.throw(_("Only Maintenance Inspectors can create repair requests"))
    
    # Create Asset Repair document
    repair_doc = frappe.get_doc({
        "doctype": "Asset Repair",
        "asset": asset_name,
        "failure_description": description,
        "repair_status": "Pending",
        "error_description": repair_type + ": " + description
    })
    
    repair_doc.insert(ignore_permissions=True)
    
    # Notify engineering team
    notify_repair_request(repair_doc.name, asset_name)
    
    return {
        "success": True,
        "repair_id": repair_doc.name,
        "message": _("Repair request submitted successfully")
    }

def notify_repair_request(repair_id, asset_name):
    """
    Send notification to engineering team about new repair request
    """
    # Get users with Maintenance Manager or Engineer roles
    recipients = get_maintenance_team_emails()
    
    subject = _("New Repair Request: {0}").format(asset_name)
    message = _("A new repair request has been submitted for asset {0}. Please review: {1}").format(
        asset_name, 
        frappe.utils.get_url_to_form("Asset Repair", repair_id)
    )
    
    # Send email
    if recipients:
        frappe.sendmail(
            recipients=recipients,
            subject=subject,
            message=message
        )
    
    # Create ToDo for engineering team
    for recipient in recipients:
        todo = frappe.get_doc({
            "doctype": "ToDo",
            "description": message,
            "reference_type": "Asset Repair",
            "reference_name": repair_id,
            "allocated_to": recipient,
            "priority": "Medium"
        })
        todo.insert(ignore_permissions=True)

def get_maintenance_team_emails():
    """
    Get email addresses of users with maintenance management roles
    """
    users = frappe.get_all("Has Role",
        filters={
            "role": ["in", ["Maintenance Manager", "Maintenance Engineer"]]
        },
        fields=["parent"],
        distinct=True
    )
    
    emails = []
    for user in users:
        user_email = frappe.db.get_value("User", user.parent, "email")
        if user_email:
            emails.append(user_email)
    
    return emails

@frappe.whitelist()
def send_overdue_notifications():
    """
    Daily scheduled task: Send notifications for overdue maintenance
    """
    today = frappe.utils.today()
    
    overdue_logs = frappe.get_all("Maintenance Log",
        filters={
            "due_date": ["<", today],
            "status": ["in", ["Pending", "In Progress"]],
            "docstatus": 0
        },
        fields=["name", "asset", "asset_name", "due_date", "performed_by"]
    )
    
    for log in overdue_logs:
        subject = _("Overdue Maintenance: {0}").format(log.asset_name)
        message = _("Maintenance task {0} for asset {1} is overdue (Due: {2})").format(
            log.name, log.asset_name, log.due_date
        )
        
        if log.performed_by:
            send_notification(
                recipients=[log.performed_by],
                subject=subject,
                message=message,
                doctype="Maintenance Log",
                docname=log.name
            )

@frappe.whitelist()
def generate_weekly_report():
    """
    Weekly scheduled task: Generate maintenance summary report
    """
    # Placeholder for weekly report generation
    pass
