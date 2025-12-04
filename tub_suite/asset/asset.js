/**
 * Asset Custom Script - Add Maintenance QR Button
 *
 * This script adds a custom button to the Asset page that generates
 * a QR code for the mobile maintenance portal (without the :8000 port)
 *
 * Installation:
 * 1. Go to: /app/client-script
 * 2. Create new Client Script
 * 3. DocType: Asset
 * 4. Type: Form
 * 5. Paste this code
 * 6. Save and reload Asset page
 */

frappe.ui.form.on('Asset', {
    refresh(frm) {
        // Only show button for saved assets
        if (!frm.is_new()) {
            // Add custom button under "More" dropdown
            frm.add_custom_button(__('🔧 Maintenance QR Code'), function() {
                // Show loading message
                frappe.show_alert({
                    message: __('Generating QR code...'),
                    indicator: 'blue'
                }, 3);

                // Call API to generate QR
                frappe.call({
                    method: 'tub_suite.api.asset.generate_maintenance_qr',
                    args: {
                        asset_name: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            // Create dialog to display QR code
                            let d = new frappe.ui.Dialog({
                                title: __('Maintenance Portal QR Code'),
                                size: 'large',
                                fields: [
                                    {
                                        fieldtype: 'HTML',
                                        fieldname: 'qr_display'
                                    }
                                ],
                                primary_action_label: __('Download QR Code'),
                                primary_action() {
                                    // Download QR code as PNG
                                    const link = document.createElement('a');
                                    link.download = `${frm.doc.name}_maintenance_qr.png`;
                                    link.href = r.message.data_uri;
                                    link.click();

                                    frappe.show_alert({
                                        message: __('QR code downloaded'),
                                        indicator: 'green'
                                    }, 3);
                                }
                            });

                            // Display QR code with instructions
                            d.fields_dict.qr_display.$wrapper.html(`
                                <div style="text-align:center; padding:20px;">
                                    <h3>Scan this QR code with mobile device</h3>
                                    <img src="${r.message.data_uri}"
                                         style="width:300px; height:300px; margin:20px auto; display:block; border:2px solid #ddd; padding:10px;" />

                                    <div style="background:#f8f9fa; padding:15px; border-radius:8px; margin-top:20px; text-align:left;">
                                        <p style="margin:5px 0;"><strong>Asset:</strong> ${r.message.asset_name}</p>
                                        <p style="margin:5px 0;"><strong>URL:</strong> <code style="background:#fff; padding:2px 5px; border-radius:3px;">${r.message.url}</code></p>
                                        <p style="margin:10px 0 5px 0; font-size:12px; color:#666;">
                                            ✓ No port number (clean URL)<br>
                                            ✓ Opens maintenance portal directly<br>
                                            ✓ Works on any mobile device
                                        </p>
                                    </div>

                                    <div style="margin-top:20px; padding:15px; background:#e7f3ff; border-radius:8px; text-align:left;">
                                        <h4 style="margin-top:0;">📱 How to use:</h4>
                                        <ol style="margin:10px 0; padding-left:20px;">
                                            <li>Scan QR with phone camera or Line app</li>
                                            <li>Login to ERPNext (if not logged in)</li>
                                            <li>Asset details load automatically</li>
                                            <li>Complete maintenance checklist</li>
                                            <li>Report issues with photos</li>
                                        </ol>
                                    </div>

                                    <div style="margin-top:15px;">
                                        <button class="btn btn-secondary btn-sm" onclick="window.print()">
                                            🖨️ Print QR Code
                                        </button>
                                        <button class="btn btn-secondary btn-sm" onclick="navigator.clipboard.writeText('${r.message.url}')">
                                            📋 Copy URL
                                        </button>
                                    </div>
                                </div>
                            `);

                            d.show();

                            // Success notification
                            frappe.show_alert({
                                message: __('QR code generated successfully'),
                                indicator: 'green'
                            }, 3);
                        } else {
                            frappe.msgprint({
                                title: __('Error'),
                                message: __('Failed to generate QR code'),
                                indicator: 'red'
                            });
                        }
                    },
                    error: function(r) {
                        frappe.msgprint({
                            title: __('Error'),
                            message: r.message || __('Failed to generate QR code. Check if qrcode library is installed.'),
                            indicator: 'red'
                        });
                    }
                });
            }, __('Actions'));
        }
    }
});
