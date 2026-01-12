"""
Hide all old/duplicate sections that are causing clutter
"""
import frappe

def hide():
    """Hide old sections"""

    print("🧹 Hiding old/duplicate sections...")

    # List of old fields to hide
    fields_to_hide = [
        'fm_en_04_section_2',           # Old "Section 2: Spare Parts Used"
        'fm_en_04_section_4',           # Old "Section 4: Hygiene & Safety"
        'fm_en_04_section_5',           # Old "Section 5: Final Remarks"
        'engineer_signature',           # Old engineer signature
        'final_remarks_break',          # Duplicate final remarks section
        'approval_section',             # Old approval section
        'verification_section',         # Old verification section
        'section_1_gm_approval_break',  # Old GM approval (replaced by section_1c_break)
        'eng_supervisor_section_break', # Old supervisor section (replaced by section_2b_break)
        'gm_final_approval_break',      # Old GM final (replaced by section_2c_break)
    ]

    hidden_count = 0

    for fieldname in fields_to_hide:
        if frappe.db.exists('Custom Field', f'Asset Repair-{fieldname}'):
            doc = frappe.get_doc('Custom Field', f'Asset Repair-{fieldname}')
            doc.hidden = 1
            doc.save(ignore_permissions=True)
            hidden_count += 1
            print(f"🙈 Hidden: {fieldname}")
        else:
            print(f"⚠️  Not found: {fieldname}")

    frappe.db.commit()

    print()
    print("=" * 60)
    print(f"✅ Hidden {hidden_count} old/duplicate sections!")
    print()
    print("🔄 Run: bench --site tub clear-cache")
    print("🔄 Then refresh browser")
    print()
    print("📝 Note: Section 1B (Supervisor Verification) will only show when")
    print("   the document moves to 'Pending Reporter Supervisor Verification' state.")
    print()
    print("   To test: Move document from Draft → Pending Reporter Supervisor Verification")
    print("=" * 60)
