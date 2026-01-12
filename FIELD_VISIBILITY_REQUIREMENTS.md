# Asset Repair Field Visibility Requirements

**CRITICAL: These rules must be enforced in the fixture file `tub_suite/fixtures/custom_field.json`**
**DO NOT use temporary SQL fixes - they get overwritten by `bench migrate`**

## Draft State
**ONLY Section 1 fields should show:**
- repair_type
- repair_source
- repair_subject
- description
- issue_photos, issue_photos_2
- reported_by, reporter_department
- supervisor_section1_signature

**MUST BE HIDDEN in Draft:**
- expected_completion_date
- issue_severity
- custom_cause_description (ระบุสาเหตุ)
- custom_purchase_order_no
- reporter_confirmation_date
- reporter_confirmation_photos
- reporter_confirmation_notes
- reporter_confirmation_section
- requires_inspector_verification
- verification_notes
- verification_status
- All engineering fields

## Pending Engineering Assessment onwards
**Show these fields:**
- expected_completion_date
- issue_severity
- custom_cause_description
- custom_purchase_order_no
- Engineering section fields

**depends_on:**
```
eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)
```

## Pending Supervisor Verification ONLY
**Reporter Confirmation fields:**
- reporter_confirmation_section
- reporter_confirmation_date
- reporter_confirmation_photos
- reporter_confirmation_notes

**depends_on:**
```
eval:doc.workflow_state=="Pending Supervisor Verification"
```

## ALWAYS HIDDEN
**Inspector Verification fields (portal only):**
- requires_inspector_verification
- verification_notes
- verification_status

**hidden: 1**

## Section 1 Fields - Lock After Draft
**These fields must be read-only after Draft state:**
- repair_type
- repair_source
- repair_subject
- description

**Use Property Setters with:**
```
read_only_depends_on: eval:doc.workflow_state!="Draft"
```
