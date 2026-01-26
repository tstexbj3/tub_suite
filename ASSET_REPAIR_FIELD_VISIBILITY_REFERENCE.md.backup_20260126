# Asset Repair Field Visibility Reference
## Complete Documentation - DO NOT FUCK THIS UP AGAIN

**Last Updated:** 2026-01-25
**Status:** WORKING - DO NOT MODIFY WITHOUT BACKING UP FIRST

---

## CRITICAL RULES

1. **NEVER run `bench migrate` without checking Custom Field changes first**
2. **ALWAYS export fixtures AFTER making visibility changes in database**
3. **ALWAYS test in all workflow states before committing**
4. **READ THIS FILE after every context compact**

---

## Workflow States Overview

```
Draft
  ↓ (Supervisor Verify)
Pending GM Approval Section 1
  ↓ (GM Approve Section 1)
Pending Engineering Assessment
  ↓ (Engineering Assessment Complete)
Pending Engineering Supervisor Review
  ↓ (Supervisor Review Complete)
Pending GM Final Approval
  ↓ (GM Final Approve)
Approved for Repair
  ↓ (Finish Repair)
Pending Supervisor Verification
  ↓ (Supervisor Verify)
Pending Reporter Confirmation
  ↓ (Reporter Confirm via Portal)
Finished
```

---

## Field Visibility by Workflow State

### Section 0: Document Header (ส่วนหัวเอกสาร FM-EN-04)

**Standard Fields (NOT Custom Fields):**

| Field | Type | Visible States | Notes |
|-------|------|----------------|-------|
| `failure_date` | Datetime | ALL STATES | Always visible, read-only after Draft |
| `description` (error_description) | Text | ALL STATES | Always visible |

**Why these show everywhere:**
- Standard ERPNext fields
- No `depends_on` conditions set
- Property Setter with `depends_on` doesn't work reliably for standard fields
- **LEAVE THEM VISIBLE - users complained when we tried to hide them**

---

### Section 1: Asset Info & Reporter

**Custom Fields:**

| Field | Type | Visible States | depends_on |
|-------|------|----------------|------------|
| `section_1_break` | Section Break | ALL | NONE |
| `repair_source` | Select | ALL | NONE |
| `repair_subject` | Data | ALL | NONE |
| `issue_photos` | Attach Image | ALL | NONE |
| `reported_by` | Link (User) | ALL | NONE |
| `reporter_department` | Link (Department) | ALL | NONE |

**Options for repair_source:**
- Portal (แจ้งผ่านระบบ)
- Manual (แจ้งด้วยตนเอง)
- Planned Maintenance (ตามแผน) ← PM issues use this

---

### Section 3B: Hygiene & Safety

**CRITICAL: This section MUST show in these states:**
- Pending Supervisor Verification (editable)
- Pending Reporter Confirmation (READ-ONLY)
- Finished (READ-ONLY)

**Custom Fields:**

| Field | Fieldname | Type | depends_on | read_only_depends_on |
|-------|-----------|------|------------|---------------------|
| Section Break | `section_3b_break` | Section Break | `eval:["Pending Supervisor Verification", "Pending Reporter Confirmation", "Finished"].includes(doc.workflow_state)` | - |
| Hygiene Status | `hygiene_status` | Select | SAME | `eval:["Pending Reporter Confirmation", "Finished"].includes(doc.workflow_state)` |
| Machine Before | `cleanliness_before_machine` | Select | SAME | SAME |
| Machine After | `cleanliness_after_machine` | Select | SAME | SAME |
| Area Before | `cleanliness_before_area` | Select | SAME | SAME |
| Area After | `cleanliness_after_area` | Select | SAME | SAME |
| Parts Inserted | `parts_inserted` | Table | SAME | SAME |
| Parts Removed | `parts_removed` | Table | SAME | SAME |
| Final Remarks | `final_remarks` | Text | SAME | SAME |
| Completion Date | `completion_handover_date` | Date | SAME | SAME |

**Hygiene Status Options:**
- เรียบร้อย (Clean)
- ไม่เรียบร้อย/ต้องแก้ไข (Not Clean)

**Cleanliness Options:**
- สะอาด (Clean)
- ไม่สะอาด (Not Clean)

---

### Reporter Confirmation Section

**CRITICAL: This section should ONLY show in Draft state**

| Field | Fieldname | Type | depends_on |
|-------|-----------|------|------------|
| Section Break | `reporter_confirmation_section` | Section Break | `eval:doc.workflow_state == "Draft"` |

**DO NOT add any fields under this section** - it's a legacy section that causes confusion

---

## Custom Field JSON Structure

**Example: section_3b_break**

```json
{
  "fieldname": "section_3b_break",
  "fieldtype": "Section Break",
  "label": "Section 3: Hygiene & Safety (บันทึกสุขลักษณะ/ความปลอดภัย)",
  "insert_after": "amended_from",
  "depends_on": "eval:[\"Pending Supervisor Verification\", \"Pending Reporter Confirmation\", \"Finished\"].includes(doc.workflow_state)",
  "dt": "Asset Repair",
  "doctype": "Custom Field"
}
```

**Example: parts_inserted (with read-only condition)**

```json
{
  "fieldname": "parts_inserted",
  "fieldtype": "Table",
  "label": "Parts Inserted (อุปกรณ์ที่นำเข้า)",
  "options": "Parts Inserted Item",
  "insert_after": "cleanliness_after_area",
  "depends_on": "eval:[\"Pending Supervisor Verification\", \"Pending Reporter Confirmation\", \"Finished\"].includes(doc.workflow_state)",
  "read_only_depends_on": "eval:[\"Pending Reporter Confirmation\", \"Finished\"].includes(doc.workflow_state)",
  "dt": "Asset Repair",
  "doctype": "Custom Field"
}
```

---

## How to Update Field Visibility

### Method 1: Via Database (RECOMMENDED)

```python
import frappe
frappe.init(site='tub')
frappe.connect()

# Update a Custom Field
cf = frappe.get_doc('Custom Field', 'Asset Repair-section_3b_break')
cf.depends_on = 'eval:["Pending Supervisor Verification", "Pending Reporter Confirmation", "Finished"].includes(doc.workflow_state)'
cf.save(ignore_permissions=True)
frappe.db.commit()

# Clear cache
# Run: bench clear-cache
```

### Method 2: Export to Fixture (AFTER database changes)

```bash
cd ~/frappe-bench
bench --site tub export-fixtures
```

This updates `tub_suite/fixtures/custom_field.json` with current database values.

### Method 3: Property Setter (for Standard Fields)

```python
import frappe
frappe.init(site='tub')
frappe.connect()

# For standard fields like failure_date
frappe.make_property_setter({
    'doctype': 'Asset Repair',
    'fieldname': 'failure_date',
    'property': 'read_only',
    'value': '1',
    'property_type': 'Check'
})
frappe.db.commit()
```

---

## Restore Script

**If someone fucks up the field visibility, run this:**

```bash
cd ~/frappe-bench
bench --site tub console < apps/tub_suite/RESTORE_FIELD_VISIBILITY.py
bench clear-cache
```

---

## Testing Checklist

**BEFORE committing any field visibility changes:**

- [ ] Test in **Draft** state - Section 1 visible, Section 3B hidden
- [ ] Test in **Pending Supervisor Verification** - Section 3B visible and editable
- [ ] Test in **Pending Reporter Confirmation** - Section 3B visible but READ-ONLY
- [ ] Test in **Finished** - Section 3B visible but READ-ONLY
- [ ] Test that **Reporter Confirmation section** is ONLY in Draft
- [ ] Test that **parts_inserted** and **parts_removed** tables show correctly
- [ ] Test that all hygiene/cleanliness fields show in correct states

---

## Common Mistakes (DO NOT DO THESE)

### ❌ WRONG: Using `||` operator

```javascript
"depends_on": "eval:doc.workflow_state==\"Draft\" || doc.workflow_state==\"Finished\""
```

**Problem:** Doesn't work reliably in Frappe v15

### ✅ CORRECT: Using `.includes()` with array

```javascript
"depends_on": "eval:[\"Draft\", \"Finished\"].includes(doc.workflow_state)"
```

---

### ❌ WRONG: Trying to hide standard fields with Custom Field

Standard fields like `failure_date`, `description` are NOT Custom Fields.

### ✅ CORRECT: Use Property Setter for standard fields

```python
frappe.make_property_setter({
    'doctype': 'Asset Repair',
    'fieldname': 'failure_date',
    'property': 'hidden',
    'value': '1',
    'property_type': 'Check'
})
```

**BUT:** Property Setter with `depends_on` doesn't work reliably. Just leave standard fields visible.

---

### ❌ WRONG: Running `bench migrate` without checking

`bench migrate` will OVERWRITE Custom Field settings with fixture values.

### ✅ CORRECT: Update database first, then export fixture

1. Update Custom Field in database
2. Test thoroughly
3. Run `bench export-fixtures`
4. Commit the updated `custom_field.json`

---

## Permissions by Role

### Maintenance Supervisor

**Can:**
- Create Asset Repair
- Edit in Draft state
- Submit to workflow (Supervisor Verify)
- Edit in Pending Supervisor Verification state
- Verify completion (Supervisor Verify)
- Confirm on behalf of reporter (Reporter Confirm)

**Cannot:**
- Edit in Engineering states
- Edit in GM Approval states
- Edit after Finished

### Maintenance Manager (GM)

**Can:**
- Approve in Pending GM Approval Section 1 (GM Approve Section 1)
- Approve in Pending GM Final Approval (GM Final Approve)
- Request changes (GM Request Changes)
- Reject (GM Reject)

**Cannot:**
- Edit Engineering fields
- Edit Hygiene/Safety fields

### Engineering Team

**Can:**
- Edit in Pending Engineering Assessment
- Fill engineering_todo_items
- Fill spare_parts_used
- Complete assessment (Engineering Assessment Complete)

**Cannot:**
- Edit Supervisor fields
- Edit GM fields

### Engineering Supervisor

**Can:**
- Edit in Pending Engineering Supervisor Review
- Review and approve (Supervisor Review Complete)
- Finish repair (Finish Repair)
- Fill hygiene/safety section in Approved for Repair

**Cannot:**
- Edit Reporter fields
- Edit GM approval fields

---

## Workflow Transitions

| From State | Action | To State | Allowed Roles |
|------------|--------|----------|---------------|
| Draft | Supervisor Verify | Pending GM Approval Section 1 | Supervisor, Maintenance Supervisor |
| Pending GM Approval Section 1 | GM Approve Section 1 | Pending Engineering Assessment | Maintenance Manager |
| Pending GM Approval Section 1 | GM Reject | Rejected | Maintenance Manager |
| Pending Engineering Assessment | Engineering Assessment Complete | Pending Engineering Supervisor Review | Engineering Team |
| Pending Engineering Supervisor Review | Supervisor Review Complete | Pending GM Final Approval | Engineering Supervisor |
| Pending GM Final Approval | GM Final Approve | Approved for Repair | Maintenance Manager |
| Pending GM Final Approval | GM Request Changes | Pending Engineering Assessment | Maintenance Manager |
| Approved for Repair | Finish Repair | Pending Supervisor Verification | Engineering Supervisor |
| Pending Supervisor Verification | Supervisor Verify | Pending Reporter Confirmation | Supervisor, Maintenance Supervisor |
| Pending Supervisor Verification | Supervisor Reject | Approved for Repair | Supervisor, Maintenance Supervisor |
| Pending Reporter Confirmation | Reporter Confirm | Finished | Supervisor, Maintenance Supervisor |

---

## File Locations

**Custom Fields Fixture:**
```
tub_suite/fixtures/custom_field.json
```

**Workflow Fixture:**
```
tub_suite/fixtures/workflow.json
```

**Field Visibility Fix Scripts:**
```
tub_suite/FIX_SECTION3B_VISIBILITY.py
tub_suite/FIX_SECTION0_CUSTOM_FIELDS.py
tub_suite/SHOW_HYGIENE_IN_PENDING_REPORTER.py
```

**Restore Script:**
```
tub_suite/RESTORE_FIELD_VISIBILITY.py (to be created)
```

---

## Backup and Restore

### Backup Current Settings

```bash
cd ~/frappe-bench
bench --site tub export-fixtures

# Backup the fixture
cp apps/tub_suite/tub_suite/fixtures/custom_field.json \
   apps/tub_suite/custom_field.json.backup_$(date +%Y%m%d_%H%M%S)
```

### Restore from Backup

```bash
cd ~/frappe-bench

# Restore fixture
cp apps/tub_suite/custom_field.json.backup_YYYYMMDD_HHMMSS \
   apps/tub_suite/tub_suite/fixtures/custom_field.json

# Import
bench --site tub migrate

# Clear cache
bench clear-cache
```

---

## PM Issue Report Workflow

**When Maintenance User reports issue from portal:**

1. Portal calls `submit_maintenance_task()` with `has_issue=1`
2. Backend creates Asset Repair:
   - `repair_source = "Planned Maintenance (ตามแผน)"`
   - `repair_subject` from portal (or default "PM Issue: {task_label}")
   - `repair_type` from portal (or default "ซ่อม")
   - `reported_by` = portal user email
   - `maintenance_task` = task label
3. Asset Repair starts in Draft state (NO workflow_state yet)
4. Email sent to Maintenance Supervisors
5. Supervisor opens in desk, reviews, clicks "Supervisor Verify"
6. Enters normal workflow → ... → Finished

**Key Files:**
- Portal: `maintenance-react-dev/src/pages/Checklist.jsx` (lines 250-297)
- Backend: `tub_suite/api/maintenance.py` (lines 109-159)

---

## Version History

| Date | Changes | By |
|------|---------|-----|
| 2026-01-25 | Fixed Section 3B visibility in Pending Reporter Confirmation | Claude |
| 2026-01-25 | Added parts_inserted/parts_removed to Section 3B | Claude |
| 2026-01-25 | Removed duplicate repair_type field | User |
| 2026-01-25 | Hidden Reporter Confirmation section except in Draft | Claude |
| 2026-01-22 | Initial PM workflow implementation | Claude |

---

**END OF REFERENCE - READ THIS BEFORE MAKING ANY CHANGES**
