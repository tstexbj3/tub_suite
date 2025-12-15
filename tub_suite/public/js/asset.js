// Asset form customization - Add QR code button
frappe.ui.form.on('Asset', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            // Add Generate QR Code button
            frm.add_custom_button(__('Generate QR Code'), function() {
                generate_asset_maintenance_qr(frm);
            }, __('Actions'));
        }
    }
});

function generate_asset_maintenance_qr(frm) {
    frappe.call({
        method: 'tub_suite.overrides.qr_asset_maintenance.generate_asset_qr',
        args: {
            asset_name: frm.doc.name
        },
        freeze: true,
        freeze_message: __('Generating QR Code...'),
        callback: function(r) {
            if (r.message) {
                frappe.msgprint({
                    title: __('QR Code Generated'),
                    message: __('QR code has been generated successfully!<br>') +
                             '<div style="text-align:center; margin-top:15px;">' +
                             '<img src="' + r.message.file_url + '" style="width:200px;height:200px;border:2px solid #ddd;border-radius:8px;"/>' +
                             '</div>' +
                             '<p style="margin-top:15px;"><strong>Scan this QR code to access maintenance portal for this asset.</strong></p>',
                    primary_action: {
                        label: __('View QR List'),
                        action: function() {
                            frappe.set_route('Form', 'QR List', r.message.qr_list);
                        }
                    }
                });
                frm.reload_doc();
            }
        }
    });
}
