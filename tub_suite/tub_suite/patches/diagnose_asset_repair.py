"""
Asset Repair Configuration Diagnostic
======================================
Run this ON PRODUCTION to identify ALL configuration issues at once.

Usage:
    bench --site tub.x-desk.tech execute tub_suite.patches.diagnose_asset_repair.run_diagnostics
"""

import frappe
from collections import defaultdict


def run_diagnostics():
    """
    Comprehensive diagnostic for Asset Repair configuration.
    Run on PRODUCTION to see all issues.
    """

    print("\n" + "=" * 70)
    print("ASSET REPAIR CONFIGURATION DIAGNOSTIC")
    print("=" * 70)

    issues = []
    warnings = []

    # ==========================================
    # 1. CHECK CUSTOM FIELD VISIBILITY
    # ==========================================
    print("\n[1/7] Checking Custom Field visibility rules...")

    custom_fields = frappe.get_all(
        "Custom Field",
        filters={"dt": "Asset Repair"},
        fields=["name", "fieldname", "dt", "depends_on", "hidden", "read_only"]
    )

    for cf in custom_fields:
        if "section" in cf['fieldname'].lower() and not cf.get('depends_on'):
            issues.append(f"Custom Field '{cf['name']}' has no depends_on (section might show in wrong states)")

    print(f"   Found {len(custom_fields)} custom fields")

    # ==========================================
    # 2. CHECK CHILD TABLE GRID COLUMNS
    # ==========================================
    print("\n[2/7] Checking child table grid columns (in_list_view)...")

    child_tables = ["Repair Spare Part", "Parts Inserted Item", "Parts Removed Item", "Engineering Todo Item"]

    for table in child_tables:
        if not frappe.db.exists("DocType", table):
            warnings.append(f"Child table '{table}' does not exist")
            continue

        fields = frappe.get_all(
            "DocField",
            filters={"parent": table, "in_list_view": 1},
            fields=["fieldname", "in_list_view", "columns"]
        )

        visible_count = len(fields)
        field_names = [f['fieldname'] for f in fields]

        if table in ["Repair Spare Part", "Parts Inserted Item", "Parts Removed Item"]:
            if visible_count != 2:
                issues.append(f"{table}: Has {visible_count} grid columns visible (expected 2). Fields: {field_names}")
            else:
                print(f"   ✓ {table}: {visible_count} columns ({', '.join(field_names)})")
        else:
            print(f"   ✓ {table}: {visible_count} columns ({', '.join(field_names)})")

    # ==========================================
    # 3. CHECK WORKFLOW STATES - allow_edit
    # ==========================================
    print("\n[3/7] Checking Workflow state permissions (allow_edit)...")

    workflows = frappe.get_all("Workflow", filters={"document_type": "Asset Repair"}, pluck="name")

    if not workflows:
        issues.append("No workflow found for Asset Repair!")
    else:
        workflow = frappe.get_doc("Workflow", workflows[0])

        for state in workflow.states:
            allow_edit = state.allow_edit or ""
            roles = [r.strip() for r in allow_edit.split(",") if r.strip()]

            if not roles:
                warnings.append(f"State '{state.state}' has no roles in allow_edit (no one can edit)")

            if state.state == "Approved for Repair":
                if "Engineering Supervisor" not in roles:
                    issues.append(f"State 'Approved for Repair' missing Engineering Supervisor. Has: {roles}")

            print(f"   {state.state}: {allow_edit or '(none)'}")

    # ==========================================
    # 4. CHECK WORKFLOW TRANSITIONS - allowed roles
    # ==========================================
    print("\n[4/7] Checking Workflow transitions (allowed roles)...")

    if workflows:
        workflow = frappe.get_doc("Workflow", workflows[0])

        for trans in workflow.transitions:
            allowed = trans.allowed or ""

            if not allowed:
                warnings.append(f"Transition '{trans.state}' -> '{trans.next_state}' has no allowed roles")

            print(f"   {trans.state} --[{trans.action}]--> {trans.next_state}: {allowed or '(none)'}")

    # ==========================================
    # 5. CHECK CLIENT SCRIPTS
    # ==========================================
    print("\n[5/7] Checking Client Scripts...")

    client_scripts = frappe.get_all(
        "Client Script",
        filters={"dt": "Asset Repair"},
        fields=["name", "enabled", "script"]
    )

    for cs in client_scripts:
        status = "✓ Enabled" if cs['enabled'] else "✗ Disabled"
        script_len = len(cs.get('script', '') or '')
        print(f"   {status}: {cs['name']} ({script_len} chars)")

        if cs.get('script'):
            if "Engineering Supervisor" not in cs['script'] and "field_locking" in cs['name'].lower():
                warnings.append(f"Client Script '{cs['name']}' might be missing Engineering Supervisor logic")

    # ==========================================
    # 6. CHECK SERVER SCRIPTS
    # ==========================================
    print("\n[6/7] Checking Server Scripts...")

    server_scripts = frappe.get_all(
        "Server Script",
        filters={"reference_doctype": "Asset Repair"},
        fields=["name", "disabled", "script_type", "doctype_event"]
    )

    for ss in server_scripts:
        status = "✗ Disabled" if ss['disabled'] else "✓ Enabled"
        print(f"   {status}: {ss['name']} ({ss.get('script_type')} on {ss.get('doctype_event')})")

    # ==========================================
    # 7. CHECK OVERRIDE CLASS
    # ==========================================
    print("\n[7/7] Checking Override Class registration...")

    from frappe import get_hooks

    override_doctypes = get_hooks("override_doctype_class", {})
    asset_repair_override = override_doctypes.get("Asset Repair", [])

    if asset_repair_override:
        print(f"   Override class: {asset_repair_override}")

        try:
            from tub_suite.overrides.asset_repair_override import CustomAssetRepair

            if hasattr(CustomAssetRepair, 'validate'):
                print(f"   ✓ validate method exists")

        except ImportError as e:
            issues.append(f"Cannot import override class: {e}")
    else:
        warnings.append("No override class registered for Asset Repair")

    # ==========================================
    # SUMMARY
    # ==========================================
    print("\n" + "=" * 70)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 70)

    if issues:
        print(f"\n❌ CRITICAL ISSUES ({len(issues)}):")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    else:
        print("\n✅ No critical issues found!")

    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")

    # ==========================================
    # PERMISSION MATRIX
    # ==========================================
    print("\n" + "=" * 70)
    print("📋 PERMISSION MATRIX (Workflow States vs Roles)")
    print("-" * 70)

    if workflows:
        workflow = frappe.get_doc("Workflow", workflows[0])

        roles = set()
        for state in workflow.states:
            for role in (state.allow_edit or "").split(","):
                if role.strip():
                    roles.add(role.strip())

        roles = sorted(roles)

        print(f"{'State':<40} | " + " | ".join([r[:15] for r in roles]))
        print("-" * 70)

        for state in workflow.states:
            allow_edit_roles = [r.strip() for r in (state.allow_edit or "").split(",")]
            row = f"{state.state:<40} | "
            for role in roles:
                if role in allow_edit_roles:
                    row += f"{'✓':^15} | "
                else:
                    row += f"{'':^15} | "
            print(row)

    print("\n" + "=" * 70)

    return {"issues": issues, "warnings": warnings}
