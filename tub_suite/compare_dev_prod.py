"""
Compare DEV vs PROD configurations field by field.

Usage:
1. On DEV:  bench --site tub execute tub_suite.compare_dev_prod.export_dev_config
2. Copy the output JSON
3. On PROD: bench --site tub.x-desk.tech execute tub_suite.compare_dev_prod.compare_with_dev --kwargs '{"dev_config": <paste JSON here>}'

Or simpler:
1. Save DEV output to file
2. Run comparison
"""

import frappe
import json


def export_dev_config():
    """Export all DEV configurations as JSON."""

    config = {
        "custom_fields": [],
        "property_setters": [],
        "child_doctypes": {}
    }

    # Get all Custom Fields for Asset Repair
    custom_fields = frappe.get_all(
        "Custom Field",
        filters={"dt": "Asset Repair"},
        fields=["fieldname", "hidden", "depends_on", "read_only_depends_on", "mandatory_depends_on"],
        order_by="idx"
    )

    for cf in custom_fields:
        config["custom_fields"].append({
            "fieldname": cf.fieldname,
            "hidden": cf.hidden,
            "depends_on": cf.depends_on,
            "read_only_depends_on": cf.read_only_depends_on,
            "mandatory_depends_on": cf.mandatory_depends_on
        })

    # Get all Property Setters
    property_setters = frappe.get_all(
        "Property Setter",
        filters={"doc_type": "Asset Repair"},
        fields=["field_name", "property", "value"],
        order_by="field_name"
    )

    for ps in property_setters:
        config["property_setters"].append({
            "field_name": ps.field_name,
            "property": ps.property,
            "value": ps.value
        })

    # Get child DocType configurations
    child_doctypes = [
        "Repair Spare Part",
        "Parts Inserted Item",
        "Parts Removed Item",
        "Engineering Todo Item"
    ]

    for dt in child_doctypes:
        if frappe.db.exists("DocType", dt):
            fields = frappe.get_all(
                "DocField",
                filters={"parent": dt},
                fields=["fieldname", "in_list_view", "hidden", "read_only"],
                order_by="idx"
            )
            config["child_doctypes"][dt] = fields

    print(json.dumps(config, indent=2))
    return config


def compare_configs():
    """Compare current site config with another (run this on PROD after getting DEV export)."""

    print("="*100)
    print("COMPARING PRODUCTION WITH DEV")
    print("="*100)

    # Get PROD config
    prod_custom_fields = frappe.get_all(
        "Custom Field",
        filters={"dt": "Asset Repair"},
        fields=["fieldname", "hidden", "depends_on", "read_only_depends_on", "mandatory_depends_on"],
        order_by="idx"
    )

    # Create dict for easy lookup
    prod_cf_dict = {cf.fieldname: cf for cf in prod_custom_fields}

    print("\n\nCUSTOM FIELD DIFFERENCES:")
    print("-"*100)

    # For now, manually list what DEV should have based on audit
    dev_expected = {
        "received_by": {"hidden": 1, "depends_on": None},
        "received_date": {"hidden": 1, "depends_on": None},
        "final_remarks": {"hidden": 0, "depends_on": 'eval:doc.workflow_state=="Finished"'},
        "repair_type": {"depends_on": 'eval:doc.workflow_state!="Pending Reporter Confirmation"', "read_only_depends_on": 'eval:doc.workflow_state!="Draft"'},
        "repair_source": {"read_only_depends_on": 'eval:doc.workflow_state!="Draft"'},
        "repair_subject": {"read_only_depends_on": 'eval:doc.workflow_state!="Draft"'},
        "section_3b_break": {"depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'},
        "hygiene_status": {"depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'},
        "cleanliness_before_machine": {"depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'},
        "cleanliness_after_machine": {"depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'},
        "cleanliness_before_area": {"depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'},
        "cleanliness_after_area": {"depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'},
        "parts_inserted": {"depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'},
        "parts_removed": {"depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'},
        "spare_parts_used": {"depends_on": 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)'},
    }

    differences = []

    for fieldname, expected in dev_expected.items():
        if fieldname not in prod_cf_dict:
            differences.append(f"❌ {fieldname}: NOT FOUND on production")
            continue

        prod_field = prod_cf_dict[fieldname]

        # Check hidden
        if "hidden" in expected and prod_field.hidden != expected["hidden"]:
            differences.append(
                f"❌ {fieldname}.hidden: PROD={prod_field.hidden}, DEV={expected['hidden']}"
            )

        # Check depends_on
        if "depends_on" in expected and prod_field.depends_on != expected["depends_on"]:
            differences.append(
                f"❌ {fieldname}.depends_on:\n"
                f"   PROD: {prod_field.depends_on}\n"
                f"   DEV:  {expected['depends_on']}"
            )

        # Check read_only_depends_on
        if "read_only_depends_on" in expected and prod_field.read_only_depends_on != expected["read_only_depends_on"]:
            differences.append(
                f"❌ {fieldname}.read_only_depends_on:\n"
                f"   PROD: {prod_field.read_only_depends_on}\n"
                f"   DEV:  {expected['read_only_depends_on']}"
            )

    if differences:
        print(f"\nFound {len(differences)} differences:\n")
        for diff in differences:
            print(diff)
            print()
    else:
        print("\n✅ All checked fields match!")

    return differences


def find_all_differences():
    """
    More comprehensive - compare ALL fields between what we see in audit.
    Run this on PROD, paste DEV audit output when prompted.
    """

    print("Comparing ALL Custom Fields...")
    print("="*100)

    # Get all PROD custom fields
    prod_fields = frappe.get_all(
        "Custom Field",
        filters={"dt": "Asset Repair"},
        fields=["fieldname", "hidden", "depends_on", "read_only_depends_on", "mandatory_depends_on"],
        order_by="fieldname"
    )

    # Manually create expected DEV values from the audit output you showed
    # This is tedious but necessary to catch EVERYTHING

    dev_fields = {
        "action_type": {"depends_on": 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)'},
        "approval_signature": {"depends_on": 'eval:doc.workflow_state=="Pending GM Final Approval"'},
        "cleanliness_after_area": {"depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'},
        "cleanliness_after_machine": {"depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'},
        "cleanliness_before_area": {"depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'},
        "cleanliness_before_machine": {"depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'},
        "completion_handover_date": {"depends_on": 'eval:["Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)'},
        "custom_cause_description": {"depends_on": 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)', "read_only_depends_on": 'eval:doc.workflow_state!="Draft"'},
        "custom_cost_type": {"depends_on": 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)'},
        "custom_engineering_section": {"depends_on": 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)', "read_only_depends_on": 'eval:[\'Pending GM Final Approval\', \'Approved for Repair\', \'Pending Supervisor Verification\', \'Pending Reporter Confirmation\', \'Finished\'].includes(doc.workflow_state)'},
        "custom_engineering_todo_items": {"depends_on": 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)'},
        "custom_gm_verification_1": {"depends_on": 'eval:["Pending GM Approval Section 1","Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)'},
        "custom_section_break_dg3tg": {"depends_on": 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)', "read_only_depends_on": 'eval:[\'Pending GM Final Approval\', \'Approved for Repair\', \'Pending Supervisor Verification\', \'Pending Reporter Confirmation\', \'Finished\'].includes(doc.workflow_state)'},
        "custom_สำหรบฝายวศวกรรม_engineering_department_3": {"depends_on": 'eval:["Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)', "read_only_depends_on": 'eval:[\'Pending GM Final Approval\', \'Approved for Repair\', \'Pending Supervisor Verification\', \'Pending Reporter Confirmation\', \'Finished\'].includes(doc.workflow_state)'},
        "eng_supervisor_review_date": {"depends_on": 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)'},
        "eng_supervisor_signature": {"depends_on": 'eval:doc.workflow_state=="Pending Engineering Supervisor Review"'},
        "engineering_operator_sign_date": {"depends_on": 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)'},
        "engineering_operator_signature": {"depends_on": 'eval:doc.workflow_state=="Pending Engineering Assessment"'},
        "engineering_operator_signed_by": {"depends_on": 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)'},
        "expected_duration_days": {"depends_on": 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)'},
        "final_remarks": {"depends_on": 'eval:doc.workflow_state=="Finished"'},
        "gm_final_approval_date": {"depends_on": 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)'},
        "gm_section1_approval_date": {"depends_on": 'eval:["Pending GM Approval Section 1","Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval"].includes(doc.workflow_state)'},
        "gm_section1_notes": {"depends_on": 'eval:doc.workflow_state=="Pending GM Approval Section 1"'},
        "gm_section1_signature": {"depends_on": 'eval:doc.workflow_state=="Pending GM Approval Section 1" && !doc.__islocal'},
        "hygiene_status": {"depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'},
        "manager_approval_date": {"depends_on": 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)'},
        "manager_approved_by": {"depends_on": 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)'},
        "parts_inserted": {"depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'},
        "parts_removed": {"depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'},
        "received_by": {"hidden": 1},
        "received_date": {"hidden": 1},
        "repair_end_date": {"depends_on": 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)'},
        "repair_result_status": {"depends_on": 'eval:["Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)'},
        "repair_source": {"read_only_depends_on": 'eval:doc.workflow_state!="Draft"'},
        "repair_start_date": {"depends_on": 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)'},
        "repair_type": {"depends_on": 'eval:doc.workflow_state!="Pending Reporter Confirmation"', "read_only_depends_on": 'eval:doc.workflow_state!="Draft"'},
        "reporter_confirmation_date": {"depends_on": 'eval:doc.workflow_state=="Finished"'},
        "reporter_confirmation_notes": {"depends_on": 'eval:doc.workflow_state=="Finished"'},
        "reporter_confirmation_photos": {"depends_on": 'eval:doc.workflow_state=="Finished"'},
        "reporter_confirmation_section": {"depends_on": 'eval:doc.workflow_state=="Finished"'},
        "section_1b_break": {"depends_on": 'eval:doc.workflow_state=="Draft" && !doc.__islocal'},
        "section_3b_break": {"depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'},
        "spare_parts_used": {"depends_on": 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)'},
        "supervisor_section1_signature": {"depends_on": 'eval:doc.workflow_state=="Draft" && !doc.__islocal'},
        "supervisor_signature": {"depends_on": 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'},
        "supervisor_verification_date": {"depends_on": 'eval:doc.workflow_state=="Finished"'},
        "custom_ระบสาเหต": {"depends_on": 'eval:doc.custom_สาเหต==\'อื่นๆ\''},
        "issue_photos_2": {"hidden": 1, "read_only_depends_on": 'eval:doc.workflow_state!="Draft"'},
        "repair_subject": {"read_only_depends_on": 'eval:doc.workflow_state!="Draft"'},
        "verification_date": {"depends_on": 'eval:doc.requires_inspector_verification==1'},
        "verification_notes": {"depends_on": 'eval:doc.requires_inspector_verification==1'},
        "verification_status": {"depends_on": 'eval:doc.requires_inspector_verification==1'},
        "verified_by": {"depends_on": 'eval:doc.requires_inspector_verification==1'},
        "custom_gm_signature": {"read_only_depends_on": 'eval:doc.workflow_state!="Pending GM Approval Section 1"'},
    }

    differences = []

    for prod_field in prod_fields:
        fieldname = prod_field.fieldname

        if fieldname not in dev_fields:
            # Field exists on PROD but we don't have expected DEV value
            # Check if it has any visibility rules that might be wrong
            if prod_field.depends_on or prod_field.read_only_depends_on or prod_field.hidden:
                print(f"⚠️  {fieldname}: Has visibility rules on PROD but not tracked in DEV expected list")
            continue

        expected = dev_fields[fieldname]

        # Check hidden
        if "hidden" in expected:
            if prod_field.hidden != expected["hidden"]:
                differences.append(
                    f"❌ {fieldname}.hidden: PROD={prod_field.hidden}, should be {expected['hidden']}"
                )

        # Check depends_on
        if "depends_on" in expected:
            if prod_field.depends_on != expected["depends_on"]:
                differences.append(
                    f"❌ {fieldname}.depends_on:\n"
                    f"   PROD: {repr(prod_field.depends_on)}\n"
                    f"   DEV:  {repr(expected['depends_on'])}"
                )

        # Check read_only_depends_on
        if "read_only_depends_on" in expected:
            if prod_field.read_only_depends_on != expected["read_only_depends_on"]:
                differences.append(
                    f"❌ {fieldname}.read_only_depends_on:\n"
                    f"   PROD: {repr(prod_field.read_only_depends_on)}\n"
                    f"   DEV:  {repr(expected['read_only_depends_on'])}"
                )

    print(f"\n{'='*100}")
    print(f"TOTAL DIFFERENCES FOUND: {len(differences)}")
    print(f"{'='*100}\n")

    for diff in differences:
        print(diff)
        print()

    return differences
