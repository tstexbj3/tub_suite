// Asset DocType Client Script - QR Code Display

frappe.ui.form.on("Asset", {
    refresh: function(frm) {
        // Add button to generate/view QR code
        if (frm.doc.name && !frm.is_new()) {
            frm.add_custom_button(__("View QR Code"), function() {
                show_qr_code(frm);
            });
            
            frm.add_custom_button(__("Print QR Label"), function() {
                print_qr_label(frm);
            });
        }
    }
});

function show_qr_code(frm) {
    frappe.call({
        method: "tub_suite.api.asset.get_asset_qr_code",
        args: {
            asset_name: frm.doc.name
        },
        callback: function(r) {
            if (r.message && r.message.qr_code_url) {
                const qr_html = "<div class=\"asset-qr-code\">" +
                    "<img src=\"" + r.message.qr_code_url + "\" alt=\"QR Code\" />" +
                    "<p><strong>" + frm.doc.asset_name + "</strong></p>" +
                    "<p>" + frm.doc.name + "</p>" +
                    "</div>";
                
                const d = new frappe.ui.Dialog({
                    title: __("Asset QR Code: ") + frm.doc.name,
                    fields: [
                        {
                            fieldtype: "HTML",
                            fieldname: "qr_display",
                            options: qr_html
                        }
                    ]
                });
                d.show();
            } else {
                frappe.msgprint(__("QR Code not found. Generating now..."));
                generate_qr_code(frm);
            }
        }
    });
}

function generate_qr_code(frm) {
    frappe.call({
        method: "tub_suite.api.asset.generate_qr_code",
        args: {
            doc: frm.doc
        },
        callback: function(r) {
            if (r.message) {
                frappe.msgprint(__("QR Code generated successfully"));
                frm.reload_doc();
            }
        }
    });
}

function print_qr_label(frm) {
    const print_format = "Asset QR Label";
    const url = "/api/method/frappe.utils.print_format.download_pdf?" +
        "doctype=Asset&" +
        "name=" + encodeURIComponent(frm.doc.name) + "&" +
        "format=" + encodeURIComponent(print_format) + "&" +
        "no_letterhead=0";
    
    const w = window.open(frappe.urllib.get_full_url(url));
    if (!w) {
        frappe.msgprint(__("Please enable pop-ups"));
    }
}
