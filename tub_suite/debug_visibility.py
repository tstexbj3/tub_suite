"""
Debug why Supervisor section isn't showing and Final Remarks is in wrong place
"""
import frappe

def debug():
    """Debug field visibility and positioning"""

    print("=" * 60)
    print("Debugging Asset Repair Form Issues")
    print("=" * 60)

    # Check document state
    doc = frappe.get_doc('Asset Repair', 'ACC-ASR-2026-00001')
    print(f"\n📄 Document: {doc.name}")
    print(f"   Workflow State: {doc.workflow_state}")
    print(f"   Reporter Confirmed: {doc.get('reporter_confirmed')}")

    # Check Section 1B settings
    print(f"\n🔍 Checking Section 1B (Supervisor Verification):")
    if frappe.db.exists('Custom Field', 'Asset Repair-section_1b_break'):
        field = frappe.get_doc('Custom Field', 'Asset Repair-section_1b_break')
        print(f"   ✅ Exists")
        print(f"   Hidden: {field.hidden}")
        print(f"   Depends On: {field.depends_on}")
        print(f"   Insert After: {field.insert_after}")

        # Evaluate the condition
        condition = field.depends_on
        if condition:
            # Check if condition should be true
            workflow_match = doc.workflow_state == "Pending Reporter Supervisor Verification"
            reporter_confirmed = doc.get('reporter_confirmed') == 1
            print(f"\n   📊 Condition evaluation:")
            print(f"      workflow_state == 'Pending Reporter Supervisor Verification': {workflow_match}")
            print(f"      reporter_confirmed != 1: {not reporter_confirmed}")
            print(f"      Should show: {workflow_match and not reporter_confirmed}")
    else:
        print(f"   ❌ NOT FOUND")

    # Check Final Remarks positioning
    print(f"\n📌 Checking Final Remarks positioning:")

    if frappe.db.exists('Custom Field', 'Asset Repair-section_4_break'):
        field = frappe.get_doc('Custom Field', 'Asset Repair-section_4_break')
        print(f"   section_4_break:")
        print(f"      Insert After: {field.insert_after}")
        print(f"      Hidden: {field.hidden}")

    if frappe.db.exists('Custom Field', 'Asset Repair-final_remarks'):
        field = frappe.get_doc('Custom Field', 'Asset Repair-final_remarks')
        print(f"   final_remarks:")
        print(f"      Insert After: {field.insert_after}")
        print(f"      Hidden: {field.hidden}")

    # Check what field comes before final_remarks
    print(f"\n🔗 Field chain to Final Remarks:")
    current = 'final_remarks'
    for i in range(10):  # Follow chain backwards
        if frappe.db.exists('Custom Field', f'Asset Repair-{current}'):
            field = frappe.get_doc('Custom Field', f'Asset Repair-{current}')
            print(f"      {current} ← {field.insert_after}")
            current = field.insert_after
            if not current or current == 'None':
                break
        else:
            break

    print("\n" + "=" * 60)
