// Copyright (c) 2024, Tipubon International Co.,Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Maintenance Schedule", {
    refresh: function(frm) {
        // Add custom buttons
        if (!frm.is_new() && frm.doc.docstatus === 0) {
            frm.add_custom_button(__("Create Maintenance Log"), function() {
                create_maintenance_log(frm);
            }, __("Actions"));
        }
        
        // Show next due date prominently
        if (frm.doc.next_due_date) {
            const due_date = frappe.datetime.str_to_obj(frm.doc.next_due_date);
            const today = frappe.datetime.now_date(true);
            
            if (due_date < today) {
                frm.dashboard.add_indicator(__("Overdue"), "red");
            } else {
                const days_until = frappe.datetime.get_day_diff(due_date, today);
                frm.dashboard.add_indicator(
                    __("Due in {0} days", [days_until]), 
                    days_until <= 7 ? "orange" : "green"
                );
            }
        }
    },
    
    frequency: function(frm) {
        // Auto-calculate next due date when frequency changes
        if (frm.doc.frequency && !frm.doc.next_due_date) {
            const today = frappe.datetime.now_date();
            frm.set_value("next_due_date", today);
        }
    },
    
    asset: function(frm) {
        // Fetch asset details
        if (frm.doc.asset) {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Asset",
                    name: frm.doc.asset
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value("asset_name", r.message.asset_name);
                    }
                }
            });
        }
    }
});

// Child table - Checklist Items
frappe.ui.form.on("Maintenance Checklist Item", {
    is_completed: function(frm, cdt, cdn) {
        const item = locals[cdt][cdn];
        
        if (item.is_completed) {
            frappe.model.set_value(cdt, cdn, "completed_by", frappe.session.user);
            frappe.model.set_value(cdt, cdn, "completed_on", frappe.datetime.now_datetime());
        } else {
            frappe.model.set_value(cdt, cdn, "completed_by", null);
            frappe.model.set_value(cdt, cdn, "completed_on", null);
        }
    }
});

function create_maintenance_log(frm) {
    frappe.model.with_doctype("Maintenance Log", function() {
        const log = frappe.model.get_new_doc("Maintenance Log");
        
        log.maintenance_schedule = frm.doc.name;
        log.asset = frm.doc.asset;
        log.asset_name = frm.doc.asset_name;
        log.maintenance_type = frm.doc.maintenance_type;
        log.due_date = frm.doc.next_due_date;
        log.performed_by = frappe.session.user;
        
        // Copy checklist items
        if (frm.doc.checklist_items) {
            frm.doc.checklist_items.forEach(function(item) {
                const log_item = frappe.model.add_child(log, "checklist_items");
                log_item.item_description = item.item_description;
                log_item.is_mandatory = item.is_mandatory;
                log_item.is_completed = 0;
            });
        }
        
        frappe.set_route("Form", "Maintenance Log", log.name);
    });
}
