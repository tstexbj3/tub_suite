# Asset Repair Workflow Configuration - FM-EN-04

## CRITICAL WORKFLOW STATES (Must exist in database)
1. Draft
2. Pending GM Approval Section 1
3. Pending Engineering Assessment
4. Pending Engineering Supervisor Review
5. Pending GM Final Approval
6. Approved for Repair
7. Repair In Progress
8. Pending Reporter Confirmation
9. Pending Reporter Supervisor Verification (Section 3 hygiene check)
10. Finished
11. Rejected
12. Cancelled

## CORRECT WORKFLOW FLOW
```
1. Operator creates Draft via portal
2. Supervisor opens Draft → Signs in Section 1B → Clicks "Supervisor Verify"
3. Draft → Pending GM Approval Section 1 (GM/Maintenance Manager Approve/Reject)
4. If Approved → Pending Engineering Assessment
5. → Pending Engineering Supervisor Review
6. → Pending GM Final Approval
7. → Approved for Repair
8. → Repair In Progress
9. → Pending Reporter Confirmation (Section 3A)
10. After reporter confirms → Pending Reporter Supervisor Verification (Section 3B hygiene)
11. → Finished
```

## KEY FIELD VISIBILITY CONDITIONS

### Section 1B (Supervisor Verification)
**Fields:**
- `section_1b_break` - Section Break
- `supervisor_section1_notes` - Small Text
- `supervisor_section1_signature` - Signature

**Visibility Condition:**
```javascript
eval:doc.workflow_state=="Draft" && !doc.__islocal
```

### Issue Photos Field
- Field: `issue_photos` (Attach Image)
- Shows uploaded photo URL
- Public (is_private = 0)

## MANDATORY FIELD CONDITIONS

### Engineer Signature
```javascript
mandatory_depends_on: eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Repair In Progress"].includes(doc.workflow_state)
```

## CRITICAL API FIXES

### Photo Upload Fix in maintenance.py
```python
# MUST use frappe.db.set_value() NOT repair.save()
# to avoid field lock validation

if len(parsed_photos) > 0 and parsed_photos[0]:
    frappe.db.set_value("Asset Repair", repair.name, "issue_photos", parsed_photos[0], update_modified=False)
```

### Server Script Issue
**Asset Repair - Lock Reporter Fields** server script blocks:
- failure_date
- description
- reported_by

On `if not doc.is_new()` - prevents editing after creation.

## WORKFLOW TRANSITION THAT NEEDS FIXING

**Current (WRONG):**
```
Draft → Submit → Pending Reporter Supervisor Verification
```

**Should be:**
```
Draft → Supervisor Verify → Pending GM Approval Section 1
```

**How to fix:**
1. Go to Workflow: "Repair Approval WorkFlow"
2. Remove transition: Draft → Submit → Pending Reporter Supervisor Verification
3. Add transition: Draft → Supervisor Verify → Pending GM Approval Section 1
4. Set allowed role: Supervisor

## ROLES NEEDED
- Supervisor (has access to Draft state)
- Maintenance Manager / GM (approves Section 1)
- Engineer
- Engineering Supervisor (WARNING: May not exist - causes workflow errors)

## FILES MODIFIED
1. `/apps/tub_suite/tub_suite/api/maintenance.py` - Photo upload handling
2. `/apps/tub_suite/maintenance-react-dev/src/pages/ReportIssue.jsx` - Photo upload UI
3. Custom Fields visibility conditions
4. Workflow transitions

## QUICK FIX COMMANDS

### If workflow state is wrong:
```python
frappe.db.set_value("Asset Repair", "ACC-ASR-XXXX-XXXXX", "workflow_state", "Pending GM Approval Section 1", update_modified=False)
frappe.db.commit()
```

### If Section 1B not showing:
```python
field = frappe.get_doc("Custom Field", {"dt": "Asset Repair", "fieldname": "section_1b_break"})
field.depends_on = 'eval:doc.workflow_state=="Draft" && !doc.__islocal'
field.save()
frappe.db.commit()
```

### Clear cache after any changes:
```bash
bench --site tub clear-cache
```

## BUILD PORTAL AFTER CHANGES:
```bash
cd ~/frappe-bench/apps/tub_suite/maintenance-react-dev
npm run build
```

## WORKFLOW FILE LOCATION
`/apps/tub_suite/tub_suite/fixtures/workflow.json`

Note: Workflow fixture has validation errors with missing "Engineering Supervisor" role
