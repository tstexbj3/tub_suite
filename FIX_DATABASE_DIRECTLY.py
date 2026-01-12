#!/usr/bin/env python3
"""
FINAL FIX - Update database directly
Since bench migrate doesn't update existing Custom Field records,
we need to update the database directly.
"""
import frappe

frappe.init(site='tub')
frappe.connect()

print("=" * 80)
print("FIXING DATABASE DIRECTLY - Field Visibility")
print("=" * 80)

engineering_depends = 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)'
reporter_depends = 'eval:doc.workflow_state=="Pending Supervisor Verification"'

# Fields that need engineering visibility
engineering_fields = {
    'custom_engineering_section': {'depends_on': engineering_depends, 'hidden': 0},
    'action_type': {'depends_on': engineering_depends, 'hidden': 0},
    'custom_cost_type': {'depends_on': engineering_depends, 'hidden': 0},
    'custom_engineering_todo_items': {'depends_on': engineering_depends, 'hidden': 0},
    'spare_parts_used': {'depends_on': engineering_depends, 'hidden': 0},
    'expected_duration_days': {'depends_on': engineering_depends, 'hidden': 0},
    'engineering_operator_signature': {'depends_on': engineering_depends, 'hidden': 0},
    'repair_start_date': {'depends_on': engineering_depends, 'hidden': 0},
    'repair_end_date': {'depends_on': engineering_depends, 'hidden': 0},
    'eng_supervisor_signature': {'depends_on': engineering_depends, 'hidden': 0},
    'approval_signature': {'depends_on': engineering_depends, 'hidden': 0},
    'completion_handover_date': {'depends_on': engineering_depends, 'hidden': 0},
    'repair_result_status': {'depends_on': engineering_depends, 'hidden': 0},
    'expected_completion_date': {'depends_on': engineering_depends, 'hidden': 0},
    'issue_severity': {'depends_on': engineering_depends, 'hidden': 0},
    'custom_cause_description': {'depends_on': engineering_depends, 'hidden': 0},
    'custom_purchase_order_no': {'depends_on': engineering_depends, 'hidden': 0},
}

# Reporter Confirmation fields
reporter_fields = {
    'reporter_confirmation_section': {'depends_on': reporter_depends, 'hidden': 0},
    'reporter_confirmation_date': {'depends_on': reporter_depends, 'hidden': 0},
    'reporter_confirmation_photos': {'depends_on': reporter_depends, 'hidden': 0},
    'reporter_confirmation_notes': {'depends_on': reporter_depends, 'hidden': 0},
}

# Inspector fields - always hidden
inspector_fields = {
    'requires_inspector_verification': {'hidden': 1},
    'verification_notes': {'hidden': 1},
    'verification_status': {'hidden': 1},
}

# Combine all
all_fields = {}
all_fields.update(engineering_fields)
all_fields.update(reporter_fields)
all_fields.update(inspector_fields)

# Update database
updated = 0
for fieldname, updates in all_fields.items():
    try:
        # Build SET clause
        set_parts = []
        values = []
        for key, value in updates.items():
            set_parts.append(f"{key} = %s")
            values.append(value)

        set_clause = ", ".join(set_parts)
        values.append(fieldname)  # for WHERE clause

        frappe.db.sql(f"""
            UPDATE `tabCustom Field`
            SET {set_clause}
            WHERE dt = 'Asset Repair' AND fieldname = %s
        """, tuple(values))

        print(f"✓ {fieldname}")
        updated += 1
    except Exception as e:
        print(f"✗ {fieldname}: {e}")

frappe.db.commit()

print("\n" + "=" * 80)
print(f"✅ UPDATED {updated} fields in database")
print("=" * 80)
print("\nNow run: bench --site tub clear-cache")
print("Then refresh your browser")
print("=" * 80)
