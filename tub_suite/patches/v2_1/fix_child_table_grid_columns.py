"""
Fix child table grid column visibility for Asset Repair child DocTypes.

This patch updates in_list_view property for fields in:
- Repair Spare Part
- Parts Inserted Item
- Parts Removed Item
- Engineering Todo Item

Background:
- Frappe fixtures don't update existing DocType field properties
- JSON files may have been updated but database not synced
- This ensures production matches intended configuration
"""

import frappe


def execute():
    """Update in_list_view for child table fields."""

    # Configuration: {DocType: {fieldname: in_list_view}}
    field_configs = {
        "Repair Spare Part": {
            # Only show: Item Name (manual entry) and Quantity
            "item_no": 0,
            "item_code": 0,
            "item_name": 1,
            "qty": 1
        },
        "Parts Inserted Item": {
            # Show: Item Code, Item Name, Quantity
            "item_code": 1,
            "item_name": 1,
            "qty": 1
        },
        "Parts Removed Item": {
            # Show: Item Code, Item Name, Quantity
            "item_code": 1,
            "item_name": 1,
            "qty": 1
        },
        "Engineering Todo Item": {
            # Show all fields: Item No, Todo, Procedure, Person, Status
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

        # Get DocType meta
        meta = frappe.get_meta(doctype_name)

        for fieldname, in_list_view_value in field_settings.items():
            # Find field in meta
            field = meta.get_field(fieldname)
            if not field:
                print(f"Field {fieldname} not found in {doctype_name}, skipping...")
                continue

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

    print("Child table grid column fix completed")
