"""
Reorganize Asset Repair custom fields to match FM-EN-04 form structure
"""
import frappe

def reorganize():
    """Reorganize all Asset Repair custom fields in proper order"""

    # Define the proper field order for FM-EN-04
    field_order = [
        # SECTION 0: Basic Info (Standard ERPNext fields - no custom fields here)

        # SECTION 1: Asset Info & Reporter
        ("section_1_break", "asset_name", "Section Break", "Section 1: Asset Info & Reporter (ข้อมูลเครื่องจักรและผู้แจ้ง)"),
        ("repair_type", "section_1_break", "Select", "Repair Type (ประเภทการซ่อม)"),
        ("repair_source", "repair_type", "Select", "Repair Source (แหล่งที่มา)"),
        ("repair_subject", "repair_source", "Data", "Subject (เรื่องที่แจ้ง)"),
        ("description", "repair_subject", "Text Editor", "Description"),  # Standard field but might need repositioning
        ("issue_photos", "description", "Attach Image", "Issue Photos (รูปถ่ายปัญหา)"),
        ("reported_by", "issue_photos", "Link", "Reported By (Inspector)"),
        ("reporter_department", "reported_by", "Data", "Reporter Department (แผนกผู้แจ้ง)"),
        ("reporter_signature", "reporter_department", "Signature", "Reporter Signature (ลายเซ็นผู้แจ้ง)"),

        # SECTION 1B: Supervisor Verification (First Approval)
        ("section_1b_break", "reporter_signature", "Section Break", "Supervisor Verification (หัวหน้าแผนกตรวจสอบครั้งที่ 1)"),
        ("supervisor_section1_notes", "section_1b_break", "Small Text", "Supervisor Notes (หมายเหตุหัวหน้า)"),
        ("supervisor_section1_signature", "supervisor_section1_notes", "Signature", "Supervisor Signature (ลายเซ็น)"),

        # SECTION 1C: GM Approval Section 1
        ("section_1c_break", "supervisor_section1_signature", "Section Break", "GM Approval - Section 1 (GM อนุมัติส่วนที่ 1)"),
        ("gm_section1_notes", "section_1c_break", "Small Text", "GM Notes (หมายเหตุ GM)"),
        ("gm_section1_signature", "gm_section1_notes", "Signature", "GM Signature (ลายเซ็น)"),

        # SECTION 2: Engineering Department
        ("section_2_break", "gm_section1_signature", "Section Break", "Section 2: Engineering Department (ฝ่ายวิศวกรรม)"),
        ("action_type", "section_2_break", "Select", "Action Type (การดำเนินการ)"),
        ("engineering_todo_items", "action_type", "Table", "Engineering Todo Items (รายการที่ต้องทำ)"),
        ("spare_parts_used", "engineering_todo_items", "Table", "Spare Parts Used (รายการอะไหล่)"),
        ("expected_duration_days", "spare_parts_used", "Int", "Expected Duration (Days)"),
        ("repair_start_date", "expected_duration_days", "Date", "Repair Start Date"),
        ("repair_end_date", "repair_start_date", "Date", "Repair End Date"),
        ("engineering_operator_signature", "repair_end_date", "Signature", "Engineering Operator Signature"),

        # SECTION 2B: Engineering Supervisor Review
        ("section_2b_break", "engineering_operator_signature", "Section Break", "Engineering Supervisor Review (หัวหน้าช่างตรวจสอบ)"),
        ("eng_supervisor_signature", "section_2b_break", "Signature", "Supervisor Signature (ลายเซ็น)"),
        ("eng_supervisor_reviewed_by", "eng_supervisor_signature", "Link", "Reviewed By"),
        ("eng_supervisor_review_date", "eng_supervisor_reviewed_by", "Datetime", "Review Date"),

        # SECTION 2C: GM Final Approval
        ("section_2c_break", "eng_supervisor_review_date", "Section Break", "GM Final Approval (GM อนุมัติสุดท้าย)"),
        ("gm_final_notes", "section_2c_break", "Small Text", "GM Final Notes (หมายเหตุ)"),
        ("gm_final_signature", "gm_final_notes", "Signature", "GM Signature (ลายเซ็น)"),

        # SECTION 2D: Repair Completion
        ("section_2d_break", "gm_final_signature", "Section Break", "Repair Completion (การซ่อมเสร็จสิ้น)"),
        ("actions_performed", "section_2d_break", "Text", "Actions Performed"),
        ("completion_date", "actions_performed", "Datetime", "Completion Date"),

        # SECTION 3A: Reporter Confirmation
        ("section_3a_break", "completion_date", "Section Break", "Reporter Confirmation (ผู้แจ้งยืนยัน)"),
        ("reporter_confirmed", "section_3a_break", "Check", "Reporter Confirmed (ยืนยันแล้ว)"),
        ("reporter_confirmation_photos", "reporter_confirmed", "Attach Image", "Confirmation Photos"),
        ("reporter_confirmation_notes", "reporter_confirmation_photos", "Small Text", "Confirmation Notes"),
        ("reporter_satisfaction", "reporter_confirmation_notes", "Select", "Satisfaction (ความพึงพอใจ)"),

        # SECTION 3B: Hygiene & Safety (Supervisor fills)
        ("section_3b_break", "reporter_satisfaction", "Section Break", "Section 3: Hygiene & Safety (บันทึกสุขลักษณะ/ความปลอดภัย)"),
        ("hygiene_status", "section_3b_break", "Select", "Hygiene Status (สถานะสุขลักษณะ)"),
        ("cleanliness_before_machine", "hygiene_status", "Select", "Machine Cleanliness Before"),
        ("cleanliness_after_machine", "cleanliness_before_machine", "Select", "Machine Cleanliness After"),
        ("cleanliness_before_area", "cleanliness_after_machine", "Select", "Area Cleanliness Before"),
        ("cleanliness_after_area", "cleanliness_before_area", "Select", "Area Cleanliness After"),
        ("parts_inserted", "cleanliness_after_area", "Table", "Parts Inserted (อุปกรณ์ที่นำเข้า)"),
        ("parts_removed", "parts_inserted", "Table", "Parts Removed (อุปกรณ์ที่นำออก)"),
        ("supervisor_verification_notes", "parts_removed", "Small Text", "Supervisor Notes (หมายเหตุหัวหน้า)"),
        ("supervisor_signature", "supervisor_verification_notes", "Signature", "Supervisor Signature (ลายเซ็น)"),

        # SECTION 4: Final Remarks
        ("section_4_break", "supervisor_signature", "Section Break", "Final Remarks (หมายเหตุเพิ่มเติม)"),
        ("final_remarks", "section_4_break", "Text", "Final Remarks (หมายเหตุ)"),
    ]

    print("🔧 Starting Asset Repair field reorganization...")
    print(f"📋 Total fields to organize: {len(field_order)}")
    print()

    updated_count = 0
    created_count = 0

    for field_name, insert_after, fieldtype, label in field_order:
        # Check if it's a section break (might need to create)
        if fieldtype == "Section Break":
            if not frappe.db.exists('Custom Field', f'Asset Repair-{field_name}'):
                # Create section break
                doc = frappe.get_doc({
                    'doctype': 'Custom Field',
                    'dt': 'Asset Repair',
                    'fieldname': field_name,
                    'label': label,
                    'fieldtype': 'Section Break',
                    'insert_after': insert_after,
                    'collapsible': 1
                })
                doc.insert(ignore_permissions=True)
                created_count += 1
                print(f"✅ Created: {field_name}")
            else:
                # Update existing section break
                doc = frappe.get_doc('Custom Field', f'Asset Repair-{field_name}')
                doc.insert_after = insert_after
                doc.label = label
                doc.save(ignore_permissions=True)
                updated_count += 1
                print(f"📝 Updated: {field_name}")
        else:
            # Update existing field
            if frappe.db.exists('Custom Field', f'Asset Repair-{field_name}'):
                doc = frappe.get_doc('Custom Field', f'Asset Repair-{field_name}')
                doc.insert_after = insert_after
                doc.save(ignore_permissions=True)
                updated_count += 1
                print(f"📝 Updated: {field_name}")
            else:
                print(f"⚠️  Field not found: {field_name} (may need to be created)")

    frappe.db.commit()

    print()
    print("=" * 60)
    print(f"✅ Reorganization complete!")
    print(f"   Created: {created_count} section breaks")
    print(f"   Updated: {updated_count} fields")
    print()
    print("🔄 Please run: bench --site tub clear-cache")
    print("🔄 Then refresh your browser to see the changes")
    print("=" * 60)
