# Copyright (c) 2024, Tipubon International Co.,Ltd. and contributors
# For license information, please see license.txt

"""
File utilities for TUB Suite maintenance photo management
Handles photo uploads with timestamps, metadata, and structured naming
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, cstr
from frappe.utils.file_manager import save_file
import re
import json


def generate_photo_filename(asset_name, activity_type, sequence, user=None):
    """
    Generate structured filename for maintenance photos

    Format: {ASSET}_{ACTIVITY}_{YYYYMMDD_HHMMSS}_{SEQ}_{USER}.jpg
    Example: PUMP-001_INSP_20251215_143052_1_INSP001.jpg

    Args:
        asset_name (str): Asset name/code (e.g., "ASSET-00001" or "PUMP-001")
        activity_type (str): Activity code - "INSP", "ISSUE", "VERIFY", "REPAIR"
        sequence (int): Photo number (1-5)
        user (str, optional): User email. Defaults to current user.

    Returns:
        str: Formatted filename with .jpg extension

    Activity Codes:
        - INSP: Normal inspection (no issues)
        - ISSUE: Problem/issue photos
        - VERIFY: Inspector verification photos after repair
        - REPAIR: Engineer repair work-in-progress photos
    """
    if not user:
        user = frappe.session.user

    # Get asset item code (cleaner than full name)
    try:
        asset_item_code = frappe.get_cached_value("Asset", asset_name, "item_code")
        if asset_item_code:
            asset_clean = asset_item_code
        else:
            asset_clean = asset_name
    except:
        asset_clean = asset_name

    # Clean asset code (remove special chars, keep only alphanumeric)
    asset_clean = re.sub(r'[^A-Z0-9]', '', asset_clean.upper())

    # Limit asset code length to 15 chars
    asset_clean = asset_clean[:15]

    # Generate timestamp: YYYYMMDD_HHMMSS
    timestamp = now_datetime().strftime("%Y%m%d_%H%M%S")

    # Get user short ID (first 8 chars of email username)
    user_short = user.split("@")[0].upper()[:8]

    # Build filename
    filename = f"{asset_clean}_{activity_type}_{timestamp}_{sequence}_{user_short}.jpg"

    return filename


@frappe.whitelist()
def attach_photo_with_metadata(doctype, docname, file_content, asset_name,
                                activity_type, sequence, metadata=None):
    """
    Upload photo with structured naming and embedded metadata

    Args:
        doctype (str): Parent doctype (e.g., "Asset Maintenance Log", "Asset Repair")
        docname (str): Parent document name
        file_content (str): Base64 encoded file data or file object
        asset_name (str): Asset being photographed
        activity_type (str): INSP/ISSUE/VERIFY/REPAIR
        sequence (int): Photo number (1-5)
        metadata (dict, optional): Additional metadata (timestamp, gps, etc.)

    Returns:
        str: File URL of uploaded photo

    Raises:
        frappe.ValidationError: If validation fails
    """
    # Validate inputs
    if activity_type not in ["INSP", "ISSUE", "VERIFY", "REPAIR"]:
        frappe.throw(_("Invalid activity type. Must be INSP, ISSUE, VERIFY, or REPAIR"))

    if not isinstance(sequence, int) or sequence < 1 or sequence > 5:
        frappe.throw(_("Sequence must be between 1 and 5"))

    # Generate structured filename
    filename = generate_photo_filename(asset_name, activity_type, sequence)

    # Prepare metadata JSON
    metadata_dict = {
        "asset": asset_name,
        "activity": activity_type,
        "sequence": sequence,
        "user": frappe.session.user,
        "timestamp": cstr(now_datetime()),
        "metadata": metadata or {}
    }

    # Save file using Frappe's file manager
    try:
        file_doc = save_file(
            fname=filename,
            content=file_content,
            dt=doctype,
            dn=docname,
            is_private=0,
            decode=True  # Decode base64 if needed
        )

        # Update file description with metadata
        frappe.db.set_value("File", file_doc.name, "description", json.dumps(metadata_dict))
        frappe.db.commit()

        frappe.logger().info(f"Photo uploaded: {filename} for {doctype} {docname}")

        return file_doc.file_url

    except Exception as e:
        frappe.logger().error(f"Photo upload failed: {str(e)}")
        frappe.throw(_("Failed to upload photo: {0}").format(str(e)))


@frappe.whitelist()
def get_maintenance_photos(doctype, docname, activity_type=None):
    """
    Get all photos for a maintenance record, grouped by activity type

    Args:
        doctype (str): Asset Maintenance Log or Asset Repair
        docname (str): Document name
        activity_type (str, optional): Filter by specific activity (INSP/ISSUE/VERIFY/REPAIR)

    Returns:
        dict: Photos grouped by activity type
        {
            "INSP": [{"file_name": "...", "file_url": "...", "timestamp": "...", ...}],
            "ISSUE": [...],
            "VERIFY": [...]
        }
    """
    filters = {
        "attached_to_doctype": doctype,
        "attached_to_name": docname,
    }

    files = frappe.get_all("File",
        filters=filters,
        fields=["name", "file_name", "file_url", "creation"],
        order_by="creation asc"
    )

    photos_by_activity = {}

    for file in files:
        try:
            # Get description field from database (might be custom field)
            file_doc = frappe.get_doc("File", file.name)
            description = getattr(file_doc, 'description', None)

            # Parse metadata from description
            if description:
                metadata = json.loads(description)
            else:
                # Handle photos without metadata (legacy or manual uploads)
                metadata = {}

            activity = metadata.get("activity", "UNKNOWN")

            # Filter by activity if specified
            if activity_type and activity != activity_type:
                continue

            # Initialize activity group if needed
            if activity not in photos_by_activity:
                photos_by_activity[activity] = []

            # Add photo info
            photo_info = {
                "file_name": file.file_name,
                "file_url": file.file_url,
                "sequence": metadata.get("sequence"),
                "user": metadata.get("user"),
                "timestamp": metadata.get("timestamp"),
                "creation": cstr(file.creation),
                "metadata": metadata.get("metadata", {})
            }

            photos_by_activity[activity].append(photo_info)

        except json.JSONDecodeError:
            # Handle photos without metadata
            if "UNKNOWN" not in photos_by_activity:
                photos_by_activity["UNKNOWN"] = []

            photos_by_activity["UNKNOWN"].append({
                "file_name": file.file_name,
                "file_url": file.file_url,
                "creation": cstr(file.creation)
            })
        except Exception as e:
            frappe.logger().error(f"Error parsing photo metadata: {str(e)}")
            continue

    # Sort photos by sequence within each activity
    for activity in photos_by_activity:
        photos_by_activity[activity].sort(key=lambda x: x.get("sequence") or 0)

    return photos_by_activity


@frappe.whitelist()
def validate_photo_requirements(photo_count, activity_type, has_issue=0):
    """
    Validate photo upload requirements before submission

    Args:
        photo_count (int): Number of photos uploaded
        activity_type (str): INSP/ISSUE/VERIFY/REPAIR
        has_issue (int): 0 or 1, whether issue is being reported

    Returns:
        dict: {"valid": bool, "message": str}

    Raises:
        frappe.ValidationError: If validation fails
    """
    photo_count = int(photo_count)

    # Minimum photo requirements
    if activity_type == "INSP" and photo_count < 1:
        frappe.throw(_("At least 1 inspection photo is required"))

    if activity_type == "ISSUE" and photo_count < 1:
        frappe.throw(_("At least 1 issue photo is required when reporting problems"))

    if activity_type == "VERIFY" and photo_count < 1:
        frappe.throw(_("At least 1 verification photo is required to confirm repair"))

    # Maximum photo limit
    if photo_count > 5:
        frappe.throw(_("Maximum 5 photos allowed per activity"))

    # General requirement: always need at least 1 photo
    if photo_count < 1:
        frappe.throw(_("At least 1 photo is required for all maintenance activities"))

    return {
        "valid": True,
        "message": _("Photo requirements validated")
    }


@frappe.whitelist()
def get_photos_without_metadata():
    """
    Get maintenance records with missing or suspicious photo metadata
    Used by managers for audit trail verification

    Returns:
        list: Records with photo issues
    """
    # Get maintenance logs from last 30 days without photos
    sql = """
        SELECT
            ml.name as log_name,
            ml.asset_name,
            ml.owner as inspector,
            ml.completion_date,
            COUNT(f.name) as photo_count
        FROM `tabAsset Maintenance Log` ml
        LEFT JOIN `tabFile` f ON (
            f.attached_to_doctype = 'Asset Maintenance Log'
            AND f.attached_to_name = ml.name
        )
        WHERE ml.completion_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY ml.name
        HAVING photo_count = 0
        ORDER BY ml.completion_date DESC
    """

    records_without_photos = frappe.db.sql(sql, as_dict=True)

    # Get photos without metadata (missing timestamp, user, etc.)
    photos_without_metadata = frappe.db.sql("""
        SELECT
            f.name,
            f.file_name,
            f.attached_to_doctype,
            f.attached_to_name,
            f.creation,
            f.description
        FROM `tabFile` f
        WHERE f.attached_to_doctype IN ('Asset Maintenance Log', 'Asset Repair')
        AND (f.description IS NULL OR f.description = '')
        AND f.creation >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        ORDER BY f.creation DESC
    """, as_dict=True)

    return {
        "records_without_photos": records_without_photos,
        "photos_without_metadata": photos_without_metadata,
        "total_issues": len(records_without_photos) + len(photos_without_metadata)
    }
