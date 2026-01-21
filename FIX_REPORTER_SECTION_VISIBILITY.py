import frappe
import os
os.chdir('/home/user/frappe-bench/sites')
frappe.init(site='tub')
frappe.connect()

# Update reporter_confirmation_section to show in both Pending Reporter Confirmation AND Finished
correct_depends_on = 'eval:doc.workflow_state=="Pending Reporter Confirmation" || doc.workflow_state=="Finished"'

frappe.db.sql("""
    UPDATE `tabCustom Field`
    SET depends_on = %s
    WHERE dt = 'Asset Repair'
    AND fieldname = 'reporter_confirmation_section'
""", (correct_depends_on,))

frappe.db.commit()
print(f"✅ Updated reporter_confirmation_section depends_on to show in both Pending Reporter Confirmation and Finished states")
