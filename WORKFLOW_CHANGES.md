# Workflow Changes (2026-01-21)

## GM Final Approval - Request Changes Option

### Change Made
Modified the workflow transition from "Pending GM Final Approval" to allow GM to send the repair back to Engineering for corrections instead of only approving or rejecting.

### Before:
From "Pending GM Final Approval":
- **GM Final Approve** → Approved for Repair
- **GM Final Reject** → Rejected

### After:
From "Pending GM Final Approval":
- **GM Final Approve** → Approved for Repair
- **GM Request Changes** → Pending Engineering Assessment (send back for corrections)

### Benefit:
- GM can now request corrections without completely rejecting the repair
- Engineering team can fix issues and resubmit
- No need to create a new repair document
- Maintains workflow history and audit trail

### Implementation:
Updated workflow transition in console:
```python
workflow = frappe.get_doc("Workflow", "Asset Repair Workflow - Supervisor Only")
for t in workflow.transitions:
    if t.state == "Pending GM Final Approval" and t.action == "GM Final Reject":
        t.action = "GM Request Changes"
        t.next_state = "Pending Engineering Assessment"
workflow.save(ignore_permissions=True)
frappe.db.commit()
frappe.clear_cache()
```

### Testing Results:
✅ GM Approval Section 1 rejection - PASSED
✅ GM Final Approval request changes - PASSED
✅ Supervisor Verification workflow - PASSED
