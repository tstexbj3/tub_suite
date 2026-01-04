# Copyright (c) 2025, Tipubon International Co.,Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import get_url


def get_asset_qr_src(asset_name):
    """
    Get QR code source for Asset labels.
    Uses the existing QR List (Asset-Maintenance-{asset_name}) if available,
    otherwise generates a QR code pointing to /maintenance?asset={asset_name}

    Args:
        asset_name: Asset ID

    Returns:
        str: QR image URL (data URI or file URL)
    """
    qr_list_name = f"Asset-Maintenance-{asset_name}"

    # Try to get existing QR List file URL
    existing_qr = frappe.db.get_value("QR List", qr_list_name, "absolute_file_url")

    if existing_qr:
        # Use existing QR List image
        return existing_qr

    # Fallback: Generate QR on-the-fly using QR Foundry
    # This creates a Manual mode QR pointing directly to maintenance portal
    maintenance_url = get_url(f"/maintenance?asset={asset_name}")

    try:
        # Use QR Foundry's generate_qr_manual function if available
        from qr_foundry.api import generate_qr_manual
        result = generate_qr_manual(manual_content=maintenance_url, label_text=asset_name)
        return result.get("data_uri", "")
    except Exception as e:
        frappe.log_error(f"QR generation failed for {asset_name}: {str(e)}")
        # Return a placeholder or empty
        return ""
