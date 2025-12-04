/**
 * Asset Repair Client Script
 * Enforces field locking and auto-fills approval data
 */

frappe.ui.form.on('Asset Repair', {
    refresh: function(frm) {
        // If document is submitted, lock all fields except approval_status
        if (frm.doc.docstatus === 1) {
            lock_submitted_fields(frm);
            add_approval_button(frm);
        }
    },

    approval_status: function(frm) {
        // When approval status changes, auto-fill approval fields
        if (frm.doc.docstatus === 1 && frm.doc.approval_status) {
            if (frm.doc.approval_status === 'Approved' || frm.doc.approval_status === 'Rejected') {
                // Auto-fill with current user and server time
                frm.set_value('approved_by', frappe.session.user);
                frm.set_value('approval_time', frappe.datetime.now_datetime());

                // Make these fields read-only immediately
                frm.set_df_property('approved_by', 'read_only', 1);
                frm.set_df_property('approval_time', 'read_only', 1);
            }
        }
    },

    before_save: function(frm) {
        // Ensure approval fields are set correctly before save
        if (frm.doc.docstatus === 1 && frm.doc.approval_status) {
            if (frm.doc.approval_status === 'Approved' || frm.doc.approval_status === 'Rejected') {
                // Server will set these, but we pre-fill for immediate feedback
                if (!frm.doc.approved_by) {
                    frm.doc.approved_by = frappe.session.user;
                }
                if (!frm.doc.approval_time) {
                    frm.doc.approval_time = frappe.datetime.now_datetime();
                }
            }
        }
    }
});

function lock_submitted_fields(frm) {
    /**
     * Lock all fields except approval_status after submission
     */

    // List of ALL fields to lock (everything except approval_status)
    const fields_to_lock = [
        'asset', 'failure_date', 'description', 'repair_status',
        'completion_date', 'repair_cost', 'actions_performed',
        'stock_consumption', 'capitalize_repair_cost',
        'increase_in_asset_life', 'company', 'cost_center',
        'project', 'purchase_invoice', 'stock_items',
        'approved_by', 'approval_time'  // These are auto-filled
    ];

    // Lock each field
    fields_to_lock.forEach(function(fieldname) {
        frm.set_df_property(fieldname, 'read_only', 1);
    });

    // Show info message
    if (!frm.doc.approval_status || frm.doc.approval_status === 'Pending') {
        frm.dashboard.add_comment(
            __('This repair request is locked. Only Approval Status can be changed.'),
            'blue',
            true
        );
    }
}

function add_approval_button(frm) {
    /**
     * Add quick approval buttons in the form
     */

    if (!frm.doc.approval_status || frm.doc.approval_status === 'Pending') {
        // Add Approve button
        frm.add_custom_button(__('Approve'), function() {
            frappe.confirm(
                __('Are you sure you want to approve this repair request?'),
                function() {
                    frm.set_value('approval_status', 'Approved');
                    frm.save();
                }
            );
        }, __('Actions')).addClass('btn-success');

        // Add Reject button
        frm.add_custom_button(__('Reject'), function() {
            frappe.confirm(
                __('Are you sure you want to reject this repair request?'),
                function() {
                    frm.set_value('approval_status', 'Rejected');
                    frm.save();
                }
            );
        }, __('Actions')).addClass('btn-danger');
    } else {
        // Show approval info
        let message = __('This request was {0} by {1} on {2}', [
            frm.doc.approval_status,
            frm.doc.approved_by || 'Unknown',
            frappe.datetime.str_to_user(frm.doc.approval_time) || 'Unknown'
        ]);

        frm.dashboard.add_comment(message, 'green', true);
    }
}
