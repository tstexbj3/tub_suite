"""
Fix child table grid columns - ALL tables should show 2 columns (item_name, qty).

v2: Corrected configuration - Parts Inserted and Parts Removed should have 2 columns, not 3.
Original patch had wrong configuration (showed item_code which should be hidden).
"""

import frappe


def execute():
    """Update in_list_view for child table fields - ALL show 2 columns."""

    # CORRECT Configuration: ALL 3 parts tables show 2 columns (item_name, qty)
    field_configs = {
        "Repair Spare Part": {
            "item_no": 0,
            "item_code": 0,
            "item_name": 1,
            "qty": 1
        },
        "Parts Inserted Item": {
            "item_code": 0,  # HIDE item_code
            "item_name": 1,
            "qty": 1
        },
        "Parts Removed Item": {
            "item_code": 0,  # HIDE item_code
            "item_name": 1,
            "qty": 1
        },
        "Engineering Todo Item": {
            "item_no": 1,
            "todo_item": 1,
            "procedure": 1,
            "responsible_person": 1,
            "status": 1
        }
    }

    for doctype_name, field_settings in field_configs.items():
        if not frappe.db.exists("DocType", doctype_name):
            print(f"DocType {doctype_name} not found, skipping...")
            continue

        for fieldname, in_list_view_value in field_settings.items():
            # Update in_list_view in database
            frappe.db.sql("""
                UPDATE `tabDocField`
                SET in_list_view = %s
                WHERE parent = %s
                  AND fieldname = %s
            """, (in_list_view_value, doctype_name, fieldname))

            print(f"Updated {doctype_name}.{fieldname}: in_list_view = {in_list_view_value}")

    # Commit changes
    frappe.db.commit()

    # Clear cache so changes take effect
    for doctype_name in field_configs.keys():
        frappe.clear_cache(doctype=doctype_name)

    print("✅ Child table grid columns fixed - ALL parts tables now show 2 columns")
