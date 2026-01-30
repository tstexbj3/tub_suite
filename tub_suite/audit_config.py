"""
Complete audit of TUB Suite configuration.

Run on DEV:  bench --site tub execute tub_suite.AUDIT_DEV_VS_PROD.audit_all > dev_config.txt
Run on PROD: bench --site tub.x-desk.tech execute tub_suite.AUDIT_DEV_VS_PROD.audit_all > prod_config.txt

Then compare the two files to see what's missing.
"""

import frappe
import json


def audit_all():
    """Audit all TUB Suite configurations."""

    print("="*100)
    print("TUB SUITE CONFIGURATION AUDIT")
    print("="*100)

    # 1. Custom Fields
    print("\n\n1. CUSTOM FIELDS (Asset Repair)")
    print("-"*100)
    custom_fields = frappe.get_all(
        "Custom Field",
        filters={"dt": "Asset Repair"},
        fields=["fieldname", "label", "fieldtype", "hidden", "depends_on", "read_only_depends_on"],
        order_by="idx"
    )
    print(f"Total Custom Fields: {len(custom_fields)}")
    for cf in custom_fields:
        print(f"  {cf.fieldname}:")
        print(f"    Type: {cf.fieldtype}, Hidden: {cf.hidden}")
        if cf.depends_on:
            print(f"    depends_on: {cf.depends_on}")
        if cf.read_only_depends_on:
            print(f"    read_only_depends_on: {cf.read_only_depends_on}")

    # 2. Property Setters
    print("\n\n2. PROPERTY SETTERS (Asset Repair)")
    print("-"*100)
    property_setters = frappe.get_all(
        "Property Setter",
        filters={"doc_type": "Asset Repair"},
        fields=["field_name", "property", "value"],
        order_by="field_name"
    )
    print(f"Total Property Setters: {len(property_setters)}")
    for ps in property_setters:
        print(f"  {ps.field_name or 'DocType'}.{ps.property} = {ps.value}")

    # 3. Workflows
    print("\n\n3. WORKFLOWS")
    print("-"*100)
    workflows = frappe.get_all("Workflow", filters={"document_type": "Asset Repair"}, pluck="name")
    for wf_name in workflows:
        wf = frappe.get_doc("Workflow", wf_name)
        print(f"  {wf_name}:")
        print(f"    States: {len(wf.states)}")
        for state in wf.states:
            print(f"      - {state.state} (allow_edit: {state.allow_edit})")
        print(f"    Transitions: {len(wf.transitions)}")

    # 4. Server Scripts
    print("\n\n4. SERVER SCRIPTS")
    print("-"*100)
    server_scripts = frappe.get_all(
        "Server Script",
        fields=["name", "script_type", "reference_doctype"],
        order_by="name"
    )
    print(f"Total Server Scripts: {len(server_scripts)}")
    for ss in server_scripts:
        print(f"  {ss.name} ({ss.script_type}) - DocType: {ss.reference_doctype}")

    # 5. Client Scripts
    print("\n\n5. CLIENT SCRIPTS")
    print("-"*100)
    client_scripts = frappe.get_all(
        "Client Script",
        fields=["name", "dt"],
        order_by="name"
    )
    print(f"Total Client Scripts: {len(client_scripts)}")
    for cs in client_scripts:
        print(f"  {cs.name} - DocType: {cs.dt}")

    # 6. Overrides (check if class exists)
    print("\n\n6. DOCTYPE OVERRIDES")
    print("-"*100)
    try:
        from tub_suite.overrides.asset_repair_override import AssetRepairOverride
        print("  ✅ AssetRepairOverride class loaded successfully")
        # Check methods
        methods = [m for m in dir(AssetRepairOverride) if not m.startswith('_')]
        print(f"  Methods: {', '.join(methods[:10])}...")
    except Exception as e:
        print(f"  ❌ AssetRepairOverride failed to load: {e}")

    # 7. Child DocTypes
    print("\n\n7. CHILD DOCTYPES (Grid Columns)")
    print("-"*100)
    child_doctypes = [
        "Repair Spare Part",
        "Parts Inserted Item",
        "Parts Removed Item",
        "Engineering Todo Item"
    ]
    for dt in child_doctypes:
        if frappe.db.exists("DocType", dt):
            meta = frappe.get_meta(dt)
            visible_fields = [f.fieldname for f in meta.fields if f.in_list_view]
            print(f"  {dt}:")
            print(f"    Grid columns: {', '.join(visible_fields)}")
        else:
            print(f"  {dt}: ❌ NOT FOUND")

    # 8. Notifications
    print("\n\n8. NOTIFICATIONS")
    print("-"*100)
    notifications = frappe.get_all(
        "Notification",
        filters={"document_type": "Asset Repair"},
        fields=["name", "subject", "enabled"],
        order_by="name"
    )
    print(f"Total Notifications: {len(notifications)}")
    for n in notifications:
        print(f"  {n.name} - Enabled: {n.enabled}")

    # 9. Print Formats
    print("\n\n9. PRINT FORMATS")
    print("-"*100)
    print_formats = frappe.get_all(
        "Print Format",
        filters={"doc_type": "Asset Repair"},
        fields=["name", "standard", "disabled"],
        order_by="name"
    )
    print(f"Total Print Formats: {len(print_formats)}")
    for pf in print_formats:
        print(f"  {pf.name} - Standard: {pf.standard}, Disabled: {pf.disabled}")

    # 10. Roles
    print("\n\n10. CUSTOM ROLES")
    print("-"*100)
    custom_roles = [
        "Maintenance Inspector",
        "Maintenance Engineer",
        "Supervisor",
        "Maintenance Supervisor",
        "Engineering Supervisor",
        "Engineering Team"
    ]
    for role in custom_roles:
        if frappe.db.exists("Role", role):
            print(f"  ✅ {role}")
        else:
            print(f"  ❌ {role} - NOT FOUND")

    # 11. Fixtures exported
    print("\n\n11. FIXTURE FILES")
    print("-"*100)
    import os
    fixture_path = frappe.get_app_path("tub_suite", "fixtures")
    if os.path.exists(fixture_path):
        fixtures = os.listdir(fixture_path)
        print(f"  Fixture files found: {len(fixtures)}")
        for f in sorted(fixtures):
            fpath = os.path.join(fixture_path, f)
            size = os.path.getsize(fpath)
            print(f"    {f}: {size:,} bytes")
    else:
        print("  ❌ Fixtures directory not found")

    print("\n" + "="*100)
    print("AUDIT COMPLETE")
    print("="*100)


if __name__ == "__main__":
    audit_all()
