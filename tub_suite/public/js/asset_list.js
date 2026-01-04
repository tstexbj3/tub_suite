// Asset List View customization - Batch QR Label Printing

frappe.listview_settings['Asset'] = {
    onload: function(listview) {
        // Add custom button for batch QR label printing (Niimbot B1)
        listview.page.add_action_item(__('Print QR Labels (Niimbot)'), function() {
            let selected = listview.get_checked_items();

            if (selected.length === 0) {
                frappe.msgprint({
                    title: __('No Selection'),
                    message: __('Please select at least one asset to print QR labels'),
                    indicator: 'orange'
                });
                return;
            }

            // Confirm before printing
            frappe.confirm(
                __('Print {0} QR label(s) for Niimbot B1 printer?', [selected.length]),
                function() {
                    print_batch_qr_labels(selected);
                }
            );
        });
    }
};

function print_batch_qr_labels(selected_assets) {
    // Call batch print API
    frappe.call({
        method: 'tub_suite.api.print_qr_labels.batch_print_qr_labels',
        args: {
            asset_names: selected_assets.map(d => d.name)
        },
        freeze: true,
        freeze_message: __('Generating {0} QR labels...', [selected_assets.length]),
        callback: function(r) {
            if (r.message && r.message.html) {
                // Open print window with generated labels
                let print_window = window.open('', 'Print_QR_Labels', 'width=800,height=600');

                if (!print_window) {
                    frappe.msgprint({
                        title: __('Popup Blocked'),
                        message: __('Please allow popups for this site to print labels'),
                        indicator: 'red'
                    });
                    return;
                }

                print_window.document.write(r.message.html);
                print_window.document.close();

                // Auto-open print dialog after page loads
                print_window.onload = function() {
                    setTimeout(function() {
                        print_window.print();
                    }, 500);
                };

                frappe.show_alert({
                    message: __('Generated {0} labels. Print dialog will open automatically.', [r.message.count]),
                    indicator: 'green'
                }, 5);
            }
        },
        error: function(err) {
            frappe.msgprint({
                title: __('Error'),
                message: __('Failed to generate QR labels. Please try again.'),
                indicator: 'red'
            });
        }
    });
}
