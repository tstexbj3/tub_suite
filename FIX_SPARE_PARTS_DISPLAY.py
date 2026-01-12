#!/usr/bin/env python3
"""
Fix Repair Spare Part table display
Use existing fields, just update which ones show in list view
"""
import frappe

frappe.init(site='tub')
frappe.connect()

print("=" * 80)
print("FIXING REPAIR SPARE PART TABLE DISPLAY")
print("=" * 80)

try:
    # Update field display settings via SQL (faster than loading DocType)

    # Hide fields we don't want in list view
    hide_fields = ['item_code', 'column_break_1', 'uom', 'column_break_2', 'warehouse']

    for fieldname in hide_fields:
        frappe.db.sql("""
            UPDATE `tabDocField`
            SET in_list_view = 0
            WHERE parent = 'Repair Spare Part'
            AND fieldname = %s
        """, (fieldname,))
        print(f"  ✓ Hidden {fieldname} from list view")

    # Show fields we want in list view
    show_fields = {
        'item_name': {'columns': 3},
        'purchase_order': {'columns': 2},
        'qty': {'columns': 1},
        'remarks': {'columns': 2}
    }

    for fieldname, props in show_fields.items():
        frappe.db.sql("""
            UPDATE `tabDocField`
            SET in_list_view = 1,
                columns = %s
            WHERE parent = 'Repair Spare Part'
            AND fieldname = %s
        """, (props['columns'], fieldname))
        print(f"  ✓ Showing {fieldname} in list view (columns: {props['columns']})")

    frappe.db.commit()

    print("\n" + "=" * 80)
    print("✅ FIXED! Table will now show:")
    print("  1. No. (auto)")
    print("  2. รายการ (item_name)")
    print("  3. ใบขอซื้อเลขที่ (purchase_order)")
    print("  4. จำนวน (qty)")
    print("  5. หมายเหตุ (remarks)")
    print("=" * 80)
    print("\nRun: bench --site tub clear-cache")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    print(traceback.format_exc())
