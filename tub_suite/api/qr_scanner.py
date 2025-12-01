# Copyright (c) 2024, Tipubon International Co.,Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json

@frappe.whitelist(allow_guest=True)
def scan_qr(token):
    """
    QR Code routing with role-based access control
    """
    
    # Decode token to get asset
    asset_name = validate_qr_token(token)
    
    if not asset_name:
        frappe.throw(_("Invalid QR code"))
    
    # Check if user is logged in
    if frappe.session.user == "Guest":
        return {
            "redirect": True,
            "url": "/login?redirect-to=/maintenance/scan/" + token
        }
    
    # Get user roles
    user_roles = frappe.get_roles()
    
    # Route based on role
    if "Maintenance Inspector" in user_roles:
        return {
            "redirect": True,
            "url": "/maintenance/asset/" + asset_name + "?token=" + token
        }
    elif "Maintenance Manager" in user_roles or "Maintenance Engineer" in user_roles:
        return {
            "redirect": True,
            "url": "/app/asset/" + asset_name
        }
    else:
        frappe.throw(_("Access denied. Required roles: Maintenance Inspector, Manager, or Engineer"))

def validate_qr_token(token):
    """
    Validate QR token and return asset name
    """
    try:
        qr_doc = frappe.get_all("QR Code", 
            filters={"token": token}, 
            fields=["reference_doctype", "reference_name"],
            limit=1)
        
        if qr_doc and len(qr_doc) > 0:
            if qr_doc[0].reference_doctype == "Asset":
                return qr_doc[0].reference_name
        
        if frappe.db.exists("Asset", token):
            return token
        
        return None
    except Exception as e:
        frappe.log_error("QR Token validation error: " + str(e))
        return None

@frappe.whitelist()
def get_asset_from_qr(token):
    """
    Get asset details from QR token
    """
    asset_name = validate_qr_token(token)
    
    if not asset_name:
        frappe.throw(_("Invalid QR code"))
    
    user_roles = frappe.get_roles()
    allowed_roles = ["Maintenance Inspector", "Maintenance Manager", "Maintenance Engineer"]
    
    if not any(role in user_roles for role in allowed_roles):
        frappe.throw(_("Access denied"))
    
    asset = frappe.get_doc("Asset", asset_name)
    
    return {
        "asset_name": asset.name,
        "asset_title": asset.asset_name,
        "asset_category": asset.asset_category,
        "location": asset.location,
        "status": asset.status,
        "image": asset.image if hasattr(asset, "image") else None
    }
