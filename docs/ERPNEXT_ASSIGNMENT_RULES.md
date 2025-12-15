# ERPNext Assignment Rules Setup Guide

How to configure automatic TODO assignment and escalation for TUB Suite maintenance workflow.

---

## What Are Assignment Rules?

Assignment Rules **automatically assign documents** to users when certain conditions are met.

**Use Cases in TUB Suite:**
- Auto-assign new Asset Repair to engineers
- Auto-assign verification tasks to inspectors
- Auto-assign approvals to managers

---

## Step-by-Step Setup

### 1. Access Assignment Rules

```
📍 Navigation Path:
Home → Settings → Automation → Assignment Rule → New
```

Or search in Awesome Bar: "Assignment Rule"

---

### 2. Create Rule: Auto-Assign Repairs to Engineers

#### Basic Details

| Field | Value |
|-------|-------|
| **Rule Name** | Auto Assign Repairs to Engineers |
| **Document Type** | Asset Repair |
| **Priority** | 1 |
| **Disabled** | ❌ Unchecked (enabled) |

#### Assignment Rule Section

**Assign Rule:**
- **Field:** `repair_status`
- **Condition:** `=` (equals)
- **Value:** `Pending`

**Advanced (Optional):** Use Python condition
```python
doc.repair_status == "Pending" and doc.requires_inspector_verification == 1
```

#### Assignment Days

| Field | Value |
|-------|-------|
| **Assignment Days** | Leave blank (assign immediately) |

#### Assign To

**Option 1: Assign to Role**
- **Assign To Field Type:** Role
- **Role:** Engineering Team

This assigns to ALL users with "Engineering Team" role.

**Option 2: Assign to Specific Users**
- **Assign To Field Type:** User
- **Users:** Select specific engineers (e.g., engineer1@example.com, engineer2@example.com)

#### Assignment Rule (Advanced Filters)

Click "Add Multiple" to add complex conditions:

| Field | Condition | Value |
|-------|-----------|-------|
| repair_status | = | Pending |
| docstatus | = | 0 (Draft) |

#### Unassign If (Auto-Close TODO)

**Close TODO when repair is no longer pending:**

**Condition:**
```python
doc.repair_status != "Pending"
```

Or use simple condition:
- **Field:** `repair_status`
- **Condition:** `!=`
- **Value:** `Pending`

#### Close Note

**Message shown when TODO auto-closes:**
```
Repair {doc.name} is no longer pending. Status: {doc.repair_status}
```

---

### 3. Create Rule: Assign Verification to Inspector

#### Basic Details

| Field | Value |
|-------|-------|
| **Rule Name** | Assign Verification to Inspector |
| **Document Type** | Asset Repair |
| **Priority** | 2 |

#### Assign Condition

**Condition:**
```python
doc.repair_status == "Completed - Pending Verification" and doc.reported_by
```

Or simple condition:
- **Field:** `repair_status`
- **Condition:** `=`
- **Value:** `Completed - Pending Verification`

#### Assign To

**Assign to original inspector:**
- **Assign To Field Type:** Field Value
- **Field:** `reported_by`

This assigns back to the inspector who originally reported the issue.

#### Unassign If

```python
doc.verification_status in ["Verified - Passed", "Verified - Failed"]
```

---

### 4. Create Rule: Assign Approval to Manager

#### Basic Details

| Field | Value |
|-------|-------|
| **Rule Name** | Assign Approval to Manager |
| **Document Type** | Asset Repair |
| **Priority** | 3 |

#### Assign Condition

```python
doc.verification_status == "Verified - Passed" and doc.approval_status == "Pending"
```

#### Assign To

- **Assign To Field Type:** Role
- **Role:** Maintenance Manager

#### Unassign If

```python
doc.approval_status in ["Approved", "Rejected"]
```

---

## Email Alerts Setup

### Navigate to Email Alerts

```
Home → Settings → Email → Email Alert → New
```

---

### Alert 1: New Repair Request

| Field | Value |
|-------|-------|
| **Name** | New Repair Request |
| **Document Type** | Asset Repair |
| **Send Alert On** | New (doc creation) |
| **Enabled** | ✅ Checked |

#### Conditions

**Condition:**
```python
doc.repair_status == "Pending"
```

#### Recipients

Add multiple recipient types:

1. **By Role:**
   - Role: Engineering Team

2. **By Role:**
   - Role: Maintenance Manager

3. **By Field:**
   - Field: reported_by (notify inspector who reported)

#### Message

**Subject:**
```
🔧 New Repair Request: {doc.name} - {doc.asset}
```

**Message:**
```html
<h3>New Asset Repair Request</h3>
<p>A new repair request has been created.</p>

<table style="border-collapse: collapse; width: 100%;">
  <tr style="background: #f5f5f5;">
    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Repair ID</strong></td>
    <td style="padding: 8px; border: 1px solid #ddd;">{doc.name}</td>
  </tr>
  <tr>
    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Asset</strong></td>
    <td style="padding: 8px; border: 1px solid #ddd;">{doc.asset}</td>
  </tr>
  <tr style="background: #f5f5f5;">
    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Reported By</strong></td>
    <td style="padding: 8px; border: 1px solid #ddd;">{doc.reported_by}</td>
  </tr>
  <tr>
    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Description</strong></td>
    <td style="padding: 8px; border: 1px solid #ddd;">{doc.error_description}</td>
  </tr>
  <tr style="background: #f5f5f5;">
    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Expected Completion</strong></td>
    <td style="padding: 8px; border: 1px solid #ddd;">{doc.expected_completion_date}</td>
  </tr>
</table>

<p style="margin-top: 20px;">
  <a href="{frappe.utils.get_url()}/app/asset-repair/{doc.name}"
     style="background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
    View Repair Request
  </a>
</p>
```

---

### Alert 2: Repair Ready for Verification

| Field | Value |
|-------|-------|
| **Name** | Repair Ready for Verification |
| **Document Type** | Asset Repair |
| **Send Alert On** | Value Change |
| **Value Changed** | repair_status |

#### Conditions

```python
doc.repair_status == "Completed - Pending Verification"
```

#### Recipients

**By Field:**
- Field: reported_by (original inspector)

#### Message

**Subject:**
```
✅ Please Verify Repair: {doc.name} - {doc.asset}
```

**Message:**
```html
<h3>Repair Completed - Verification Required</h3>
<p>The repair you reported has been completed by the engineering team.</p>

<p><strong>Please visit the asset and verify the repair:</strong></p>
<ol>
  <li>Go to the asset location</li>
  <li>Inspect the repair work</li>
  <li>Take after-repair photos</li>
  <li>Submit verification</li>
</ol>

<table style="border-collapse: collapse; width: 100%;">
  <tr>
    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Asset</strong></td>
    <td style="padding: 8px; border: 1px solid #ddd;">{doc.asset}</td>
  </tr>
  <tr style="background: #f5f5f5;">
    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Original Issue</strong></td>
    <td style="padding: 8px; border: 1px solid #ddd;">{doc.error_description}</td>
  </tr>
  <tr>
    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Repair Notes</strong></td>
    <td style="padding: 8px; border: 1px solid #ddd;">{doc.actions_performed}</td>
  </tr>
</table>

<p style="margin-top: 20px;">
  <a href="{frappe.utils.get_url()}/maintenance/verify/{doc.name}"
     style="background: #10b981; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
    Verify Repair (Mobile)
  </a>
</p>
```

---

### Alert 3: Repair Ready for Approval

| Field | Value |
|-------|-------|
| **Name** | Repair Ready for Approval |
| **Document Type** | Asset Repair |
| **Send Alert On** | Value Change |
| **Value Changed** | verification_status |

#### Conditions

```python
doc.verification_status == "Verified - Passed"
```

#### Recipients

**By Role:**
- Role: Maintenance Manager

#### Message

**Subject:**
```
✅ Repair Verified - Approve: {doc.name}
```

**Message:**
```html
<h3>Repair Verified by Inspector - Ready for Approval</h3>

<p>The inspector has verified that the repair was completed successfully.</p>

<table style="border-collapse: collapse; width: 100%;">
  <tr>
    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Repair ID</strong></td>
    <td style="padding: 8px; border: 1px solid #ddd;">{doc.name}</td>
  </tr>
  <tr style="background: #f5f5f5;">
    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Asset</strong></td>
    <td style="padding: 8px; border: 1px solid #ddd;">{doc.asset}</td>
  </tr>
  <tr>
    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Verified By</strong></td>
    <td style="padding: 8px; border: 1px solid #ddd;">{doc.verified_by}</td>
  </tr>
  <tr style="background: #f5f5f5;">
    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Verification Notes</strong></td>
    <td style="padding: 8px; border: 1px solid #ddd;">{doc.verification_notes}</td>
  </tr>
</table>

<p><strong>Action Required:</strong> Please review and approve this repair request.</p>

<p style="margin-top: 20px;">
  <a href="{frappe.utils.get_url()}/app/asset-repair/{doc.name}"
     style="background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
    Review & Approve
  </a>
</p>
```

---

### Alert 4: Overdue Repairs (Escalation)

| Field | Value |
|-------|-------|
| **Name** | Overdue Repairs Notification |
| **Document Type** | Asset Repair |
| **Send Alert On** | Days After |
| **Days After Date Field** | expected_completion_date |
| **Days in Advance** | 0 (send on due date) |

Or use negative value for escalation:
- **Days in Advance:** -2 (send 2 days AFTER overdue)

#### Conditions

```python
doc.repair_status in ["Pending", "In Progress"] and doc.expected_completion_date
```

#### Recipients

1. **By Role:** Engineering Team
2. **By Role:** Maintenance Manager

#### Message

**Subject:**
```
⚠️ OVERDUE: Repair {doc.name} - {doc.asset}
```

**Message:**
```html
<h3 style="color: #ef4444;">⚠️ Overdue Repair Request</h3>

<p>This repair request is overdue and requires immediate attention.</p>

<table style="border-collapse: collapse; width: 100%;">
  <tr>
    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Repair ID</strong></td>
    <td style="padding: 8px; border: 1px solid #ddd;">{doc.name}</td>
  </tr>
  <tr style="background: #fee;">
    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Expected Completion</strong></td>
    <td style="padding: 8px; border: 1px solid #ddd;">{doc.expected_completion_date}</td>
  </tr>
  <tr>
    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Status</strong></td>
    <td style="padding: 8px; border: 1px solid #ddd;">{doc.repair_status}</td>
  </tr>
  <tr style="background: #f5f5f5;">
    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Asset</strong></td>
    <td style="padding: 8px; border: 1px solid #ddd;">{doc.asset}</td>
  </tr>
</table>

<p style="margin-top: 20px;">
  <a href="{frappe.utils.get_url()}/app/asset-repair/{doc.name}"
     style="background: #ef4444; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
    View Overdue Repair
  </a>
</p>
```

---

## Testing Assignment Rules

### 1. Test Auto-Assignment

```bash
# Create test repair via console
bench --site [your-site] console

repair = frappe.get_doc({
    "doctype": "Asset Repair",
    "asset": "ASSET-001",
    "failure_date": frappe.utils.today(),
    "error_description": "Test issue",
    "repair_status": "Pending",
    "reported_by": "inspector@example.com"
})
repair.insert()
frappe.db.commit()

# Check if TODO was created
todos = frappe.get_all("ToDo",
    filters={
        "reference_type": "Asset Repair",
        "reference_name": repair.name
    },
    fields=["name", "allocated_to", "status"]
)
print(todos)
```

### 2. Verify Email Sent

```bash
# Check email queue
bench --site [your-site] console

emails = frappe.get_all("Email Queue",
    filters={"reference_doctype": "Asset Repair"},
    fields=["name", "recipient", "status", "creation"],
    limit=5,
    order_by="creation desc"
)
print(emails)
```

### 3. Check Assignment Rule Logs

```
Navigate to: Assignment Rule → Click on rule → View "Assignment Rule Log"
```

---

## Common Issues

### Issue: TODO Not Created

**Cause:** Assignment Rule condition not met or disabled.

**Solution:**
1. Check Assignment Rule is enabled (Disabled = unchecked)
2. Verify condition matches document
3. Check user has role specified in "Assign To"

### Issue: Email Not Sent

**Cause:** Email account not configured or Email Alert disabled.

**Solution:**
1. Go to: Email Account → Verify outgoing email enabled
2. Go to: Email Alert → Check "Enabled" is checked
3. Test email: Send test email from Email Account

### Issue: Assignment Rule Not Triggering

**Cause:** Priority conflict or condition syntax error.

**Solution:**
1. Check for Python syntax errors in condition
2. Lower priority number = higher priority
3. Check Document Type is correct (case-sensitive)

---

## Quick Reference

### Assignment Rule Conditions Syntax

**Simple:**
```python
doc.field_name == "Value"
```

**Multiple Conditions:**
```python
doc.status == "Open" and doc.priority == "High"
```

**Check if field exists:**
```python
doc.get("field_name")
```

**Check if field in list:**
```python
doc.status in ["Open", "In Progress"]
```

### Email Alert Jinja Variables

| Variable | Example |
|----------|---------|
| `{doc.field}` | {doc.name} |
| `{doc.owner}` | User who created |
| `{frappe.utils.get_url()}` | Site URL |
| `{frappe.utils.now()}` | Current datetime |
| `{frappe.utils.today()}` | Current date |

---

## Backup & Export

### Export Assignment Rules

```bash
# Export as JSON
bench --site [your-site] export-doc Assignment\ Rule "Auto Assign Repairs to Engineers"

# File saved to: sites/[your-site]/assignments_backup.json
```

### Import on Another Site

```bash
# Import from JSON
bench --site [production-site] import-doc \
  apps/tub_suite/tub_suite/fixtures/assignment_rules.json
```

---

**Last Updated:** 2025-12-15
**TUB Suite Version:** 2.0.0
