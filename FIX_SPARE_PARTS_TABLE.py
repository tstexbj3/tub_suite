#!/usr/bin/env python3
"""
Fix Repair Spare Part child table structure
Restore the fields that were working before migrate broke it
"""
import frappe

frappe.init(site='tub')
frappe.connect()

print("=" * 80)
print("FIXING REPAIR SPARE PART CHILD TABLE")
print("=" * 80)

# First, check if we need to enable developer mode
developer_mode = frappe.conf.get('developer_mode')
if not developer_mode:
    print("\n⚠️  Developer mode is OFF")
    print("Enabling developer mode temporarily...")
    frappe.db.sql("""
        UPDATE `tabSingles`
        SET value = '1'
        WHERE doctype = 'System Settings'
        AND field = 'developer_mode'
    """)
    frappe.db.commit()
    print("✓ Developer mode enabled")

# Get the Repair Spare Part DocType
try:
    doctype = frappe.get_doc("DocType", "Repair Spare Part")

    print("\n📋 Current fields in Repair Spare Part:")
    for field in doctype.fields:
        print(f"  - {field.fieldname} ({field.fieldtype}): {field.label}")

    # Define the fields we need
    required_fields = [
        {
            'fieldname': 'item_description',
            'label': 'รายการ',
            'fieldtype': 'Data',
            'in_list_view': 1,
            'columns': 3
        },
        {
            'fieldname': 'purchase_order_no',
            'label': 'ใบขอซื้อเลขที่',
            'fieldtype': 'Data',
            'in_list_view': 1,
            'columns': 2
        },
        {
            'fieldname': 'quantity',
            'label': 'จำนวน',
            'fieldtype': 'Int',
            'in_list_view': 1,
            'columns': 1
        },
        {
            'fieldname': 'remarks',
            'label': 'หมายเหตุ',
            'fieldtype': 'Small Text',
            'in_list_view': 1,
            'columns': 2
        }
    ]

    print("\n🔧 Required fields:")
    for field in required_fields:
        print(f"  - {field['fieldname']}: {field['label']}")

    # Check which fields are missing
    existing_fieldnames = [f.fieldname for f in doctype.fields]
    missing_fields = [f for f in required_fields if f['fieldname'] not in existing_fieldnames]

    if missing_fields:
        print(f"\n⚠️  Missing {len(missing_fields)} fields - need to add them")
        print("This requires developer mode and DocType modification")
        print("\nRun these commands:")
        print("1. bench --site tub set-config developer_mode 1")
        print("2. bench --site tub clear-cache")
        print("3. Edit Repair Spare Part DocType manually in the UI")
    else:
        print("\n✅ All required fields exist")

        # Update field properties (labels, in_list_view, columns)
        for field_def in required_fields:
            for field in doctype.fields:
                if field.fieldname == field_def['fieldname']:
                    field.label = field_def['label']
                    field.in_list_view = field_def['in_list_view']
                    field.columns = field_def['columns']
                    print(f"  ✓ Updated {field.fieldname}")

        doctype.save()
        frappe.db.commit()
        print("\n✅ Repair Spare Part table fixed!")
        print("Run: bench --site tub clear-cache")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    print(traceback.format_exc())

print("=" * 80)
