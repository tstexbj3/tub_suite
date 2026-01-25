#!/usr/bin/env python3
"""
RESTORE ASSET REPAIR FIELD VISIBILITY TO WORKING STATE

Run this if someone fucks up the field visibility settings.

Usage:
    cd ~/frappe-bench
    bench --site tub console < apps/tub_suite/RESTORE_FIELD_VISIBILITY.py
    bench clear-cache
"""

import frappe

def restore_field_visibility():
    frappe.init(site='tub')
    frappe.connect()

    print("=" * 80)
    print("RESTORING ASSET REPAIR FIELD VISIBILITY TO WORKING STATE")
    print("=" * 80)

    changes = []

    # 1. Section 3B: Must show in Pending Supervisor Verification, Pending Reporter Confirmation, Finished
    print("\n1. Fixing Section 3B visibility...")

    section_3b_fields = {
        'section_3b_break': 'Section Break',
        'hygiene_status': 'Hygiene Status',
        'cleanliness_before_machine': 'Machine Before',
        'cleanliness_after_machine': 'Machine After',
        'cleanliness_before_area': 'Area Before',
        'cleanliness_after_area': 'Area After',
        'parts_inserted': 'Parts Inserted Table',
        'parts_removed': 'Parts Removed Table',
        'final_remarks': 'Final Remarks',
        'completion_handover_date': 'Completion Date'
    }

    for fieldname, label in section_3b_fields.items():
        cf_name = f'Asset Repair-{fieldname}'
        if frappe.db.exists('Custom Field', cf_name):
            doc = frappe.get_doc('Custom Field', cf_name)

            # Show in these states
            doc.depends_on = 'eval:["Pending Supervisor Verification", "Pending Reporter Confirmation", "Finished"].includes(doc.workflow_state)'

            # Read-only in Pending Reporter Confirmation and Finished
            doc.read_only_depends_on = 'eval:["Pending Reporter Confirmation", "Finished"].includes(doc.workflow_state)'

            doc.save(ignore_permissions=True)
            changes.append(f"✓ {label} ({fieldname})")
            print(f"   ✓ {label}")

    # 2. Reporter Confirmation Section: Only show in Draft
    print("\n2. Fixing Reporter Confirmation section...")

    if frappe.db.exists('Custom Field', 'Asset Repair-reporter_confirmation_section'):
        doc = frappe.get_doc('Custom Field', 'Asset Repair-reporter_confirmation_section')
        doc.depends_on = 'eval:doc.workflow_state == "Draft"'
        doc.save(ignore_permissions=True)
        changes.append("✓ Reporter Confirmation section")
        print("   ✓ Reporter Confirmation section (Draft only)")

    # 3. Section 1: Always visible
    print("\n3. Checking Section 1 fields...")

    section_1_fields = {
        'section_1_break': 'Section 1 Break',
        'repair_source': 'Repair Source',
        'repair_subject': 'Repair Subject',
        'issue_photos': 'Issue Photos',
        'reported_by': 'Reported By',
        'reporter_department': 'Reporter Department'
    }

    for fieldname, label in section_1_fields.items():
        cf_name = f'Asset Repair-{fieldname}'
        if frappe.db.exists('Custom Field', cf_name):
            doc = frappe.get_doc('Custom Field', cf_name)
            if doc.depends_on:
                print(f"   ⚠ {label} has depends_on: {doc.depends_on}")
                print(f"     (Keeping as-is, check if intentional)")

    # Commit all changes
    frappe.db.commit()

    print("\n" + "=" * 80)
    print(f"RESTORE COMPLETE - {len(changes)} fields updated")
    print("=" * 80)

    print("\nChanges made:")
    for change in changes:
        print(f"  {change}")

    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("1. Run: bench clear-cache")
    print("2. Reload Asset Repair form in browser")
    print("3. Test in all workflow states:")
    print("   - Draft: Section 1 visible, Section 3B hidden")
    print("   - Pending Supervisor Verification: Section 3B visible, editable")
    print("   - Pending Reporter Confirmation: Section 3B visible, READ-ONLY")
    print("   - Finished: Section 3B visible, READ-ONLY")
    print("=" * 80)

if __name__ == "__main__":
    restore_field_visibility()
