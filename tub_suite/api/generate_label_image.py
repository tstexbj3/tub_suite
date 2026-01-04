# Copyright (c) 2025, Tipubon International Co.,Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from PIL import Image, ImageDraw, ImageFont
import qrcode
from io import BytesIO
import base64


@frappe.whitelist()
def generate_label_image(asset_name):
    """
    Generate a complete QR label image (50x30mm) as PNG for Niimbot.
    Uses PIL to create image with QR code + text.

    Args:
        asset_name: Asset ID

    Returns:
        dict: {"image_data": base64_png_data_uri, "filename": "..."}
    """
    # Validate permission
    if not frappe.has_permission("Asset", "read", asset_name):
        frappe.throw(_("No permission to read Asset: {0}").format(asset_name))

    # Get asset data
    asset = frappe.get_doc("Asset", asset_name)

    # Generate QR code
    from qr_foundry.print_helpers import qr_src
    qr_url = qr_src("Asset", asset.name)

    # Parse QR data URI or URL
    qr_image = get_qr_image_from_url(qr_url)

    # Create label image (50mm x 30mm at 300 DPI = 591 x 354 pixels)
    # Use 300 DPI for better quality on thermal printer
    width = 591  # 50mm * 300/25.4
    height = 354  # 30mm * 300/25.4

    # Create white background
    label = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(label)

    # Resize QR code (26mm x 26mm at 300 DPI = 307 x 307 pixels)
    qr_size = 307
    qr_image = qr_image.resize((qr_size, qr_size), Image.Resampling.LANCZOS)

    # Paste QR code on left side (with some padding)
    padding = 24  # ~2mm padding
    label.paste(qr_image, (padding, (height - qr_size) // 2))

    # Text section starts after QR code
    text_x = padding + qr_size + 24  # QR + gap
    text_width = width - text_x - padding

    # Try to load fonts with Thai support
    import glob
    import os

    # Get app path
    app_path = frappe.get_app_path("tub_suite")

    # Search for fonts that support Thai
    font_search_paths = [
        os.path.join(app_path, "../fonts/NotoSansThai.ttf"),  # Our downloaded font
        "/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf",
        "/usr/share/fonts/truetype/thai-tlwg/Sarabun.ttf",
        "/usr/share/fonts/truetype/tlwg/Garuda.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]

    font_path = None
    for path in font_search_paths:
        if os.path.exists(path):
            font_path = path
            break

    # Load fonts
    try:
        if font_path:
            font_brand = ImageFont.truetype(font_path, 28)
            font_id = ImageFont.truetype(font_path, 22)
            font_name = ImageFont.truetype(font_path, 20)
            font_location = ImageFont.truetype(font_path, 18)
        else:
            raise Exception("No suitable font found")
    except Exception as e:
        frappe.log_error(f"Font loading error: {str(e)}")
        # Fallback to default font
        font_brand = ImageFont.load_default()
        font_id = ImageFont.load_default()
        font_name = ImageFont.load_default()
        font_location = ImageFont.load_default()

    # Draw text elements with better spacing
    y_pos = 50

    # Brand
    draw.text((text_x, y_pos), "TUB ASSETS", font=font_brand, fill='black')
    y_pos += 40

    # Asset ID
    asset_id = asset.name
    if len(asset_id) > 22:
        asset_id = asset_id[:19] + "..."
    draw.text((text_x, y_pos), asset_id, font=font_id, fill='black')
    y_pos += 35

    # Asset Name (wrap to 2 lines, better Thai handling)
    asset_name_text = asset.asset_name or asset.item_name or "-"

    # For Thai text, count characters not words
    max_chars_per_line = 16  # Increased for Thai characters

    if len(asset_name_text) > max_chars_per_line:
        # Split into 2 lines
        line1 = asset_name_text[:max_chars_per_line]
        line2 = asset_name_text[max_chars_per_line:max_chars_per_line*2]

        draw.text((text_x, y_pos), line1, font=font_name, fill='#333333')
        y_pos += 30
        if line2:
            draw.text((text_x, y_pos), line2, font=font_name, fill='#333333')
            y_pos += 30
    else:
        draw.text((text_x, y_pos), asset_name_text, font=font_name, fill='#333333')
        y_pos += 35

    # Location (remove emoji, use text icon instead)
    location = asset.location or "ไม่ระบุสถานที่"
    if len(location) > 15:
        location = location[:12] + "..."
    # Use text instead of emoji for compatibility
    draw.text((text_x, y_pos), f">> {location}", font=font_location, fill='#666666')

    # Convert to PNG bytes
    img_buffer = BytesIO()
    label.save(img_buffer, format='PNG', optimize=True)
    img_buffer.seek(0)

    # Convert to base64 data URI
    img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
    data_uri = f"data:image/png;base64,{img_base64}"

    filename = f"QR_Label_{asset.name}.png"

    return {
        "image_data": data_uri,
        "filename": filename
    }


def get_qr_image_from_url(qr_url):
    """
    Get QR code image from URL or data URI.
    Returns PIL Image object.
    """
    if qr_url.startswith('data:image'):
        # Data URI - extract base64
        header, encoded = qr_url.split(',', 1)
        img_data = base64.b64decode(encoded)
        return Image.open(BytesIO(img_data))
    else:
        # Regular URL - download
        import requests
        response = requests.get(qr_url)
        return Image.open(BytesIO(response.content))
