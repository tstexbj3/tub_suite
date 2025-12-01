# Copyright (c) 2024, Tipubon International Co.,Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _

@frappe.whitelist()
def get_asset_details(asset_name):
    """
    Get comprehensive asset details for inspector portal
    Includes: basic info, photos, pending maintenance tasks
    """
    user_roles = frappe.get_roles()
    allowed_roles = ["Maintenance Inspector", "Maintenance Manager", "Maintenance Engineer"]
    
    if not any(role in user_roles for role in allowed_roles):
        frappe.throw(_("Access denied"))
    
    # Get asset
    asset = frappe.get_doc("Asset", asset_name)
    
    # Get all attachments (photos)
    attachments = frappe.get_all("File",
        filters={
            "attached_to_doctype": "Asset",
            "attached_to_name": asset_name
        },
        fields=["file_url", "file_name", "creation"]
    )
    
    # Get pending maintenance tasks
    pending_tasks = get_pending_maintenance_tasks(asset_name)
    
    return {
        "asset_name": asset.name,
        "asset_title": asset.asset_name,
        "asset_category": asset.asset_category,
        "location": asset.location,
        "status": asset.status,
        "item_code": asset.item_code if hasattr(asset, "item_code") else None,
        "purchase_date": asset.purchase_date if hasattr(asset, "purchase_date") else None,
        "attachments": attachments,
        "pending_tasks": pending_tasks
    }

def get_pending_maintenance_tasks(asset_name):
    """
    Get pending maintenance schedules for asset
    """
    schedules = frappe.get_all("Maintenance Schedule",
        filters={
            "asset": asset_name,
            "status": ["in", ["Scheduled", "Active"]]
        },
        fields=["name", "maintenance_type", "next_due_date", "priority", "assigned_to"],
        order_by="next_due_date asc"
    )
    
    return schedules

@frappe.whitelist()
def get_asset_history(asset_name):
    """
    Get maintenance history for asset
    Uses ignore_permissions but validates user access
    """
    user_roles = frappe.get_roles()
    allowed_roles = ["Maintenance Inspector", "Maintenance Manager", "Maintenance Engineer"]
    
    if not any(role in user_roles for role in allowed_roles):
        frappe.throw(_("Access denied"))
    
    # Temporarily bypass permissions to fetch history
    frappe.flags.ignore_permissions = True
    
    logs = frappe.get_all("Maintenance Log",
        filters={"asset": asset_name, "docstatus": 1},
        fields=["name", "completion_date", "performed_by", "status", "maintenance_type", 
                "completion_percentage", "findings"],
        order_by="completion_date desc",
        limit=20
    )
    
    frappe.flags.ignore_permissions = False
    
    return logs

@frappe.whitelist()
def generate_qr_code(doc):
    """
    Generate QR code for asset (placeholder - integrates with QR Foundry)
    """
    frappe.msgprint(_("QR Code generation integrated with QR Foundry"))
    return True

@frappe.whitelist()
def get_asset_qr_code(asset_name):
    """
    Get QR code URL for asset
    """
    qr_doc = frappe.get_all("QR Code",
        filters={
            "reference_doctype": "Asset",
            "reference_name": asset_name
        },
        fields=["name", "token", "qr_code_image"],
        limit=1
    )
    
    if qr_doc and len(qr_doc) > 0:
        return {
            "qr_code_url": qr_doc[0].qr_code_image,
            "token": qr_doc[0].token
        }
    
    return None
