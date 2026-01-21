#!/usr/bin/env python3
import frappe
import os
os.chdir('/home/user/frappe-bench/sites')
frappe.init(site='tub')
frappe.connect()

field = frappe.get_doc('Custom Field', {'dt': 'Asset Repair', 'fieldname': 'section_3b_break'})
print(f"Current depends_on: {field.depends_on}")

correct_depends_on = 'eval:doc.workflow_state=="Pending Supervisor Verification" || doc.workflow_state=="Finished"'

frappe.db.sql("""UPDATE `tabCustom Field` SET depends_on = %s WHERE dt = 'Asset Repair' AND fieldname = 'section_3b_break'""", (correct_depends_on,))
frappe.db.commit()
print(f"✅ Updated to: {correct_depends_on}")
