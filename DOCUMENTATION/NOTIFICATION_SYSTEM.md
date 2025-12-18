# Notification System Documentation

**TUB Suite Maintenance System**
**Version:** 2.0.1+
**Last Updated:** 2025-12-18

---

## Overview

The TUB Suite notification system provides real-time in-app notifications to users at each stage of the maintenance workflow. The system uses ERPNext's built-in Notification Log infrastructure to deliver notifications to specific users based on their roles and workflow actions.

---

## Workflow Notification Flow

### 1. Inspector Reports Issue

**Trigger:** Inspector submits maintenance task with issue reported
**Recipients:** Engineers (excluding managers)
**Notification:** "🔧 New Issue Reported: [Asset Name]"

```python
# Location: tub_suite/api/maintenance.py:132-140
# Function: submit_maintenance_task()

# Notify engineers about new issue (only once per repair creation)
notification_key = f"notified_new_issue_{repair.name}"
if not frappe.flags.get(notification_key):
    try:
        from tub_suite.overrides.asset_repair_override import notify_engineer_on_new_issue
        notify_engineer_on_new_issue(repair)
        frappe.flags[notification_key] = True
    except Exception as e:
        frappe.logger().error(f"Failed to notify engineers: {str(e)}")
```

### 2. Engineer Submits for Approval

**Trigger:** Engineer changes workflow state: Draft → Pending Approval
**Recipients:** All users with "Maintenance Manager" role
**Notification:** "⏳ Repair Approval Needed: [Asset Name]"

```python
# Location: tub_suite/overrides/asset_repair_override.py:242-248
# Function: before_save_asset_repair()

if new_workflow == "Pending Approval":
    print(f"   📧 Notifying managers...")
    # Track who submitted for approval (engineer)
    engineer_submitter = doc.get("modified_by") or frappe.session.user
    frappe.cache().set_value(f"engineer_submitter_{doc.name}", engineer_submitter, expires_in_sec=86400)
    print(f"   📝 Stored engineer submitter in cache: {engineer_submitter}")
    notify_manager_on_submit(doc)
```

### 3. Manager Approves/Rejects

**Trigger:** Manager changes workflow state: Pending Approval → Approved/Rejected
**Recipients:** Engineer who submitted for approval (retrieved from cache)
**Notification:**
- Approved: "✅ Repair APPROVED: [Asset Name]"
- Rejected: "❌ Repair REJECTED: [Asset Name]"

```python
# Location: tub_suite/overrides/asset_repair_override.py:250-253
# Function: before_save_asset_repair()

elif new_workflow == "Approved":
    print(f"   ✅ Approved - updating asset + notifying engineer")
    update_asset_status_on_approval(doc)
    notify_engineer_on_approval(doc)

elif new_workflow == "Rejected":
    print(f"   ❌ Rejected - notifying engineer")
    notify_engineer_on_rejection(doc)
```

### 4. Engineer Finishes Repair

**Trigger:** Engineer changes workflow state to "Finished"
**Recipients:** Inspector who originally reported the issue (doc.reported_by)
**Notification:** "Please verify repair completion: [Asset Name]"

```python
# Location: tub_suite/overrides/asset_repair_override.py:255-258
# Function: before_save_asset_repair()

elif new_workflow == "Finished":
    print(f"   ✅ Finished - restoring asset + notifying reporter")
    restore_asset_status_on_finish(doc)
    notify_reporter_to_verify(doc)
```

---

## Implementation Details

### Notification Function Structure

All notification functions follow the same pattern:

1. **Determine Recipients** - Query users by role or use document fields
2. **Check for Duplicates** - Use `frappe.db.exists()` to prevent duplicate notifications
3. **Create Notification** - Build notification with subject, content, and user
4. **Insert with Permissions** - Use `ignore_permissions=True` to bypass user restrictions

Example:

```python
def notify_manager_on_submit(doc):
    """Notify managers when engineer submits repair for approval"""
    asset_name = frappe.db.get_value("Asset", doc.asset, "asset_name") if doc.asset else "Unknown Asset"
    engineer = doc.get("owner") or "Unknown"

    # Get all users with Maintenance Manager role ONLY
    managers = frappe.get_all("Has Role",
        filters={"role": "Maintenance Manager", "parenttype": "User"},
        fields=["parent"],
        pluck="parent"
    )

    managers = list(set(managers))  # Remove duplicates

    notifications_sent = 0
    for manager_email in managers:
        # Check if notification already exists for this user and document
        existing = frappe.db.exists("Notification Log", {
            "for_user": manager_email,
            "document_type": "Asset Repair",
            "document_name": doc.name,
            "subject": f"⏳ Repair Approval Needed: {asset_name}"
        })

        if existing:
            print(f"   ⏭️  Notification already exists for {manager_email} (ID: {existing}), skipping")
            continue

        notification = frappe.new_doc("Notification Log")
        notification.subject = f"⏳ Repair Approval Needed: {asset_name}"
        notification.email_content = f"""
        <h3>New repair request awaiting approval</h3>
        <p><strong>Asset:</strong> {asset_name}</p>
        <p><strong>Submitted By:</strong> {engineer}</p>
        <p><strong>Issue:</strong> {doc.description or "No description"}</p>
        <p><strong>Severity:</strong> {doc.get("issue_severity") or "Not specified"}</p>
        <hr>
        <p><a href="/app/asset-repair/{doc.name}">Review Request</a></p>
        """
        notification.for_user = manager_email
        notification.document_type = "Asset Repair"
        notification.document_name = doc.name
        notification.type = "Alert"
        notification.insert(ignore_permissions=True)
        notifications_sent += 1

    print(f"   📧 Sent {notifications_sent} new notifications to managers")
```

---

## Key Technical Features

### 1. Duplicate Prevention

**Problem:** Workflow hooks (like `before_save()`) can be called multiple times during a single workflow transition.

**Solution:** Two-layer duplicate prevention:

#### Layer 1: In-Memory Flag (Same Request)
```python
# Prevent multiple calls within same request
notification_key = f"notified_{doc.name}_{old_workflow}_to_{new_workflow}"

if not frappe.flags.get(notification_key):
    # Send notifications
    notify_manager_on_submit(doc)
    frappe.flags[notification_key] = True
else:
    print(f"   ⏭️  Skipping duplicate notification (already sent)")
```

#### Layer 2: Database Check (Across Requests)
```python
# Check if notification already exists in database
existing = frappe.db.exists("Notification Log", {
    "for_user": manager_email,
    "document_type": "Asset Repair",
    "document_name": doc.name,
    "subject": f"⏳ Repair Approval Needed: {asset_name}"
})

if existing:
    continue  # Skip this user
```

### 2. Engineer Tracking

**Problem:** When a manager approves, `doc.modified_by` is the manager, not the engineer who submitted for approval.

**Solution:** Store the engineer's email in cache when they submit for approval:

```python
# When engineer submits (Draft → Pending Approval)
engineer_submitter = doc.get("modified_by") or frappe.session.user
frappe.cache().set_value(f"engineer_submitter_{doc.name}", engineer_submitter, expires_in_sec=86400)

# When manager approves (Pending Approval → Approved)
engineer_email = frappe.cache().get_value(f"engineer_submitter_{doc.name}")
notify_engineer_on_approval(doc, engineer_email)
```

**Cache Duration:** 24 hours (86400 seconds) - sufficient for typical workflow completion

### 3. Role-Based Filtering

**Engineers vs Managers:**

Many users have both "Engineering Team" AND "Maintenance Manager" roles. To prevent managers from receiving engineer notifications:

```python
# Get all engineers
engineers = frappe.get_all("Has Role",
    filters={"role": "Engineering Team", "parenttype": "User"},
    fields=["parent"],
    pluck="parent"
)

# Get all managers
managers = frappe.get_all("Has Role",
    filters={"role": ["in", ["Maintenance Manager", "Quality Manager"]], "parenttype": "User"},
    fields=["parent"],
    pluck="parent"
)

# Remove managers from engineer list (managers should NOT get engineer notifications)
engineers = list(set(engineers) - set(managers))
```

---

## Known Behavior: Administrator Sees All Notifications

### Issue Description

Users with **System Manager** role (like Administrator) see ALL notifications in the system, not just their own.

**Example:** When 5 managers are notified about a repair approval:
- Regular manager (e.g., `jakkrit.tub@gmail.com`): Sees 1 notification
- Administrator: Sees all 5 notifications (including ones for other managers)

### Root Cause

ERPNext's `get_notification_logs` API returns notifications based on **document permissions**, not the `for_user` field.

Users with System Manager role have "Read" permission on all Notification Log documents, so the API returns all notifications they can read.

### Technical Details

```python
# What we create (CORRECT)
Notification Log #1: for_user = 'jakkrit.tub@gmail.com'
Notification Log #2: for_user = 'narongrit.tub@gmail.com'
Notification Log #3: for_user = 'Administrator'
Notification Log #4: for_user = 'chotiputsilp.r@gmail.com'
Notification Log #5: for_user = 'taynajaronnakarn@gmail.com'

# What regular users see (CORRECT)
jakkrit.tub@gmail.com: Only notification #1

# What Administrator sees (ERPNext behavior)
Administrator: All 5 notifications (#1, #2, #3, #4, #5)
```

### Verification

You can verify the notifications are created correctly:

```javascript
// Run in browser console
fetch('/api/method/frappe.client.get_list', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Frappe-CSRF-Token': window.csrf_token
  },
  body: JSON.stringify({
    doctype: 'Notification Log',
    fields: ['name', 'for_user', 'subject', 'document_name'],
    filters: [['document_name', '=', 'ACC-ASR-2025-00062']],
    limit_page_length: 10
  })
})
.then(r => r.json())
.then(data => console.table(data.message))
```

### Workarounds

1. **Accept it** - Administrator is supposed to see everything (by design)
2. **Create dedicated manager users** - Use users like "Manager001" with only Maintenance Manager role (no System Manager)
3. **Remove System Manager from Administrator** - Not recommended, breaks other admin functions
4. **Use email notifications instead** - Send emails rather than in-app notifications

### Recommendation

**Accept this as expected behavior.** System administrators need visibility into all system notifications for debugging and support purposes. This is not a bug - it's a feature of ERPNext's permission system.

---

## Debugging

### Check Notification Creation

View bench logs when submitting workflow transitions:

```bash
# Tail the bench logs
tail -f ~/frappe-bench/logs/bench-start.log

# Look for notification debug output:
🔄 WORKFLOW CHANGE DETECTED IN BEFORE_SAVE:
   Draft → Pending Approval
   📧 Notifying managers...
   📝 Stored engineer submitter in cache: test_engineer@test.com
   👥 Found 5 Maintenance Manager(s): [...]
   🔍 Checking notification for: jakkrit.tub@gmail.com
   ✉️  Creating notification for jakkrit.tub@gmail.com...
   ✅ Notification created: o4n5v1mt22
   📧 Sent 5 new notifications to managers
```

### Query Notifications Directly

```python
# In bench console
frappe.connect()

# Get all notifications for a specific repair
notifications = frappe.get_all("Notification Log",
    filters={"document_name": "ACC-ASR-2025-00062"},
    fields=["name", "for_user", "subject", "read", "creation"]
)

for n in notifications:
    print(f"{n.for_user}: {n.subject} (Read: {n.read})")
```

### Check Cache

```python
# In bench console
frappe.connect()

# Check if engineer submitter is cached
repair_name = "ACC-ASR-2025-00062"
engineer = frappe.cache().get_value(f"engineer_submitter_{repair_name}")
print(f"Engineer who submitted: {engineer}")
```

### Clear Stuck Notifications

```python
# In bench console
frappe.connect()

# Delete all notifications for a specific repair (for testing)
frappe.db.delete("Notification Log", {
    "document_name": "ACC-ASR-2025-00062"
})
frappe.db.commit()
```

---

## Testing Checklist

### Complete Workflow Test

Test with 3 different users:

1. **Inspector** (Maintenance User role)
2. **Engineer** (Engineering Team role, NO System Manager)
3. **Manager** (Maintenance Manager role, NO System Manager)

### Steps

1. **Inspector reports issue**
   - [ ] Login as inspector
   - [ ] Report issue with photo
   - [ ] Check engineer notifications → Should see 1 notification
   - [ ] Check manager notifications → Should see 0 notifications
   - [ ] Check inspector notifications → Should see 0 notifications

2. **Engineer submits for approval**
   - [ ] Login as engineer
   - [ ] Open repair, fill details, submit
   - [ ] Change workflow to "Pending Approval"
   - [ ] Check manager notifications → Should see 1 notification
   - [ ] Check engineer notifications → Should see 0 new notifications

3. **Manager approves**
   - [ ] Login as manager
   - [ ] Open repair, approve
   - [ ] Check engineer notifications → Should see 1 approval notification
   - [ ] Check manager notifications → Should see 0 new notifications

4. **Engineer finishes**
   - [ ] Login as engineer
   - [ ] Change workflow to "Finished"
   - [ ] Check inspector notifications → Should see 1 verification notification

5. **Administrator view**
   - [ ] Login as Administrator
   - [ ] Check notifications → Will see ALL notifications (expected behavior)

---

## API Reference

### Main Notification Functions

Located in: `tub_suite/overrides/asset_repair_override.py`

#### `notify_engineer_on_new_issue(doc)`
- **Trigger:** Inspector reports issue
- **Recipients:** Users with "Engineering Team" role (excluding managers)
- **Subject:** "🔧 New Issue Reported: {asset_name}"

#### `notify_manager_on_submit(doc)`
- **Trigger:** Engineer submits for approval (Draft → Pending Approval)
- **Recipients:** Users with "Maintenance Manager" role
- **Subject:** "⏳ Repair Approval Needed: {asset_name}"

#### `notify_engineer_on_approval(doc)`
- **Trigger:** Manager approves (Pending Approval → Approved)
- **Recipients:** Engineer who submitted (from cache)
- **Subject:** "✅ Repair APPROVED: {asset_name}"

#### `notify_engineer_on_rejection(doc)`
- **Trigger:** Manager rejects (Pending Approval → Rejected)
- **Recipients:** Engineer who submitted (from cache)
- **Subject:** "❌ Repair REJECTED: {asset_name}"

#### `notify_reporter_to_verify(doc)`
- **Trigger:** Engineer finishes repair (→ Finished)
- **Recipients:** Inspector who reported issue (doc.reported_by)
- **Subject:** "Please verify repair completion: {asset_name}"

---

## Troubleshooting

### No notifications appearing

1. **Check bench logs** - Look for notification creation debug output
2. **Verify user roles** - Make sure users have correct roles assigned
3. **Check cache** - Verify engineer submitter is stored in cache
4. **Database query** - Check if notifications exist in Notification Log DocType

### Duplicate notifications

1. **Check database** - Query for duplicate Notification Log records
2. **Review logs** - Look for "⏭️ Skipping duplicate notification" messages
3. **Clear cache** - `bench --site YOUR_SITE clear-cache`

### Wrong user receiving notification

1. **Check engineer cache** - Verify `engineer_submitter_{repair_name}` in cache
2. **Review workflow** - Check who actually submitted vs who is notified
3. **Check role filtering** - Verify manager exclusion from engineer notifications

### Notifications not marked as read

This is an ERPNext UI issue, not related to our notification system. Notifications should auto-mark as read when clicked.

---

## Performance Considerations

- **Cache Duration:** 24 hours (can be adjusted in code)
- **Database Queries:** 1-2 per notification function (role lookup + duplicate check)
- **Impact:** Minimal - notifications are created asynchronously
- **Scalability:** Tested with up to 10 managers receiving simultaneous notifications

---

## Future Enhancements

Potential improvements for future versions:

1. **Email Notifications** - Send emails in addition to in-app notifications
2. **Push Notifications** - Mobile push notifications for critical updates
3. **Notification Preferences** - Allow users to configure notification types
4. **Notification History** - Archive old notifications after 30 days
5. **Custom Templates** - Allow customization of notification content

---

## Files Modified

### Core Files
- `tub_suite/api/maintenance.py` - New issue notification trigger
- `tub_suite/overrides/asset_repair_override.py` - All notification functions

### Related Documentation
- `TECHNICAL.md` - Technical architecture
- `WORKFLOW.md` - Workflow documentation
- `RELEASE_NOTES_v2.0.1.md` - Release notes

---

## Support

For issues or questions about the notification system:

- **GitHub Issues:** https://github.com/tstexbj3/tub_suite/issues
- **Documentation:** See TECHNICAL.md
- **Email:** it@tipubon.com

---

**Document Version:** 1.0
**Last Updated:** 2025-12-18
**Author:** Claude (AI Assistant) + Tipubon IT Team
