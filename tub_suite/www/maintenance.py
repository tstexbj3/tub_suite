# Copyright (c) 2024, Tipubon International Co.,Ltd. and contributors
# For license information, please see license.txt

import frappe
import frappe.sessions
import json
import re

no_cache = 1  # Prevent caching

# Patterns to sanitize boot data
SCRIPT_TAG_PATTERN = re.compile(r"\<script[^<]*\</script\>")
CLOSING_SCRIPT_TAG_PATTERN = re.compile(r"</script\>")


def get_context(context):
    """
    Called by Frappe when serving the maintenance page.
    Provides CSRF token and boot data to the React app.
    """

    # Log that this function is being called
    frappe.logger().info("========== MAINTENANCE get_context() CALLED ==========")
    frappe.logger().info(f"User: {frappe.session.user}")

    # Generate CSRF token
    csrf_token = frappe.sessions.get_csrf_token()
    frappe.logger().info(f"Generated CSRF token: {csrf_token[:20]}...")
    frappe.db.commit()  # Must commit immediately!

    # Get user session data
    if frappe.session.user == "Guest":
        boot = frappe.website.utils.get_boot_data()
    else:
        try:
            boot = frappe.sessions.get()
        except Exception as e:
            frappe.log_error(f"Failed to get session boot data: {str(e)}")
            boot = {}

    # Sanitize boot data to prevent XSS
    boot_json = frappe.as_json(boot, indent=None, separators=(",", ":"))
    boot_json = SCRIPT_TAG_PATTERN.sub("", boot_json)
    boot_json = CLOSING_SCRIPT_TAG_PATTERN.sub("", boot_json)
    boot_json = json.dumps(boot_json)

    # Return context for Jinja template
    context.update({
        "csrf_token": csrf_token,
        "boot": boot_json,
        "build_version": frappe.utils.get_build_version(),
        "app_name": "TUB Maintenance Portal"
    })

    return context


@frappe.whitelist(methods=["POST"], allow_guest=True)
def get_context_for_dev():
    """
    Development-only endpoint for React dev server.
    Returns boot data and CSRF token that would normally be injected by Jinja template.
    """
    if not frappe.conf.developer_mode:
        frappe.throw("This method is only available in developer mode")

    # Generate CSRF token
    csrf_token = frappe.sessions.get_csrf_token()
    frappe.db.commit()

    try:
        boot = frappe.sessions.get()
    except Exception as e:
        frappe.log_error(f"Failed to get session boot data: {str(e)}")
        boot = {}

    # Sanitize boot data
    boot_json = frappe.as_json(boot, indent=None, separators=(",", ":"))
    boot_json = SCRIPT_TAG_PATTERN.sub("", boot_json)
    boot_json = CLOSING_SCRIPT_TAG_PATTERN.sub("", boot_json)

    return {
        "boot": boot_json,
        "csrf_token": csrf_token
    }
