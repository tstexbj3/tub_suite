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

# Include JS & CSS files (removed broken asset.js reference)
# ----------------------
# app_include_css = "/assets/tub_suite/css/maintenance.css"
# app_include_js = "/assets/tub_suite/js/maintenance.js"

# Scheduled Tasks
# ---------------
scheduler_events = {
    "hourly": [
        "tub_suite.api.maintenance.send_overdue_notifications"
    ],
}

# Web Routes
# ----------
website_route_rules = [
    {"from_route": "/maintenance/<path:path>", "to_route": "maintenance"},
]

# DocType Class Overrides
# ------------------------
# Override ERPNext's Asset Repair controller with our custom one
override_doctype_class = {
    "Asset Repair": "tub_suite.overrides.asset_repair_override.CustomAssetRepair"
}

# Document Events
# ---------------
# Hook into Asset Repair document to add security validation
doc_events = {
    "Asset Repair": {
        "validate": "tub_suite.api.asset.validate_asset_repair_permissions",
        "before_save": "tub_suite.api.asset.validate_asset_repair_permissions",
        "validate_update_after_submit": "tub_suite.api.asset.validate_asset_repair_permissions",
        "before_update_after_submit": "tub_suite.api.asset.validate_asset_repair_permissions",
    }
}
