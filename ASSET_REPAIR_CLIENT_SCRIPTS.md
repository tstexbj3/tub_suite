# Asset Repair Client Scripts

**Last Updated:** 2026-01-26
**Status:** WORKING

---

## Overview

Client Scripts are JavaScript code that runs on Asset Repair forms to enforce field-level permissions and visibility that cannot be controlled by standard ERPNext permissions or Custom Field settings.

---

## Active Client Scripts

### 1. Lock Engineering Sections After Completion

**DocType:** Asset Repair

**Why Needed:**
- Supervisor role has `Write: 1` permission at DocType level
- This overrides field-level `read_only_depends_on` conditions
- Without this script, supervisors can edit engineering fields in "Pending Supervisor Verification" state

**What It Does:**
1. Forces engineering fields to read-only after engineering work is complete
2. Hides Reporter Confirmation section except in Finished state

**Locked States:**
- Pending GM Final Approval
- Approved for Repair
- Pending Supervisor Verification
- Pending Reporter Confirmation
- Finished

**Fields Made Read-Only:**
- `action_type` - Type of action (ซ่อม/เปลี่ยนอะไหล่/ปรับปรุง)
- `custom_cost_type` - Cost type (ในประกัน/นอกประกัน)
- `custom_รายละเอยดการดำเนนการ` - Action details
- `custom_ระบสาเหต` - Root cause
- `estimated_cost` - Estimated cost
- `spare_parts_used` - Spare parts table
- `estimated_repair_duration` - Duration
- `assigned_engineer` - Assigned engineer
- `engineering_assessment_date` - Assessment date
- `engineering_assessment_by` - Assessed by
- `engineering_notes` - Engineering notes
- `supervisor_review_date` - Supervisor review date
- `supervisor_reviewed_by` - Reviewed by

**Full Script:**

```javascript
frappe.ui.form.on('Asset Repair', {
    refresh: function(frm) {
        // Lock engineering sections after engineering work is done
        const engineering_locked_states = [
            'Pending GM Final Approval',
            'Approved for Repair',
            'Pending Supervisor Verification',
            'Pending Reporter Confirmation',
            'Finished'
        ];

        if (engineering_locked_states.includes(frm.doc.workflow_state)) {
            // Lock all fields in Engineering Department sections
            const engineering_fields = [
                'action_type',
                'custom_cost_type',
                'custom_รายละเอยดการดำเนนการ',
                'custom_ระบสาเหต',
                'estimated_cost',
                'spare_parts_used',
                'estimated_repair_duration',
                'assigned_engineer',
                'engineering_assessment_date',
                'engineering_assessment_by',
                'engineering_notes',
                'supervisor_review_date',
                'supervisor_reviewed_by'
            ];

            engineering_fields.forEach(field => {
                frm.set_df_property(field, 'read_only', 1);
            });
        }

        // Show Reporter Confirmation section ONLY in Finished state
        if (frm.doc.workflow_state !== 'Finished') {
            frm.set_df_property('reporter_confirmation_section', 'hidden', 1);
            frm.set_df_property('reporter_confirmation_date', 'hidden', 1);
            frm.set_df_property('reporter_confirmation_photos', 'hidden', 1);
            frm.set_df_property('reporter_confirmation_notes', 'hidden', 1);
        }
    }
});
```

---

## How to Add/Update Client Scripts

### Via Web UI (RECOMMENDED):

1. Go to: **Setup → Customize → Client Script**
2. Click **New**
3. Fill in:
   - **Name:** Lock Engineering Sections After Completion
   - **DocType:** Asset Repair
   - **Enabled:** ✓ (checked)
   - **Script:** (paste JavaScript code above)
4. Click **Save**

### Via Bench Console:

```python
import frappe
frappe.init(site='tub')
frappe.connect()

script = frappe.get_doc({
    'doctype': 'Client Script',
    'name': 'Lock Engineering Sections After Completion',
    'dt': 'Asset Repair',
    'enabled': 1,
    'script': '''
frappe.ui.form.on('Asset Repair', {
    refresh: function(frm) {
        // ... script code here ...
    }
});
'''
})
script.insert()
frappe.db.commit()
```

---

## Testing Client Scripts

**Test Procedure:**

1. Open Asset Repair document in browser
2. Open browser DevTools (F12) → Console tab
3. Change workflow state to test different states
4. Verify fields are locked/hidden as expected

**Expected Behavior:**

| Workflow State | Engineering Fields | Reporter Confirmation Section |
|----------------|-------------------|------------------------------|
| Draft | Editable | Hidden |
| Pending GM Approval Section 1 | Editable | Hidden |
| Pending Engineering Assessment | Editable | Hidden |
| Pending Engineering Supervisor Review | Editable | Hidden |
| Pending GM Final Approval | **READ-ONLY** | Hidden |
| Approved for Repair | **READ-ONLY** | Hidden |
| Pending Supervisor Verification | **READ-ONLY** | Hidden |
| Pending Reporter Confirmation | **READ-ONLY** | Hidden |
| Finished | **READ-ONLY** | **Visible** |

---

## Debugging Client Scripts

### Check if script is loaded:

Open browser DevTools → Console:
```javascript
// Check frappe.ui.form.handlers
console.log(frappe.ui.form.handlers['Asset Repair']);
```

### Check if script is running:

Add console.log to script:
```javascript
frappe.ui.form.on('Asset Repair', {
    refresh: function(frm) {
        console.log('Client script running!');
        console.log('Workflow state:', frm.doc.workflow_state);

        // ... rest of script ...
    }
});
```

### Check field properties:

```javascript
// In browser console
let frm = cur_frm;
console.log('action_type read_only:', frm.get_df('action_type').read_only);
console.log('reporter_confirmation_section hidden:', frm.get_df('reporter_confirmation_section').hidden);
```

---

## Common Issues

### Issue 1: Script doesn't run

**Possible Causes:**
- Client Script not enabled
- JavaScript syntax error
- Cache not cleared

**Fix:**
1. Check Client Script is enabled in UI
2. Check browser console for JavaScript errors
3. Clear cache: `bench --site tub clear-cache`
4. Hard refresh browser: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

### Issue 2: Fields still editable

**Possible Causes:**
- User has higher permission level (e.g., Administrator)
- Script not checking correct workflow_state value
- Field name typo in script

**Fix:**
1. Test with non-Administrator user
2. Add console.log to check workflow_state value
3. Verify field names match Custom Field fieldname values

### Issue 3: Script runs but fields revert to editable

**Possible Causes:**
- Another script or code overriding the read_only property
- Form refresh after save

**Fix:**
1. Ensure script runs on both `refresh` and `onload` events
2. Add script logic to `validate` event if needed

---

## Alternative Approaches (NOT USED)

### ❌ Field-level `read_only_depends_on`

**Why Not Used:**
- Role-based Write permissions override field-level conditions
- Supervisor needs Write permission for other fields but not engineering fields

### ❌ DocType Permission based on workflow state

**Why Not Used:**
- Too coarse-grained - would lock ALL fields, not just engineering fields
- Supervisors need to edit Hygiene/Safety fields in same state

### ❌ Server-side validation

**Why Not Used:**
- Only prevents save, doesn't prevent editing
- Poor user experience - error after filling form

### ✅ Client Script (CHOSEN APPROACH)

**Why Used:**
- Granular control over specific fields
- Works alongside role-based permissions
- Real-time feedback - fields locked immediately on form load
- Easy to update without database changes

---

## Version History

| Date | Changes | By |
|------|---------|-----|
| 2026-01-26 | Created "Lock Engineering Sections After Completion" client script | Claude |
| 2026-01-26 | Added Reporter Confirmation section hiding logic | Claude |
| 2026-01-26 | Updated to hide reporter fields except in Finished state | Claude |

---

**END OF DOCUMENTATION**
