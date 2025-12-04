# Complete Asset Repair Security Setup

## Problem
Managers can still edit all fields (Description, Failure Date, etc.) after submission.

## Root Cause
The validation hooks require Frappe server restart to take effect.

## Complete Setup Steps

### Step 1: Run Setup Functions (Browser Console)

Open browser console (F12) on `http://localhost:8000` and run these **one by one**:

#### 1a. Setup Custom Fields
```javascript
frappe.call({
    method: 'tub_suite.api.asset.setup_approval_fields',
    callback: function(r) {
        console.log(r.message);
        frappe.msgprint('Fields: ' + r.message.message);
    }
});
```

#### 1b. Setup Client Script
```javascript
frappe.call({
    method: 'tub_suite.api.asset.setup_client_script',
    callback: function(r) {
        console.log(r.message);
        frappe.msgprint('Script: ' + r.message.message);
    }
});
```

### Step 2: Clear Cache

In browser console:
```javascript
frappe.call({
    method: 'frappe.client.clear_cache',
    callback: function() {
        frappe.msgprint('Cache cleared. Please restart server.');
    }
});
```

### Step 3: Restart Frappe Server (REQUIRED!)

**This is the most important step!** The hooks.py changes require server restart.

Run in Windows PowerShell or WSL:

```bash
# Stop current server (if running in terminal, press Ctrl+C)

# Then restart:
wsl -d Ubuntu-24.04 --exec bash -c "cd ~/frappe-bench && bench restart"

# If bench restart doesn't work, use:
wsl -d Ubuntu-24.04 --exec bash -c "cd ~/frappe-bench && bench start"
```

### Step 4: Verify Setup

1. **Refresh browser** (Ctrl+Shift+R)
2. **Open any Asset Repair** (or create a test one)
3. **Submit it** (Draft → Submit)
4. **Try to edit Description field**

**Expected Result:**
- Server error: "Cannot modify Description after submission. This repair request is locked."

5. **Try to change Approval Status** to "Approved"
6. **Click Save**

**Expected Result:**
- ✅ Saves successfully
- ✅ Approved By = Your username (auto-filled)
- ✅ Approval Date & Time = Current server time (auto-filled)

---

## If Still Not Working

### Quick Test - Check if validation is running

Open browser console and run:

```javascript
frappe.call({
    method: 'frappe.client.get',
    args: {
        doctype: 'Asset Repair',
        name: 'YOUR-REPAIR-NAME-HERE'  // Replace with actual repair name
    },
    callback: function(r) {
        console.log('Current doc:', r.message);
    }
});
```

### Manual Validation Test

```javascript
// Get a submitted repair
frappe.call({
    method: 'frappe.client.get',
    args: {
        doctype: 'Asset Repair',
        name: 'YOUR-REPAIR-NAME'
    },
    callback: function(r) {
        let doc = r.message;
        doc.description = "TRYING TO HACK";

        // Try to save it
        frappe.call({
            method: 'frappe.client.save',
            args: {
                doc: doc
            },
            callback: function(r) {
                console.log('Should fail!', r);
            },
            error: function(r) {
                console.log('Good! Validation blocked it:', r);
            }
        });
    }
});
```

---

## Alternative: Use Permissions Instead

If the validation approach keeps failing, we can use Role Permissions:

### Option A: Workflow (Most Robust)

Create a Workflow for Asset Repair:
1. States: Draft → Pending Approval → Approved/Rejected
2. Only "Draft" state allows editing
3. After submission, workflow prevents field changes

### Option B: Server Script (Simpler)

Instead of hooks, use Server Script:

1. Go to: **Desk → Server Script → New**
2. **Script Type**: DocType Event
3. **DocType**: Asset Repair
4. **Event**: Before Save
5. **Script**:
```python
if doc.docstatus == 1:  # Submitted
    old_doc = frappe.get_doc("Asset Repair", doc.name)

    protected = ['description', 'failure_date', 'repair_status', 'asset']

    for field in protected:
        if doc.get(field) != old_doc.get(field):
            frappe.throw(f"Cannot modify {field} after submission")

    # Auto-fill approval
    if doc.approval_status != old_doc.approval_status:
        if doc.approval_status in ['Approved', 'Rejected']:
            doc.approved_by = frappe.session.user
            doc.approval_time = frappe.utils.now()
```

6. **Enable**: Yes
7. **Save**

This runs without needing server restart!

---

## Files Deployed

✅ `~/frappe-bench/apps/tub_suite/tub_suite/api/asset.py` - Validation logic
✅ `~/frappe-bench/apps/tub_suite/tub_suite/hooks.py` - Doc events hook

## What Each Component Does

1. **hooks.py**: Tells Frappe to run validation on Asset Repair saves
2. **validate_asset_repair_permissions()**: Server-side validation that blocks edits
3. **Client Script**: Makes fields read-only in UI (cosmetic)
4. **Custom Fields**: Adds approval_status, approved_by, approval_time

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Still editable | Restart server (Step 3) |
| No approval fields | Run setup_approval_fields() |
| Validation not running | Check hooks.py deployed correctly |
| Server won't restart | Kill process: `killall -9 node python` |

---

## Next Steps After Setup

Once working, you should see:

**Before submission:**
- All fields editable ✅

**After submission:**
- Description = ❌ Locked
- Failure Date = ❌ Locked
- Repair Status = ❌ Locked
- Approval Status = ✅ Unlocked
- Approved By = ❌ Auto-filled (read-only)
- Approval Time = ❌ Auto-filled (read-only)

The approval timestamp comes from server and cannot be backdated!
