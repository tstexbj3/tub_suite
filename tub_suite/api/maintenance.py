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
                      issue_photos=None, before_photo=None, after_photo=None,
                      repair_subject="", repair_type=""):
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

        # Get user's department
        user_dept = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "department") or None

        repair = frappe.get_doc({
            "doctype": "Asset Repair",
            "asset": asset_name,
            "failure_date": frappe.utils.now(),
            "description": issue_description,
            "repair_subject": repair_subject,
            "repair_type": repair_type,
            "repair_source": "Planned Maintenance (ตามแผน)",
            "reported_by": frappe.session.user,
            "reporter_department": "Maintenance Department",
            "maintenance_task": task_label
        })
        repair.insert(ignore_permissions=True)
        repair_name = repair.name

        # Set first issue photo to issue_photos field
        if issue_photos and len(issue_photos) > 0:
            repair.issue_photos = issue_photos[0]
            repair.save(ignore_permissions=True)

        # Attach issue photos to repair request
        for idx, photo_url in enumerate(issue_photos):
            if photo_url:
                attach_file_to_doc("Asset Repair", repair.name, photo_url, f"Issue Photo {idx + 1}")

        # Notify Maintenance Supervisor about new PM issue
        try:
            supervisors = frappe.get_all("Has Role",
                filters={"role": "Maintenance Supervisor", "parenttype": "User"},
                fields=["parent"]
            )
            for supervisor in supervisors:
                frappe.sendmail(
                    recipients=[supervisor.parent],
                    subject=f"New PM Issue Reported: {repair_subject}",
                    message=f"""
                        <p><strong>New PM Issue Reported</strong></p>
                        <p>Asset: {asset_name}</p>
                        <p>Task: {task_label}</p>
                        <p>Subject: {repair_subject}</p>
                        <p>Type: {repair_type}</p>
                        <p>Repair ID: {repair.name}</p>
                        <p>Please review and verify in ERPNext.</p>
                    """
                )
        except Exception as e:
            frappe.logger().error(f"Failed to notify Maintenance Supervisor: {str(e)}")

        # NOTE: Asset status change to "Out of Order" is handled by engineer
        # when they set issue_severity to "Major - Asset Must Stop"
        # Minor issues keep asset operational

    # Update task last completion date and next due date
    # ONLY if no issue - if issue reported, task completes after repair verification
    from frappe.utils import add_days, add_months, nowdate

    # Get the task to find periodicity
    task_doc = frappe.get_doc("Asset Maintenance Task", task_name)

    # Update last completion date ONLY if no issue
    # If issue reported: task stays open until repair is verified by inspector
    if not has_issue:
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
    else:
        # Issue reported - task remains open until repair is verified
        frappe.logger().info(f"Task {task_name}: Issue reported, task stays open until repair verified")

    frappe.db.commit()

    return {
        "success": True,
        "log_name": log.name,
        "repair_name": repair_name,
        "has_issue": has_issue,
        "message": _("Maintenance task completed successfully") if not has_issue else _("Issue reported. Repair request created. Asset status: Out of Order")
    }

@frappe.whitelist()
def create_operator_repair_request(asset_name, repair_subject, repair_source, repair_type,
                                   failure_date, failure_description, reporter_name,
                                   reporter_department=None, issue_photos=None):
    """
    Create a repair request from the maintenance portal (operator-initiated)

    Args:
        asset_name: Asset name
        repair_subject: Subject of the repair
        repair_source: Source of repair (ตามแผน/นอกแผน)
        repair_type: Type of repair (ซ่อม/ติดตั้งใหม่)
        failure_date: Date of failure
        failure_description: Description of the issue
        reporter_name: Name of reporter
        reporter_department: Department of reporter
        issue_photos: List of photo URLs
    """
    try:
        # Log what portal is sending
        frappe.logger().info(f"create_operator_repair_request called with repair_type='{repair_type}'")

        # Parse issue_photos if JSON string
        if isinstance(issue_photos, str):
            try:
                issue_photos = json.loads(issue_photos)
            except:
                issue_photos = []
        elif issue_photos is None:
            issue_photos = []

        # Validate required fields
        if not asset_name:
            frappe.throw(_("Asset is required"))
        if not repair_subject:
            frappe.throw(_("Subject is required"))
        if not repair_source:
            frappe.throw(_("Repair source is required"))
        if not repair_type:
            frappe.throw(_("Repair type is required"))
        if len(issue_photos) == 0:
            frappe.throw(_("At least 1 photo is required"))
        
        # Map short form to full form for repair_source
        if repair_source == "Portal":
            repair_source = "Portal (แจ้งผ่านระบบ)"


        # Create Asset Repair document
        repair = frappe.get_doc({
            "doctype": "Asset Repair",
            "asset": asset_name,
            "failure_date": failure_date or frappe.utils.now(),
            "repair_subject": repair_subject,
            "repair_source": repair_source,
            "repair_type": repair_type,
            "description": failure_description,
            "repair_status": "Pending",
            "reported_by": frappe.session.user,
            "reporter_department": reporter_department
        })
        repair.insert(ignore_permissions=True)
        frappe.logger().info(f"After insert: repair_type='{repair.repair_type}'")

        # Set photo field values directly without triggering validation
        if len(issue_photos) > 0:
            repair.db_set("issue_photos", issue_photos[0], update_modified=False)
        if len(issue_photos) > 1:
            repair.db_set("issue_photos_2", issue_photos[1], update_modified=False)

        # Attach issue photos
        for idx, photo_url in enumerate(issue_photos, start=1):
            if photo_url:
                attach_file_to_doc("Asset Repair", repair.name, photo_url, f"Issue Photo {idx}")

        # Notify engineers about new issue
        try:
            from tub_suite.overrides.asset_repair_override import notify_engineer_on_new_issue
            notify_engineer_on_new_issue(repair)
        except Exception as e:
            frappe.logger().error(f"Failed to notify engineers: {str(e)}")

        frappe.db.commit()

        return {
            "success": True,
            "repair_name": repair.name,
            "message": _("Repair request created successfully")
        }

    except Exception as e:
        frappe.logger().error(f"Error creating operator repair request: {str(e)}")
        import traceback
        frappe.logger().error(traceback.format_exc())
        frappe.throw(_("Error creating repair request: {0}").format(str(e)))

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

                    # Check if this task has a pending repair
                    # Locked states: Draft, Pending Approval, Approved, OR Finished (until verified)
                    today = frappe.utils.nowdate()

                    # Check for pending repairs (not finished/cancelled/rejected)
                    pending_repairs = frappe.get_all("Asset Repair", filters={
                        "asset": asset.name,
                        "maintenance_task": task.get("maintenance_task"),
                        "workflow_state": ["not in", ["Cancelled", "Rejected"]]
                    }, fields=["name", "workflow_state", "repair_status", "maintenance_task", "failure_date", "verification_status"])

                    # Task is locked if repair is:
                    # - Draft, Pending Approval, Approved (any verification_status)
                    # - Finished but NOT verified as passed
                    unverified_repairs = [
                        r for r in pending_repairs
                        if r.workflow_state != "Finished" or r.verification_status != "Verified - Passed"
                    ]

                    task["pending_repair"] = 1 if len(unverified_repairs) > 0 else 0

                    # Convert last_completion_date to string for comparison (it's a date object)
                    last_completed = str(task.get("last_completion_date")) if task.get("last_completion_date") else None

                    if last_completed == today:
                        # Check if there's an unverified repair for THIS SPECIFIC TASK created today
                        open_repairs = [r for r in unverified_repairs if str(r.failure_date) == today]
                        task["has_open_issue"] = 1 if len(open_repairs) > 0 else 0
                        frappe.logger().info(f"Task {task['name']}: last_completed={task.get('last_completion_date')}, today={today}, unverified_repairs={len(unverified_repairs)}, open_repairs_today={len(open_repairs)}")
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

        # If verification passed, complete the maintenance task
        if verification_status == "Verified - Passed":
            # Find the original maintenance task and complete it
            task_label = repair.get("maintenance_task")
            asset_name = repair.get("asset")

            if task_label and asset_name:
                # Find the Asset Maintenance document for this asset
                maintenance_docs = frappe.get_all("Asset Maintenance",
                    filters={"asset_name": asset_name},
                    fields=["name"],
                    limit=1
                )

                if maintenance_docs:
                    # Find the specific task within this Asset Maintenance
                    tasks = frappe.get_all("Asset Maintenance Task",
                        filters={
                            "maintenance_task": task_label,
                            "parent": maintenance_docs[0].name
                        },
                        fields=["name", "parent", "periodicity"],
                        limit=1
                    )

                    if tasks:
                        from frappe.utils import add_days, add_months, nowdate
                        task = tasks[0]
                        task_doc = frappe.get_doc("Asset Maintenance Task", task.name)

                        # Set task completion date
                        task_doc.last_completion_date = nowdate()

                        # Calculate next due date
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
                            next_due = add_months(completion_date, 1)

                        task_doc.next_due_date = next_due
                        task_doc.save(ignore_permissions=True)
                        frappe.logger().info(f"Completed task {task.name}: last_completion={nowdate()}, next_due={next_due}")

                        # Update the corresponding Maintenance Log to Completed
                        # Filter by task, asset_maintenance, and status = "Planned"
                        logs = frappe.get_all("Asset Maintenance Log",
                            filters={
                                "task": task.name,
                                "asset_maintenance": maintenance_docs[0].name,
                                "maintenance_status": "Planned"
                            },
                            fields=["name"],
                            limit=1
                        )

                        if logs:
                            log_doc = frappe.get_doc("Asset Maintenance Log", logs[0].name)
                            log_doc.maintenance_status = "Completed"
                            log_doc.completion_date = nowdate()
                            log_doc.save(ignore_permissions=True)
                            frappe.logger().info(f"Completed maintenance log {logs[0].name} for asset {asset_name}")

        frappe.db.commit()

        frappe.logger().info(f"Repair {repair_name} verified by {frappe.session.user}")

        return {
            "success": True,
            "repair_name": repair.name,
            "verification_status": verification_status,
            "verified_by": repair.verified_by,
            "verification_date": repair.verification_date,
            "message": _("Repair verification submitted successfully. Task marked as completed.")
        }

    except Exception as e:
        frappe.logger().error(f"Error verifying repair: {str(e)}")
        frappe.db.rollback()
        frappe.throw(_("Error submitting verification: {0}").format(str(e)))


@frappe.whitelist()
def get_repairs_needing_verification():
    """
    Get repairs that need supervisor verification by the logged-in supervisor
    Returns repairs where:
    - workflow_state = "Pending Supervisor Verification"
    - current user has Supervisor or Maintenance Supervisor role
    - filters by repair_source based on supervisor type

    Used by mobile portal to show pending verifications to supervisors
    """
    try:
        # Check if current user is a supervisor
        user_roles = frappe.get_roles()
        is_regular_supervisor = "Supervisor" in user_roles
        is_maintenance_supervisor = "Maintenance Supervisor" in user_roles

        if not is_regular_supervisor and not is_maintenance_supervisor:
            return []  # Not a supervisor, return empty

        # Build filters based on supervisor type
        filters = {
            "workflow_state": "Pending Supervisor Verification"
        }

        # Filter by repair source based on supervisor type
        if is_regular_supervisor and not is_maintenance_supervisor:
            # Regular Supervisor can only verify Portal repairs
            filters["repair_source"] = "Portal (แจ้งผ่านระบบ)"
        elif is_maintenance_supervisor:
            # Maintenance Supervisor can only verify PM repairs
            filters["repair_source"] = "Planned Maintenance (ตามแผน)"

        repairs = frappe.get_all("Asset Repair",
            filters=filters,
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
def get_repairs_for_confirmation():
    """
    Get repairs awaiting supervisor verification or reporter confirmation
    Returns repairs where:
    - workflow_state = "Pending Supervisor Verification" OR "Pending Reporter Confirmation"
    - reported_by = current user

    Used by portal to show repairs ready for reporter confirmation
    """
    try:
        repairs = frappe.get_all("Asset Repair",
            filters={
                "workflow_state": "Pending Reporter Confirmation",
                "reported_by": frappe.session.user,
            },
            fields=[
                "name", "asset", "description", "failure_date",
                "workflow_state", "repair_status", "reported_by",
                "completion_handover_date", "repair_result_status"
            ],
            order_by="completion_handover_date desc"
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
        frappe.logger().error(f"Error fetching repairs for confirmation: {str(e)}")
        return []


@frappe.whitelist()
def submit_reporter_confirmation(repair_name, confirmation_photos=None, confirmation_notes="", signature=None):
    """
    Reporter confirms repair completion from portal
    Updates reporter_confirmation fields in Finished state

    Args:
        repair_name: Name of the Asset Repair document
        confirmation_photos: JSON string of photo attachments
        confirmation_notes: Reporter's notes about the confirmation
        signature: Signature data
    """
    try:
        # Get the repair document
        repair = frappe.get_doc("Asset Repair", repair_name)

        # Verify user is the original reporter
        if repair.reported_by != frappe.session.user:
            frappe.throw(_("Only the original reporter can confirm this repair"))

        # Verify workflow state
        if repair.workflow_state != "Pending Reporter Confirmation":
            frappe.throw(_("Repair must be in Pending Reporter Confirmation state for confirmation"))

        # Update confirmation fields
        if confirmation_photos:
            # Parse JSON if it's a string and extract first photo
            if isinstance(confirmation_photos, str):
                try:
                    import json
                    photos_list = json.loads(confirmation_photos)
                    if photos_list and len(photos_list) > 0:
                        repair.reporter_confirmation_photos = photos_list[0]
                except:
                    repair.reporter_confirmation_photos = confirmation_photos
            else:
                repair.reporter_confirmation_photos = confirmation_photos

        if confirmation_notes:
            repair.reporter_confirmation_notes = confirmation_notes

        if signature:
            repair.reporter_signature = signature

        # Auto-fill confirmation date
        repair.reporter_confirmation_date = frappe.utils.now()

        # Save the document first
        repair.flags.ignore_permissions = False
        repair.save(ignore_permissions=False)
        
        # Apply workflow transition to Finished
        from frappe.model.workflow import apply_workflow
        apply_workflow(repair, "Reporter Confirm")
        frappe.db.commit()

        return {
            "success": True,
            "message": _("Confirmation submitted successfully"),
            "repair_name": repair_name
        }

    except Exception as e:
        frappe.logger().error(f"Error submitting reporter confirmation: {str(e)}")
        frappe.db.rollback()
        frappe.throw(_("Error submitting confirmation: {0}").format(str(e)))


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


@frappe.whitelist()
def get_inspector_todo_list(days_ahead=7):
    """
    Get maintenance tasks assigned to current user, categorized by urgency
    ONLY accessible to users with "Maintenance User" role

    Returns:
        {
            "overdue": [...],      # Tasks past due date
            "due_today": [...],    # Tasks due today
            "upcoming": [...],     # Tasks due within days_ahead
            "summary": {
                "overdue_count": 0,
                "due_today_count": 0,
                "upcoming_count": 0,
                "total": 0
            }
        }
    """
    from datetime import datetime, timedelta

    # Permission check: ONLY Maintenance User role can access
    if not frappe.has_permission("Asset Maintenance", "read") or \
       "Maintenance User" not in frappe.get_roles(frappe.session.user):
        frappe.throw("Access denied. Only Maintenance Users can view the task list.",
                    frappe.PermissionError)

    try:
        current_user = frappe.session.user
        today = frappe.utils.today()
        future_date = frappe.utils.add_days(today, int(days_ahead))

        # Get all Asset Maintenance records (including drafts - no docstatus filter)
        maintenance_list = frappe.get_all("Asset Maintenance",
            fields=["name", "asset_name", "company", "maintenance_team", "docstatus"]
        )

        frappe.logger().info(f"Found {len(maintenance_list)} Asset Maintenance records")

        overdue = []
        due_today = []
        upcoming = []

        total_tasks_found = 0

        # For each maintenance schedule, get tasks assigned to current user
        for maintenance in maintenance_list:
            tasks = frappe.get_all("Asset Maintenance Task",
                filters={
                    "parent": maintenance.name,
                    "assign_to": current_user,
                    "maintenance_status": ("in", ["Planned", "Overdue"])  # Only active tasks
                },
                fields=[
                    "name", "maintenance_task", "description", "periodicity",
                    "next_due_date", "assign_to", "maintenance_type", "maintenance_status", "last_completion_date"
                ]
            )

            total_tasks_found += len(tasks)
            if tasks:
                frappe.logger().info(f"  {maintenance.name}: {len(tasks)} tasks assigned to {current_user}")

            for task in tasks:
                # Enrich with asset details
                asset = frappe.get_doc("Asset", maintenance.asset_name)

                task_data = {
                    "name": task.name,
                    "asset_name": maintenance.asset_name,
                    "asset_title": asset.asset_name or asset.item_name,
                    "location": asset.location or "",
                    "maintenance_task": task.maintenance_task,
                    "description": task.description or "",
                    "periodicity": task.periodicity,
                    "next_due_date": task.next_due_date,
                    "maintenance_type": task.maintenance_type,
                    "maintenance_status": task.maintenance_status,
                    "last_completion_date": task.last_completion_date
                }

                # Categorize tasks based on:
                # 1. For SUBMITTED Asset Maintenance: Trust maintenance_status (ERPNext manages it)
                # 2. For DRAFT Asset Maintenance: Calculate from next_due_date (status not updated)

                if not task.next_due_date:
                    # Skip tasks without due date
                    continue

                due_date = frappe.utils.getdate(task.next_due_date)
                today_date = frappe.utils.getdate(today)
                days_diff = (due_date - today_date).days

                # For SUBMITTED maintenance: Trust ERPNext's maintenance_status
                # For DRAFT maintenance: Calculate from dates (scheduled job doesn't update Draft records)
                is_submitted = maintenance.docstatus == 1

                if is_submitted and task.maintenance_status == "Overdue":
                    # Submitted + Overdue status = Truly overdue (managed by ERPNext)
                    task_data["days_overdue"] = -days_diff if days_diff < 0 else 0
                    overdue.append(task_data)
                elif not is_submitted and days_diff < 0:
                    # Draft but date is past = Show as overdue (status won't update until submitted)
                    task_data["days_overdue"] = -days_diff
                    overdue.append(task_data)
                elif days_diff == 0:
                    # Due today (both Draft and Submitted)
                    task_data["days_overdue"] = 0
                    due_today.append(task_data)
                elif days_diff > 0 and days_diff <= int(days_ahead):
                    # Upcoming (both Draft and Submitted)
                    task_data["days_overdue"] = 0
                    upcoming.append(task_data)

        # Sort by due date
        overdue.sort(key=lambda x: x.get("next_due_date") or "")
        due_today.sort(key=lambda x: x.get("maintenance_task") or "")
        upcoming.sort(key=lambda x: x.get("next_due_date") or "")

        frappe.logger().info(f"Total tasks found for {current_user}: {total_tasks_found}")
        frappe.logger().info(f"Categorized: Overdue={len(overdue)}, Due Today={len(due_today)}, Upcoming={len(upcoming)}")
        frappe.logger().info(f"=== END TODO LIST DEBUG ===")

        return {
            "overdue": overdue,
            "due_today": due_today,
            "upcoming": upcoming,
            "summary": {
                "overdue_count": len(overdue),
                "due_today_count": len(due_today),
                "upcoming_count": len(upcoming),
                "total": len(overdue) + len(due_today) + len(upcoming)
            }
        }

    except Exception as e:
        frappe.logger().error(f"Error fetching inspector todo list: {str(e)}")
        return {
            "overdue": [],
            "due_today": [],
            "upcoming": [],
            "summary": {
                "overdue_count": 0,
                "due_today_count": 0,
                "upcoming_count": 0,
                "total": 0
            }
        }


@frappe.whitelist()
def debug_todo_data():
    """Debug endpoint to check Asset Maintenance data"""
    current_user = frappe.session.user

    # Get ALL Asset Maintenance records (no filters)
    all_maintenance = frappe.get_all("Asset Maintenance",
        fields=["name", "asset_name", "docstatus"],
        limit=20
    )

    # Get all tasks
    all_tasks = frappe.get_all("Asset Maintenance Task",
        fields=["name", "parent", "maintenance_task", "assign_to", "next_due_date", "maintenance_status"],
        limit=50
    )

    # Get filtered maintenance (what the todo list uses)
    filtered_maintenance = frappe.get_all("Asset Maintenance",
        filters={
            "docstatus": 1
        },
        fields=["name", "asset_name", "docstatus"]
    )

    # Get tasks assigned to current user
    my_tasks = frappe.get_all("Asset Maintenance Task",
        filters={"assign_to": current_user},
        fields=["name", "parent", "maintenance_task", "assign_to", "next_due_date"]
    )

    return {
        "current_user": current_user,
        "all_maintenance_count": len(all_maintenance),
        "all_maintenance_sample": all_maintenance,
        "all_tasks_count": len(all_tasks),
        "all_tasks_sample": all_tasks[:10],
        "filtered_maintenance_count": len(filtered_maintenance),
        "filtered_maintenance": filtered_maintenance,
        "my_tasks_count": len(my_tasks),
        "my_tasks": my_tasks
    }


@frappe.whitelist()
def reset_tasks_for_testing():
    """
    TESTING ONLY: Reset all task completion dates to 7 days ago
    This unlocks tasks that were completed today so they can be tested again
    """
    from frappe.utils import add_days, nowdate

    # Set completion date to 7 days ago
    past_date = add_days(nowdate(), -7)

    # Get all Asset Maintenance Tasks
    tasks = frappe.get_all("Asset Maintenance Task", fields=["name"])

    updated_count = 0
    for task in tasks:
        doc = frappe.get_doc("Asset Maintenance Task", task.name)
        doc.last_completion_date = past_date
        doc.save(ignore_permissions=True)
        updated_count += 1

    frappe.db.commit()

    return {
        "success": True,
        "message": f"Reset {updated_count} tasks to {past_date}",
        "tasks_updated": updated_count
    }
