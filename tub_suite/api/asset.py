# Copyright (c) 2024, Tipubon International Co.,Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json
from datetime import datetime, timedelta, date

# ============================================================================
# SECURITY UTILITIES
# ============================================================================

def check_rate_limit(action, max_requests=50, window_seconds=60):
    """
    Rate limiting to prevent brute force attacks

    Args:
        action: Action identifier (e.g., "search_assets", "submit_checklist")
        max_requests: Maximum requests allowed in the time window
        window_seconds: Time window in seconds

    Returns:
        bool: True if within limit, raises exception if exceeded
    """
    user = frappe.session.user
    cache_key = f"rate_limit:{action}:{user}"

    # Get current count (convert from bytes to int)
    count = frappe.cache().get(cache_key)
    if count is None:
        count = 0
    else:
        # Redis cache returns bytes, convert to int
        count = int(count) if isinstance(count, (bytes, str)) else count

    if count >= max_requests:
        log_security_event("RATE_LIMIT_EXCEEDED", {
            "action": action,
            "count": count,
            "max_requests": max_requests
        })
        frappe.throw(
            _("Too many requests. Please wait a moment before trying again."),
            frappe.TooManyRequestsError
        )

    # Increment counter with expiry
    frappe.cache().setex(cache_key, window_seconds, count + 1)
    return True

def log_security_event(event_type, details):
    """
    Log security-related events for audit trail

    Args:
        event_type: Type of event (e.g., "UNAUTHORIZED_ACCESS", "RATE_LIMIT_EXCEEDED")
        details: Dictionary of event details
    """
    try:
        frappe.get_doc({
            "doctype": "Error Log",
            "error": event_type,
            "method": details.get("method", ""),
            "error_message": json.dumps({
                "user": frappe.session.user,
                "ip_address": frappe.local.request_ip if hasattr(frappe.local, 'request_ip') else None,
                "timestamp": str(datetime.now()),
                **details
            }, indent=2)
        }).insert(ignore_permissions=True)
    except Exception as e:
        frappe.log_error(f"Failed to log security event: {str(e)}", "Security Logging Error")

def validate_maintenance_role():
    """
    Check if user has maintenance-related role

    Returns:
        bool: True if authorized, raises exception otherwise
    """
    user_roles = frappe.get_roles()
    allowed_roles = [
        "Maintenance Inspector",
        "Maintenance Manager",
        "Maintenance Engineer",
        "Maintenance User",
        "Engineering Team"
    ]

    if not any(role in user_roles for role in allowed_roles):
        log_security_event("UNAUTHORIZED_ACCESS", {
            "reason": "Missing maintenance role",
            "user_roles": user_roles
        })
        frappe.throw(_("Access denied. Maintenance role required."))

    return True

def sanitize_input(value, max_length=500):
    """
    Sanitize user input to prevent injection attacks

    Args:
        value: Input value to sanitize
        max_length: Maximum allowed length

    Returns:
        str: Sanitized value
    """
    if not value:
        return value

    # Convert to string and limit length
    sanitized = str(value)[:max_length]

    return sanitized

def log_asset_access(asset_name, action, additional_data=None):
    """
    Log asset access for audit trail

    Args:
        asset_name: Asset being accessed
        action: Action performed (view, search, update, etc.)
        additional_data: Additional context data
    """
    try:
        data = {
            "asset": asset_name,
            "action": action,
            "user": frappe.session.user,
            "ip_address": frappe.local.request_ip if hasattr(frappe.local, 'request_ip') else None,
            "timestamp": str(datetime.now())
        }

        if additional_data:
            data.update(additional_data)

        frappe.get_doc({
            "doctype": "Activity Log",
            "subject": f"Asset {action}: {asset_name}",
            "content": json.dumps(data, indent=2),
            "user": frappe.session.user,
            "ip_address": data.get("ip_address")
        }).insert(ignore_permissions=True)
    except Exception as e:
        frappe.log_error(f"Failed to log asset access: {str(e)}", "Asset Access Logging Error")

# ============================================================================
# HELPER FUNCTIONS - NEW
# ============================================================================

def get_active_repair(asset_name):
    """
    Get active repair (Pending or In Progress) for an asset

    Args:
        asset_name: Asset name

    Returns:
        dict: Active repair details or None
    """
    try:
        repairs = frappe.get_all("Asset Repair",
            filters={
                "asset": asset_name,
                "repair_status": ["in", ["Pending", "In Progress"]],
                "docstatus": ["<", 2]
            },
            fields=["name", "failure_date", "description", "repair_status"],
            order_by="failure_date desc",
            limit=1
        )
        return repairs[0] if repairs else None
    except Exception as e:
        frappe.log_error(str(e), "Get Active Repair Error")
        return None

def get_asset_history(asset_name, limit=10):
    """
    Get combined maintenance and repair history for an asset

    Args:
        asset_name: Asset name
        limit: Maximum number of history items to return

    Returns:
        list: Combined history items sorted by date (newest first)
    """
    try:
        history = []

        # Get maintenance inspections (grouped by date)
        inspections = frappe.db.sql("""
            SELECT
                DATE(completion_date) as date,
                COUNT(*) as tasks_completed,
                MIN(creation) as time,
                GROUP_CONCAT(DISTINCT owner) as inspectors
            FROM `tabAsset Maintenance Log`
            WHERE asset_maintenance IN (
                SELECT name FROM `tabAsset Maintenance`
                WHERE asset_name = %s
            )
            AND completion_date IS NOT NULL
            GROUP BY DATE(completion_date)
            ORDER BY date DESC
            LIMIT %s
        """, (asset_name, limit), as_dict=True)

        for insp in inspections:
            history.append({
                "type": "inspection",
                "date": str(insp.date),
                "time": str(insp.time),
                "tasks_completed": insp.tasks_completed,
                "inspectors": insp.inspectors,
                "icon": "📋"
            })

        # Get repairs
        repairs = frappe.get_all("Asset Repair",
            filters={"asset": asset_name},
            fields=["name", "failure_date", "completion_date", "description", "repair_status", "owner"],
            order_by="failure_date desc",
            limit=limit
        )

        for repair in repairs:
            history.append({
                "type": "repair",
                "date": str(repair.failure_date),
                "description": repair.description,
                "status": repair.repair_status,
                "repair_name": repair.name,
                "completion_date": str(repair.completion_date) if repair.completion_date else None,
                "owner": repair.owner,
                "icon": "🔧"
            })

        # Sort by date (newest first)
        history.sort(key=lambda x: x["date"], reverse=True)

        return history[:limit]
    except Exception as e:
        frappe.log_error(str(e), "Get Asset History Error")
        return []

# ============================================================================
# API ENDPOINTS (ENHANCED WITH SECURITY)
# ============================================================================

@frappe.whitelist(allow_guest=False)
def search_assets(query):
    """
    Search for multiple assets by code - returns up to 10 results

    Security features:
    - Rate limiting (50 searches per minute)
    - Role validation
    - Input sanitization
    - Audit logging
    """
    # Security checks
    check_rate_limit("search_assets", max_requests=50, window_seconds=60)
    validate_maintenance_role()

    # Sanitize input
    asset_code = sanitize_input(query, max_length=100)

    if not asset_code or len(asset_code) < 2:
        return {
            "success": False,
            "message": "Search term must be at least 2 characters"
        }

    try:
        # Search by item code or asset name (case insensitive)
        assets = frappe.db.sql("""
            SELECT name, asset_name, item_code, asset_category, location, status
            FROM `tabAsset`
            WHERE LOWER(item_code) LIKE LOWER(%s)
               OR LOWER(name) LIKE LOWER(%s)
               OR LOWER(asset_name) LIKE LOWER(%s)
            ORDER BY name
            LIMIT 10
        """, (f"%{asset_code}%", f"%{asset_code}%", f"%{asset_code}%"), as_dict=True)

        # Log the search
        log_asset_access("SEARCH", "search", {
            "search_term": asset_code,
            "results_count": len(assets)
        })

        return {
            "success": True,
            "assets": assets,
            "count": len(assets)
        }
    except Exception as e:
        frappe.log_error(str(e), "Asset Search Error")
        return {
            "success": False,
            "message": "An error occurred during search"
        }

@frappe.whitelist(allow_guest=False)
def get_asset_with_checklist(asset_name):
    """
    Get asset details including maintenance checklist

    IMPROVEMENTS:
    - Issue #3: Detects if asset is unavailable (Out of Order, etc.)
    - Shows active repair information
    - Hides checklist if asset is unavailable

    Security features:
    - Rate limiting (100 requests per minute)
    - Role validation
    - Permission checking
    - Audit logging
    """
    # Security checks
    check_rate_limit("get_asset_with_checklist", max_requests=100, window_seconds=60)
    validate_maintenance_role()

    # Sanitize input
    asset_name = sanitize_input(asset_name, max_length=200)

    # Check if user has read permission for Asset
    if not frappe.has_permission("Asset", "read", asset_name):
        log_security_event("PERMISSION_DENIED", {
            "method": "get_asset_with_checklist",
            "asset": asset_name,
            "permission": "read"
        })
        frappe.throw(_("You do not have permission to view this asset"))

    try:
        # Get asset
        asset = frappe.get_doc("Asset", asset_name)

        # Log access
        log_asset_access(asset_name, "view_checklist")

        # Get asset photo
        photo = None
        if asset.get("image"):
            photo = asset.get("image")
        else:
            attachments = frappe.get_all("File",
                filters={
                    "attached_to_doctype": "Asset",
                    "attached_to_name": asset_name,
                    "is_private": 0
                },
                fields=["file_url"],
                order_by="creation asc",
                limit=1
            )
            if attachments:
                photo = attachments[0].file_url

        # IMPROVEMENT #3: Check if asset is unavailable
        unavailable_statuses = ["Out of Order", "Scrapped", "Sold", "In Maintenance"]
        is_unavailable = asset.status in unavailable_statuses
        active_repair = None

        if is_unavailable:
            active_repair = get_active_repair(asset_name)

        # Get active asset maintenance with tasks
        maintenance_records = frappe.get_all("Asset Maintenance",
            filters={
                "asset_name": asset_name,
                "docstatus": ["<", 2]
            },
            fields=["name"],
            limit=1
        )

        checklist_items = []

        # IMPROVEMENT #3: Only show checklist if asset is available
        if maintenance_records and not is_unavailable:
            maintenance = frappe.get_doc("Asset Maintenance", maintenance_records[0].name)
            if hasattr(maintenance, "asset_maintenance_tasks"):
                today = date.today()

                for task in maintenance.asset_maintenance_tasks:
                    next_due_date = None
                    last_completion_date = None
                    is_overdue = False
                    is_checkable = True
                    status_badge = None
                    completed_by = None
                    completed_time = None

                    # Get latest completion log
                    logs = frappe.get_all("Asset Maintenance Log",
                        filters={
                            "asset_maintenance": maintenance.name,
                            "task": task.name
                        },
                        fields=["completion_date", "owner", "creation"],
                        order_by="completion_date desc",
                        limit=1
                    )

                    if logs and logs[0].completion_date:
                        last_completion_date = logs[0].completion_date

                        # IMPROVEMENT #1: Check if completed today (same day grace period)
                        if last_completion_date == today:
                            is_checkable = False
                            completed_by = logs[0].owner
                            completed_time = logs[0].creation
                            status_badge = {
                                "text": "เสร็จวันนี้",
                                "color": "blue",
                                "type": "completed_today"
                            }
                        else:
                            # Calculate next due date
                            from dateutil.relativedelta import relativedelta

                            periodicity_map = {
                                "Daily": relativedelta(days=1),
                                "Weekly": relativedelta(weeks=1),
                                "Monthly": relativedelta(months=1),
                                "Quarterly": relativedelta(months=3),
                                "Half-yearly": relativedelta(months=6),
                                "Yearly": relativedelta(years=1),
                                "2 Yearly": relativedelta(years=2),
                                "3 Yearly": relativedelta(years=3)
                            }

                            if task.periodicity in periodicity_map:
                                next_due_date = last_completion_date + periodicity_map[task.periodicity]
                    elif task.start_date:
                        next_due_date = task.start_date

                    # Determine status badge
                    if next_due_date and not status_badge:
                        diff_days = (next_due_date - today).days

                        if diff_days < 0:
                            is_overdue = True
                            status_badge = {
                                "text": "เกินกำหนด",
                                "color": "red",
                                "type": "overdue"
                            }
                        elif diff_days == 0:
                            status_badge = {
                                "text": "ถึงกำหนดวันนี้",
                                "color": "orange",
                                "type": "due_today"
                            }
                        elif diff_days <= 7:
                            status_badge = {
                                "text": "ใกล้ถึงกำหนด",
                                "color": "orange",
                                "type": "due_soon"
                            }
                        else:
                            is_checkable = False  # Not due yet
                            status_badge = {
                                "text": f"ครั้งถัดไป {next_due_date.strftime('%d/%m/%Y')}",
                                "color": "gray",
                                "type": "not_due_yet"
                            }

                    checklist_items.append({
                        "name": task.name,
                        "item_description": task.maintenance_task,
                        "periodicity": task.periodicity or "",
                        "maintenance_type": task.maintenance_type or "",
                        "maintenance_status": task.maintenance_status or "",
                        "start_date": str(task.start_date) if task.start_date else "",
                        "end_date": str(task.end_date) if task.end_date else "",
                        "last_completion_date": str(last_completion_date) if last_completion_date else "",
                        "next_due_date": str(next_due_date) if next_due_date else "",
                        "is_overdue": is_overdue,
                        "is_mandatory": 1,
                        "is_completed": 0,
                        "is_checkable": is_checkable,  # NEW
                        "status_badge": status_badge,  # NEW
                        "completed_by": completed_by,  # NEW
                        "completed_time": str(completed_time) if completed_time else None  # NEW
                    })

        result = {
            "success": True,
            "asset": {
                "name": asset.name,
                "asset_name": asset.asset_name,
                "item_code": asset.item_code,
                "asset_category": asset.asset_category,
                "location": asset.location,
                "status": asset.status,
                "photo": photo
            },
            "checklist": checklist_items,
            "unavailable": is_unavailable,  # NEW
            "unavailable_reason": asset.status if is_unavailable else None,  # NEW
            "active_repair": active_repair  # NEW
        }

        return result
    except Exception as e:
        frappe.log_error(str(e), "Get Asset Checklist Error")
        return {
            "success": False,
            "message": "An error occurred while loading asset details"
        }

@frappe.whitelist(allow_guest=False)
def submit_checklist(asset_name, checklist_data, issue_description=None):
    """
    Submit completed checklist

    Security features:
    - Rate limiting (20 submissions per minute)
    - Role validation
    - Input validation and sanitization
    - Audit logging
    - Transaction safety
    """
    # Security checks
    check_rate_limit("submit_checklist", max_requests=20, window_seconds=60)
    validate_maintenance_role()

    # Sanitize inputs
    asset_name = sanitize_input(asset_name, max_length=200)
    if issue_description:
        issue_description = sanitize_input(issue_description, max_length=2000)

    # Validate checklist data
    try:
        checklist = json.loads(checklist_data) if isinstance(checklist_data, str) else checklist_data
        if not isinstance(checklist, list):
            frappe.throw(_("Invalid checklist data format"))
    except (json.JSONDecodeError, TypeError):
        frappe.throw(_("Invalid checklist data"))

    try:
        # Get asset maintenance record
        maintenance_records = frappe.get_all("Asset Maintenance",
            filters={"asset_name": asset_name, "docstatus": ["<", 2]},
            fields=["name"],
            limit=1
        )

        result = {"success": True}
        completed_tasks = []

        # Create maintenance log for each completed task
        if maintenance_records:
            maintenance_name = maintenance_records[0].name

            for item in checklist:
                if item.get("is_completed"):
                    log = frappe.get_doc({
                        "doctype": "Asset Maintenance Log",
                        "asset_maintenance": maintenance_name,
                        "task": item.get("name"),
                        "maintenance_status": "Completed",
                        "completion_date": frappe.utils.nowdate(),
                        "description": f"Mobile inspection: {item.get('item_description', '')}"
                    })
                    log.insert(ignore_permissions=True)
                    completed_tasks.append(log.name)

            result["completed_tasks"] = completed_tasks
            result["total_completed"] = len(completed_tasks)

        # Create asset repair if issue reported
        if issue_description and issue_description.strip():
            try:
                repair = frappe.get_doc({
                    "doctype": "Asset Repair",
                    "asset": asset_name,
                    "failure_date": frappe.utils.nowdate(),
                    "description": issue_description,
                    "repair_status": "Pending"
                })
                repair.insert(ignore_permissions=True)
                frappe.db.commit()
                result["repair_name"] = repair.name

                # Send notification
                try:
                    send_repair_notification(repair, asset_name, issue_description, frappe.session.user)
                except Exception as notif_error:
                    frappe.log_error(f"Notification failed: {str(notif_error)}", "Repair Notification Error")
            except Exception as repair_error:
                frappe.log_error(str(repair_error), "Asset Repair Creation Failed")
                result["repair_error"] = str(repair_error)

        # Log checklist submission
        log_asset_access(asset_name, "submit_checklist", {
            "completed_tasks": len(completed_tasks),
            "issue_reported": bool(issue_description and issue_description.strip())
        })

        return result
    except Exception as e:
        frappe.log_error(str(e), "Submit Checklist Error")
        frappe.db.rollback()
        return {"success": False, "message": "An error occurred while submitting checklist"}

@frappe.whitelist(allow_guest=False)
def get_maintenance_history(asset_name):
    """
    Get maintenance history for an asset (last 10 items)

    IMPROVEMENT #4: New endpoint for history view

    Returns combined inspection and repair history
    """
    # Security checks
    check_rate_limit("get_maintenance_history", max_requests=100, window_seconds=60)
    validate_maintenance_role()

    # Sanitize input
    asset_name = sanitize_input(asset_name, max_length=200)

    # Check permission
    if not frappe.has_permission("Asset", "read", asset_name):
        frappe.throw(_("You do not have permission to view this asset"))

    try:
        history = get_asset_history(asset_name, limit=10)

        # Log access
        log_asset_access(asset_name, "view_history", {
            "history_items": len(history)
        })

        return {
            "success": True,
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        frappe.log_error(str(e), "Get Maintenance History Error")
        return {
            "success": False,
            "message": "An error occurred while loading history"
        }

def create_todo_for_engineers(repair_doc, asset_name, issue_description):
    """Create ToDo items for engineers when a repair is created"""
    try:
        # Get engineers with Engineering Team or Maintenance Engineer role
        engineers = frappe.get_all("Has Role",
            filters={"role": ["in", ["Maintenance Engineer", "Engineering Team"]], "parenttype": "User"},
            fields=["parent"],
            distinct=True
        )

        # Get managers too
        managers = frappe.get_all("Has Role",
            filters={"role": "Maintenance Manager", "parenttype": "User"},
            fields=["parent"],
            distinct=True
        )

        # Combine and deduplicate
        all_users = list(set([e.parent for e in engineers] + [m.parent for m in managers]))
        all_users = [u for u in all_users if u not in ["Administrator", "Guest"]]

        # Create ToDo for each user
        for user in all_users:
            todo = frappe.get_doc({
                "doctype": "ToDo",
                "allocated_to": user,
                "reference_type": "Asset Repair",
                "reference_name": repair_doc.name,
                "description": f"New repair request for {asset_name}: {issue_description[:100]}...",
                "priority": "High",
                "status": "Open"
            })
            todo.insert(ignore_permissions=True)

        frappe.db.commit()
        return len(all_users)
    except Exception as e:
        frappe.log_error(str(e)[:140], "ToDo Error")
        return 0

def send_repair_notification(repair_doc, asset_name, issue_description, inspector_email):
    """Send email notification to maintenance team and create ToDo items"""
    try:
        # First, create ToDo items for engineers
        create_todo_for_engineers(repair_doc, asset_name, issue_description)

        recipients = []

        managers = frappe.get_all("Has Role",
            filters={"role": "Maintenance Manager", "parenttype": "User"},
            fields=["parent"],
            distinct=True
        )
        recipients.extend([m.parent for m in managers])

        # Get engineers with either Maintenance Engineer or Engineering Team role
        engineers = frappe.get_all("Has Role",
            filters={"role": ["in", ["Maintenance Engineer", "Engineering Team"]], "parenttype": "User"},
            fields=["parent"],
            distinct=True
        )
        recipients.extend([e.parent for e in engineers])

        recipients = list(set(recipients))
        recipients = [r for r in recipients if r not in ["Administrator", "Guest"]]

        if not recipients:
            return
    except Exception as e:
        frappe.log_error(str(e)[:140], "Notification Error")
        return

    asset = frappe.get_doc("Asset", asset_name)
    inspector_name = frappe.db.get_value("User", inspector_email, "full_name") or inspector_email

    subject = f"🔧 New Repair Request: {asset.asset_name}"

    message = f"""
    <h3>New Asset Repair Request</h3>
    <p>A new repair request has been submitted from the mobile inspection portal.</p>
    <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
        <tr style="background: #f5f5f5;">
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Repair Request</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">{repair_doc.name}</td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Asset</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">{asset.asset_name} ({asset.name})</td>
        </tr>
        <tr style="background: #f5f5f5;">
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Item Code</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">{asset.item_code or 'N/A'}</td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Location</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">{asset.location or 'N/A'}</td>
        </tr>
        <tr style="background: #f5f5f5;">
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Reported By</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">{inspector_name}</td>
        </tr>
    </table>
    <h4>Problem Description:</h4>
    <p style="background: #fff3e0; padding: 15px; border-left: 4px solid #ff9800;">{issue_description}</p>
    <p style="margin-top: 20px;">
        <a href="{frappe.utils.get_url()}/app/asset-repair/{repair_doc.name}"
           style="background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
            View Repair Request
        </a>
    </p>
    """

    frappe.sendmail(
        recipients=recipients,
        subject=subject,
        message=message,
        reference_doctype="Asset Repair",
        reference_name=repair_doc.name
    )


# ============================================================================
# ASSET REPAIR SECURITY - Lock submitted repairs
# ============================================================================

# DISABLED: def validate_asset_repair_permissions(doc, method=None):
# DISABLED:     """
# DISABLED:     Security validation for Asset Repair documents
# DISABLED:     - Once submitted, only approval_status can be manually changed
# DISABLED:     - approval_time and approved_by are set server-side automatically
# DISABLED:     - Prevents any user (including managers) from editing repair details after submission
# DISABLED: 
# DISABLED:     Hook this via: doc_events in hooks.py
# DISABLED:     """
# DISABLED:     if doc.docstatus == 1:  # Document is submitted
# DISABLED:         # Get original document from database (bypass cache)
# DISABLED:         old_doc = frappe.db.get_value("Asset Repair", doc.name, "*", as_dict=True)
# DISABLED:         if not old_doc:
# DISABLED:             return
# DISABLED: 
# DISABLED:         # List of ALL fields that CANNOT be changed after submission
# DISABLED:         protected_fields = [
# DISABLED:             'asset', 'asset_name', 'failure_date', 'description',
# DISABLED:             'repair_status', 'completion_date', 'repair_cost',
# DISABLED:             'actions_performed', 'stock_consumption', 'capitalize_repair_cost',
# DISABLED:             'increase_in_asset_life', 'company', 'cost_center',
# DISABLED:             'project', 'purchase_invoice', 'total_repair_cost',
# DISABLED:             'downtime', 'naming_series'
# DISABLED:         ]
# DISABLED: 
# DISABLED:         # Check if any protected field was modified
# DISABLED:         for field in protected_fields:
# DISABLED:             old_value = old_doc.get(field)
# DISABLED:             new_value = doc.get(field)
# DISABLED: 
# DISABLED:             # Convert to strings for comparison to handle None values
# DISABLED:             if str(old_value or '') != str(new_value or ''):
# DISABLED:                 log_security_event("UNAUTHORIZED_FIELD_MODIFICATION", {
# DISABLED:                     "repair": doc.name,
# DISABLED:                     "field": field,
# DISABLED:                     "old_value": str(old_value),
# DISABLED:                     "new_value": str(new_value),
# DISABLED:                     "user": frappe.session.user
# DISABLED:                 })
# DISABLED:                 frappe.throw(
# DISABLED:                     _("Cannot modify {0} after submission. This repair request is locked.").format(
# DISABLED:                         frappe.bold(field.replace('_', ' ').title())
# DISABLED:                     ),
# DISABLED:                     frappe.PermissionError
# DISABLED:                 )
# DISABLED: 
# DISABLED:         # PROTECTED: Users cannot manually set approval_time or approved_by
# DISABLED:         if doc.get('approval_time') != old_doc.get('approval_time'):
# DISABLED:             if not doc.flags.auto_approval:  # Only allow if set programmatically
# DISABLED:                 frappe.throw(
# DISABLED:                     _("Approval Date & Time is automatically set by the system and cannot be modified manually."),
# DISABLED:                     frappe.PermissionError
# DISABLED:                 )
# DISABLED: 
# DISABLED:         if doc.get('approved_by') != old_doc.get('approved_by'):
# DISABLED:             if not doc.flags.auto_approval:  # Only allow if set programmatically
# DISABLED:                 frappe.throw(
# DISABLED:                     _("Approved By is automatically set by the system and cannot be modified manually."),
# DISABLED:                     frappe.PermissionError
# DISABLED:                 )
# DISABLED: 
# DISABLED:         # Auto-fill approval fields when status changes
# DISABLED:         if doc.get('approval_status') != old_doc.get('approval_status'):
# DISABLED:             if doc.get('approval_status') in ['Approved', 'Rejected']:
# DISABLED:                 # Set approval fields automatically with server data
# DISABLED:                 doc.flags.auto_approval = True
# DISABLED:                 doc.approval_time = frappe.utils.now()
# DISABLED:                 doc.approved_by = frappe.session.user
# DISABLED: 
# DISABLED: 
# DISABLED: @frappe.whitelist()
def approve_asset_repair(repair_name, approval_status):
    """
    Approve or reject an Asset Repair request
    - Only users with proper permissions can approve
    - Automatically sets server timestamp (unchangeable)
    - All other fields remain locked

    Args:
        repair_name: Name of the Asset Repair document
        approval_status: "Approved" or "Rejected"

    Returns:
        dict: Success message with approval details
    """
    check_rate_limit("approve_repair", max_requests=20, window_seconds=60)

    # Validate approval_status
    if approval_status not in ["Approved", "Rejected"]:
        frappe.throw(_("Invalid approval status. Must be 'Approved' or 'Rejected'."))

    # Get document
    doc = frappe.get_doc("Asset Repair", repair_name)

    # Check if user has permission to approve
    if not frappe.has_permission("Asset Repair", "write", doc):
        log_security_event("UNAUTHORIZED_APPROVAL_ATTEMPT", {
            "repair": repair_name,
            "user": frappe.session.user
        })
        frappe.throw(_("You do not have permission to approve this repair request."), frappe.PermissionError)

    # Check if already approved/rejected
    if doc.get('approval_status') and doc.get('approval_status') != 'Pending':
        frappe.throw(_("This repair request has already been {0}.").format(doc.approval_status.lower()))

    # Update with server timestamp (cannot be tampered)
    doc.approval_status = approval_status
    doc.approval_time = frappe.utils.now()  # Server timestamp
    doc.approved_by = frappe.session.user

    # Save with ignore permissions to allow the update
    doc.flags.ignore_validate_update_after_submit = True
    doc.save(ignore_permissions=True)

    frappe.db.commit()

    log_security_event("REPAIR_APPROVAL", {
        "repair": repair_name,
        "status": approval_status,
        "approved_by": frappe.session.user,
        "timestamp": doc.approval_time
    })

    return {
        "success": True,
        "message": _("Repair request {0} successfully.").format(approval_status.lower()),
        "approval_status": approval_status,
        "approval_time": doc.approval_time,
        "approved_by": doc.approved_by
    }


@frappe.whitelist()
def setup_client_script():
    """
    Add Client Script to Asset Repair for UI field locking
    This makes fields read-only in the UI when document is submitted
    """
    script_name = "Asset Repair - Lock Fields After Submit"

    # Check if script already exists
    existing = frappe.db.exists("Client Script", {"name": script_name})

    script_content = """
// Lock all fields except approval fields after submission
frappe.ui.form.on('Asset Repair', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
            // Lock all fields except approval-related fields
            const fields_to_lock = [
                'asset', 'failure_date', 'description', 'repair_status',
                'completion_date', 'repair_cost', 'actions_performed',
                'stock_consumption', 'capitalize_repair_cost',
                'increase_in_asset_life', 'company', 'cost_center',
                'project', 'purchase_invoice', 'stock_items',
                'approved_by', 'approval_time'
            ];

            // Approval fields that CAN be edited:
            // - approval_status
            // - approval_notes
            // - approval_signature

            fields_to_lock.forEach(function(fieldname) {
                frm.set_df_property(fieldname, 'read_only', 1);
            });

            // Add approval buttons
            if (!frm.doc.approval_status || frm.doc.approval_status === 'Pending') {
                frm.add_custom_button(__('Approve'), function() {
                    frm.set_value('approval_status', 'Approved');
                    frm.save();
                }, __('Actions')).addClass('btn-success');

                frm.add_custom_button(__('Reject'), function() {
                    frm.set_value('approval_status', 'Rejected');
                    frm.save();
                }, __('Actions')).addClass('btn-danger');
            }
        }
    },

    approval_status: function(frm) {
        // Auto-fill approval fields when status changes
        if (frm.doc.docstatus === 1 && frm.doc.approval_status) {
            if (frm.doc.approval_status === 'Approved' || frm.doc.approval_status === 'Rejected') {
                frm.set_value('approved_by', frappe.session.user);
                frm.set_value('approval_time', frappe.datetime.now_datetime());
                frm.set_df_property('approved_by', 'read_only', 1);
                frm.set_df_property('approval_time', 'read_only', 1);
            }
        }
    }
});
"""

    if existing:
        # Update existing script
        doc = frappe.get_doc("Client Script", script_name)
        doc.script = script_content
        doc.save()
        action = "updated"
    else:
        # Create new script
        doc = frappe.get_doc({
            "doctype": "Client Script",
            "name": script_name,
            "dt": "Asset Repair",
            "enabled": 1,
            "script_type": "Form",
            "script": script_content
        })
        doc.insert()
        action = "created"

    frappe.db.commit()

    return {
        "success": True,
        "action": action,
        "message": f"Client Script {action}. Please reload any open Asset Repair forms."
    }


@frappe.whitelist()
def configure_workflow_for_approval_fields():
    """
    Configure the Repair Approval WorkFlow to allow editing approval fields
    """
    workflow_name = "Repair Approval WorkFlow"

    # Fields that should be editable in submitted states
    approval_fields = "approval_notes\napproval_signature\napproved_by\napproval_time"

    # States that should allow editing these fields
    editable_states = ["Pending Approval", "Approved", "Rejected"]

    # Use direct SQL update to bypass validation
    for state_name in editable_states:
        frappe.db.sql("""
            UPDATE `tabWorkflow Document State`
            SET allow_edit = %s
            WHERE parent = %s AND state = %s
        """, (approval_fields, workflow_name, state_name))

    frappe.db.commit()

    # Clear cache
    frappe.clear_cache(doctype="Workflow")
    frappe.clear_cache(doctype="Asset Repair")

    return {
        "success": True,
        "message": f"Configured workflow! States {', '.join(editable_states)} now allow editing approval fields. Reload page!"
    }


@frappe.whitelist()
def cleanup_old_approval_fields():
    """
    Remove old duplicate approval fields (custom_* fields)
    """
    old_fields = [
        'custom_approval_status',
        'custom_approved_by',
        'custom_signature',
        'custom_approval_date',
        'custom_approval_note',
        'approval_section_break'
    ]

    deleted = 0
    for fieldname in old_fields:
        existing = frappe.db.exists("Custom Field", {
            "dt": "Asset Repair",
            "fieldname": fieldname
        })

        if existing:
            frappe.delete_doc("Custom Field", existing, force=1)
            deleted += 1

    frappe.db.commit()
    frappe.clear_cache(doctype="Asset Repair")

    return {
        "success": True,
        "deleted": deleted,
        "message": f"Deleted {deleted} old approval fields. Please reload Asset Repair form."
    }


@frappe.whitelist()
def setup_approval_fields():
    """
    Add custom fields to Asset Repair for approval workflow
    Call this via browser console or bench execute
    """
    custom_fields = [
        {
            "dt": "Asset Repair",
            "fieldname": "repair_type",
            "fieldtype": "Select",
            "label": "Repair Type",
            "options": "Repair\nPreventive Maintenance\nBreakdown\nInspection\nReplacement",
            "insert_after": "description",
            "allow_on_submit": 0
        },
        {
            "dt": "Asset Repair",
            "fieldname": "approval_section",
            "fieldtype": "Section Break",
            "label": "Approval Details",
            "insert_after": "repair_status",
            "collapsible": 0
        },
        {
            "dt": "Asset Repair",
            "fieldname": "approval_status",
            "fieldtype": "Select",
            "label": "Approval Status",
            "options": "Pending\nApproved\nRejected",
            "default": "Pending",
            "insert_after": "approval_section",
            "in_list_view": 1,
            "in_standard_filter": 1,
            "read_only": 0,
            "allow_on_submit": 1
        },
        {
            "dt": "Asset Repair",
            "fieldname": "approval_column",
            "fieldtype": "Column Break",
            "insert_after": "approval_status"
        },
        {
            "dt": "Asset Repair",
            "fieldname": "approved_by",
            "fieldtype": "Link",
            "label": "Approved By",
            "options": "User",
            "insert_after": "approval_column",
            "read_only": 1,
            "allow_on_submit": 1
        },
        {
            "dt": "Asset Repair",
            "fieldname": "approval_time",
            "fieldtype": "Datetime",
            "label": "Approval Date & Time",
            "insert_after": "approved_by",
            "read_only": 1,
            "allow_on_submit": 1,
            "description": "Server timestamp - cannot be modified"
        },
        {
            "dt": "Asset Repair",
            "fieldname": "approval_notes_break",
            "fieldtype": "Section Break",
            "insert_after": "approval_time"
        },
        {
            "dt": "Asset Repair",
            "fieldname": "approval_notes",
            "fieldtype": "Small Text",
            "label": "Approval Notes",
            "insert_after": "approval_notes_break",
            "allow_on_submit": 1,
            "description": "Manager can add notes when approving/rejecting"
        },
        {
            "dt": "Asset Repair",
            "fieldname": "approval_signature_break",
            "fieldtype": "Column Break",
            "insert_after": "approval_notes"
        },
        {
            "dt": "Asset Repair",
            "fieldname": "approval_signature",
            "fieldtype": "Signature",
            "label": "Manager Signature",
            "insert_after": "approval_signature_break",
            "allow_on_submit": 1
        }
    ]

    created = 0
    updated = 0

    for field in custom_fields:
        existing = frappe.db.exists("Custom Field", {
            "dt": field["dt"],
            "fieldname": field["fieldname"]
        })

        if existing:
            doc = frappe.get_doc("Custom Field", existing)
            doc.update(field)
            doc.save()
            updated += 1
        else:
            custom_field = frappe.get_doc({
                "doctype": "Custom Field",
                **field
            })
            custom_field.insert()
            created += 1

    frappe.db.commit()

    return {
        "success": True,
        "created": created,
        "updated": updated,
        "message": f"Created {created} fields, updated {updated} fields. Please reload Asset Repair form."
    }


@frappe.whitelist()
def disable_field_editing_after_submit():
    """
    Disable allow_on_submit for all Asset Repair fields except approval fields
    This is the nuclear option - prevents ANY field editing after submit
    """
    # Get all fields from Asset Repair doctype
    meta = frappe.get_meta("Asset Repair")

    # Fields that SHOULD be editable after submit (approval fields only)
    allowed_fields = ['approval_status', 'approved_by', 'approval_time', 'approval_notes', 'approval_signature']

    created = 0
    updated = 0

    for field in meta.fields:
        if field.fieldname in allowed_fields:
            continue  # Skip approval fields

        # Disable allow_on_submit for this field
        property_name = f"Asset Repair-{field.fieldname}-allow_on_submit"

        existing = frappe.db.exists("Property Setter", {
            "doc_type": "Asset Repair",
            "field_name": field.fieldname,
            "property": "allow_on_submit"
        })

        if existing:
            doc = frappe.get_doc("Property Setter", existing)
            doc.value = "0"
            doc.save()
            updated += 1
        else:
            frappe.get_doc({
                "doctype": "Property Setter",
                "doctype_or_field": "DocField",
                "doc_type": "Asset Repair",
                "field_name": field.fieldname,
                "property": "allow_on_submit",
                "property_type": "Check",
                "value": "0"
            }).insert()
            created += 1

    # Also set approval fields to read_only (except approval_status)
    for field in ['approved_by', 'approval_time']:
        existing = frappe.db.exists("Property Setter", {
            "doc_type": "Asset Repair",
            "field_name": field,
            "property": "read_only"
        })

        if existing:
            doc = frappe.get_doc("Property Setter", existing)
            doc.value = "1"
            doc.save()
            updated += 1
        else:
            frappe.get_doc({
                "doctype": "Property Setter",
                "doctype_or_field": "DocField",
                "doc_type": "Asset Repair",
                "field_name": field,
                "property": "read_only",
                "property_type": "Check",
                "value": "1"
            }).insert()
            created += 1

    frappe.db.commit()
    frappe.clear_cache(doctype="Asset Repair")

    return {
        "success": True,
        "created": created,
        "updated": updated,
        "message": f"Disabled editing for all fields after submit. Created {created}, updated {updated}. Reload Asset Repair form and clear cache."
    }


@frappe.whitelist()
def test_direct_validation(repair_name):
    """Directly test the validation function on a specific repair"""
    try:
        doc = frappe.get_doc("Asset Repair", repair_name)

        # Try to modify description
        original_desc = doc.description
        doc.description = "TESTING VALIDATION - THIS SHOULD FAIL"

        # Call validation
        try:
            validate_asset_repair_permissions(doc, "validate")
            return {
                "validation_called": True,
                "validation_blocked": False,
                "message": "WARNING: Validation did not block the change!"
            }
        except Exception as e:
            return {
                "validation_called": True,
                "validation_blocked": True,
                "error_message": str(e),
                "message": "SUCCESS: Validation blocked the change as expected!"
            }

    except Exception as e:
        return {
            "error": str(e),
            "traceback": frappe.get_traceback()
        }


@frappe.whitelist()
def test_validation_hook():
    """Test if the validation hook is properly configured"""
    import inspect

    # Check if hooks.py has the doc_events
    try:
        from tub_suite import hooks
        doc_events = getattr(hooks, 'doc_events', None)

        result = {
            "hooks_file_loaded": True,
            "doc_events_exists": doc_events is not None,
            "doc_events_content": str(doc_events) if doc_events else "NOT FOUND",
            "validation_function_exists": callable(validate_asset_repair_permissions),
            "validation_function_path": inspect.getfile(validate_asset_repair_permissions) if callable(validate_asset_repair_permissions) else "NOT FOUND"
        }

        return result
    except Exception as e:
        return {
            "error": str(e),
            "traceback": frappe.get_traceback()
        }


@frappe.whitelist()
def setup_server_script():
    """
    Create Server Script for Asset Repair field locking
    This works immediately without server restart
    """
    script_name = "Asset Repair - Lock Fields"

    script_code = """# Lock all fields except approval_status after submission
if doc.docstatus == 1:
    # Get original document from database
    old_doc = frappe.get_doc("Asset Repair", doc.name)

    # Check if approval status changed (allow auto-fill in this case)
    approval_status_changed = (doc.get('approval_status') != old_doc.get('approval_status'))

    # Fields that CANNOT be changed after submission
    protected_fields = [
        'asset', 'asset_name', 'failure_date', 'description',
        'repair_status', 'completion_date', 'repair_cost',
        'actions_performed', 'stock_consumption', 'capitalize_repair_cost',
        'increase_in_asset_life', 'company', 'cost_center',
        'project', 'purchase_invoice', 'total_repair_cost',
        'downtime', 'naming_series'
    ]

    # Check if any protected field was modified
    for field in protected_fields:
        old_value = old_doc.get(field)
        new_value = doc.get(field)

        if str(old_value) != str(new_value):
            frappe.throw(f"Cannot modify {field.replace('_', ' ').title()} after submission. This repair request is locked.", frappe.PermissionError)

    # Auto-fill approval fields when status changes to Approved/Rejected
    if approval_status_changed and doc.approval_status in ['Approved', 'Rejected']:
        doc.approved_by = frappe.session.user
        doc.approval_time = frappe.utils.now()
    else:
        # If approval status didn't change, don't allow manual modification of approval fields
        if doc.get('approval_time') != old_doc.get('approval_time'):
            frappe.throw("Approval Date & Time is automatically set by the system and cannot be modified manually.", frappe.PermissionError)

        if doc.get('approved_by') != old_doc.get('approved_by'):
            frappe.throw("Approved By is automatically set by the system and cannot be modified manually.", frappe.PermissionError)
"""

    existing = frappe.db.exists("Server Script", {"name": script_name})

    if existing:
        script_doc = frappe.get_doc("Server Script", existing)
        script_doc.script_type = "DocType Event"
        script_doc.doctype_event = "Before Save"
        script_doc.reference_doctype = "Asset Repair"
        script_doc.script = script_code
        script_doc.enabled = 1
        script_doc.save()
        action = "updated"
    else:
        script_doc = frappe.get_doc({
            "doctype": "Server Script",
            "name": script_name,
            "script_type": "DocType Event",
            "doctype_event": "Before Save",
            "reference_doctype": "Asset Repair",
            "script": script_code,
            "enabled": 1
        })
        script_doc.insert()
        action = "created"

    frappe.db.commit()

    return {
        "success": True,
        "action": action,
        "script_name": script_name,
        "message": f"Server Script {action}! Field locking is now active. Test by editing a submitted Asset Repair."
    }

@frappe.whitelist()
def add_engineering_team_permission():
    """Add Engineering Team role permissions to Asset Repair DocType"""
    
    doctype_name = "Asset Repair"
    role = "Engineering Team"
    
    # Check if permission already exists
    existing = frappe.db.exists("DocPerm", {
        "parent": doctype_name,
        "role": role
    })
    
    if existing:
        return {"success": True, "message": f"Permission for {role} already exists"}
    
    # Get the DocType document
    doc = frappe.get_doc("DocType", doctype_name)
    
    # Add new permission row
    doc.append("permissions", {
        "role": role,
        "read": 1,
        "write": 1,
        "create": 1,
        "delete": 1,
        "submit": 1,
        "cancel": 1,
        "amend": 1,
        "report": 1,
        "export": 1,
        "print": 1,
        "email": 1,
        "share": 1
    })
    
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    
    return {
        "success": True,
        "message": f"Successfully added {role} permissions to {doctype_name}"
    }
