#!/usr/bin/env python3
"""
Hide sections that shouldn't appear in Finished state
"""

import frappe
frappe.init(site='tub')
frappe.connect()

print('=== HIDING UNWANTED SECTIONS ===\n')

# These should be HIDDEN (not used anymore)
fields_to_hide = [
    'verification_section',  # Inspector Verification - not used
    'requires_inspector_verification',  # Old field
    'verification_status',  # Old field
    'custom_ฝายวศวกรรม',  # Empty section
]

for fieldname in fields_to_hide:
    cf_name = f'Asset Repair-{fieldname}'
    if frappe.db.exists('Custom Field', cf_name):
        cf = frappe.get_doc('Custom Field', cf_name)
        print(f'{fieldname}:')
        print(f'  OLD hidden: {cf.hidden}')
        cf.hidden = 1
        cf.save(ignore_permissions=True)
        print(f'  NEW hidden: 1 ✅')
    else:
        print(f'{fieldname}: NOT FOUND')
    print()

# gm_section1_approval_date should only show in certain states
print('=== FIXING GM SECTION 1 APPROVAL DATE ===\n')
cf_name = 'Asset Repair-gm_section1_approval_date'
if frappe.db.exists('Custom Field', cf_name):
    cf = frappe.get_doc('Custom Field', cf_name)
    print(f'gm_section1_approval_date:')
    print(f'  OLD depends_on: {cf.depends_on}')
    # Show only in states where GM Section 1 is relevant
    cf.depends_on = 'eval:["Pending GM Approval Section 1","Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval"].includes(doc.workflow_state)'
    cf.save(ignore_permissions=True)
    print(f'  NEW depends_on: {cf.depends_on} ✅')
else:
    print('gm_section1_approval_date: NOT FOUND')

frappe.db.commit()

print('\n=== DONE ===')
print('Run: bench --site tub clear-cache && bench --site tub export-fixtures')
