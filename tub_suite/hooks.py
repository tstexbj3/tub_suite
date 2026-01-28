app_name = "tub_suite"
app_title = "TUB Suite"
app_publisher = "Tipubon International Co.,Ltd."
app_description = "Custom modules for Tipubon International Co., Ltd."
app_email = "it@tipubon.com"
app_license = "mit"

# Fixtures - for easy migration to production
# ------------
# IMPORT MODE: These fixtures will be IMPORTED during 'bench migrate'
# The fixture files in tub_suite/fixtures/ will be applied to the database
fixtures = [
    {"dt": "Custom Field", "filters": [["dt", "in", ["Asset Repair", "Asset", "Asset Maintenance"]]]},
    {"dt": "Property Setter", "filters": [["doc_type", "in", ["Asset Repair", "Asset", "Asset Maintenance"]]]},
    {"dt": "Workflow", "filters": [["document_type", "=", "Asset Repair"]]},
    {"dt": "Workflow State"},
    {"dt": "Workflow Action Master"},
    {"dt": "Role", "filters": [["name", "in", ["Maintenance Inspector", "Maintenance Engineer", "Supervisor", "Maintenance Supervisor", "Engineering Supervisor", "Engineering Team"]]]},
    {"dt": "DocType", "filters": [["name", "in", ["Asset Repair Engineering Detail"]]]},
    {"dt": "Notification", "filters": [["is_standard", "=", 0]]},
    {"dt": "Print Format", "filters": [["name", "=", "FM-EN-04"]]},
    {"dt": "Custom DocPerm", "filters": [["role", "in", ["Maintenance User", "Supervisor", "Maintenance Supervisor", "Maintenance Manager", "Engineering Supervisor", "Engineering Team"]]]}
]

# Export fixtures configuration
# When you run: bench --site SITE export-fixtures
# It will use the filters below to export FROM database TO fixture files
export_fixtures = [
    {
        "dt": "Custom Field",
        "filters": [["dt", "in", ["Asset Repair", "Asset", "Asset Maintenance"]]]
    },
    {
        "dt": "Property Setter",
        "filters": [["doc_type", "in", ["Asset Repair", "Asset", "Asset Maintenance"]]]
    },
    {
        "dt": "Workflow",
        "filters": [["document_type", "=", "Asset Repair"]]
    },
    {"dt": "Workflow State"},
    {"dt": "Workflow Action Master"},
    {
        "dt": "Role",
        "filters": [["name", "in", [
            "Maintenance Inspector",
            "Maintenance Engineer",
            "Supervisor",
            "Maintenance Supervisor",
            "Engineering Supervisor",
            "Engineering Team"
        ]]]
    },
    {
        "dt": "DocType",
        "filters": [["name", "in", ["Asset Repair Engineering Detail"]]]
    },
    {
        "dt": "Notification",
        "filters": [["is_standard", "=", 0]]  # Only custom notifications
    },
    {
        "dt": "Print Format",
        "filters": [["name", "=", "FM-EN-04"]]  # Asset Repair print format
    },
    {
        "dt": "Custom DocPerm",
        "filters": [["role", "in", [
            "Maintenance User",
            "Supervisor",
            "Maintenance Supervisor",
            "Maintenance Manager",
            "Engineering Supervisor",
            "Engineering Team"
        ]]]
    }
]

# Scheduled Tasks
# ---------------
# scheduler_events = {
#     "hourly": [
#         "tub_suite.api.maintenance.send_overdue_notifications"
#     ],
# }
scheduler_events = {}

# Web Routes
# ----------
website_route_rules = [
    {"from_route": "/maintenance", "to_route": "maintenance"},
    {"from_route": "/maintenance/<path:path>", "to_route": "maintenance"},
]

# DocType Class Overrides
# ------------------------
override_doctype_class = {
    "Asset Repair": "tub_suite.overrides.asset_repair_override.CustomAssetRepair"
}

# Document Events
# -----------------
doc_events = {
    "Asset Repair": {
        "validate": "tub_suite.overrides.asset_repair_override.validate_asset_repair",
        "before_save": "tub_suite.overrides.asset_repair_override.before_save_asset_repair",
        "before_submit": "tub_suite.overrides.asset_repair_override.before_submit_asset_repair",
        "on_update_after_submit": "tub_suite.overrides.asset_repair_override.on_update_after_submit_asset_repair"
    }
}

# DocType JavaScript
# ------------------
doctype_js = {
    "Asset": "public/js/asset.js"
}

# DocType List View JavaScript
# -----------------------------
doctype_list_js = {
    "Asset": "public/js/asset_list.js"
}

# Jinja Filters and Methods
# --------------------------
jinja = {
    "methods": [
        "tub_suite.utils.qr_helpers.get_asset_qr_src"
    ]
}
