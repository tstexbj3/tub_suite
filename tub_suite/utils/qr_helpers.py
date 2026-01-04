# Copyright (c) 2025, Tipubon International Co.,Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import get_url
import qrcode
from io import BytesIO
import base64


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

    # Fallback: Generate QR on-the-fly pointing directly to maintenance portal
    maintenance_url = get_url(f"/maintenance?asset={asset_name}")

    try:
        # Generate QR code using qrcode library
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(maintenance_url)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64 data URI
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        data_uri = f"data:image/png;base64,{img_base64}"

        return data_uri
    except Exception as e:
        frappe.log_error(f"QR generation failed for {asset_name}: {str(e)}")
        # Return a placeholder or empty
        return ""
