import frappe

def get_context(context):
    context.no_cache = 1
    
    # Check if user is logged in
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/maintenance"
        raise frappe.Redirect
    
    # Check if user has inspector role
    roles = frappe.get_roles()
    if "Maintenance Inspector" not in roles and "Maintenance Manager" not in roles:
        frappe.throw("Access Denied: You need Maintenance Inspector or Manager role")
    
    context.title = "Maintenance Inspector Portal"
    return context
