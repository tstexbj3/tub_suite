# Copyright (c) 2025, Tipubon International Co.,Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json
import base64
from io import BytesIO


@frappe.whitelist()
def batch_print_qr_labels(asset_names):
    """
    Generate continuous thermal label HTML for Niimbot B1 printer.
    Each asset gets one 50×30mm label with page-break-after for continuous tape printing.

    Args:
        asset_names: JSON array of asset names

    Returns:
        dict: {"html": rendered_html}
    """
    from tub_suite.utils.qr_helpers import get_asset_qr_src

    # Parse asset names if JSON string
    if isinstance(asset_names, str):
        asset_names = json.loads(asset_names)

    if not asset_names:
        frappe.throw(_("No assets selected"))

    # Validate permissions for each asset
    for asset_name in asset_names:
        if not frappe.has_permission("Asset", "read", asset_name):
            frappe.throw(_("No permission to read Asset: {0}").format(asset_name))

    # Fetch asset data
    assets = []
    for asset_name in asset_names:
        try:
            asset = frappe.get_doc("Asset", asset_name)

            # Generate QR URL using our custom helper
            qr_url = get_asset_qr_src(asset.name)

            assets.append({
                "name": asset.name,
                "asset_name": asset.asset_name or asset.item_name or "-",
                "location": asset.location or "ไม่ระบุสถานที่",
                "qr_url": qr_url
            })
        except Exception as e:
            frappe.log_error(f"Error processing asset {asset_name}: {str(e)}")
            frappe.throw(_("Error loading Asset {0}: {1}").format(asset_name, str(e)))

    # Render batch template
    html = frappe.render_template(
        "tub_suite/tub_suite/print_format/asset_qr_label_batch.html",
        {"assets": assets}
    )

    return {"html": html, "count": len(assets)}


@frappe.whitelist()
def generate_label_png(asset_name):
    """
    Generate a PNG image of the QR label for Niimbot import.
    Uses html2image or similar to convert the HTML label to PNG.

    Args:
        asset_name: Asset ID

    Returns:
        dict: {"png_data": base64_data_uri}
    """
    from qr_foundry.print_helpers import qr_src

    # Validate permission
    if not frappe.has_permission("Asset", "read", asset_name):
        frappe.throw(_("No permission to read Asset: {0}").format(asset_name))

    # Get asset data
    asset = frappe.get_doc("Asset", asset_name)

    # Generate QR URL
    qr_url = qr_src("Asset", asset.name)

    # Render HTML template
    html = frappe.render_template(
        "tub_suite/tub_suite/print_format/asset_qr_label_50x30mm/asset_qr_label_50x30mm.html",
        {"doc": asset}
    )

    # Try to convert HTML to PNG using various methods
    try:
        # Method 1: Use wkhtmltoimage if available
        png_data = html_to_png_wkhtmltoimage(html, asset_name)
        if png_data:
            return {"png_data": png_data}
    except:
        pass

    # Method 2: Return HTML with instructions to screenshot
    # This is a fallback - user will need to use browser screenshot
    frappe.msgprint({
        "title": _("PNG Generation"),
        "message": _("""PNG generation requires additional setup.<br><br>
        <b>Quick Alternative:</b><br>
        1. Open Print → Asset QR Label 50x30mm<br>
        2. Right-click on the label → Save as image<br>
        3. Or use Windows Snipping Tool (Win + Shift + S)<br>
        4. Import PNG into Niimbot software"""),
        "indicator": "orange"
    })

    # Return the HTML so user can open it
    return {"html": html, "message": "Use screenshot tool to capture label"}


def html_to_png_wkhtmltoimage(html, filename):
    """
    Convert HTML to PNG using wkhtmltoimage
    Returns base64 data URI
    """
    import subprocess
    import tempfile
    import os

    try:
        # Create temp files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as html_file:
            html_file.write(html)
            html_path = html_file.name

        png_path = tempfile.mktemp(suffix='.png')

        # Run wkhtmltoimage
        cmd = [
            'wkhtmltoimage',
            '--width', '189',  # 50mm at 96dpi
            '--height', '113', # 30mm at 96dpi
            '--quality', '100',
            html_path,
            png_path
        ]

        result = subprocess.run(cmd, capture_output=True, timeout=10)

        if result.returncode == 0 and os.path.exists(png_path):
            # Read PNG and convert to base64
            with open(png_path, 'rb') as f:
                png_bytes = f.read()
                png_base64 = base64.b64encode(png_bytes).decode('utf-8')
                data_uri = f"data:image/png;base64,{png_base64}"

            # Cleanup
            os.unlink(html_path)
            os.unlink(png_path)

            return data_uri

        # Cleanup on failure
        if os.path.exists(html_path):
            os.unlink(html_path)
        if os.path.exists(png_path):
            os.unlink(png_path)

    except Exception as e:
        frappe.log_error(f"PNG generation failed: {str(e)}")

    return None
