from frappe import _

def get_data():
    return [
        {
            "module_name": "Maintenance QR",
            "_doctype": "Maintenance Schedule",
            "color": "#3498db",
            "icon": "octicon octicon-tools",
            "type": "module",
            "label": _("Maintenance QR"),
            "description": _("Asset Maintenance QR System")
        }
    ]
