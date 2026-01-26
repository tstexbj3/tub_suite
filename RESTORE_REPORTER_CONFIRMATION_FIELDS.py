#!/usr/bin/env python3
"""
Restore Reporter Confirmation section fields that were accidentally deleted
Run: bench --site tub console < RESTORE_REPORTER_CONFIRMATION_FIELDS.py
"""

import frappe
frappe.init(site='tub')
frappe.connect()

print('=== RESTORING REPORTER CONFIRMATION FIELDS ===\n')

# 1. Check if reporter_confirmation_section exists
section_exists = frappe.db.exists('Custom Field', {
    'dt': 'Asset Repair',
    'fieldname': 'reporter_confirmation_section'
})

if not section_exists:
    print('Creating reporter_confirmation_section...')
    cf = frappe.get_doc({
        'doctype': 'Custom Field',
        'dt': 'Asset Repair',
        'fieldname': 'reporter_confirmation_section',
        'label': 'Reporter Confirmation (ผู้แจ้งยืนยัน)',
        'fieldtype': 'Section Break',
        'insert_after': 'section_3b_break',
        'depends_on': 'eval:doc.workflow_state=="Finished"',
        'collapsible': 1
    })
    cf.insert(ignore_permissions=True)
    print('✅ Created reporter_confirmation_section')
else:
    print('✅ reporter_confirmation_section already exists')

# 2. Check if reporter_confirmation_date exists
date_exists = frappe.db.exists('Custom Field', {
    'dt': 'Asset Repair',
    'fieldname': 'reporter_confirmation_date'
})

if not date_exists:
    print('\nCreating reporter_confirmation_date...')
    cf = frappe.get_doc({
        'doctype': 'Custom Field',
        'dt': 'Asset Repair',
        'fieldname': 'reporter_confirmation_date',
        'label': 'Confirmation Date (วันที่ยืนยัน)',
        'fieldtype': 'Date',
        'insert_after': 'reporter_confirmation_section',
        'depends_on': 'eval:doc.workflow_state=="Finished"',
        'read_only': 1
    })
    cf.insert(ignore_permissions=True)
    print('✅ Created reporter_confirmation_date')
else:
    print('✅ reporter_confirmation_date already exists')

# 3. Check if reporter_confirmation_photos exists
photos_exists = frappe.db.exists('Custom Field', {
    'dt': 'Asset Repair',
    'fieldname': 'reporter_confirmation_photos'
})

if not photos_exists:
    print('\nCreating reporter_confirmation_photos...')
    cf = frappe.get_doc({
        'doctype': 'Custom Field',
        'dt': 'Asset Repair',
        'fieldname': 'reporter_confirmation_photos',
        'label': 'Confirmation Photos (รูปภาพยืนยัน)',
        'fieldtype': 'Attach Image',
        'insert_after': 'reporter_confirmation_date',
        'depends_on': 'eval:doc.workflow_state=="Finished"'
    })
    cf.insert(ignore_permissions=True)
    print('✅ Created reporter_confirmation_photos')
else:
    print('✅ reporter_confirmation_photos already exists')

# 4. Fix reporter_confirmation_notes depends_on
print('\nFixing reporter_confirmation_notes depends_on...')
cf = frappe.get_doc('Custom Field', 'Asset Repair-reporter_confirmation_notes')
cf.depends_on = 'eval:doc.workflow_state=="Finished"'
cf.save(ignore_permissions=True)
print('✅ Fixed reporter_confirmation_notes')

frappe.db.commit()

print('\n=== DONE ===')
print('Now run:')
print('  bench --site tub clear-cache')
print('  bench --site tub export-fixtures')
