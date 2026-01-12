"""
Fix Section 3B visibility - should only show at end of workflow
"""
import frappe

def fix():
    """Fix Section 3B to only show at end of workflow"""

    print("🔧 Fixing Section 3B visibility...")

    # Section 3B should only show in the LAST "Pending Reporter Supervisor Verification"
    # (after reporter confirms), not the first one

    # The condition needs to check if we're in the SECOND occurrence of that state
    # We can check if reporter_confirmed is True as indicator

    section3b_fields = [
        'section_3b_break',
        'hygiene_status',
        'cleanliness_before_machine',
        'cleanliness_after_machine',
        'cleanliness_before_area',
        'cleanliness_after_area',
        'parts_inserted',
        'parts_removed',
        'supervisor_verification_notes',
        'supervisor_signature',
    ]

    # These fields should only show when:
    # - State is "Pending Reporter Supervisor Verification" AND reporter_confirmed is True
    # - OR state is "Finished"

    depends_on_condition = 'eval:(doc.workflow_state=="Pending Reporter Supervisor Verification" && doc.reporter_confirmed==1) || doc.workflow_state=="Finished"'

    updated = 0
    for fieldname in section3b_fields:
        if frappe.db.exists('Custom Field', f'Asset Repair-{fieldname}'):
            field = frappe.get_doc('Custom Field', f'Asset Repair-{fieldname}')
            field.depends_on = depends_on_condition
            field.save(ignore_permissions=True)
            updated += 1
            print(f"👁️  Updated: {fieldname}")

    # Also hide section_4_break and final_remarks in Draft/early states
    # Final remarks should always be visible at the end
    if frappe.db.exists('Custom Field', 'Asset Repair-section_4_break'):
        field = frappe.get_doc('Custom Field', 'Asset Repair-section_4_break')
        # Move it to very end - after supervisor_signature
        field.insert_after = 'supervisor_signature'
        field.depends_on = None  # Always visible
        field.save(ignore_permissions=True)
        print(f"📌 Moved: section_4_break → after supervisor_signature")

    frappe.db.commit()

    print()
    print("=" * 60)
    print(f"✅ Updated {updated} fields in Section 3B")
    print()
    print("📋 Section 3B will now only show when:")
    print("   • State = 'Pending Reporter Supervisor Verification'")
    print("   • AND reporter_confirmed = True (after reporter confirms)")
    print("   • OR State = 'Finished'")
    print()
    print("📋 To test workflow:")
    print("   1. Open document ACC-ASR-2026-00001")
    print("   2. Click 'Save' button first")
    print("   3. Then click 'Actions → Submit'")
    print("   4. Section 1B should appear for supervisor")
    print()
    print("🔄 Run: bench --site tub clear-cache")
    print("🔄 Then refresh browser")
    print("=" * 60)
