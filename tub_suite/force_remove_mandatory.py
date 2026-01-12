"""
Force remove mandatory from engineer_signature and check all mandatory fields
"""
import frappe

def fix():
    """Force remove mandatory and check all mandatory fields"""

    print("🔍 Checking all mandatory fields in Asset Repair...")

    # Get all custom fields
    fields = frappe.get_all('Custom Field',
        filters={'dt': 'Asset Repair'},
        fields=['fieldname', 'label', 'reqd', 'mandatory_depends_on', 'hidden'],
        order_by='fieldname')

    print("\n📋 Mandatory fields:")
    mandatory_found = []

    for f in fields:
        if f['reqd'] == 1 or f.get('mandatory_depends_on'):
            mandatory_found.append(f)
            print(f"   • {f['fieldname']:40} | reqd={f['reqd']} | mandatory_depends_on={f.get('mandatory_depends_on')} | hidden={f['hidden']}")

    # Force fix engineer_signature
    if frappe.db.exists('Custom Field', 'Asset Repair-engineer_signature'):
        field = frappe.get_doc('Custom Field', 'Asset Repair-engineer_signature')
        print(f"\n🔧 Fixing engineer_signature:")
        print(f"   Before: reqd={field.reqd}, mandatory_depends_on={field.mandatory_depends_on}, hidden={field.hidden}")

        field.reqd = 0
        field.mandatory_depends_on = None
        field.hidden = 1
        field.save(ignore_permissions=True)

        print(f"   After:  reqd={field.reqd}, mandatory_depends_on={field.mandatory_depends_on}, hidden={field.hidden}")

    # Check if there are Property Setters overriding this
    print(f"\n🔍 Checking for Property Setters on engineer_signature:")
    property_setters = frappe.get_all('Property Setter',
        filters={
            'doc_type': 'Asset Repair',
            'field_name': 'engineer_signature'
        },
        fields=['property', 'value'])

    if property_setters:
        print("   Found Property Setters:")
        for ps in property_setters:
            print(f"      {ps.property} = {ps.value}")
    else:
        print("   No Property Setters found")

    frappe.db.commit()
    frappe.clear_cache(doctype='Asset Repair')

    print()
    print("=" * 60)
    print("✅ Fixed engineer_signature")
    print()
    print("🔄 You must restart bench for this to take effect:")
    print("   Ctrl+C to stop bench")
    print("   bench start")
    print("=" * 60)
