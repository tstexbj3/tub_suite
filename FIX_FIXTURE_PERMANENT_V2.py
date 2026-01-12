#!/usr/bin/env python3
"""
PERMANENT FIX V2 - Complete engineering fields visibility
Updates custom_field.json fixture file directly

Run this ONCE, then run: bench --site tub migrate
"""
import json

print("=" * 80)
print("PERMANENT FIXTURE FIX V2 - Complete Engineering Field Visibility")
print("=" * 80)

# Load fixture
fixture_path = "tub_suite/fixtures/custom_field.json"
with open(fixture_path, 'r', encoding='utf-8') as f:
    fields = json.load(f)

# Visibility rules
engineering_depends = 'eval:["Pending Engineering Assessment","Pending Engineering Supervisor Review","Pending GM Final Approval","Approved for Repair","Pending Supervisor Verification","Finished"].includes(doc.workflow_state)'
reporter_depends = 'eval:doc.workflow_state=="Pending Supervisor Verification"'

# Complete list of engineering fields to hide from Draft
engineering_fields = [
    # Engineering Section 1 - Assessment fields
    'custom_engineering_section',  # Section break
    'action_type',
    'custom_cost_type',
    'custom_engineering_todo_items',  # THIS WAS MISSING!
    'spare_parts_used',

    # Engineering Section 2 - Dates and signatures
    'expected_duration_days',
    'engineering_operator_signature',
    'engineering_operator_sign_date',
    'engineering_operator_signed_by',
    'repair_start_date',
    'repair_end_date',
    'eng_supervisor_signature',
    'eng_supervisor_review_date',
    'approval_signature',
    'manager_approval_date',
    'manager_approved_by',
    'gm_final_approval_date',

    # Engineering Section 3 - Completion
    'completion_handover_date',
    'repair_result_status',

    # Other engineering fields
    'expected_completion_date',
    'issue_severity',
    'custom_cause_description',
    'custom_purchase_order_no',
]

# Fields to fix
field_updates = {}

# Add all engineering fields
for fieldname in engineering_fields:
    field_updates[fieldname] = {'depends_on': engineering_depends, 'hidden': 0}

# Reporter Confirmation - only at Pending Supervisor Verification
field_updates.update({
    'reporter_confirmation_section': {'depends_on': reporter_depends, 'hidden': 0},
    'reporter_confirmation_date': {'depends_on': reporter_depends, 'hidden': 0},
    'reporter_confirmation_photos': {'depends_on': reporter_depends, 'hidden': 0},
    'reporter_confirmation_notes': {'depends_on': reporter_depends, 'hidden': 0},
})

# Inspector fields - always hidden (portal only)
field_updates.update({
    'requires_inspector_verification': {'hidden': 1},
    'verification_notes': {'hidden': 1},
    'verification_status': {'hidden': 1},
})

# Apply updates
updated_count = 0
not_found = []

for fieldname, updates in field_updates.items():
    found = False
    for field in fields:
        if field.get('dt') != 'Asset Repair':
            continue

        if field.get('fieldname') == fieldname:
            found = True
            old_depends = field.get('depends_on')
            old_hidden = field.get('hidden')

            # Apply updates
            for key, value in updates.items():
                field[key] = value

            print(f"\n✓ {fieldname}:")
            if 'depends_on' in updates:
                print(f"  depends_on: {updates['depends_on'][:60]}...")
            if 'hidden' in updates:
                print(f"  hidden: {updates['hidden']}")

            updated_count += 1
            break

    if not found:
        not_found.append(fieldname)

# Save fixture
with open(fixture_path, 'w', encoding='utf-8') as f:
    json.dump(fields, f, indent=1, ensure_ascii=False)

print("\n" + "=" * 80)
print(f"✅ UPDATED {updated_count} fields in {fixture_path}")
if not_found:
    print(f"⚠️  NOT FOUND ({len(not_found)}): {', '.join(not_found)}")
print("=" * 80)
print("\nNEXT STEPS:")
print("1. Review changes: git diff tub_suite/fixtures/custom_field.json")
print("2. When ready: bench --site tub migrate")
print("3. Clear cache: bench --site tub clear-cache")
print("\nThis fix is PERMANENT - it will survive future migrations!")
print("=" * 80)
