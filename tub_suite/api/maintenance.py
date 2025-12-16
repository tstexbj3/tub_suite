# Copyright (c) 2024, Tipubon International Co.,Ltd. and contributors
# For license information, please see license.txt
# Enhanced maintenance API with repair workflow

import frappe
from frappe import _
import json
import base64
from werkzeug.utils import secure_filename
from frappe.utils.file_manager import save_file

@frappe.whitelist()
def submit_maintenance_task(maintenance_name, task_name, asset_name, has_issue=0,
                      issue_description="", notes="", inspection_photos=None,
                      issue_photos=None, before_photo=None, after_photo=None):
    """
    Submit maintenance task completion

    NEW in v2.0.0:
    - inspection_photos required for normal completion (with timestamp)
    - issue_photos required when reporting issues (with timestamp)
    - Photos use structured naming and embedded metadata

    BACKWARD COMPATIBILITY (v1.x):
    - Still accepts before_photo, after_photo parameters
    - Automatically converts to inspection_photos format

    Workflow:
    - If no issue: Mark task as completed, attach inspection photos, update last_completion_date
    - If issue reported: Create repair request, attach issue photos, set asset to "Out of Order"

    Args:
        maintenance_name: Asset Maintenance document name
        task_name: Asset Maintenance Task name
        asset_name: Asset name
        has_issue: 0 or 1
        issue_description: Problem description (if has_issue=1)
        notes: Inspection notes
        inspection_photos: List of photo URLs with metadata (for normal completion) - v2.0+
        issue_photos: List of photo URLs with metadata (if has_issue=1) - v2.0+
        before_photo: DEPRECATED - kept for backward compatibility with v1.x frontend
        after_photo: DEPRECATED - kept for backward compatibility with v1.x frontend
    """
    from tub_suite.api.file_utils import validate_photo_requirements

    # BACKWARD COMPATIBILITY: Convert old API format to new format
    if before_photo or after_photo:
        # Old API call detected - convert to new format
        inspection_photos = []
        if before_photo:
            inspection_photos.append(before_photo)
        if after_photo:
            inspection_photos.append(after_photo)
        frappe.logger().info(f"LEGACY API: Converted before/after photos to inspection_photos for compatibility")

    # Parse photo arrays if JSON strings
    if isinstance(inspection_photos, str):
        try:
            inspection_photos = json.loads(inspection_photos)
        except:
            inspection_photos = []
    elif inspection_photos is None:
        inspection_photos = []

    if isinstance(issue_photos, str):
        try:
            issue_photos = json.loads(issue_photos)
        except:
            issue_photos = []
    elif issue_photos is None:
        issue_photos = []

    # Validate photo requirements
    if not has_issue:
        # Normal inspection: require inspection photos
        validate_photo_requirements(len(inspection_photos), "INSP", has_issue=0)
    else:
        # Issue reported: require issue photos
        validate_photo_requirements(len(issue_photos), "ISSUE", has_issue=1)

    # Create Asset Maintenance Log
    log_data = {
        "doctype": "Asset Maintenance Log",
        "asset_maintenance": maintenance_name,
        "task": task_name,
        "asset_name": asset_name,
        "maintenance_status": "Completed" if not has_issue else "Planned",
        "actions_performed": notes  # Save notes to actions_performed field
    }

    # Only set completion_date if no issue (status = Completed)
    if not has_issue:
        log_data["completion_date"] = frappe.utils.nowdate()

    log = frappe.get_doc(log_data)

    log.insert(ignore_permissions=True)

    # Attach inspection photos (normal completion)
    if not has_issue and inspection_photos:
        for idx, photo_url in enumerate(inspection_photos, start=1):
            if photo_url:
                attach_file_to_doc("Asset Maintenance Log", log.name, photo_url,
                                 f"Inspection Photo {idx}")

    # If has issue, create repair request and change asset status
    repair_name = None
    if has_issue:
        # Get task details to populate maintenance_task field
        task_doc = frappe.get_doc("Asset Maintenance Task", task_name)
        task_label = task_doc.maintenance_task or task_doc.task_name or "Unnamed Task"

        repair = frappe.get_doc({
            "doctype": "Asset Repair",
            "asset": asset_name,
            "failure_date": frappe.utils.nowdate(),
            "description": issue_description,
            "repair_status": "Pending",
            "reported_by": frappe.session.user,  # Track who reported
            "maintenance_task": task_label,  # Which task this came from
            "requires_inspector_verification": 1,  # Enable verification workflow
            "verification_status": "Pending Verification"
        })
        repair.insert(ignore_permissions=True)
        repair_name = repair.name

        # Attach issue photos to repair request
        for idx, photo_url in enumerate(issue_photos):
            if photo_url:
                attach_file_to_doc("Asset Repair", repair.name, photo_url, f"Issue Photo {idx + 1}")

        # NOTE: Asset status change to "Out of Order" is handled by engineer
        # when they set issue_severity to "Major - Asset Must Stop"
        # Minor issues keep asset operational

    # Update task last completion date and next due date
    # ALWAYS update - inspector completed the task regardless of issue reported
    from frappe.utils import add_days, add_months, nowdate

    # Get the task to find periodicity
    task_doc = frappe.get_doc("Asset Maintenance Task", task_name)

    # Update last completion date (ALWAYS)
    task_doc.last_completion_date = nowdate()

    # Calculate next due date based on periodicity
    completion_date = frappe.utils.getdate(nowdate())
    periodicity = task_doc.periodicity

    if periodicity == "Daily":
        next_due = add_days(completion_date, 1)
    elif periodicity == "Weekly":
        next_due = add_days(completion_date, 7)
    elif periodicity == "Monthly":
        next_due = add_months(completion_date, 1)
    elif periodicity == "Quarterly":
        next_due = add_months(completion_date, 3)
    elif periodicity == "Half-yearly":
        next_due = add_months(completion_date, 6)
    elif periodicity == "Yearly":
        next_due = add_months(completion_date, 12)
    elif periodicity == "2 Yearly":
        next_due = add_months(completion_date, 24)
    elif periodicity == "3 Yearly":
        next_due = add_months(completion_date, 36)
    else:
        # Default to 1 month if periodicity not recognized
        next_due = add_months(completion_date, 1)

    task_doc.next_due_date = next_due
    task_doc.save(ignore_permissions=True)
    frappe.logger().info(f"Updated task {task_name}: last_completion={nowdate()}, next_due={next_due}")

    frappe.db.commit()

    return {
        "success": True,
        "log_name": log.name,
        "repair_name": repair_name,
        "has_issue": has_issue,
        "message": _("Maintenance task completed successfully") if not has_issue else _("Issue reported. Repair request created. Asset status: Out of Order")
    }

@frappe.whitelist()
def complete_repair(repair_name, repair_notes="", after_repair_photos=None):
    """
    Complete a repair request
    Restores asset status to normal and updates task

    Args:
        repair_name: Name of the Asset Repair document
        repair_notes: Notes about the repair completion
        after_repair_photos: List of photo URLs taken after repair
    """
    # Parse after_repair_photos if it's a JSON string
    if isinstance(after_repair_photos, str):
        try:
            after_repair_photos = json.loads(after_repair_photos)
        except:
            after_repair_photos = []
    elif after_repair_photos is None:
        after_repair_photos = []

    if not after_repair_photos or len(after_repair_photos) == 0:
        frappe.throw(_("After repair photos are required to complete the repair"))

    # Get repair document
    repair_doc = frappe.get_doc("Asset Repair", repair_name)

    # Update repair status
    repair_doc.repair_status = "Completed"
    repair_doc.completion_date = frappe.utils.nowdate()
    repair_doc.completed_by = frappe.session.user
    if repair_notes:
        repair_doc.actions_performed = repair_notes
    repair_doc.save(ignore_permissions=True)

    # Attach after-repair photos
    for idx, photo_url in enumerate(after_repair_photos):
        if photo_url:
            attach_file_to_doc("Asset Repair", repair_doc.name, photo_url, f"After Repair Photo {idx + 1}")

    # Restore asset status to normal
    try:
        asset_doc = frappe.get_doc("Asset", repair_doc.asset)
        asset_doc.status = "Submitted"  # or original status
        asset_doc.add_comment("Comment", f"Repair completed. Asset restored to normal operation.")
        asset_doc.save(ignore_permissions=True)
        frappe.logger().info(f"Asset {repair_doc.asset} status restored to normal")
    except Exception as e:
        frappe.log_error(f"Failed to restore asset status: {str(e)}", "Asset Status Restore Error")

    frappe.db.commit()

    return {
        "success": True,
        "repair_name": repair_doc.name,
        "asset_name": repair_doc.asset,
        "message": _("Repair completed successfully. Asset status restored to normal.")
    }

@frappe.whitelist()
def get_pending_repairs(asset_name=None):
    """
    Get pending repair requests
    Optionally filter by asset
    """
    filters = {
        "repair_status": ["in", ["Pending", "In Progress"]]
    }

    if asset_name:
        filters["asset"] = asset_name

    repairs = frappe.get_all("Asset Repair",
        filters=filters,
        fields=["name", "asset", "description", "repair_status", "creation"],
        order_by="creation desc"
    )

    # Add asset details
    for repair in repairs:
        asset_details = frappe.db.get_value("Asset", repair.asset,
            ["asset_name", "item_code", "item_name", "location"], as_dict=True)
        if asset_details:
            repair.update(asset_details)

    return repairs

@frappe.whitelist()
def get_maintenance_by_asset(asset_name):
    """
    Get maintenance tasks for assets matching search term
    Search by asset name, item code, or item name
    Returns ALL matching assets with their tasks
    """
    try:
        import traceback
        print(f"\n🔵 API CALLED: get_maintenance_by_asset({asset_name}) - v2.0.1 CODE LOADED\n")
        frappe.logger().info(f"get_maintenance_by_asset called with asset_name: {asset_name}")

        if not asset_name:
            frappe.throw(_("Asset name is required"))

        # Try exact match first
        exact_match = frappe.db.get_value("Asset", asset_name, ["name", "item_code", "item_name", "location", "asset_category"], as_dict=True)

        if exact_match:
            # Exact match found - return just this one asset
            frappe.logger().info(f"Exact match found: {exact_match.name}")
            assets = [exact_match]
        else:
            # No exact match - search for partial matches across all fields
            frappe.logger().info(f"No exact match, searching for partial matches...")

            search_pattern = f"%{asset_name}%"
            assets = frappe.db.sql("""
                SELECT DISTINCT name, item_code, item_name, location, asset_category
                FROM `tabAsset`
                WHERE name LIKE %(pattern)s
                   OR item_code LIKE %(pattern)s
                   OR item_name LIKE %(pattern)s
                ORDER BY name ASC
            """, {"pattern": search_pattern}, as_dict=True)

            frappe.logger().info(f"Found {len(assets)} matching assets")

        if not assets:
            # Return empty list for no matches
            frappe.logger().info(f"No assets found matching: {asset_name}")
            return []

        # Collect all assets with their tasks
        results = []

        for asset in assets:
            # Get maintenance schedules for this asset
            maintenance_list = frappe.get_all("Asset Maintenance",
                filters={"asset_name": asset.name},
                fields=["name", "asset_name", "company", "docstatus"]
            )

            # Get all tasks for this asset
            asset_tasks = []
            for maint in maintenance_list:
                tasks = frappe.get_all("Asset Maintenance Task",
                    filters={"parent": maint.name},
                    fields=["name", "maintenance_task", "maintenance_type",
                           "periodicity", "next_due_date", "last_completion_date", "idx"],
                    order_by="idx asc"
                )

                for task in tasks:
                    task["parent"] = maint.name
                    task["asset_name"] = asset.name
                    task["item_code"] = asset.item_code
                    task["item_name"] = asset.item_name

                    # Check if this task has an open issue reported today
                    today = frappe.utils.nowdate()

                    # Convert last_completion_date to string for comparison (it's a date object)
                    last_completed = str(task.get("last_completion_date")) if task.get("last_completion_date") else None

                    if last_completed == today:
                        # Check if there's a pending repair for THIS SPECIFIC TASK created today
                        # Use workflow_state instead of repair_status (workflow doesn't update repair_status until "Finished")
                        open_repairs = frappe.get_all("Asset Repair", filters={
                            "asset": asset.name,
                            "maintenance_task": task.get("maintenance_task"),  # ✅ Filter by specific task
                            "failure_date": today,
                            "workflow_state": ["not in", ["Finished", "Cancelled", "Rejected"]]
                        }, fields=["name", "workflow_state", "repair_status", "maintenance_task"])

                        task["has_open_issue"] = 1 if len(open_repairs) > 0 else 0

                        # DEBUG: Print to console to verify new code is running
                        print(f"\n=== BADGE DEBUG ===")
                        print(f"Asset: {asset.name}")
                        print(f"Task: {task.get('maintenance_task')}")
                        print(f"Last completed: {task.get('last_completion_date')}")
                        print(f"Today: {today}")
                        print(f"Open repairs found: {len(open_repairs)}")
                        for r in open_repairs:
                            print(f"  - {r.name}: workflow_state={r.workflow_state}")
                        print(f"Setting has_open_issue = {task['has_open_issue']}")
                        print(f"===================\n")

                        frappe.logger().info(f"Task {task['name']}: last_completed={task.get('last_completion_date')}, today={today}, open_repairs={len(open_repairs)}, workflow_states={[r.workflow_state for r in open_repairs]}")
                    else:
                        task["has_open_issue"] = 0

                    # Calculate next_due_date if not set
                    if not task.get("next_due_date") and task.get("last_completion_date"):
                        from frappe.utils import add_days, add_months
                        completion_date = frappe.utils.getdate(task["last_completion_date"])
                        periodicity = task.get("periodicity")

                        if periodicity == "Daily":
                            task["next_due_date"] = str(add_days(completion_date, 1))
                        elif periodicity == "Weekly":
                            task["next_due_date"] = str(add_days(completion_date, 7))
                        elif periodicity == "Monthly":
                            task["next_due_date"] = str(add_months(completion_date, 1))
                        elif periodicity == "Quarterly":
                            task["next_due_date"] = str(add_months(completion_date, 3))
                        elif periodicity == "Half-yearly":
                            task["next_due_date"] = str(add_months(completion_date, 6))
                        elif periodicity == "Yearly":
                            task["next_due_date"] = str(add_months(completion_date, 12))
                        elif periodicity == "2 Yearly":
                            task["next_due_date"] = str(add_months(completion_date, 24))
                        elif periodicity == "3 Yearly":
                            task["next_due_date"] = str(add_months(completion_date, 36))

                    asset_tasks.append(task)

            # Add this asset to results (even if it has no tasks)
            results.append({
                "asset": {
                    "name": asset.name,
                    "item_code": asset.item_code,
                    "item_name": asset.item_name,
                    "location": asset.get("location"),
                    "asset_category": asset.get("asset_category")
                },
                "tasks": asset_tasks,
                "task_count": len(asset_tasks)
            })

        frappe.logger().info(f"Returning {len(results)} assets with tasks")

        # Return array of assets
        return results

    except Exception as e:
        frappe.logger().error(f"Error in get_maintenance_by_asset: {str(e)}")
        import traceback
        frappe.logger().error(traceback.format_exc())
        frappe.throw(_("Error fetching maintenance data: {0}").format(str(e)))

def attach_file_to_doc(doctype, docname, file_url, file_label):
    """
    Helper function to attach file to a document
    """
    try:
        # Check if file already attached
        existing = frappe.db.exists("File", {
            "file_url": file_url,
            "attached_to_doctype": doctype,
            "attached_to_name": docname
        })

        if not existing:
            file_doc = frappe.get_doc({
                "doctype": "File",
                "file_url": file_url,
                "attached_to_doctype": doctype,
                "attached_to_name": docname,
                "attached_to_field": None,
                "file_name": file_label,
                "is_private": 0
            })
            file_doc.insert(ignore_permissions=True)
            frappe.logger().info(f"Attached file {file_label} to {doctype} {docname}")
    except Exception as e:
        frappe.log_error(f"Failed to attach file: {str(e)}", "File Attachment Error")


# ============================================================================
# INSPECTOR VERIFICATION WORKFLOW (NEW in v2.0.0)
# ============================================================================

@frappe.whitelist()
def get_repair_for_verification(repair_name):
    """
    Get Asset Repair details for inspector verification
    Shows issue description, repair notes, and allows photo upload

    Args:
        repair_name: Asset Repair document name

    Returns:
        dict: Repair details with asset info
    """
    try:
        # Get repair document
        repair = frappe.get_doc("Asset Repair", repair_name)

        # Check if user is the original reporter
        if repair.reported_by != frappe.session.user:
            user_roles = frappe.get_roles()
            if "Maintenance Manager" not in user_roles:
                frappe.throw(_("Only the original reporter or a manager can verify this repair"))

        # Get asset details
        asset = frappe.get_doc("Asset", repair.asset)

        # Get issue photos
        from tub_suite.api.file_utils import get_maintenance_photos
        photos = get_maintenance_photos("Asset Repair", repair_name, activity_type="ISSUE")

        return {
            "success": True,
            "repair": {
                "name": repair.name,
                "asset": repair.asset,
                "asset_name": asset.asset_name,
                "item_code": asset.item_code,
                "location": asset.location,
                "description": repair.description,
                "actions_performed": repair.actions_performed or "",
                "repair_status": repair.repair_status,
                "verification_status": repair.verification_status or "Pending Verification",
                "reported_by": repair.reported_by,
                "creation": repair.creation
            },
            "issue_photos": photos.get("ISSUE", [])
        }
    except Exception as e:
        frappe.logger().error(f"Error loading repair for verification: {str(e)}")
        frappe.throw(_("Error loading repair details: {0}").format(str(e)))


@frappe.whitelist()
def verify_repair_completion(repair_name, verification_photos=None, verification_notes="",
                             verification_status="Verified - Passed"):
    """
    Inspector verifies repair completion with after-repair photos

    NEW in v2.0.0: Inspector must verify repairs they reported before manager approval

    Args:
        repair_name: Asset Repair document name
        verification_photos: List of photo URLs (after-repair photos)
        verification_notes: Inspector's verification notes
        verification_status: "Verified - Passed" or "Verified - Failed"

    Returns:
        dict: Success message and updated repair info
    """
    from tub_suite.api.file_utils import validate_photo_requirements

    # Parse verification_photos if JSON string
    if isinstance(verification_photos, str):
        try:
            verification_photos = json.loads(verification_photos)
        except:
            verification_photos = []
    elif verification_photos is None:
        verification_photos = []

    # Validate photo requirements
    validate_photo_requirements(len(verification_photos), "VERIFY", has_issue=0)

    # Validate verification_status
    if verification_status not in ["Verified - Passed", "Verified - Failed"]:
        frappe.throw(_("Invalid verification status. Must be 'Verified - Passed' or 'Verified - Failed'"))

    try:
        # Get repair document
        repair = frappe.get_doc("Asset Repair", repair_name)

        # Check if user is the original reporter
        if repair.reported_by != frappe.session.user:
            user_roles = frappe.get_roles()
            if "Maintenance Manager" not in user_roles:
                frappe.throw(_("Only the original reporter or a manager can verify this repair"))

        # Update repair with verification info
        repair.verified_by = frappe.session.user
        repair.verification_date = frappe.utils.now()
        repair.verification_notes = verification_notes
        repair.verification_status = verification_status

        # Save repair
        repair.flags.ignore_validate_update_after_submit = True
        repair.save(ignore_permissions=True)

        # Attach verification photos
        for idx, photo_url in enumerate(verification_photos):
            if photo_url:
                attach_file_to_doc("Asset Repair", repair.name, photo_url,
                                 f"Verification Photo {idx + 1}")

        frappe.db.commit()

        frappe.logger().info(f"Repair {repair_name} verified by {frappe.session.user}")

        # TODO: Send notification to manager for approval
        # This will be handled by Assignment Rules in ERPNext

        return {
            "success": True,
            "repair_name": repair.name,
            "verification_status": verification_status,
            "verified_by": repair.verified_by,
            "verification_date": repair.verification_date,
            "message": _("Repair verification submitted successfully. Waiting for manager approval.")
        }

    except Exception as e:
        frappe.logger().error(f"Error verifying repair: {str(e)}")
        frappe.db.rollback()
        frappe.throw(_("Error submitting verification: {0}").format(str(e)))


@frappe.whitelist()
def get_repairs_needing_verification():
    """
    Get repairs that are finished and need verification by the logged-in user
    Returns repairs where:
    - workflow_state = "Finished"
    - reported_by = current user
    - verification_status != "Verified - Passed"

    Used by mobile portal to show pending verifications to original reporters
    """
    try:
        repairs = frappe.get_all("Asset Repair",
            filters={
                "workflow_state": "Finished",
                "reported_by": frappe.session.user,
                "verification_status": ["!=", "Verified - Passed"]
            },
            fields=[
                "name", "asset", "description", "failure_date",
                "workflow_state", "verification_status", "reported_by",
                "actions_performed", "completion_date", "repair_status"
            ],
            order_by="failure_date desc"
        )

        # Enrich with asset details
        for repair in repairs:
            if repair.asset:
                asset = frappe.get_doc("Asset", repair.asset)
                repair["asset_name"] = asset.asset_name
                repair["item_code"] = asset.item_code
                repair["item_name"] = asset.item_name
                repair["location"] = asset.location or ""

        return repairs

    except Exception as e:
        frappe.logger().error(f"Error fetching repairs needing verification: {str(e)}")
        return []


@frappe.whitelist()
def get_user_roles():
    """
    Get roles for the current logged-in user
    Used by mobile portal to control UI visibility
    """
    return frappe.get_roles()


@frappe.whitelist(allow_guest=False)
def get_portal_settings():
    """
    Get portal settings for controlling UI features
    Returns settings like search visibility, etc.
    """
    try:
        settings = frappe.get_single("Maintenance Portal Settings")
        return {
            "enable_search_for_all": settings.get("enable_search_for_all_users") or 0,
            "search_allowed_roles": ["Maintenance Manager", "System Manager", "Administrator"]
        }
    except Exception as e:
        frappe.logger().error(f"Error fetching portal settings: {str(e)}")
        # Return default settings if not configured yet
        return {
            "enable_search_for_all": 0,
            "search_allowed_roles": ["Maintenance Manager", "System Manager", "Administrator"]
        }
