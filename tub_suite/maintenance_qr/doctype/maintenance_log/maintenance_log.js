// Copyright (c) 2024, Tipubon International Co.,Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Maintenance Log", {
    refresh: function(frm) {
        // Update completion percentage display
        update_completion_display(frm);
        
        // Add QR Scanner button if not completed
        if (frm.doc.docstatus === 0 && frm.doc.status !== "Completed") {
            frm.add_custom_button(__("Scan QR Code"), function() {
                open_qr_scanner(frm);
            }, __("Actions"));
        }
        
        // Show status indicator
        if (frm.doc.status) {
            const status_colors = {
                "Draft": "gray",
                "Pending": "orange",
                "In Progress": "blue",
                "Completed": "green",
                "Overdue": "red",
                "Cancelled": "dark-gray"
            };
            
            frm.dashboard.add_indicator(
                __(frm.doc.status),
                status_colors[frm.doc.status] || "gray"
            );
        }
    },
    
    onload: function(frm) {
        // Set default values for new docs
        if (frm.is_new()) {
            frm.set_value("performed_by", frappe.session.user);
            frm.set_value("status", "Draft");
        }
    },
    
    maintenance_schedule: function(frm) {
        // Fetch schedule details
        if (frm.doc.maintenance_schedule) {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Maintenance Schedule",
                    name: frm.doc.maintenance_schedule
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value("asset", r.message.asset);
                        frm.set_value("asset_name", r.message.asset_name);
                        frm.set_value("maintenance_type", r.message.maintenance_type);
                        frm.set_value("due_date", r.message.next_due_date);
                        
                        // Copy checklist if empty
                        if ((!frm.doc.checklist_items || frm.doc.checklist_items.length === 0) && r.message.checklist_items) {
                            frm.clear_table("checklist_items");
                            r.message.checklist_items.forEach(function(item) {
                                const new_item = frm.add_child("checklist_items");
                                new_item.item_description = item.item_description;
                                new_item.is_mandatory = item.is_mandatory;
                                new_item.is_completed = 0;
                            });
                            frm.refresh_field("checklist_items");
                        }
                    }
                }
            });
        }
    },
    
    before_submit: function(frm) {
        // Validate mandatory items are completed
        const missing = [];
        
        if (frm.doc.checklist_items) {
            frm.doc.checklist_items.forEach(function(item) {
                if (item.is_mandatory && !item.is_completed) {
                    missing.push(item.item_description);
                }
            });
        }
        
        if (missing.length > 0) {
            frappe.throw(
                __("Cannot submit: The following mandatory items are not completed:<br>{0}", 
                [missing.join("<br>")])
            );
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
        
        // Recalculate completion percentage
        frm.trigger("calculate_completion");
    },
    
    checklist_items_remove: function(frm) {
        frm.trigger("calculate_completion");
    }
});

function update_completion_display(frm) {
    if (frm.doc.checklist_items && frm.doc.checklist_items.length > 0) {
        const completed = frm.doc.checklist_items.filter(i => i.is_completed).length;
        const total = frm.doc.checklist_items.length;
        const percentage = Math.round((completed / total) * 100);
        
        frm.set_value("completion_percentage", percentage);
        
        // Add progress indicator
        frm.dashboard.add_progress(
            __("Checklist Progress"),
            percentage,
            __("{0} of {1} items completed", [completed, total])
        );
    }
}

function open_qr_scanner(frm) {
    // Open QR scanner in new window
    const url = "/qr-scanner?log=" + encodeURIComponent(frm.doc.name);
    window.open(url, "_blank", "width=600,height=800");
}
