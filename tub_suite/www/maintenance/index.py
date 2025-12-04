# -*- coding: utf-8 -*-
import frappe

def get_context(context):
    # Require login
    if frappe.session.user == 'Guest':
        frappe.throw(_("Please login to access maintenance portal"), frappe.PermissionError)

    context.no_cache = 1
    context.show_sidebar = False
