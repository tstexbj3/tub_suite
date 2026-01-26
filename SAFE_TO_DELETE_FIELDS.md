# Safe to Delete - Asset Repair Custom Fields

**Date:** 2026-01-26
**Verified:** These fields have ZERO usage in documents AND no code references

---

## ✅ SAFE TO DELETE (15 fields)

Delete these via **Customize Form**:

1. `approved_by` - Approved By
2. `custom_cause_description` - ระบุสาเหตุ
3. `custom_purchase_order_no` - ใบสั่งของเลขที่
4. `custom_การดำเนนการ` - การดำเนินการ (Table)
5. `custom_ใบสงของเลขท` - ใบสั่งของเลขที่
6. `engineering_operator_signed_by` - Signed By (ผู้ประเมิน)
7. `expected_completion_date` - Expected Completion Date
8. `final_remarks` - Final Remarks (หมายเหตุ)
9. `gm_section1_approved_by` - GM Approved By
10. `gm_section1_notes` - GM Notes (หมายเหตุ GM)
11. `manager_approved_by` - Approved By (ผู้อนุมัติ)
12. `received_by` - Received By (already hidden)
13. `received_date` - Received Date (already hidden)
14. `supervisor_verified_by` - Verified By (หัวหน้าตรวจรับ)
15. `verified_by` - Verified By (Inspector)

---

## ⚠️ KEEP (still referenced in code - 8 fields)

**Do NOT delete these yet:**

1. `completion_handover_date` - Used in print format + Python
2. `gm_section1_signature` - Used in print format + Python (legacy)
3. `reporter_signature` - Used in print format + Python
4. `verification_date` - Used in print format + Python
5. `verification_notes` - Used in print format + Client Script
6. `confirmation_date` - Used in Python + Client Script
7. `approval_time` - Used in Python
8. `custom_ระบสาเหต` - Used in Client Script

**To delete these later:**
- Remove from print format first
- Remove from Python code
- Remove from Client Scripts
- Then delete fields

---

## How to Delete

### Via UI (EASY):
1. Go to **Setup → Customize → Customize Form**
2. Select **Asset Repair**
3. Find each field in the list
4. Click the row → Click trash icon
5. Click **Update** at bottom
6. Run `bench clear-cache`
7. Run `bench --site tub export-fixtures`

### Via Script (BATCH):
```python
import frappe
frappe.init(site='tub')
frappe.connect()

safe_to_delete = [
    'approved_by',
    'custom_cause_description',
    'custom_purchase_order_no',
    'custom_การดำเนนการ',
    'custom_ใบสงของเลขท',
    'engineering_operator_signed_by',
    'expected_completion_date',
    'final_remarks',
    'gm_section1_approved_by',
    'gm_section1_notes',
    'manager_approved_by',
    'received_by',
    'received_date',
    'supervisor_verified_by',
    'verified_by'
]

for fieldname in safe_to_delete:
    try:
        frappe.db.sql("DELETE FROM `tabCustom Field` WHERE dt='Asset Repair' AND fieldname=%s", fieldname)
        print(f"✅ Deleted {fieldname}")
    except Exception as e:
        print(f"❌ Error deleting {fieldname}: {e}")

frappe.db.commit()
print("\n✅ Done! Run: bench clear-cache && bench --site tub export-fixtures")
```

---

## After Deletion

**Expected reduction:**
- From: 88 fields
- To: 73 fields
- Reduction: 15 fields (17%)

**Next steps:**
1. Delete these 15 fields
2. Test all workflow states
3. Export fixtures
4. Commit changes
