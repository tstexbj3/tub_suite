app_name = "tub_suite"
app_title = "TUB Suite"
app_publisher = "Tipubon International Co.,Ltd."
app_description = "Custom modules for Tipubon International Co., Ltd."
app_email = "it@tipubon.com"
app_license = "mit"

# Fixtures - for easy migration to production
# ------------
fixtures = [
    {"dt": "Custom Field"},
    {"dt": "Property Setter"},
    {"dt": "Workflow"},
    {"dt": "Workflow State"},
    {"dt": "Workflow Action Master"},
    {"dt": "Role"},
    {"dt": "Notification"},
]

# Include JS & CSS files
# ----------------------
app_include_css = "/assets/tub_suite/css/maintenance.css"
app_include_js = "/assets/tub_suite/js/maintenance.js"

# DocType JS
# ----------
doctype_js = {
    "Asset": "public/js/asset.js",
}

# Scheduled Tasks
# ---------------
scheduler_events = {
    "daily": [
        "tub_suite.api.maintenance.send_overdue_notifications"
    ],
    "weekly": [
        "tub_suite.api.maintenance.generate_weekly_report"
    ],
}

# Document Events
# ---------------
doc_events = {
    "Asset": {
        "after_insert": "tub_suite.api.asset.generate_qr_code",
        "on_update": "tub_suite.api.asset.update_qr_code",
    }
}

# Web Routes
# ----------
# Custom web pages for QR scanner and inspector portal
website_route_rules = [
    {"from_route": "/qr-scanner/<path:path>", "to_route": "qr-scanner"},
    {"from_route": "/maintenance/<path:path>", "to_route": "maintenance"},
]
