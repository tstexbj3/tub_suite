# TUB Maintenance Portal - Known Issues and Investigation Guide

**Document Type:** Bug Tracking and Investigation
**Version:** 1.0
**Last Updated:** December 16, 2024

---

## Current Known Issues

### 🔴 ISSUE #1: Asset Status Badge Not Updating After Approval

**Status:** UNDER INVESTIGATION
**Priority:** HIGH
**Reported:** December 16, 2024
**Affected:** Search results display

---

#### Symptom

When manager approves a repair with "Major - Asset Must Stop" severity:
- Asset **should** change status to "Out of Order"
- Search results **should** show red "Out of Order" badge
- **Actual:** Badge still shows old status (e.g., "Submitted")

**Example from user report:**
```
Search for "u-ac" shows:
- Asset: เครื่องปรับอากาศห้องประชุม 1
- Badge: "Submitted" (green)
- Expected: "Out of Order" (red)
```

---

#### What SHOULD Happen

```
1. Engineer creates repair
2. Engineer sets severity = "Major - Asset Must Stop"
3. Engineer submits for approval
4. Manager approves repair
   ↓
5. System calls: update_asset_status_on_approval()
   ↓
6. Asset document updated: status = "Out of Order"
   ↓
7. Search results show: "Out of Order" badge (red)
```

---

#### Investigation Findings

**Code Exists and Looks Correct:**

File: `tub_suite/overrides/asset_repair_override.py`

```python
# Line 234-295
def update_asset_status_on_approval(doc):
    """Update asset status when manager APPROVES repair"""

    severity = doc.get("issue_severity")
    workflow_state = doc.get("workflow_state")

    if workflow_state != "Approved":
        return

    asset_doc = frappe.get_doc("Asset", doc.asset)

    if severity == "Major - Asset Must Stop":
        # Should change to Out of Order
        if asset_doc.status != "Out of Order":
            asset_doc.status = "Out of Order"
            asset_doc.save(ignore_permissions=True)
```

**Hooks Registered:**

File: `tub_suite/hooks.py`

```python
# Line 41-43
override_doctype_class = {
    "Asset Repair": "tub_suite.overrides.asset_repair_override.CustomAssetRepair"
}

# Line 47-54
doc_events = {
    "Asset Repair": {
        "validate": "tub_suite.overrides.asset_repair_override.validate_asset_repair",
        "before_save": "tub_suite.overrides.asset_repair_override.before_save_asset_repair",
        "before_submit": "tub_suite.overrides.asset_repair_override.before_submit_asset_repair",
        "on_update_after_submit": "tub_suite.overrides.asset_repair_override.on_update_after_submit_asset_repair"
    }
}
```

**Function Called From Two Places:**

1. `on_update_after_submit()` method (line 68-69):
   ```python
   if old_workflow != new_workflow and new_workflow == "Approved":
       update_asset_status_on_approval(self)
   ```

2. `before_save_asset_repair()` function (line 205-206):
   ```python
   if workflow_changed:
       if doc.get("workflow_state") == "Approved":
           update_asset_status_on_approval(doc)
   ```

---

#### Possible Causes

**1. Hooks Not Active**
- System may not have loaded custom class override
- `bench restart` not run after code changes
- Code syntax error preventing load

**2. Workflow State Issue**
- Workflow state value not exactly "Approved"
- Possible values: "Approved", "approved", " Approved " (spaces)
- Case sensitivity

**3. Issue Severity Field**
- Value not exactly "Major - Asset Must Stop"
- Possible: "Major", "major", "Major - Asset must Stop" (case diff)

**4. Caching**
- Frontend caching old asset status
- Browser cache showing stale data
- API cache issue

**5. Search Query Issue**
- Search API (`search_assets`) not fetching fresh data
- Database query caching
- Asset status updated but not committed

---

#### Debugging Steps

**Step 1: Verify Hooks Loaded**

```bash
cd /home/user/frappe-bench
bench console
```

```python
>>> from tub_suite import hooks
>>> print(hooks.override_doctype_class)
# Should show: {'Asset Repair': 'tub_suite.overrides.asset_repair_override.CustomAssetRepair'}

>>> print(hooks.doc_events)
# Should show Asset Repair events

>>> # Test if custom class loaded
>>> import frappe
>>> doc = frappe.get_doc("Asset Repair", "AR-001")  # Use real repair ID
>>> print(type(doc))
# Should show: <class 'tub_suite.overrides.asset_repair_override.CustomAssetRepair'>
```

**Step 2: Check Actual Values**

```python
>>> # Check repair document
>>> repair = frappe.get_doc("Asset Repair", "AR-001")
>>> print(f"Workflow State: '{repair.workflow_state}'")
>>> print(f"Issue Severity: '{repair.issue_severity}'")
>>> print(f"Asset: {repair.asset}")

>>> # Check asset document
>>> asset = frappe.get_doc("Asset", repair.asset)
>>> print(f"Asset Status: '{asset.status}'")
>>> print(f"Asset Name: {asset.asset_name}")
```

**Step 3: Manual Trigger Test**

```python
>>> from tub_suite.overrides.asset_repair_override import update_asset_status_on_approval
>>> repair = frappe.get_doc("Asset Repair", "AR-001")
>>> update_asset_status_on_approval(repair)
>>> frappe.db.commit()

>>> # Check if asset changed
>>> asset = frappe.get_doc("Asset", repair.asset)
>>> print(f"Asset Status After Manual Trigger: {asset.status}")
```

**Step 4: Test Search API**

```python
>>> from tub_suite.api.asset import search_assets
>>> results = search_assets("u-ac")
>>> for asset in results['assets']:
...     print(f"{asset['name']}: {asset['status']}")
```

**Step 5: Check Console Logs**

After approval, check if print statements appear:

```python
# These should print when approval happens:
print(f"🔧 ASSET STATUS UPDATE CALLED")
print(f"   Repair: {doc.name}")
print(f"   Severity: {doc.get('issue_severity')}")
```

If NOT printing → Function not being called

---

#### Temporary Workarounds

**For Users - Refresh Data:**
1. Hard refresh browser: Ctrl+Shift+R
2. Clear browser cache
3. Open in incognito window
4. Try different browser

**For Admins - Manual Fix:**
1. Open Asset document directly
2. Click "Edit" (if submitted, amend or cancel+submit)
3. Change status to "Out of Order" manually
4. Add comment: "Manual status change - approved repair [AR-ID]"
5. Save

**For Developers - Force Update:**
```python
# Run in bench console
asset = frappe.get_doc("Asset", "U-AC-01C")
asset.status = "Out of Order"
asset.save(ignore_permissions=True)
frappe.db.commit()
```

---

#### Required Tests

To verify fix:

**Test Case 1: New Repair Approval**
1. Create new repair
2. Set severity = "Major - Asset Must Stop"
3. Submit for approval
4. Manager approves
5. **CHECK:** Open Asset document - status should be "Out of Order"
6. **CHECK:** Search for asset - badge should be red "Out of Order"

**Test Case 2: Minor Repair (Should NOT Change)**
1. Create repair with severity = "Minor - Asset Operational"
2. Submit and approve
3. **CHECK:** Asset status should NOT change
4. **CHECK:** Should stay "Submitted"

**Test Case 3: Multiple Repairs**
1. Create 2 Major repairs for same asset
2. Approve first → status "Out of Order"
3. Complete and verify first
4. **CHECK:** Status should STAY "Out of Order" (2nd repair still open)
5. Complete and verify second
6. **CHECK:** Status should restore to "Submitted"

---

#### Next Steps for Resolution

**Immediate Actions:**
1. [ ] Run debugging steps 1-5 above
2. [ ] Check bench console logs during approval
3. [ ] Verify hooks are loaded correctly
4. [ ] Test manual trigger function

**If Hooks Not Loading:**
1. [ ] Check for Python syntax errors
2. [ ] Run `bench migrate`
3. [ ] Run `bench restart`
4. [ ] Clear all caches: `bench --site tub clear-cache`
5. [ ] Reload browser

**If Values Don't Match:**
1. [ ] Check exact string values in database
2. [ ] Add `.strip()` to comparisons
3. [ ] Make comparisons case-insensitive
4. [ ] Update field definitions if needed

**If Function Not Called:**
1. [ ] Check workflow is assigned to Asset Repair
2. [ ] Verify workflow state transition occurs
3. [ ] Add more print statements for debugging
4. [ ] Check if transaction is being rolled back

---

## Other Known Issues

### 🟡 Issue #2: Search Results Photo Display

**Status:** MINOR
**Priority:** LOW

Some assets show no photo in search results even though photo exists in Asset document.

**Cause:** Photo may be in custom field or attachment instead of standard `image` field.

**Workaround:** Open asset directly to view photo.

---

### 🟡 Issue #3: Badge Status Styling Missing on New Statuses

**Status:** COSMETIC
**Priority:** LOW

If custom asset statuses added, badges may show with default styling instead of colored badges.

**Solution:** Add CSS for new statuses:
```css
.status-your-new-status {
  background: #your-color;
  color: white;
}
```

---

## Resolved Issues (For Reference)

### ✅ Issue: Photo Upload Crash in VerifyRepair

**Fixed:** December 16, 2024
**Cause:** Missing `assetName` prop in PhotoUpload component
**Solution:** Added `assetName={repair.repair?.asset || 'ASSET'}` to component

### ✅ Issue: Completion Date Not Auto-Filling

**Fixed:** December 16, 2024
**Cause:** Auto-fill logic checking current state instead of transition
**Solution:** Changed to detect workflow transition: `old_workflow != new_workflow`

### ✅ Issue: Single QR Card Not Centered

**Fixed:** December 16, 2024
**Cause:** Grid layout with no centering
**Solution:** Changed to flexbox with `justify-content: center`

---

## Reporting New Issues

**To report a bug:**

1. **Document the Issue:**
   - What did you do? (steps to reproduce)
   - What happened? (actual result)
   - What should happen? (expected result)
   - Screenshots if applicable

2. **Gather Information:**
   - User role performing action
   - Browser and version
   - Date and time of issue
   - Any error messages
   - Console logs (F12 → Console tab)

3. **Submit Report:**
   - Email system administrator
   - Include all information from steps 1-2
   - Mention if issue is blocking work
   - Or create GitHub issue if using repository

**Good Bug Report Example:**
```
Title: Asset status not changing to Out of Order after approval

Steps to Reproduce:
1. Login as Engineer
2. Create repair for asset U-AC-01C
3. Set severity to "Major - Asset Must Stop"
4. Submit for approval
5. Login as Manager
6. Approve repair
7. Search for "u-ac" in portal

Expected: Asset shows "Out of Order" badge (red)
Actual: Asset shows "Submitted" badge (green)

Environment:
- Role: Maintenance Manager
- Browser: Chrome 120
- Date: 2024-12-16 14:30
- Repair ID: AR-00042
- Asset ID: U-AC-01C

Notes: Tried hard refresh, still shows old status
```

---

## Issue Tracking

| ID | Title | Priority | Status | Assigned To | Target Fix |
|----|-------|----------|--------|-------------|------------|
| #1 | Asset status badge not updating | HIGH | INVESTIGATING | Dev Team | TBD |
| #2 | Search photo display | LOW | BACKLOG | - | - |
| #3 | Badge styling for custom statuses | LOW | BACKLOG | - | - |

---

**Document Version:** 1.0
**Last Updated:** December 16, 2024
**Maintained By:** TUB Suite Development Team

**For bug reports:** Contact system administrator or development team
