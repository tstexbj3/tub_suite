# Copyright (c) 2024, Tipubon International Co.,Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class MaintenanceSchedule(Document):
    def validate(self):
        self.validate_due_date()
        self.validate_checklist()
    
    def validate_due_date(self):
        """Validate that due date is in the future for new schedules"""
        if self.is_new() and self.next_due_date:
            if frappe.utils.getdate(self.next_due_date) < frappe.utils.today():
                frappe.throw(_("Next Due Date cannot be in the past"))
    
    def validate_checklist(self):
        """Validate that checklist has at least one item"""
        if not self.checklist_items or len(self.checklist_items) == 0:
            frappe.msgprint(_("Warning: Maintenance schedule has no checklist items"), indicator="orange", alert=True)
    
    def on_submit(self):
        """Mark schedule as Active when submitted"""
        self.status = "Active"
        self.save()
    
    def on_cancel(self):
        """Mark schedule as Cancelled"""
        self.status = "Cancelled"
        self.save()
