// TUB Suite Maintenance QR System - Global JavaScript

frappe.provide("tub_suite.maintenance");

// QR Code Scanner Initialization
tub_suite.maintenance.initScanner = function(video_element, callback) {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        frappe.msgprint(__("Camera access is not supported on this device"));
        return;
    }

    navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
        .then(function(stream) {
            video_element.srcObject = stream;
            video_element.play();
            
            // Start scanning loop
            tub_suite.maintenance.scanLoop(video_element, callback);
        })
        .catch(function(err) {
            frappe.msgprint(__("Camera access denied: ") + err.message);
        });
};

// QR Code Scanning Loop
tub_suite.maintenance.scanLoop = function(video, callback) {
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");
    
    function scan() {
        if (video.readyState === video.HAVE_ENOUGH_DATA) {
            canvas.height = video.videoHeight;
            canvas.width = video.videoWidth;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
            // QR code detection logic here (requires jsQR library)
            // For now, this is a placeholder
        }
        
        requestAnimationFrame(scan);
    }
    
    scan();
};

// Update Checklist Item Status
tub_suite.maintenance.toggleChecklistItem = function(frm, item_idx) {
    const item = frm.doc.checklist_items[item_idx];
    item.is_completed = !item.is_completed;
    
    if (item.is_completed) {
        item.completed_by = frappe.session.user;
        item.completed_on = frappe.datetime.now_datetime();
    } else {
        item.completed_by = null;
        item.completed_on = null;
    }
    
    frm.refresh_field("checklist_items");
    frm.dirty();
};

// Calculate Completion Percentage
tub_suite.maintenance.calculateCompletion = function(checklist_items) {
    if (!checklist_items || checklist_items.length === 0) {
        return 0;
    }
    
    const completed = checklist_items.filter(item => item.is_completed).length;
    return Math.round((completed / checklist_items.length) * 100);
};

// Validate Mandatory Items
tub_suite.maintenance.validateMandatory = function(checklist_items) {
    const missing = [];
    
    checklist_items.forEach(item => {
        if (item.is_mandatory && !item.is_completed) {
            missing.push(item.item_description);
        }
    });
    
    return missing;
};

// Show Maintenance Status
tub_suite.maintenance.showStatus = function(status) {
    const color_map = {
        "Pending": "orange",
        "Completed": "green",
        "Overdue": "red",
        "Draft": "gray",
        "Cancelled": "dark-gray"
    };
    
    const color = color_map[status] || "blue";
    return "<span class=\"indicator-pill " + color + "\">" + __(status) + "</span>";
};

// Format Date for Display
tub_suite.maintenance.formatDate = function(date_str) {
    if (!date_str) return "";
    
    const date = frappe.datetime.str_to_obj(date_str);
    return frappe.datetime.obj_to_user(date);
};

console.log("TUB Suite Maintenance QR System loaded");
