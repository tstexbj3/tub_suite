#!/usr/bin/env python3
"""
Update custom_field.json fixture file with permanent field visibility rules
This is the CORRECT way - changes persist through bench migrate
"""
import json

fixture_path = "tub_suite/fixtures/custom_field.json"

# Load fixture
with open(fixture_path, 'r', encoding='utf-8') as f:
    fields = json.load(f)

# Fields that should hide from Draft, show from Pending Engineering Assessment onwards
engineering_depends = 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)'

engineering_fields = [
    'expected_completion_date',
    'issue_severity',
    'custom_cause_description',
    'custom_purchase_order_no'
]

# Reporter Confirmation fields - only at Pending Supervisor Verification
reporter_depends = 'eval:doc.workflow_state=="Pending Supervisor Verification"'
reporter_fields = [
    'reporter_confirmation_date',
    'reporter_confirmation_photos',
    'reporter_confirmation_notes',
    'reporter_confirmation_section'
]

# Inspector fields - always hidden
inspector_fields = [
    'requires_inspector_verification',
    'verification_notes',
    'verification_status'
]

# Update fields
updated_count = 0
for field in fields:
    if field.get('dt') != 'Asset Repair':
        continue

    fieldname = field.get('fieldname')

    if fieldname in engineering_fields:
        field['depends_on'] = engineering_depends
        field['hidden'] = 0
        print(f"✓ {fieldname}: Set engineering visibility")
        updated_count += 1

    elif fieldname in reporter_fields:
        field['depends_on'] = reporter_depends
        field['hidden'] = 0
        print(f"✓ {fieldname}: Set reporter visibility")
        updated_count += 1

    elif fieldname in inspector_fields:
        field['hidden'] = 1
        print(f"✓ {fieldname}: Hidden")
        updated_count += 1

# Save fixture
with open(fixture_path, 'w', encoding='utf-8') as f:
    json.dump(fields, f, indent=1, ensure_ascii=False)

print(f"\n✅ Updated {updated_count} fields in {fixture_path}")
print("Now run: bench --site tub migrate")
