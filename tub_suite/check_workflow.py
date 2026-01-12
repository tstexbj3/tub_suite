"""
Check workflow configuration for Asset Repair
"""
import frappe
import frappe.model.workflow as wf

def check():
    """Check workflow setup"""

    print("=" * 60)
    print("Checking Asset Repair Workflow Configuration")
    print("=" * 60)

    # Check if workflow exists
    workflow = wf.get_workflow('Asset Repair')

    if workflow:
        print(f"\n✅ Workflow found: {workflow.name}")
        print(f"   Is Active: {workflow.is_active}")
        print(f"   Workflow State Field: {workflow.workflow_state_field}")

        # Check document
        doc = frappe.get_doc('Asset Repair', 'ACC-ASR-2026-00001')
        print(f"\n📄 Document: {doc.name}")
        print(f"   Current State: {doc.workflow_state}")
        print(f"   Docstatus: {doc.docstatus}")

        # Get available transitions
        try:
            transitions = wf.get_transitions(doc)
            print(f"\n🔄 Available Actions from '{doc.workflow_state}':")
            if transitions:
                for t in transitions:
                    print(f"   • {t.action} → {t.next_state}")
            else:
                print("   ⚠️  No transitions available")
        except Exception as e:
            print(f"   ❌ Error getting transitions: {e}")

        # Check workflow states
        print(f"\n📋 Workflow States:")
        for state in workflow.states:
            print(f"   • {state.state}")

    else:
        print("\n❌ No workflow found for Asset Repair!")
        print("\n   Checking if workflow exists in database:")

        workflows = frappe.get_all('Workflow',
            filters={'document_type': 'Asset Repair'},
            fields=['name', 'is_active'])

        if workflows:
            print("   Found workflows:")
            for w in workflows:
                print(f"     • {w.name} (active: {w.is_active})")
        else:
            print("     No workflows found for Asset Repair")

    print("\n" + "=" * 60)
