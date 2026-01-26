#!/usr/bin/env python3
"""
STEP 1: Delete all 3 conflicting Client Scripts
STEP 2: Create ONE consolidated script
Run: bench --site tub console < CONSOLIDATE_CLIENT_SCRIPTS.py
"""

import frappe
frappe.init(site='tub')
frappe.connect()

print('=== STEP 1: DELETE OLD SCRIPTS ===\n')

old_scripts = [
    'Asset Repair - Field Locking UI',
    'Asset Repair-Engineering Field Visibility',
    'Lock Engineering Sections After Completion'
]

for script_name in old_scripts:
    if frappe.db.exists('Client Script', script_name):
        frappe.delete_doc('Client Script', script_name, force=1)
        print(f'✅ Deleted: {script_name}')
    else:
        print(f'⚠️  Not found: {script_name}')

frappe.db.commit()

print('\n=== STEP 2: CREATE NEW CONSOLIDATED SCRIPT ===\n')

new_script = """frappe.ui.form.on('Asset Repair', {
    refresh: function(frm) {
        // === ENGINEERING FIELDS LOCKING ===
        // Lock engineering fields after engineering work is complete
        const engineering_locked_states = [
            'Pending GM Final Approval',
            'Approved for Repair',
            'Pending Supervisor Verification',
            'Pending Reporter Confirmation',
            'Finished'
        ];

        if (engineering_locked_states.includes(frm.doc.workflow_state)) {
            const engineering_fields = [
                'action_type',
                'custom_cost_type',
                'custom_รายละเอยดการดำเนนการ',
                'custom_ระบสาเหต',
                'estimated_cost',
                'spare_parts_used',
                'estimated_repair_duration',
                'assigned_engineer',
                'engineering_assessment_date',
                'engineering_assessment_by',
                'engineering_notes',
                'supervisor_review_date',
                'supervisor_reviewed_by',
                'custom_engineering_todo_items',
                'expected_duration_days',
                'repair_start_date',
                'repair_end_date'
            ];

            engineering_fields.forEach(field => {
                if (frm.fields_dict[field]) {
                    frm.set_df_property(field, 'read_only', 1);
                }
            });
        }

        // === REPORTER FIELDS LOCKING ===
        // Always lock reported_by
        frm.set_df_property('reported_by', 'read_only', 1);

        // Allow Supervisor to edit reporter fields ONLY in Draft
        if (frm.doc.workflow_state === 'Draft' && frappe.user_roles.includes('Maintenance Supervisor')) {
            frm.set_df_property('failure_date', 'read_only', 0);
            frm.set_df_property('description', 'read_only', 0);
            frm.set_df_property('repair_subject', 'read_only', 0);
        } else {
            frm.set_df_property('failure_date', 'read_only', 1);
            frm.set_df_property('description', 'read_only', 1);
            frm.set_df_property('repair_subject', 'read_only', 1);
        }
    }
});
"""

cs = frappe.get_doc({
    'doctype': 'Client Script',
    'name': 'Asset Repair - Master Form Control',
    'dt': 'Asset Repair',
    'enabled': 1,
    'script': new_script
})

cs.insert(ignore_permissions=True)
frappe.db.commit()

print('✅ Created: Asset Repair - Master Form Control')
print('\n=== DONE ===')
print('Now run:')
print('  bench --site tub clear-cache')
print('  Hard refresh browser (Ctrl+Shift+R)')
print('\nReporter Confirmation section will now use Custom Field depends_on ONLY')
print('No Client Script hiding/showing - simpler and more reliable!')
