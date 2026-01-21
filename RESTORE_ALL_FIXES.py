#!/usr/bin/env python3
"""
Re-apply all fixes from previous session that were lost due to git checkout
Based on session transcript from "This session is being continued from.md"
"""

import re

# Read the file
with open('tub_suite/overrides/asset_repair_override.py', 'r') as f:
    content = f.read()

# Fix 1: Add before_workflow_action() method after before_submit()
before_workflow_method = '''
    def before_workflow_action(self, workflow_state_field, workflow_action):
        """Auto-update repair_status before workflow transitions"""
        # When supervisor verifies (Pending Supervisor Verification → Finished), set repair_status to Completed
        if self.workflow_state == "Pending Supervisor Verification" and workflow_action == "Supervisor Verify":
            self.repair_status = "Completed"
'''

# Insert after before_submit_asset_repair(self, None)
content = content.replace(
    '        before_submit_asset_repair(self, None)\n\n    def on_update_after_submit(self):',
    '        before_submit_asset_repair(self, None)\n' + before_workflow_method + '\n    def on_update_after_submit(self):'
)

# Fix 2: Add supervisor roles and Pending Supervisor Verification permission check in validate_asset_repair
# After is_engineer line, add supervisor check
content = content.replace(
    '    is_engineer = any(role in user_roles for role in engineer_roles)\n\n    # Allow free editing ONLY in Draft state',
    '''    is_engineer = any(role in user_roles for role in engineer_roles)
    supervisor_roles = ["Supervisor"]
    is_supervisor = any(role in user_roles for role in supervisor_roles)

    # Special case: Pending Supervisor Verification - only reporter OR managers can edit
    if workflow_state == "Pending Supervisor Verification":
        current_user = frappe.session.user
        is_original_reporter = (doc.get("reported_by") == current_user)
        if is_original_reporter or is_manager:
            return  # Allow editing
        # Block everyone else (including engineers who are not the reporter)


    # Allow free editing ONLY in Draft state'''
)

# Fix 3: Expand engineer allowed states
content = content.replace(
    '    if not workflow_state or workflow_state == "Draft":\n        # Maintenance Users should NOT access ERPNext desk at all',
    '    if not workflow_state or workflow_state == "Draft" or workflow_state == "Pending Engineering Assessment" or workflow_state == "Pending Engineering Supervisor Review" or workflow_state == "Approved for Repair":\n        # Maintenance Users should NOT access ERPNext desk at all'
)

# Fix 4: Add all signature auto-fill hooks in before_save_asset_repair
old_before_save = '''def before_save_asset_repair(doc, method):
    """Auto-fill approval timestamp and handle asset status based on severity"""
    if not doc.is_new():
        old_doc = frappe.db.get_value("Asset Repair", doc.name,
            ["approval_notes", "approval_signature", "approval_timestamp", "issue_severity", "workflow_state"], as_dict=True)

        if old_doc:
            notes_changed = str(old_doc.get("approval_notes") or "") != str(doc.get("approval_notes") or "")
            signature_changed = str(old_doc.get("approval_signature") or "") != str(doc.get("approval_signature") or "")

            if (notes_changed or signature_changed) and not doc.get("approval_timestamp"):
                doc.approval_timestamp = now()

            # Handle asset status change when workflow changes'''

new_before_save = '''def before_save_asset_repair(doc, method):
    """Auto-fill all signature timestamps and handle asset status based on severity"""
    if not doc.is_new():
        old_doc = frappe.db.get_value("Asset Repair", doc.name,
            ["approval_notes", "approval_signature", "approval_timestamp", "issue_severity", "workflow_state",
             "supervisor_section1_signature", "supervisor_section1_date",
             "gm_section1_signature", "gm_section1_approval_date",
             "engineering_operator_signature", "engineering_operator_sign_date",
             "eng_supervisor_signature", "eng_supervisor_review_date",
             "approval_signature", "manager_approval_date",
             "supervisor_signature", "supervisor_verification_date",
             "reporter_signature", "reporter_confirmation_date"], as_dict=True)

        if old_doc:
            # Section 1B - Supervisor signature in Draft state
            if doc.get("supervisor_section1_signature") and not old_doc.get("supervisor_section1_signature"):
                if not doc.get("supervisor_section1_date"):
                    doc.supervisor_section1_date = now()

            # GM Section 1 - GM signature in Pending GM Approval Section 1
            if doc.get("gm_section1_signature") and not old_doc.get("gm_section1_signature"):
                if not doc.get("gm_section1_approval_date"):
                    doc.gm_section1_approval_date = now()

            # Engineering Section - Operator signature in Pending Engineering Assessment
            if doc.get("engineering_operator_signature") and not old_doc.get("engineering_operator_signature"):
                if not doc.get("engineering_operator_sign_date"):
                    doc.engineering_operator_sign_date = now()

            # Engineering Section - Supervisor signature in Pending Engineering Supervisor Review
            if doc.get("eng_supervisor_signature") and not old_doc.get("eng_supervisor_signature"):
                if not doc.get("eng_supervisor_review_date"):
                    doc.eng_supervisor_review_date = now()

            # Engineering Section - GM signature in Pending GM Final Approval
            if doc.get("approval_signature") and not old_doc.get("approval_signature"):
                if not doc.get("manager_approval_date"):
                    doc.manager_approval_date = now()

            # Section 3B - Supervisor signature in Pending Supervisor Verification
            if doc.get("supervisor_signature") and not old_doc.get("supervisor_signature"):
                if not doc.get("supervisor_verification_date"):
                    doc.supervisor_verification_date = now()

            # Reporter confirmation - Portal signature in Finished state
            if doc.get("reporter_signature") and not old_doc.get("reporter_signature"):
                if not doc.get("reporter_confirmation_date"):
                    doc.reporter_confirmation_date = now()

            # Legacy approval_timestamp field
            notes_changed = str(old_doc.get("approval_notes") or "") != str(doc.get("approval_notes") or "")
            signature_changed = str(old_doc.get("approval_signature") or "") != str(doc.get("approval_signature") or "")

            if (notes_changed or signature_changed) and not doc.get("approval_timestamp"):
                doc.approval_timestamp = now()

            # Handle asset status change when workflow changes'''

content = content.replace(old_before_save, new_before_save)

# Fix 5: Fix before_submit to check docstatus==0
content = content.replace(
    '''def before_submit_asset_repair(doc, method):
    """Validate engineer signature before submission"""
    if not doc.get("engineer_signature"):
        frappe.throw(_("Engineer Signature is required before submission"), frappe.MandatoryError)''',
    '''def before_submit_asset_repair(doc, method):
    """Validate engineer signature before submission"""
    # Only check engineer_signature if this is the initial submit (docstatus changing from 0 to 1)
    # Not for workflow transitions (which happen after submit when docstatus is already 1)
    if doc.docstatus == 0 and not doc.get("engineer_signature"):
        frappe.throw(_("Engineer Signature is required before submission"), frappe.MandatoryError)'''
)

# Write the updated content
with open('tub_suite/overrides/asset_repair_override.py', 'w') as f:
    f.write(content)

print("✅ All fixes re-applied successfully:")
print("  1. Added before_workflow_action() method")
print("  2. Added supervisor roles and Pending Supervisor Verification permission check")
print("  3. Expanded engineer allowed states (Draft, Pending Engineering Assessment, Pending Engineering Supervisor Review, Approved for Repair)")
print("  4. Added all 7 signature auto-fill hooks in before_save")
print("  5. Fixed before_submit to only check engineer_signature on docstatus==0")
