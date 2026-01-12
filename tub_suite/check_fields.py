"""
Check which fields are causing issues in Asset Repair form
"""
import frappe

def check():
    """Check problematic fields"""

    print("=" * 60)
    print("Checking Asset Repair form fields...")
    print("=" * 60)

    # Check all custom fields
    fields = frappe.get_all('Custom Field',
        filters={'dt': 'Asset Repair'},
        fields=['fieldname', 'label', 'hidden', 'insert_after'],
        order_by='fieldname')

    print("\n=== Fields with 'spare', 'section', 'engineer', 'final' ===\n")
    for f in fields:
        fname = f['fieldname'].lower()
        if any(x in fname for x in ['spare', 'section', 'engineer', 'final']):
            print(f"{f['fieldname']:40} | hidden={str(f['hidden']):5} | {f.get('label', '')}")

    print("\n=== Checking Section 1B ===\n")
    if frappe.db.exists('Custom Field', 'Asset Repair-section_1b_break'):
        field = frappe.get_doc('Custom Field', 'Asset Repair-section_1b_break')
        print("✅ section_1b_break EXISTS")
        print(f"   hidden: {field.hidden}")
        print(f"   depends_on: {field.depends_on}")
        print(f"   insert_after: {field.insert_after}")
    else:
        print("❌ section_1b_break NOT FOUND")

    print("\n=== Checking current document ===\n")
    doc = frappe.get_doc('Asset Repair', 'ACC-ASR-2026-00001')
    print(f"Document: {doc.name}")
    print(f"Workflow State: {doc.workflow_state}")
    print(f"Docstatus: {doc.docstatus}")

    print("\n" + "=" * 60)
