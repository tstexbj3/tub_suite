"""Create Supervisor role for Asset Repair workflow"""
import frappe

def create_role():
    """Create Supervisor role if it doesn't exist"""

    if frappe.db.exists('Role', 'Supervisor'):
        print("✅ Supervisor role already exists")
        return

    # Create the role
    role = frappe.get_doc({
        'doctype': 'Role',
        'role_name': 'Supervisor',
        'desk_access': 1,
        'disabled': 0
    })
    role.insert(ignore_permissions=True)
    frappe.db.commit()

    print("✅ Created Supervisor role")
    print("\nTo assign this role to a user, run:")
    print("frappe.get_doc('User', 'user@example.com').add_roles('Supervisor')")
    print("frappe.db.commit()")
