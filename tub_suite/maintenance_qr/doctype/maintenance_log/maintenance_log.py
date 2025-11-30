# Copyright (c) 2024, Tipubon International Co.,Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from tub_suite.utils import validate_checklist_completion, calculate_next_maintenance_date

class MaintenanceLog(Document):
    def validate(self):
        self.calculate_completion_percentage()
        self.update_status()
    
    def before_submit(self):
        """Validate completion before submission"""
        is_complete, missing_items = validate_checklist_completion(self.checklist_items)
        
        if not is_complete:
            frappe.throw(
                _("Cannot submit: The following mandatory items are not completed: {0}").format(
                    ", ".join(missing_items)
                )
            )
        
        self.status = "Completed"
        self.completion_date = frappe.utils.now()
    
    def on_submit(self):
        """Update maintenance schedule after completion"""
        if self.maintenance_schedule:
            schedule = frappe.get_doc("Maintenance Schedule", self.maintenance_schedule)
            
            # Calculate next due date based on frequency
            if schedule.frequency:
                schedule.next_due_date = calculate_next_maintenance_date(
                    self.completion_date or frappe.utils.today(),
                    schedule.frequency
                )
                schedule.save()
    
    def calculate_completion_percentage(self):
        """Calculate completion percentage based on checklist"""
        if not self.checklist_items or len(self.checklist_items) == 0:
            self.completion_percentage = 0
            return
        
        completed = sum(1 for item in self.checklist_items if item.is_completed)
        total = len(self.checklist_items)
        self.completion_percentage = (completed / total) * 100
    
    def update_status(self):
        """Update status based on completion and due date"""
        if self.docstatus == 2:
            self.status = "Cancelled"
        elif self.docstatus == 1:
            self.status = "Completed"
        elif self.completion_percentage == 100:
            self.status = "Completed"
        elif self.completion_percentage > 0:
            self.status = "In Progress"
        elif self.due_date and frappe.utils.getdate(self.due_date) < frappe.utils.today():
            self.status = "Overdue"
        else:
            self.status = "Pending"
