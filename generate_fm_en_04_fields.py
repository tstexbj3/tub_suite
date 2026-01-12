#!/usr/bin/env python3
import json

# Define all new fields for FM-EN-04
new_fields = []

# ============================================
# SECTION 0: Basic Info (above Section 1)
# ============================================
new_fields.extend([
    {
        'fieldname': 'repair_source',
        'label': 'Repair Source (แหล่งที่มา)',
        'fieldtype': 'Select',
        'options': '\nPortal (แจ้งผ่านระบบ)\nManual (แจ้งด้วยตนเอง)\nPlanned Maintenance (ตามแผน)',
        'insert_after': 'repair_type',
        'in_list_view': 0,
        'in_standard_filter': 1,
        'reqd': 1,
        'description': 'How the repair request was created'
    },
    {
        'fieldname': 'received_by',
        'label': 'Received By (ผู้รับแจ้ง)',
        'fieldtype': 'Link',
        'options': 'User',
        'insert_after': 'repair_source',
        'in_list_view': 0,
        'description': 'Person who received the repair request'
    },
    {
        'fieldname': 'received_date',
        'label': 'Received Date (วันที่รับแจ้ง)',
        'fieldtype': 'Datetime',
        'insert_after': 'received_by',
        'in_list_view': 0,
        'description': 'When the request was received'
    }
])

# ============================================
# SECTION 1: Asset Info & Reporter
# ============================================
new_fields.extend([
    {
        'fieldname': 'section_1_break',
        'label': 'Section 1: Asset Info & Reporter (ข้อมูลเครื่องจักรและผู้แจ้ง)',
        'fieldtype': 'Section Break',
        'insert_after': 'received_date',
        'collapsible': 1
    },
    {
        'fieldname': 'repair_subject',
        'label': 'Subject (เรื่องที่แจ้ง)',
        'fieldtype': 'Data',
        'insert_after': 'section_1_break',
        'in_list_view': 1,
        'reqd': 1,
        'bold': 1,
        'description': 'Brief subject of the repair request'
    },
    {
        'fieldname': 'reporter_department',
        'label': 'Reporter Department (แผนกผู้แจ้ง)',
        'fieldtype': 'Data',
        'insert_after': 'reported_by',
        'in_list_view': 0,
        'description': 'Department of the person reporting'
    },
    {
        'fieldname': 'reporter_signature',
        'label': 'Reporter Signature (ลายเซ็นผู้แจ้ง)',
        'fieldtype': 'Signature',
        'insert_after': 'issue_photos',
        'description': 'Signature of the reporter'
    },
    {
        'fieldname': 'issue_photos',
        'label': 'Issue Photos (รูปถ่ายปัญหา)',
        'fieldtype': 'Attach Image',
        'insert_after': 'description',
        'description': 'Photos showing the problem'
    },
    {
        'fieldname': 'section_1_gm_approval_break',
        'label': 'GM Preliminary Approval (GM อนุมัติเบื้องต้น)',
        'fieldtype': 'Section Break',
        'insert_after': 'reporter_signature',
        'collapsible': 1,
        'depends_on': 'eval:doc.workflow_state != "Draft"'
    },
    {
        'fieldname': 'gm_section1_approved_by',
        'label': 'GM Approved By (GM ผู้อนุมัติ)',
        'fieldtype': 'Link',
        'options': 'User',
        'insert_after': 'section_1_gm_approval_break',
        'read_only': 1
    },
    {
        'fieldname': 'gm_section1_approval_date',
        'label': 'GM Approval Date (วันที่อนุมัติ)',
        'fieldtype': 'Datetime',
        'insert_after': 'gm_section1_approved_by',
        'read_only': 1
    },
    {
        'fieldname': 'gm_section1_notes',
        'label': 'GM Notes (หมายเหตุ GM)',
        'fieldtype': 'Small Text',
        'insert_after': 'gm_section1_approval_date'
    }
])

# ============================================
# SECTION 2: Engineering Department
# ============================================
new_fields.extend([
    {
        'fieldname': 'section_2_break',
        'label': 'Section 2: Engineering Department (ฝ่ายวิศวกรรม)',
        'fieldtype': 'Section Break',
        'insert_after': 'gm_section1_notes',
        'collapsible': 1
    },
    {
        'fieldname': 'action_type',
        'label': 'Action Type (การดำเนินการ)',
        'fieldtype': 'Select',
        'options': '\nช่างภายใน (Internal)\nช่างภายนอก (External)\nมีค่าใช้จ่าย (With Cost)\nไม่มีค่าใช้จ่าย (No Cost)',
        'insert_after': 'section_2_break',
        'in_list_view': 0
    },
    {
        'fieldname': 'engineering_todo_items',
        'label': 'Engineering Todo Items (รายการที่ต้องทำ)',
        'fieldtype': 'Table',
        'options': 'Engineering Todo Item',
        'insert_after': 'action_type',
        'description': 'List of tasks for engineers'
    },
    {
        'fieldname': 'spare_parts_used',
        'label': 'Spare Parts Used (รายการอะไหล่)',
        'fieldtype': 'Table',
        'options': 'Repair Spare Part',
        'insert_after': 'engineering_todo_items',
        'description': 'Spare parts used in repair'
    },
    {
        'fieldname': 'expected_duration_days',
        'label': 'Expected Duration (Days) (ระยะเวลาคาดการณ์)',
        'fieldtype': 'Int',
        'insert_after': 'spare_parts_used',
        'description': 'Expected duration in days'
    },
    {
        'fieldname': 'repair_start_date',
        'label': 'Repair Start Date (วันที่เริ่มซ่อม)',
        'fieldtype': 'Date',
        'insert_after': 'expected_duration_days',
        'in_list_view': 0
    },
    {
        'fieldname': 'repair_end_date',
        'label': 'Repair End Date (วันที่เสร็จสิ้น)',
        'fieldtype': 'Date',
        'insert_after': 'repair_start_date',
        'in_list_view': 0
    },
    {
        'fieldname': 'engineering_operator_signature',
        'label': 'Engineering Operator Signature (ลายเซ็นผู้ประเมิน)',
        'fieldtype': 'Signature',
        'insert_after': 'repair_end_date'
    },
    {
        'fieldname': 'engineering_operator_sign_date',
        'label': 'Operator Sign Date (วันที่ประเมิน)',
        'fieldtype': 'Datetime',
        'insert_after': 'engineering_operator_signature',
        'read_only': 1
    },
    {
        'fieldname': 'eng_supervisor_section_break',
        'label': 'Engineering Supervisor Review (หัวหน้าช่างตรวจสอบ)',
        'fieldtype': 'Section Break',
        'insert_after': 'engineering_operator_sign_date',
        'collapsible': 1
    },
    {
        'fieldname': 'eng_supervisor_reviewed_by',
        'label': 'Reviewed By (หัวหน้าช่าง)',
        'fieldtype': 'Link',
        'options': 'User',
        'insert_after': 'eng_supervisor_section_break',
        'read_only': 1
    },
    {
        'fieldname': 'eng_supervisor_review_date',
        'label': 'Review Date (วันที่ตรวจสอบ)',
        'fieldtype': 'Datetime',
        'insert_after': 'eng_supervisor_reviewed_by',
        'read_only': 1
    },
    {
        'fieldname': 'eng_supervisor_signature',
        'label': 'Supervisor Signature (ลายเซ็น)',
        'fieldtype': 'Signature',
        'insert_after': 'eng_supervisor_review_date'
    },
    {
        'fieldname': 'gm_final_approval_break',
        'label': 'GM Final Approval (GM อนุมัติสุดท้าย)',
        'fieldtype': 'Section Break',
        'insert_after': 'eng_supervisor_signature',
        'collapsible': 1
    },
    {
        'fieldname': 'gm_final_approved_by',
        'label': 'GM Approved By (GM ผู้อนุมัติ)',
        'fieldtype': 'Link',
        'options': 'User',
        'insert_after': 'gm_final_approval_break',
        'read_only': 1
    },
    {
        'fieldname': 'gm_final_approval_date',
        'label': 'Final Approval Date (วันที่อนุมัติ)',
        'fieldtype': 'Datetime',
        'insert_after': 'gm_final_approved_by',
        'read_only': 1
    },
    {
        'fieldname': 'gm_final_notes',
        'label': 'GM Final Notes (หมายเหตุ)',
        'fieldtype': 'Small Text',
        'insert_after': 'gm_final_approval_date'
    },
    {
        'fieldname': 'repair_completion_break',
        'label': 'Repair Completion (การซ่อมเสร็จสิ้น)',
        'fieldtype': 'Section Break',
        'insert_after': 'gm_final_notes',
        'collapsible': 1
    },
    {
        'fieldname': 'repair_completed_by',
        'label': 'Completed By (ผู้ทำซ่อมเสร็จ)',
        'fieldtype': 'Link',
        'options': 'User',
        'insert_after': 'repair_completion_break',
        'read_only': 1
    },
    {
        'fieldname': 'completion_date',
        'label': 'Completion Date (วันที่เสร็จ)',
        'fieldtype': 'Datetime',
        'insert_after': 'repair_completed_by',
        'read_only': 1,
        'in_list_view': 0
    }
])

# ============================================
# SECTION 3: Reporter's Supervisor Verification
# ============================================
new_fields.extend([
    {
        'fieldname': 'section_3_break',
        'label': 'Section 3: Supervisor Verification (หัวหน้าแผนกตรวจสอบ)',
        'fieldtype': 'Section Break',
        'insert_after': 'completion_date',
        'collapsible': 1
    },
    {
        'fieldname': 'hygiene_status',
        'label': 'Hygiene Status (สถานะสุขลักษณะ)',
        'fieldtype': 'Select',
        'options': '\nเรียบร้อย/สะอาดไม่เสี่ยงต่อการปนเปื้อน (Clean)\nไม่เรียบร้อย/ต้องแก้ไข (Not Clean)',
        'insert_after': 'section_3_break'
    },
    {
        'fieldname': 'hygiene_issue_notes',
        'label': 'Hygiene Issue Notes (หมายเหตุปัญหา)',
        'fieldtype': 'Small Text',
        'insert_after': 'hygiene_status',
        'depends_on': 'eval:doc.hygiene_status && doc.hygiene_status.includes("ไม่เรียบร้อย")'
    },
    {
        'fieldname': 'cleanliness_before_machine',
        'label': 'Machine Cleanliness Before (ความสะอาดเครื่องก่อน)',
        'fieldtype': 'Select',
        'options': '\nสะอาด (Clean)\nไม่สะอาด (Not Clean)',
        'insert_after': 'hygiene_issue_notes'
    },
    {
        'fieldname': 'cleanliness_after_machine',
        'label': 'Machine Cleanliness After (ความสะอาดเครื่องหลัง)',
        'fieldtype': 'Select',
        'options': '\nสะอาด (Clean)\nไม่สะอาด (Not Clean)',
        'insert_after': 'cleanliness_before_machine'
    },
    {
        'fieldname': 'cleanliness_before_area',
        'label': 'Area Cleanliness Before (ความสะอาดสถานที่ก่อน)',
        'fieldtype': 'Select',
        'options': '\nสะอาด (Clean)\nไม่สะอาด (Not Clean)',
        'insert_after': 'cleanliness_after_machine'
    },
    {
        'fieldname': 'cleanliness_after_area',
        'label': 'Area Cleanliness After (ความสะอาดสถานที่หลัง)',
        'fieldtype': 'Select',
        'options': '\nสะอาด (Clean)\nไม่สะอาด (Not Clean)',
        'insert_after': 'cleanliness_before_area'
    },
    {
        'fieldname': 'parts_inserted',
        'label': 'Parts Inserted (อุปกรณ์ที่นำเข้า)',
        'fieldtype': 'Table',
        'options': 'Parts Inserted Item',
        'insert_after': 'cleanliness_after_area',
        'description': 'Parts inserted during repair'
    },
    {
        'fieldname': 'parts_removed',
        'label': 'Parts Removed (อุปกรณ์ที่นำออก)',
        'fieldtype': 'Table',
        'options': 'Parts Removed Item',
        'insert_after': 'parts_inserted',
        'description': 'Parts removed during repair'
    },
    {
        'fieldname': 'supervisor_verification_notes',
        'label': 'Supervisor Notes (หมายเหตุหัวหน้า)',
        'fieldtype': 'Text',
        'insert_after': 'parts_removed'
    },
    {
        'fieldname': 'supervisor_verified_by',
        'label': 'Verified By (หัวหน้าตรวจรับ)',
        'fieldtype': 'Link',
        'options': 'User',
        'insert_after': 'supervisor_verification_notes',
        'read_only': 1
    },
    {
        'fieldname': 'supervisor_verification_date',
        'label': 'Verification Date (วันที่ตรวจรับ)',
        'fieldtype': 'Datetime',
        'insert_after': 'supervisor_verified_by',
        'read_only': 1
    },
    {
        'fieldname': 'supervisor_signature',
        'label': 'Supervisor Signature (ลายเซ็น)',
        'fieldtype': 'Signature',
        'insert_after': 'supervisor_verification_date'
    }
])

# ============================================
# SECTION 4: Reporter Confirmation (Phase 8)
# ============================================
new_fields.extend([
    {
        'fieldname': 'reporter_confirmation_break',
        'label': 'Reporter Confirmation (ผู้แจ้งยืนยัน)',
        'fieldtype': 'Section Break',
        'insert_after': 'supervisor_signature',
        'collapsible': 1
    },
    {
        'fieldname': 'reporter_confirmed',
        'label': 'Reporter Confirmed (ยืนยันแล้ว)',
        'fieldtype': 'Check',
        'insert_after': 'reporter_confirmation_break',
        'read_only': 1
    },
    {
        'fieldname': 'reporter_confirmation_date',
        'label': 'Confirmation Date (วันที่ยืนยัน)',
        'fieldtype': 'Datetime',
        'insert_after': 'reporter_confirmed',
        'read_only': 1
    },
    {
        'fieldname': 'reporter_confirmation_photos',
        'label': 'Confirmation Photos (รูปภาพยืนยัน)',
        'fieldtype': 'Attach Image',
        'insert_after': 'reporter_confirmation_date',
        'description': 'Photos after repair completion'
    },
    {
        'fieldname': 'reporter_confirmation_notes',
        'label': 'Confirmation Notes (หมายเหตุ)',
        'fieldtype': 'Small Text',
        'insert_after': 'reporter_confirmation_photos'
    },
    {
        'fieldname': 'reporter_satisfaction',
        'label': 'Satisfaction (ความพึงพอใจ)',
        'fieldtype': 'Select',
        'options': '\nพอใจ (Satisfied)\nไม่พอใจ (Not Satisfied)',
        'insert_after': 'reporter_confirmation_notes'
    }
])

# ============================================
# SECTION 5: Final Remarks
# ============================================
new_fields.extend([
    {
        'fieldname': 'final_remarks_break',
        'label': 'Final Remarks (หมายเหตุสุดท้าย)',
        'fieldtype': 'Section Break',
        'insert_after': 'reporter_satisfaction',
        'collapsible': 1
    },
    {
        'fieldname': 'final_remarks',
        'label': 'Final Remarks (หมายเหตุ)',
        'fieldtype': 'Text',
        'insert_after': 'final_remarks_break',
        'description': 'Any final remarks or notes'
    }
])

# Build complete custom field JSON structure
custom_fields = []
for i, field in enumerate(new_fields):
    custom_field = {
        'allow_in_quick_entry': 0,
        'allow_on_submit': field.get('allow_on_submit', 0),
        'bold': field.get('bold', 0),
        'collapsible': field.get('collapsible', 0),
        'collapsible_depends_on': field.get('collapsible_depends_on'),
        'columns': 0,
        'default': field.get('default'),
        'depends_on': field.get('depends_on'),
        'description': field.get('description'),
        'docstatus': 0,
        'doctype': 'Custom Field',
        'dt': 'Asset Repair',
        'fetch_from': field.get('fetch_from'),
        'fetch_if_empty': 0,
        'fieldname': field['fieldname'],
        'fieldtype': field['fieldtype'],
        'hidden': field.get('hidden', 0),
        'hide_border': 0,
        'hide_days': 0,
        'hide_seconds': 0,
        'ignore_user_permissions': 0,
        'ignore_xss_filter': 0,
        'in_global_search': 0,
        'in_list_view': field.get('in_list_view', 0),
        'in_preview': 0,
        'in_standard_filter': field.get('in_standard_filter', 0),
        'insert_after': field['insert_after'],
        'is_system_generated': 0,
        'is_virtual': 0,
        'label': field['label'],
        'length': 0,
        'link_filters': None,
        'mandatory_depends_on': field.get('mandatory_depends_on'),
        'modified': '2026-01-08 19:00:00.000000',
        'module': None,
        'name': f"Asset Repair-{field['fieldname']}",
        'no_copy': 0,
        'non_negative': 0,
        'options': field.get('options'),
        'permlevel': 0,
        'placeholder': None,
        'precision': None,
        'print_hide': 0,
        'print_hide_if_no_value': 0,
        'print_width': None,
        'read_only': field.get('read_only', 0),
        'read_only_depends_on': field.get('read_only_depends_on'),
        'report_hide': 0,
        'reqd': field.get('reqd', 0),
        'search_index': 0,
        'show_dashboard': 0,
        'sort_options': 0,
        'translatable': 0,
        'unique': 0,
        'width': None
    }
    custom_fields.append(custom_field)

# Save to file
with open('fm_en_04_new_fields.json', 'w', encoding='utf-8') as f:
    json.dump(custom_fields, f, indent=2, ensure_ascii=False)

print(f'Created {len(custom_fields)} new custom fields')
print('Sections created:')
print('  - Section 0: Basic Info (3 fields)')
print('  - Section 1: Asset Info & Reporter (10 fields)')
print('  - Section 2: Engineering Department (19 fields)')
print('  - Section 3: Supervisor Verification (14 fields)')
print('  - Section 4: Reporter Confirmation (6 fields)')
print('  - Section 5: Final Remarks (2 fields)')
print(f'\nTotal: {len(custom_fields)} fields')
