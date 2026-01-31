"""
Asset Repair Configuration Mega-Sync
====================================
Generated from DEV (site: tub): 2026-01-31T14:30:34.201786
Target: PROD (site: tub.x-desk.tech)

This patch syncs ALL Asset Repair configuration to match DEV.

Usage:
    1. Copy this file to: ~/frappe-bench/apps/tub_suite/tub_suite/patches/mega_sync_dev_to_prod.py
    2. Add to patches.txt: tub_suite.patches.mega_sync_dev_to_prod
    3. Run: bench --site tub.x-desk.tech migrate
    4. Clear cache: bench --site tub.x-desk.tech clear-cache
"""

import frappe
import json

# Configuration data exported from DEV
CONFIG = {
    "custom_fields": {
        "Asset Repair-section_3b_break": {
            "depends_on": "eval:doc.workflow_state==\"Pending Supervisor Verification\" || doc.workflow_state==\"Finished\"",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "amended_from"
        },
        "Asset Repair-final_remarks": {
            "depends_on": "eval:doc.workflow_state==\"Finished\"",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "fm_en_04_section_5"
        },
        "Asset Repair-verification_status": {
            "depends_on": "eval:doc.requires_inspector_verification==1",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 1,
            "in_standard_filter": 1,
            "columns": 0,
            "default": "Pending Verification",
            "options": "\nPending Verification\nVerified - Passed\nVerified - Failed\nNot Required",
            "fetch_from": null,
            "insert_after": "verification_notes"
        },
        "Asset Repair-verification_notes": {
            "depends_on": "eval:doc.requires_inspector_verification==1",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "verification_date"
        },
        "Asset Repair-verification_date": {
            "depends_on": "eval:doc.requires_inspector_verification==1",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 1,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "verified_by"
        },
        "Asset Repair-verified_by": {
            "depends_on": "eval:doc.requires_inspector_verification==1",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 1,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": "User",
            "fetch_from": null,
            "insert_after": "requires_inspector_verification"
        },
        "Asset Repair-requires_inspector_verification": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": "1",
            "options": null,
            "fetch_from": null,
            "insert_after": "verification_section"
        },
        "Asset Repair-verification_section": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 1,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "custom_\u0e43\u0e1a\u0e2a\u0e07\u0e02\u0e2d\u0e07\u0e40\u0e25\u0e02\u0e17"
        },
        "Asset Repair-custom_\u0e43\u0e1a\u0e2a\u0e07\u0e02\u0e2d\u0e07\u0e40\u0e25\u0e02\u0e17": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": "Material Request",
            "fetch_from": null,
            "insert_after": "stock_consumption_details_section"
        },
        "Asset Repair-custom_\u0e01\u0e32\u0e23\u0e14\u0e33\u0e40\u0e19\u0e19\u0e01\u0e32\u0e23": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 1,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": "Asset Repair Engineering Detail",
            "fetch_from": null,
            "insert_after": "custom_\u0e1d\u0e32\u0e22\u0e27\u0e28\u0e27\u0e01\u0e23\u0e23\u0e21"
        },
        "Asset Repair-custom_\u0e1d\u0e32\u0e22\u0e27\u0e28\u0e27\u0e01\u0e23\u0e23\u0e21": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 1,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "total_repair_cost"
        },
        "Asset Repair-custom_\u0e23\u0e30\u0e1a\u0e2a\u0e32\u0e40\u0e2b\u0e15": {
            "depends_on": "eval:doc.custom_\u0e2a\u0e32\u0e40\u0e2b\u0e15=='\u0e2d\u0e37\u0e48\u0e19\u0e46'",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "custom_\u0e2a\u0e32\u0e40\u0e2b\u0e15"
        },
        "Asset Repair-custom_\u0e2a\u0e32\u0e40\u0e2b\u0e15": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": "\u0e02\u0e32\u0e14\u0e01\u0e32\u0e23\u0e1a\u0e33\u0e23\u0e38\u0e07\u0e23\u0e31\u0e01\u0e29\u0e32\n\u0e43\u0e0a\u0e49\u0e07\u0e32\u0e19\u0e1c\u0e34\u0e14\u0e1b\u0e23\u0e30\u0e40\u0e20\u0e17\n\u0e2d\u0e30\u0e44\u0e2b\u0e25\u0e48\u0e44\u0e21\u0e48\u0e21\u0e35\u0e04\u0e38\u0e13\u0e20\u0e32\u0e1e\n\u0e40\u0e1e\u0e34\u0e48\u0e21\u0e2d\u0e32\u0e22\u0e38\u0e01\u0e32\u0e23\u0e43\u0e0a\u0e49\u0e07\u0e32\u0e19\n\u0e2d\u0e37\u0e48\u0e19\u0e46",
            "fetch_from": null,
            "insert_after": "completion_date"
        },
        "Asset Repair-issue_severity": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 1,
            "in_list_view": 1,
            "in_standard_filter": 1,
            "columns": 0,
            "default": null,
            "options": "Minor - Asset Operational\nMajor - Asset Must Stop",
            "fetch_from": null,
            "insert_after": "expected_completion_date"
        },
        "Asset Repair-custom_repair_type": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 1,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 1,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": "\u0e0b\u0e48\u0e2d\u0e21\n\u0e41\u0e01\u0e49\u0e44\u0e02\n\u0e15\u0e34\u0e14\u0e15\u0e31\u0e49\u0e07\u0e43\u0e2b\u0e21\u0e48\n\u0e1b\u0e23\u0e31\u0e1a\u0e1b\u0e23\u0e38\u0e07\n\u0e2d\u0e37\u0e48\u0e19\u0e46",
            "fetch_from": null,
            "insert_after": "repair_status"
        },
        "Asset Repair-expected_completion_date": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 1,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "failure_date"
        },
        "Asset Repair-maintenance_task": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 1,
            "reqd": 0,
            "in_list_view": 1,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "asset_name"
        },
        "Asset Repair-reported_by": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 1,
            "reqd": 0,
            "in_list_view": 1,
            "in_standard_filter": 1,
            "columns": 0,
            "default": null,
            "options": "User",
            "fetch_from": null,
            "insert_after": "error_description"
        },
        "Asset Repair-gm_section1_approval_date": {
            "depends_on": "eval:[\"Pending GM Approval Section 1\",\"Pending Engineering Assessment\",\"Pending Engineering Supervisor Review\",\"Pending GM Final Approval\"].includes(doc.workflow_state)",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 1,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "gm_section1_approved_by"
        },
        "Asset Repair-reporter_confirmation_notes": {
            "depends_on": "eval:doc.workflow_state==\"Finished\"",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "reporter_confirmation_photos"
        },
        "Asset Repair-reporter_confirmation_photos": {
            "depends_on": "eval:doc.workflow_state==\"Finished\"",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "reporter_confirmation_date"
        },
        "Asset Repair-reporter_confirmation_date": {
            "depends_on": "eval:doc.workflow_state==\"Finished\"",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "reporter_confirmation_cb"
        },
        "Asset Repair-reporter_confirmation_section": {
            "depends_on": "eval:doc.workflow_state==\"Finished\"",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "confirmation_date"
        },
        "Asset Repair-custom_column_break_hee8t": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "total_repair_cost"
        },
        "Asset Repair-custom_column_break_iac9m": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "custom_column_break_uqswk"
        },
        "Asset Repair-custom_column_break_uqswk": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "custom_column_break_hee8t"
        },
        "Asset Repair-custom_\u0e2a\u0e33\u0e2b\u0e23\u0e1a\u0e1d\u0e32\u0e22\u0e27\u0e28\u0e27\u0e01\u0e23\u0e23\u0e21_engineering_department_3": {
            "depends_on": "eval:[\"Approved for Repair\",\"Pending Supervisor Verification\",\"Finished\"].includes(doc.workflow_state)",
            "mandatory_depends_on": null,
            "read_only_depends_on": "eval:['Pending GM Final Approval', 'Approved for Repair', 'Pending Supervisor Verification', 'Pending Reporter Confirmation', 'Finished'].includes(doc.workflow_state)",
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "gm_final_approval_date"
        },
        "Asset Repair-custom_section_break_dg3tg": {
            "depends_on": "eval:[\"Pending Engineering Assessment\",\"Pending Engineering Supervisor Review\",\"Pending GM Final Approval\",\"Approved for Repair\",\"Pending Supervisor Verification\",\"Finished\"].includes(doc.workflow_state)",
            "mandatory_depends_on": null,
            "read_only_depends_on": "eval:['Pending GM Final Approval', 'Approved for Repair', 'Pending Supervisor Verification', 'Pending Reporter Confirmation', 'Finished'].includes(doc.workflow_state)",
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "spare_parts_used"
        },
        "Asset Repair-custom_engineering_section": {
            "depends_on": "eval:[\"Pending Engineering Assessment\",\"Pending Engineering Supervisor Review\",\"Pending GM Final Approval\",\"Approved for Repair\",\"Pending Supervisor Verification\",\"Finished\"].includes(doc.workflow_state)",
            "mandatory_depends_on": null,
            "read_only_depends_on": "eval:['Pending GM Final Approval', 'Approved for Repair', 'Pending Supervisor Verification', 'Pending Reporter Confirmation', 'Finished'].includes(doc.workflow_state)",
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "custom_\u0e23\u0e30\u0e1a\u0e2a\u0e32\u0e40\u0e2b\u0e15"
        },
        "Asset Repair-repair_type": {
            "depends_on": "eval:doc.workflow_state!=\"Pending Reporter Confirmation\"",
            "mandatory_depends_on": null,
            "read_only_depends_on": "eval:doc.workflow_state!=\"Draft\"",
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 1,
            "in_standard_filter": 1,
            "columns": 0,
            "default": null,
            "options": "\u0e0b\u0e48\u0e2d\u0e21 (Repair)\n\u0e41\u0e01\u0e49\u0e44\u0e02 (Fix/Correction)\n\u0e15\u0e34\u0e14\u0e15\u0e31\u0e49\u0e07\u0e43\u0e2b\u0e21\u0e48 (New Installation)\n\u0e1b\u0e23\u0e31\u0e1a\u0e1b\u0e23\u0e38\u0e07 (Improvement)",
            "fetch_from": null,
            "insert_after": "section_1_break"
        },
        "Asset Repair-parts_inserted": {
            "depends_on": "eval:doc.workflow_state==\"Pending Supervisor Verification\" || doc.workflow_state==\"Finished\"",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": "Parts Inserted Item",
            "fetch_from": null,
            "insert_after": "cleanliness_after_area"
        },
        "Asset Repair-parts_removed": {
            "depends_on": "eval:doc.workflow_state==\"Pending Supervisor Verification\" || doc.workflow_state==\"Finished\"",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": "Parts Removed Item",
            "fetch_from": null,
            "insert_after": "parts_inserted"
        },
        "Asset Repair-cleanliness_after_area": {
            "depends_on": "eval:doc.workflow_state==\"Pending Supervisor Verification\" || doc.workflow_state==\"Finished\"",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": "\n\u0e2a\u0e30\u0e2d\u0e32\u0e14 (Clean)\n\u0e44\u0e21\u0e48\u0e2a\u0e30\u0e2d\u0e32\u0e14 (Not Clean)",
            "fetch_from": null,
            "insert_after": "cleanliness_before_area"
        },
        "Asset Repair-cleanliness_before_area": {
            "depends_on": "eval:doc.workflow_state==\"Pending Supervisor Verification\" || doc.workflow_state==\"Finished\"",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": "\n\u0e2a\u0e30\u0e2d\u0e32\u0e14 (Clean)\n\u0e44\u0e21\u0e48\u0e2a\u0e30\u0e2d\u0e32\u0e14 (Not Clean)",
            "fetch_from": null,
            "insert_after": "cleanliness_after_machine"
        },
        "Asset Repair-cleanliness_after_machine": {
            "depends_on": "eval:doc.workflow_state==\"Pending Supervisor Verification\" || doc.workflow_state==\"Finished\"",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": "\n\u0e2a\u0e30\u0e2d\u0e32\u0e14 (Clean)\n\u0e44\u0e21\u0e48\u0e2a\u0e30\u0e2d\u0e32\u0e14 (Not Clean)",
            "fetch_from": null,
            "insert_after": "cleanliness_before_machine"
        },
        "Asset Repair-cleanliness_before_machine": {
            "depends_on": "eval:doc.workflow_state==\"Pending Supervisor Verification\" || doc.workflow_state==\"Finished\"",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": "\n\u0e2a\u0e30\u0e2d\u0e32\u0e14 (Clean)\n\u0e44\u0e21\u0e48\u0e2a\u0e30\u0e2d\u0e32\u0e14 (Not Clean)",
            "fetch_from": null,
            "insert_after": "hygiene_status"
        },
        "Asset Repair-hygiene_status": {
            "depends_on": "eval:doc.workflow_state==\"Pending Supervisor Verification\" || doc.workflow_state==\"Finished\"",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": "\n\u0e40\u0e23\u0e35\u0e22\u0e1a\u0e23\u0e49\u0e2d\u0e22/\u0e2a\u0e30\u0e2d\u0e32\u0e14\u0e44\u0e21\u0e48\u0e40\u0e2a\u0e35\u0e48\u0e22\u0e07\u0e15\u0e48\u0e2d\u0e01\u0e32\u0e23\u0e1b\u0e19\u0e40\u0e1b\u0e37\u0e49\u0e2d\u0e19 (Clean)\n\u0e44\u0e21\u0e48\u0e40\u0e23\u0e35\u0e22\u0e1a\u0e23\u0e49\u0e2d\u0e22/\u0e15\u0e49\u0e2d\u0e07\u0e41\u0e01\u0e49\u0e44\u0e02 (Not Clean)",
            "fetch_from": null,
            "insert_after": "section_3b_break"
        },
        "Asset Repair-completion_handover_date": {
            "depends_on": "eval:[\"Approved for Repair\",\"Pending Supervisor Verification\",\"Finished\"].includes(doc.workflow_state)",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 1,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": "",
            "options": null,
            "fetch_from": null,
            "insert_after": "custom_\u0e2a\u0e33\u0e2b\u0e23\u0e1a\u0e1d\u0e32\u0e22\u0e27\u0e28\u0e27\u0e01\u0e23\u0e23\u0e21_engineering_department_3"
        },
        "Asset Repair-supervisor_signature": {
            "depends_on": "eval:doc.workflow_state==\"Pending Supervisor Verification\" || doc.workflow_state==\"Finished\"",
            "mandatory_depends_on": "eval:doc.workflow_state==\"Pending Supervisor Verification\"",
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "custom_supervisor_notes_\u0e2b\u0e21\u0e32\u0e22\u0e40\u0e2b\u0e15\u0e2b\u0e27\u0e2b\u0e19\u0e32"
        },
        "Asset Repair-confirmation_date": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 1,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "supervisor_verification_date"
        },
        "Asset Repair-supervisor_section1_date": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 1,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "custom_gm_signature"
        },
        "Asset Repair-custom_gm_signature": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": "eval:doc.workflow_state!=\"Pending GM Approval Section 1\"",
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "custom_gm_verification_1"
        },
        "Asset Repair-custom_gm_verification_1": {
            "depends_on": "eval:[\"Pending GM Approval Section 1\",\"Pending Engineering Assessment\",\"Pending Engineering Supervisor Review\",\"Pending GM Final Approval\",\"Approved for Repair\",\"Pending Supervisor Verification\",\"Finished\"].includes(doc.workflow_state)",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "supervisor_section1_signature"
        },
        "Asset Repair-custom_column_break_ye9t4": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "section_break_5"
        },
        "Asset Repair-issue_photos_2": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": "eval:doc.workflow_state!=\"Draft\"",
            "hidden": 1,
            "read_only": 1,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "issue_photos"
        },
        "Asset Repair-reporter_confirmation_cb": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "reporter_confirmation_section"
        },
        "Asset Repair-custom_cause_description": {
            "depends_on": "eval:[\"Pending Engineering Assessment\",\"Pending Engineering Supervisor Review\",\"Pending GM Final Approval\",\"Approved for Repair\",\"Pending Supervisor Verification\",\"Finished\"].includes(doc.workflow_state)",
            "mandatory_depends_on": null,
            "read_only_depends_on": "eval:doc.workflow_state!=\"Draft\"",
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "section_break_9"
        },
        "Asset Repair-repair_result_status": {
            "depends_on": "eval:[\"Approved for Repair\",\"Pending Supervisor Verification\",\"Finished\"].includes(doc.workflow_state)",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": "\u0e40\u0e23\u0e35\u0e22\u0e1a\u0e23\u0e49\u0e2d\u0e22 (Satisfactory)\n\u0e44\u0e21\u0e48\u0e40\u0e23\u0e35\u0e22\u0e1a\u0e23\u0e49\u0e2d\u0e22 (Unsatisfactory)\n\u0e2d\u0e37\u0e48\u0e19\u0e46 (Other)",
            "fetch_from": null,
            "insert_after": "completion_handover_date"
        },
        "Asset Repair-manager_approved_by": {
            "depends_on": "eval:[\"Pending Engineering Assessment\",\"Pending Engineering Supervisor Review\",\"Pending GM Final Approval\",\"Approved for Repair\",\"Pending Supervisor Verification\",\"Finished\"].includes(doc.workflow_state)",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 1,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": "User",
            "fetch_from": null,
            "insert_after": "approval_signature"
        },
        "Asset Repair-manager_approval_date": {
            "depends_on": "eval:[\"Pending Engineering Assessment\",\"Pending Engineering Supervisor Review\",\"Pending GM Final Approval\",\"Approved for Repair\",\"Pending Supervisor Verification\",\"Finished\"].includes(doc.workflow_state)",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 1,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "manager_approved_by"
        },
        "Asset Repair-approval_signature": {
            "depends_on": "eval:doc.workflow_state==\"Pending GM Final Approval\"",
            "mandatory_depends_on": "eval:doc.workflow_state==\"Pending GM Final Approval\"",
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "repair_end_date"
        },
        "Asset Repair-eng_supervisor_review_date": {
            "depends_on": "eval:[\"Pending Engineering Assessment\",\"Pending Engineering Supervisor Review\",\"Pending GM Final Approval\",\"Approved for Repair\",\"Pending Supervisor Verification\",\"Finished\"].includes(doc.workflow_state)",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 1,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "eng_supervisor_signature"
        },
        "Asset Repair-eng_supervisor_signature": {
            "depends_on": "eval:doc.workflow_state==\"Pending Engineering Supervisor Review\"",
            "mandatory_depends_on": "eval:[\"Pending Engineering Supervisor Review\",\"Pending GM Final Approval\",\"Approved for Repair\",\"Repair In Progress\",\"Pending Reporter Confirmation\",\"Pending Reporter Supervisor Verification\",\"Finished\"].includes(doc.workflow_state)",
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "repair_start_date"
        },
        "Asset Repair-engineering_operator_signed_by": {
            "depends_on": "eval:[\"Pending Engineering Assessment\",\"Pending Engineering Supervisor Review\",\"Pending GM Final Approval\",\"Approved for Repair\",\"Pending Supervisor Verification\",\"Finished\"].includes(doc.workflow_state)",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 1,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": "User",
            "fetch_from": null,
            "insert_after": "engineering_operator_signature"
        },
        "Asset Repair-engineering_operator_sign_date": {
            "depends_on": "eval:[\"Pending Engineering Assessment\",\"Pending Engineering Supervisor Review\",\"Pending GM Final Approval\",\"Approved for Repair\",\"Pending Supervisor Verification\",\"Finished\"].includes(doc.workflow_state)",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 1,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "engineering_operator_signed_by"
        },
        "Asset Repair-engineering_operator_signature": {
            "depends_on": "eval:doc.workflow_state==\"Pending Engineering Assessment\"",
            "mandatory_depends_on": "eval:doc.workflow_state==\"Pending Engineering Assessment\"",
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "expected_duration_days"
        },
        "Asset Repair-repair_end_date": {
            "depends_on": "eval:[\"Pending Engineering Assessment\",\"Pending Engineering Supervisor Review\",\"Pending GM Final Approval\",\"Approved for Repair\",\"Pending Supervisor Verification\",\"Finished\"].includes(doc.workflow_state)",
            "mandatory_depends_on": "eval:doc.workflow_state==\"Pending Engineering Assessment\"",
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "custom_column_break_owryd"
        },
        "Asset Repair-repair_start_date": {
            "depends_on": "eval:[\"Pending Engineering Assessment\",\"Pending Engineering Supervisor Review\",\"Pending GM Final Approval\",\"Approved for Repair\",\"Pending Supervisor Verification\",\"Finished\"].includes(doc.workflow_state)",
            "mandatory_depends_on": "eval:doc.workflow_state==\"Pending Engineering Assessment\"",
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "custom_column_break_mc64p"
        },
        "Asset Repair-expected_duration_days": {
            "depends_on": "eval:[\"Pending Engineering Assessment\",\"Pending Engineering Supervisor Review\",\"Pending GM Final Approval\",\"Approved for Repair\",\"Pending Supervisor Verification\",\"Finished\"].includes(doc.workflow_state)",
            "mandatory_depends_on": "eval:doc.workflow_state==\"Pending Engineering Assessment\"",
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "custom_section_break_dg3tg"
        },
        "Asset Repair-spare_parts_used": {
            "depends_on": "eval:[\"Pending Engineering Assessment\",\"Pending Engineering Supervisor Review\",\"Pending GM Final Approval\",\"Approved for Repair\",\"Pending Supervisor Verification\",\"Finished\"].includes(doc.workflow_state)",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": "Repair Spare Part",
            "fetch_from": null,
            "insert_after": "custom_engineering_todo_items"
        },
        "Asset Repair-custom_engineering_todo_items": {
            "depends_on": "eval:[\"Pending Engineering Assessment\",\"Pending Engineering Supervisor Review\",\"Pending GM Final Approval\",\"Approved for Repair\",\"Pending Supervisor Verification\",\"Finished\"].includes(doc.workflow_state)",
            "mandatory_depends_on": "eval:doc.workflow_state==\"Pending Engineering Assessment\"",
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": "Asset Repair Engineering Detail",
            "fetch_from": null,
            "insert_after": "custom_cost_type"
        },
        "Asset Repair-custom_cost_type": {
            "depends_on": "eval:[\"Pending Engineering Assessment\",\"Pending Engineering Supervisor Review\",\"Pending GM Final Approval\",\"Approved for Repair\",\"Pending Supervisor Verification\",\"Finished\"].includes(doc.workflow_state)",
            "mandatory_depends_on": "eval:doc.workflow_state==\"Pending Engineering Assessment\"",
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": "\u0e21\u0e35\u0e04\u0e48\u0e32\u0e43\u0e0a\u0e49\u0e08\u0e48\u0e32\u0e22 (With Cost)\n\u0e44\u0e21\u0e48\u0e21\u0e35\u0e04\u0e48\u0e32\u0e43\u0e0a\u0e49\u0e08\u0e48\u0e32\u0e22 (No Cost)",
            "fetch_from": null,
            "insert_after": "action_type"
        },
        "Asset Repair-action_type": {
            "depends_on": "eval:[\"Pending Engineering Assessment\",\"Pending Engineering Supervisor Review\",\"Pending GM Final Approval\",\"Approved for Repair\",\"Pending Supervisor Verification\",\"Finished\"].includes(doc.workflow_state)",
            "mandatory_depends_on": "eval:doc.workflow_state==\"Pending Engineering Assessment\"",
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": "\u0e0a\u0e48\u0e32\u0e07\u0e20\u0e32\u0e22\u0e43\u0e19 (Internal)\n\u0e0a\u0e48\u0e32\u0e07\u0e20\u0e32\u0e22\u0e19\u0e2d\u0e01 (External)",
            "fetch_from": null,
            "insert_after": "custom_engineering_section"
        },
        "Asset Repair-supervisor_verification_date": {
            "depends_on": "eval:doc.workflow_state==\"Finished\"",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 1,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "supervisor_verified_by"
        },
        "Asset Repair-custom_column_break_owryd": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "eng_supervisor_review_date"
        },
        "Asset Repair-custom_column_break_mc64p": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "engineering_operator_sign_date"
        },
        "Asset Repair-gm_final_approval_date": {
            "depends_on": "eval:[\"Pending Engineering Assessment\",\"Pending Engineering Supervisor Review\",\"Pending GM Final Approval\",\"Approved for Repair\",\"Pending Supervisor Verification\",\"Finished\"].includes(doc.workflow_state)",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 1,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "manager_approval_date"
        },
        "Asset Repair-gm_section1_signature": {
            "depends_on": "eval:doc.workflow_state==\"Pending GM Approval Section 1\" && !doc.__islocal",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "gm_section1_notes"
        },
        "Asset Repair-section_1b_break": {
            "depends_on": "eval:doc.workflow_state==\"Draft\" && !doc.__islocal",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "description"
        },
        "Asset Repair-supervisor_section1_signature": {
            "depends_on": "eval:doc.workflow_state==\"Draft\" && !doc.__islocal",
            "mandatory_depends_on": "eval:doc.workflow_state==\"Pending Reporter Supervisor Verification\" && doc.reporter_confirmed != 1",
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "section_1b_break"
        },
        "Asset Repair-reporter_signature": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 1,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "gm_section1_signature"
        },
        "Asset Repair-gm_section1_notes": {
            "depends_on": "eval:doc.workflow_state==\"Pending GM Approval Section 1\"",
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "custom_column_break_hee8t"
        },
        "Asset Repair-section_1_break": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "workflow_state"
        },
        "Asset Repair-received_date": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 1,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "received_by"
        },
        "Asset Repair-received_by": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 1,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": "User",
            "fetch_from": null,
            "insert_after": "reporter_department"
        },
        "Asset Repair-reporter_department": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "reported_by"
        },
        "Asset Repair-issue_photos": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "repair_subject"
        },
        "Asset Repair-repair_subject": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": "eval:doc.workflow_state!=\"Draft\"",
            "hidden": 0,
            "read_only": 0,
            "reqd": 1,
            "in_list_view": 1,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "repair_source"
        },
        "Asset Repair-repair_source": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": "eval:doc.workflow_state!=\"Draft\"",
            "hidden": 0,
            "read_only": 0,
            "reqd": 1,
            "in_list_view": 0,
            "in_standard_filter": 1,
            "columns": 0,
            "default": null,
            "options": "\nPortal (\u0e41\u0e08\u0e49\u0e07\u0e1c\u0e48\u0e32\u0e19\u0e23\u0e30\u0e1a\u0e1a)\nManual (\u0e41\u0e08\u0e49\u0e07\u0e14\u0e49\u0e27\u0e22\u0e15\u0e19\u0e40\u0e2d\u0e07)\nPlanned Maintenance (\u0e15\u0e32\u0e21\u0e41\u0e1c\u0e19)",
            "fetch_from": null,
            "insert_after": "repair_type"
        },
        "Asset Repair-supervisor_verified_by": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 1,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": "User",
            "fetch_from": null,
            "insert_after": "supervisor_signature"
        },
        "Asset Repair-gm_section1_approved_by": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 1,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": "User",
            "fetch_from": null,
            "insert_after": "reporter_signature"
        },
        "Asset Repair-fm_en_04_section_0": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "naming_series"
        },
        "Asset Repair-fm_en_04_section_2": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "actions_performed"
        },
        "Asset Repair-fm_en_04_section_4": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "spare_parts_used"
        },
        "Asset Repair-fm_en_04_section_5": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "parts_removed"
        },
        "Asset Repair-column_break_repair_header": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 0,
            "read_only": 0,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": null,
            "fetch_from": null,
            "insert_after": "received_date"
        },
        "Asset Repair-workflow_state": {
            "depends_on": null,
            "mandatory_depends_on": null,
            "read_only_depends_on": null,
            "hidden": 1,
            "read_only": 1,
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "columns": 0,
            "default": null,
            "options": "Workflow State",
            "fetch_from": null,
            "insert_after": "asset_name"
        }
    },
    "property_setters": {
        "Asset Repair-repair_source-in_list_view": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "repair_source",
            "property": "in_list_view",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-main-field_order": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocType",
            "field_name": null,
            "property": "field_order",
            "property_type": "Data",
            "value": "[\"asset\", \"repair_status\", \"company\", \"column_break_2\", \"asset_name\", \"workflow_state\", \"section_1_break\", \"repair_type\", \"repair_source\", \"repair_subject\", \"issue_photos\", \"issue_photos_2\", \"reported_by\", \"reporter_department\", \"received_by\", \"received_date\", \"column_break_repair_header\", \"maintenance_task\", \"naming_series\", \"fm_en_04_section_0\", \"failure_date\", \"description\", \"section_1b_break\", \"supervisor_section1_signature\", \"custom_gm_verification_1\", \"custom_gm_signature\", \"supervisor_section1_date\", \"section_break_5\", \"custom_column_break_ye9t4\", \"expected_completion_date\", \"issue_severity\", \"column_break_6\", \"completion_date\", \"custom_\\u0e2a\\u0e32\\u0e40\\u0e2b\\u0e15\", \"custom_\\u0e23\\u0e30\\u0e1a\\u0e2a\\u0e32\\u0e40\\u0e2b\\u0e15\", \"custom_engineering_section\", \"action_type\", \"custom_cost_type\", \"custom_engineering_todo_items\", \"spare_parts_used\", \"custom_section_break_dg3tg\", \"expected_duration_days\", \"engineering_operator_signature\", \"engineering_operator_signed_by\", \"engineering_operator_sign_date\", \"custom_column_break_mc64p\", \"repair_start_date\", \"eng_supervisor_signature\", \"eng_supervisor_review_date\", \"custom_column_break_owryd\", \"repair_end_date\", \"approval_signature\", \"manager_approved_by\", \"manager_approval_date\", \"gm_final_approval_date\", \"custom_\\u0e2a\\u0e33\\u0e2b\\u0e23\\u0e1a\\u0e1d\\u0e32\\u0e22\\u0e27\\u0e28\\u0e27\\u0e01\\u0e23\\u0e23\\u0e21_engineering_department_3\", \"completion_handover_date\", \"repair_result_status\", \"section_break_23\", \"downtime\", \"column_break_19\", \"amended_from\", \"section_3b_break\", \"hygiene_status\", \"cleanliness_before_machine\", \"cleanliness_after_machine\", \"cleanliness_before_area\", \"cleanliness_after_area\", \"parts_inserted\", \"parts_removed\", \"fm_en_04_section_5\", \"final_remarks\", \"supervisor_verification_notes\", \"supervisor_signature\", \"supervisor_verified_by\", \"supervisor_verification_date\", \"confirmation_date\", \"reporter_confirmation_section\", \"reporter_confirmation_cb\", \"reporter_confirmation_date\", \"reporter_confirmation_photos\", \"reporter_confirmation_notes\", \"stock_consumption_details_section\", \"column_break_ecxh\", \"column_break_ypxm\", \"requires_inspector_verification\", \"verification_date\", \"verification_notes\", \"verification_status\", \"stock_items\", \"total_repair_cost\", \"column_break_doyp\", \"gm_section1_notes\", \"gm_section1_signature\", \"reporter_signature\", \"gm_section1_approved_by\", \"gm_section1_approval_date\", \"column_break_9\", \"actions_performed\", \"accounting_dimensions_section\", \"cost_center\", \"column_break_14\", \"project\", \"accounting_details\", \"purchase_invoice\", \"capitalize_repair_cost\", \"stock_consumption\", \"column_break_8\", \"repair_cost\", \"asset_depreciation_details_section\", \"increase_in_asset_life\", \"section_break_9\", \"custom_cause_description\"]"
        },
        "Asset Repair-completion_photos-read_only_depends_on": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "completion_photos",
            "property": "read_only_depends_on",
            "property_type": "Data",
            "value": "eval:[\"Pending Reporter Confirmation\", \"Finished\"].includes(doc.workflow_state)"
        },
        "Asset Repair-completion_photos-depends_on": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "completion_photos",
            "property": "depends_on",
            "property_type": "Data",
            "value": "eval:[\"Pending Supervisor Verification\", \"Pending Reporter Confirmation\", \"Finished\"].includes(doc.workflow_state)"
        },
        "Asset Repair-repair_type-depends_on": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "repair_type",
            "property": "depends_on",
            "property_type": "Data",
            "value": "eval:doc.workflow_state!=\"Pending Reporter Confirmation\""
        },
        "Asset Repair-reporter_confirmation_section-depends_on": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "reporter_confirmation_section",
            "property": "depends_on",
            "property_type": "Data",
            "value": "eval:doc.workflow_state!=\"Pending Reporter Confirmation\""
        },
        "Asset Repair-section_break_9-collapsible": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "section_break_9",
            "property": "collapsible",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-section_break_9-hidden": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "section_break_9",
            "property": "hidden",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-section_break_5-collapsible": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "section_break_5",
            "property": "collapsible",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-section_break_5-hidden": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "section_break_5",
            "property": "hidden",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-asset_depreciation_details_section-collapsible": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "asset_depreciation_details_section",
            "property": "collapsible",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-asset_depreciation_details_section-hidden": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "asset_depreciation_details_section",
            "property": "hidden",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-accounting_details-collapsible": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "accounting_details",
            "property": "collapsible",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-accounting_dimensions_section-hidden": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "accounting_dimensions_section",
            "property": "hidden",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-stock_consumption_details_section-collapsible": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "stock_consumption_details_section",
            "property": "collapsible",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-stock_consumption_details_section-hidden": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "stock_consumption_details_section",
            "property": "hidden",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-section_break_23-collapsible": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "section_break_23",
            "property": "collapsible",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-description-read_only_depends_on": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "description",
            "property": "read_only_depends_on",
            "property_type": "Data",
            "value": "eval:doc.workflow_state!=\"Draft\""
        },
        "Asset Repair-repair_type-read_only_depends_on": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "repair_type",
            "property": "read_only_depends_on",
            "property_type": "Data",
            "value": "eval:doc.workflow_state!=\"Draft\""
        },
        "Asset Repair-repair_source-read_only_depends_on": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "repair_source",
            "property": "read_only_depends_on",
            "property_type": "Data",
            "value": "eval:!doc.__islocal"
        },
        "Asset Repair-repair_subject-read_only_depends_on": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "repair_subject",
            "property": "read_only_depends_on",
            "property_type": "Data",
            "value": "eval:doc.workflow_state!=\"Draft\""
        },
        "Asset Repair-custom_issue_severity-read_only_depends_on": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "custom_issue_severity",
            "property": "read_only_depends_on",
            "property_type": "Data",
            "value": "eval:doc.workflow_state!=\"Draft\""
        },
        "Asset Repair-actions_performed-hidden": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "actions_performed",
            "property": "hidden",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-section_break_23-label": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "section_break_23",
            "property": "label",
            "property_type": "Data",
            "value": "\u0e2a\u0e33\u0e2b\u0e23\u0e31\u0e1a\u0e1d\u0e48\u0e32\u0e22\u0e27\u0e34\u0e28\u0e27\u0e01\u0e23\u0e23\u0e21 (Engineering Department) 3"
        },
        "Asset Repair-description-read_only": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "description",
            "property": "read_only",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-repair_status-options": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "repair_status",
            "property": "options",
            "property_type": null,
            "value": "Pending\nUnder Repair\nCompleted\nCancelled"
        },
        "Asset Repair-section_break_23-hidden": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "section_break_23",
            "property": "hidden",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-repair_status-read_only": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "repair_status",
            "property": "read_only",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-company-hidden": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "company",
            "property": "hidden",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-purchase_invoice-hidden": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "purchase_invoice",
            "property": "hidden",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-accounting_details-hidden": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "accounting_details",
            "property": "hidden",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-project-hidden": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "project",
            "property": "hidden",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-accounting_dimensions-hidden": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "accounting_dimensions",
            "property": "hidden",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-cost_center-hidden": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "cost_center",
            "property": "hidden",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-capitalize_repair_cost-hidden": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "capitalize_repair_cost",
            "property": "hidden",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-stock_items-hidden": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "stock_items",
            "property": "hidden",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-stock_consumption-hidden": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "stock_consumption",
            "property": "hidden",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-repair_cost-hidden": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "repair_cost",
            "property": "hidden",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-reported_by-read_only": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "reported_by",
            "property": "read_only",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-failure_date-read_only": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "failure_date",
            "property": "read_only",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-failure_description-read_only": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "failure_description",
            "property": "read_only",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-error_description-read_only": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "error_description",
            "property": "read_only",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-completion_date-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "completion_date",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-repair_status-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "repair_status",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-amended_from-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "amended_from",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-column_break_19-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "column_break_19",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-downtime-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "downtime",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-section_break_23-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "section_break_23",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-increase_in_asset_life-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "increase_in_asset_life",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-asset_depreciation_details_section-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "asset_depreciation_details_section",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-repair_cost-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "repair_cost",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-column_break_8-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "column_break_8",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-stock_consumption-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "stock_consumption",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-capitalize_repair_cost-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "capitalize_repair_cost",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-purchase_invoice-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "purchase_invoice",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-accounting_details-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "accounting_details",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-project-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "project",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-column_break_14-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "column_break_14",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-cost_center-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "cost_center",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-accounting_dimensions_section-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "accounting_dimensions_section",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-actions_performed-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "actions_performed",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-column_break_9-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "column_break_9",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-description-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "description",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-section_break_9-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "section_break_9",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-total_repair_cost-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "total_repair_cost",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-stock_items-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "stock_items",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-stock_consumption_details_section-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "stock_consumption_details_section",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-custom_\u0e23\u0e30\u0e1a\u0e2a\u0e32\u0e40\u0e2b\u0e15-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "custom_\u0e23\u0e30\u0e1a\u0e2a\u0e32\u0e40\u0e2b\u0e15",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-custom_\u0e2a\u0e32\u0e40\u0e2b\u0e15-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "custom_\u0e2a\u0e32\u0e40\u0e2b\u0e15",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-column_break_6-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "column_break_6",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-failure_date-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "failure_date",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-section_break_5-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "section_break_5",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-naming_series-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "naming_series",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-asset_name-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "asset_name",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-column_break_2-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "column_break_2",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-company-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "company",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-asset-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "asset",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-workflow_state-allow_on_submit": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "workflow_state",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "0"
        },
        "Asset Repair-naming_series-options": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "naming_series",
            "property": "options",
            "property_type": "Text",
            "value": "ACC-ASR-.YYYY.-"
        },
        "Asset Repair-repair_status-in_list_view": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "repair_status",
            "property": "in_list_view",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-downtime-in_list_view": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "downtime",
            "property": "in_list_view",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-asset-in_list_view": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "asset",
            "property": "in_list_view",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-asset_name-in_list_view": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocField",
            "field_name": "asset_name",
            "property": "in_list_view",
            "property_type": "Check",
            "value": "1"
        },
        "Asset Repair-main-default_print_format": {
            "doc_type": "Asset Repair",
            "doctype_or_field": "DocType",
            "field_name": null,
            "property": "default_print_format",
            "property_type": "Data",
            "value": "\u0e43\u0e1a\u0e2a\u0e31\u0e48\u0e07\u0e0b\u0e48\u0e2d\u0e21"
        }
    },
    "docfields": {
        "Repair Spare Part.column_break_1": {
            "parent": "Repair Spare Part",
            "fieldname": "column_break_1",
            "in_list_view": 0,
            "columns": 0,
            "read_only": 0,
            "hidden": 0
        },
        "Repair Spare Part.uom": {
            "parent": "Repair Spare Part",
            "fieldname": "uom",
            "in_list_view": 0,
            "columns": 0,
            "read_only": 0,
            "hidden": 0
        },
        "Repair Spare Part.qty": {
            "parent": "Repair Spare Part",
            "fieldname": "qty",
            "in_list_view": 1,
            "columns": 0,
            "read_only": 0,
            "hidden": 0
        },
        "Repair Spare Part.column_break_2": {
            "parent": "Repair Spare Part",
            "fieldname": "column_break_2",
            "in_list_view": 0,
            "columns": 0,
            "read_only": 0,
            "hidden": 0
        },
        "Repair Spare Part.purchase_order": {
            "parent": "Repair Spare Part",
            "fieldname": "purchase_order",
            "in_list_view": 0,
            "columns": 0,
            "read_only": 0,
            "hidden": 0
        },
        "Repair Spare Part.warehouse": {
            "parent": "Repair Spare Part",
            "fieldname": "warehouse",
            "in_list_view": 0,
            "columns": 0,
            "read_only": 0,
            "hidden": 0
        },
        "Repair Spare Part.item_no": {
            "parent": "Repair Spare Part",
            "fieldname": "item_no",
            "in_list_view": 0,
            "columns": 0,
            "read_only": 0,
            "hidden": 0
        },
        "Repair Spare Part.item_code": {
            "parent": "Repair Spare Part",
            "fieldname": "item_code",
            "in_list_view": 0,
            "columns": 0,
            "read_only": 0,
            "hidden": 0
        },
        "Repair Spare Part.remarks": {
            "parent": "Repair Spare Part",
            "fieldname": "remarks",
            "in_list_view": 0,
            "columns": 0,
            "read_only": 0,
            "hidden": 0
        },
        "Repair Spare Part.item_name": {
            "parent": "Repair Spare Part",
            "fieldname": "item_name",
            "in_list_view": 1,
            "columns": 0,
            "read_only": 1,
            "hidden": 0
        },
        "Parts Inserted Item.qty": {
            "parent": "Parts Inserted Item",
            "fieldname": "qty",
            "in_list_view": 1,
            "columns": 0,
            "read_only": 0,
            "hidden": 0
        },
        "Parts Inserted Item.item_code": {
            "parent": "Parts Inserted Item",
            "fieldname": "item_code",
            "in_list_view": 0,
            "columns": 0,
            "read_only": 0,
            "hidden": 0
        },
        "Parts Inserted Item.serial_no": {
            "parent": "Parts Inserted Item",
            "fieldname": "serial_no",
            "in_list_view": 0,
            "columns": 0,
            "read_only": 0,
            "hidden": 0
        },
        "Parts Inserted Item.column_break_1": {
            "parent": "Parts Inserted Item",
            "fieldname": "column_break_1",
            "in_list_view": 0,
            "columns": 0,
            "read_only": 0,
            "hidden": 0
        },
        "Parts Inserted Item.item_name": {
            "parent": "Parts Inserted Item",
            "fieldname": "item_name",
            "in_list_view": 1,
            "columns": 0,
            "read_only": 1,
            "hidden": 0
        },
        "Parts Removed Item.serial_no": {
            "parent": "Parts Removed Item",
            "fieldname": "serial_no",
            "in_list_view": 0,
            "columns": 0,
            "read_only": 0,
            "hidden": 0
        },
        "Parts Removed Item.item_code": {
            "parent": "Parts Removed Item",
            "fieldname": "item_code",
            "in_list_view": 0,
            "columns": 0,
            "read_only": 0,
            "hidden": 0
        },
        "Parts Removed Item.item_name": {
            "parent": "Parts Removed Item",
            "fieldname": "item_name",
            "in_list_view": 1,
            "columns": 0,
            "read_only": 1,
            "hidden": 0
        },
        "Parts Removed Item.disposal_method": {
            "parent": "Parts Removed Item",
            "fieldname": "disposal_method",
            "in_list_view": 0,
            "columns": 0,
            "read_only": 0,
            "hidden": 0
        },
        "Parts Removed Item.qty": {
            "parent": "Parts Removed Item",
            "fieldname": "qty",
            "in_list_view": 1,
            "columns": 0,
            "read_only": 0,
            "hidden": 0
        },
        "Parts Removed Item.column_break_1": {
            "parent": "Parts Removed Item",
            "fieldname": "column_break_1",
            "in_list_view": 0,
            "columns": 0,
            "read_only": 0,
            "hidden": 0
        },
        "Engineering Todo Item.todo_item": {
            "parent": "Engineering Todo Item",
            "fieldname": "todo_item",
            "in_list_view": 1,
            "columns": 0,
            "read_only": 0,
            "hidden": 0
        },
        "Engineering Todo Item.item_no": {
            "parent": "Engineering Todo Item",
            "fieldname": "item_no",
            "in_list_view": 1,
            "columns": 0,
            "read_only": 0,
            "hidden": 0
        },
        "Engineering Todo Item.responsible_person": {
            "parent": "Engineering Todo Item",
            "fieldname": "responsible_person",
            "in_list_view": 1,
            "columns": 0,
            "read_only": 0,
            "hidden": 0
        },
        "Engineering Todo Item.status": {
            "parent": "Engineering Todo Item",
            "fieldname": "status",
            "in_list_view": 1,
            "columns": 0,
            "read_only": 0,
            "hidden": 0
        },
        "Engineering Todo Item.procedure": {
            "parent": "Engineering Todo Item",
            "fieldname": "procedure",
            "in_list_view": 1,
            "columns": 0,
            "read_only": 0,
            "hidden": 0
        }
    },
    "workflow_states": [
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Pending Reporter Confirmation",
            "allow_edit": "Supervisor",
            "doc_status": "0",
            "update_field": null,
            "update_value": null
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Draft",
            "allow_edit": "Supervisor",
            "doc_status": "0",
            "update_field": null,
            "update_value": null
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Pending Supervisor Verification",
            "allow_edit": "Supervisor",
            "doc_status": "0",
            "update_field": null,
            "update_value": null
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Rejected",
            "allow_edit": "All",
            "doc_status": "0",
            "update_field": null,
            "update_value": null
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Pending Engineering Assessment",
            "allow_edit": "All",
            "doc_status": "0",
            "update_field": null,
            "update_value": null
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Pending GM Final Approval",
            "allow_edit": "Maintenance Manager",
            "doc_status": "0",
            "update_field": null,
            "update_value": null
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Pending Engineering Supervisor Review",
            "allow_edit": "Engineering Supervisor",
            "doc_status": "0",
            "update_field": null,
            "update_value": null
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Approved for Repair",
            "allow_edit": "Engineering Supervisor",
            "doc_status": "0",
            "update_field": null,
            "update_value": null
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Finished",
            "allow_edit": "Maintenance Manager",
            "doc_status": "1",
            "update_field": null,
            "update_value": null
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Cancelled",
            "allow_edit": "System Manager",
            "doc_status": "2",
            "update_field": null,
            "update_value": null
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Pending GM Approval Section 1",
            "allow_edit": "Maintenance Manager",
            "doc_status": "0",
            "update_field": null,
            "update_value": null
        }
    ],
    "workflow_transitions": [
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Approved for Repair",
            "action": "Finish Repair",
            "next_state": "Pending Supervisor Verification",
            "allowed": "Engineering Supervisor",
            "allow_self_approval": 1,
            "condition": null
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Pending Supervisor Verification",
            "action": "PM Supervisor Verify",
            "next_state": "Pending Reporter Confirmation",
            "allowed": "Maintenance Supervisor",
            "allow_self_approval": 1,
            "condition": "doc.repair_source == \"Planned Maintenance (\u0e15\u0e32\u0e21\u0e41\u0e1c\u0e19)\""
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Finished",
            "action": "Cancel",
            "next_state": "Cancelled",
            "allowed": "System Manager",
            "allow_self_approval": 1,
            "condition": null
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Pending Engineering Supervisor Review",
            "action": "Supervisor Review Complete",
            "next_state": "Pending GM Final Approval",
            "allowed": "Engineering Supervisor",
            "allow_self_approval": 1,
            "condition": null
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Pending Reporter Confirmation",
            "action": "Reporter Confirm",
            "next_state": "Finished",
            "allowed": "Supervisor",
            "allow_self_approval": 1,
            "condition": null
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Pending GM Approval Section 1",
            "action": "GM Reject",
            "next_state": "Rejected",
            "allowed": "Maintenance Manager",
            "allow_self_approval": 1,
            "condition": null
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Pending GM Final Approval",
            "action": "GM Request Changes",
            "next_state": "Pending Engineering Assessment",
            "allowed": "Maintenance Manager",
            "allow_self_approval": 1,
            "condition": null
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Pending GM Final Approval",
            "action": "GM Final Approve",
            "next_state": "Approved for Repair",
            "allowed": "Maintenance Manager",
            "allow_self_approval": 1,
            "condition": null
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Draft",
            "action": "Supervisor Verify",
            "next_state": "Pending GM Approval Section 1",
            "allowed": "Supervisor",
            "allow_self_approval": 1,
            "condition": null
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Pending Supervisor Verification",
            "action": "Supervisor Verify",
            "next_state": "Pending Reporter Confirmation",
            "allowed": "Supervisor",
            "allow_self_approval": 1,
            "condition": "doc.repair_source != \"Planned Maintenance (\u0e15\u0e32\u0e21\u0e41\u0e1c\u0e19)\""
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Pending Reporter Confirmation",
            "action": "Reporter Confirm",
            "next_state": "Finished",
            "allowed": "Maintenance User",
            "allow_self_approval": 1,
            "condition": null
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Pending Reporter Confirmation",
            "action": "Reporter Confirm",
            "next_state": "Finished",
            "allowed": "Maintenance Supervisor",
            "allow_self_approval": 1,
            "condition": null
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Pending Supervisor Verification",
            "action": "PM Supervisor Reject",
            "next_state": "Approved for Repair",
            "allowed": "Maintenance Supervisor",
            "allow_self_approval": 1,
            "condition": "doc.repair_source == \"Planned Maintenance (\u0e15\u0e32\u0e21\u0e41\u0e1c\u0e19)\""
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Pending Engineering Assessment",
            "action": "Engineering Assessment Complete",
            "next_state": "Pending Engineering Supervisor Review",
            "allowed": "Engineering Team",
            "allow_self_approval": 1,
            "condition": null
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Pending GM Approval Section 1",
            "action": "Gm Approve Section 1",
            "next_state": "Pending Engineering Assessment",
            "allowed": "Maintenance Manager",
            "allow_self_approval": 1,
            "condition": null
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Pending Supervisor Verification",
            "action": "Supervisor Reject",
            "next_state": "Approved for Repair",
            "allowed": "Supervisor",
            "allow_self_approval": 1,
            "condition": "doc.repair_source != \"Planned Maintenance (\u0e15\u0e32\u0e21\u0e41\u0e1c\u0e19)\""
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Pending Supervisor Verification",
            "action": "Supervisor Verify",
            "next_state": "Pending Reporter Confirmation",
            "allowed": "Maintenance Supervisor",
            "allow_self_approval": 1,
            "condition": null
        },
        {
            "parent": "Asset Repair Workflow - Supervisor Only",
            "state": "Pending Supervisor Verification",
            "action": "Supervisor Reject",
            "next_state": "Approved for Repair",
            "allowed": "Maintenance Supervisor",
            "allow_self_approval": 1,
            "condition": null
        }
    ],
    "client_scripts": {
        "Asset Repair - Master Form Control": {
            "script": "frappe.ui.form.on('Asset Repair', {\n    refresh: function(frm) {\n        // === ENGINEERING FIELDS LOCKING ===\n        // Lock engineering fields after engineering work is complete\n        const engineering_locked_states = [\n            'Pending GM Final Approval',\n            'Approved for Repair',\n            'Pending Supervisor Verification',\n            'Pending Reporter Confirmation',\n            'Finished'\n        ];\n\n        if (engineering_locked_states.includes(frm.doc.workflow_state)) {\n            const engineering_fields = [\n                'action_type',\n                'custom_cost_type',\n                'custom_\u0e23\u0e32\u0e22\u0e25\u0e30\u0e40\u0e2d\u0e22\u0e14\u0e01\u0e32\u0e23\u0e14\u0e33\u0e40\u0e19\u0e19\u0e01\u0e32\u0e23',\n                'custom_\u0e23\u0e30\u0e1a\u0e2a\u0e32\u0e40\u0e2b\u0e15',\n                'estimated_cost',\n                'spare_parts_used',\n                'estimated_repair_duration',\n                'assigned_engineer',\n                'engineering_assessment_date',\n                'engineering_assessment_by',\n                'engineering_notes',\n                'supervisor_review_date',\n                'supervisor_reviewed_by',\n                'custom_engineering_todo_items',\n                'expected_duration_days',\n                'repair_start_date',\n                'repair_end_date'\n            ];\n\n            engineering_fields.forEach(field => {\n                if (frm.fields_dict[field]) {\n                    frm.set_df_property(field, 'read_only', 1);\n                }\n            });\n        }\n\n        // === REPORTER FIELDS LOCKING ===\n        // Always lock reported_by\n        frm.set_df_property('reported_by', 'read_only', 1);\n\n        // Allow Supervisor to edit reporter fields ONLY in Draft\n        if (frm.doc.workflow_state === 'Draft' && frappe.user_roles.includes('Maintenance Supervisor')) {\n            frm.set_df_property('failure_date', 'read_only', 0);\n            frm.set_df_property('description', 'read_only', 0);\n            frm.set_df_property('repair_subject', 'read_only', 0);\n        } else {\n            frm.set_df_property('failure_date', 'read_only', 1);\n            frm.set_df_property('description', 'read_only', 1);\n            frm.set_df_property('repair_subject', 'read_only', 1);\n        }\n    }\n});\n",
            "enabled": 1
        }
    },
    "server_scripts": {}
}


def execute():
    """Sync all configuration from DEV to PROD."""

    print("=" * 60)
    print("MEGA-SYNC: Applying DEV configuration to PROD")
    print("Site: tub.x-desk.tech")
    print("=" * 60)

    # 1. Custom Fields
    print("\n[1/7] Syncing Custom Fields...")
    for cf_name, values in CONFIG["custom_fields"].items():
        try:
            if frappe.db.exists("Custom Field", cf_name):
                for field, value in values.items():
                    frappe.db.set_value("Custom Field", cf_name, field, value, update_modified=False)
                print(f"  ✓ {cf_name}")
        except Exception as e:
            print(f"  ✗ {cf_name}: {e}")

    # 2. Property Setters
    print("\n[2/7] Syncing Property Setters...")
    for ps_name, values in CONFIG["property_setters"].items():
        try:
            if frappe.db.exists("Property Setter", ps_name):
                for field, value in values.items():
                    frappe.db.set_value("Property Setter", ps_name, field, value, update_modified=False)
                print(f"  ✓ {ps_name}")
            else:
                # Create new Property Setter
                ps = frappe.new_doc("Property Setter")
                ps.update(values)
                ps.name = ps_name
                ps.insert(ignore_permissions=True)
                print(f"  + Created: {ps_name}")
        except Exception as e:
            print(f"  ✗ {ps_name}: {e}")

    # 3. DocFields (grid columns)
    print("\n[3/7] Syncing DocFields (grid columns)...")
    for key, values in CONFIG["docfields"].items():
        try:
            frappe.db.sql("""
                UPDATE `tabDocField`
                SET in_list_view = %s, columns = %s, read_only = %s, hidden = %s
                WHERE parent = %s AND fieldname = %s
            """, (values["in_list_view"], values["columns"], values["read_only"],
                  values["hidden"], values["parent"], values["fieldname"]))
            print(f"  ✓ {key}")
        except Exception as e:
            print(f"  ✗ {key}: {e}")

    # 4. Workflow States
    print("\n[4/7] Syncing Workflow States...")
    for ws in CONFIG["workflow_states"]:
        try:
            frappe.db.sql("""
                UPDATE `tabWorkflow Document State`
                SET allow_edit = %s, doc_status = %s, update_field = %s, update_value = %s
                WHERE parent = %s AND state = %s
            """, (ws["allow_edit"], ws.get("doc_status"), ws.get("update_field"),
                  ws.get("update_value"), ws["parent"], ws["state"]))
            print(f"  ✓ {ws['state']}")
        except Exception as e:
            print(f"  ✗ {ws['state']}: {e}")

    # 5. Workflow Transitions
    print("\n[5/7] Syncing Workflow Transitions...")
    for wt in CONFIG["workflow_transitions"]:
        try:
            frappe.db.sql("""
                UPDATE `tabWorkflow Transition`
                SET allowed = %s, `condition` = %s, allow_self_approval = %s
                WHERE parent = %s AND state = %s AND action = %s AND next_state = %s
            """, (wt["allowed"], wt["condition"], wt.get("allow_self_approval"),
                  wt["parent"], wt["state"], wt["action"], wt["next_state"]))
            print(f"  ✓ {wt['state']} -> {wt['next_state']}")
        except Exception as e:
            print(f"  ✗ {wt['state']}: {e}")

    # 6. Client Scripts
    print("\n[6/7] Syncing Client Scripts...")
    for cs_name, values in CONFIG["client_scripts"].items():
        try:
            if frappe.db.exists("Client Script", cs_name):
                frappe.db.set_value("Client Script", cs_name, "script", values["script"], update_modified=False)
                frappe.db.set_value("Client Script", cs_name, "enabled", values["enabled"], update_modified=False)
                print(f"  ✓ {cs_name}")
        except Exception as e:
            print(f"  ✗ {cs_name}: {e}")

    # 7. Server Scripts
    print("\n[7/7] Syncing Server Scripts...")
    for ss_name, values in CONFIG["server_scripts"].items():
        try:
            if frappe.db.exists("Server Script", ss_name):
                frappe.db.set_value("Server Script", ss_name, "script", values["script"], update_modified=False)
                frappe.db.set_value("Server Script", ss_name, "disabled", values["disabled"], update_modified=False)
                print(f"  ✓ {ss_name}")
        except Exception as e:
            print(f"  ✗ {ss_name}: {e}")

    # Commit and clear cache
    print("\n" + "=" * 60)
    frappe.db.commit()
    frappe.clear_cache()

    print("✅ MEGA-SYNC COMPLETE!")
    print("=" * 60)
    print("\n⚠️  IMPORTANT: Clear browser cache and hard refresh (Ctrl+Shift+R)")
