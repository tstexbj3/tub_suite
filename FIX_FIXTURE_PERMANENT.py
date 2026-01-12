#!/usr/bin/env python3
"""
PERMANENT FIX for field visibility
Updates custom_field.json fixture file directly

Run this ONCE, then run: bench --site tub migrate
"""
import json

print("=" * 80)
print("PERMANENT FIXTURE FIX - Field Visibility Rules")
print("=" * 80)

# Load fixture
fixture_path = "tub_suite/fixtures/custom_field.json"
with open(fixture_path, 'r', encoding='utf-8') as f:
    fields = json.load(f)

# Visibility rules from WORKFLOW_AND_FIELDS.md
engineering_depends = 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)'
reporter_depends = 'eval:doc.workflow_state=="Pending Supervisor Verification"'

# Fields to fix
field_updates = {
    # Engineering fields - hide from Draft
    'expected_completion_date': {'depends_on': engineering_depends, 'hidden': 0},
    'issue_severity': {'depends_on': engineering_depends, 'hidden': 0},
    'custom_cause_description': {'depends_on': engineering_depends, 'hidden': 0},
    'custom_purchase_order_no': {'depends_on': engineering_depends, 'hidden': 0},

    # Reporter Confirmation - only at Pending Supervisor Verification
    'reporter_confirmation_section': {'depends_on': reporter_depends, 'hidden': 0},
    'reporter_confirmation_date': {'depends_on': reporter_depends, 'hidden': 0},
    'reporter_confirmation_photos': {'depends_on': reporter_depends, 'hidden': 0},
    'reporter_confirmation_notes': {'depends_on': reporter_depends, 'hidden': 0},

    # Inspector fields - always hidden (portal only)
    'requires_inspector_verification': {'hidden': 1},
    'verification_notes': {'hidden': 1},
    'verification_status': {'hidden': 1},
}

# Apply updates
updated_count = 0
for field in fields:
    if field.get('dt') != 'Asset Repair':
        continue

    fieldname = field.get('fieldname')
    if fieldname in field_updates:
        updates = field_updates[fieldname]
        old_depends = field.get('depends_on')
        old_hidden = field.get('hidden')

        # Apply updates
        for key, value in updates.items():
            field[key] = value

        print(f"\n✓ {fieldname}:")
        if 'depends_on' in updates:
            print(f"  OLD depends_on: {old_depends}")
            print(f"  NEW depends_on: {updates['depends_on']}")
        if 'hidden' in updates:
            print(f"  OLD hidden: {old_hidden}")
            print(f"  NEW hidden: {updates['hidden']}")

        updated_count += 1

# Save fixture
with open(fixture_path, 'w', encoding='utf-8') as f:
    json.dump(fields, f, indent=1, ensure_ascii=False)

print("\n" + "=" * 80)
print(f"✅ UPDATED {updated_count} fields in {fixture_path}")
print("=" * 80)
print("\nNEXT STEPS:")
print("1. Review changes: git diff tub_suite/fixtures/custom_field.json")
print("2. When ready: bench --site tub migrate")
print("3. Clear cache: bench --site tub clear-cache")
print("\nThis fix is PERMANENT - it will survive future migrations!")
print("=" * 80)
