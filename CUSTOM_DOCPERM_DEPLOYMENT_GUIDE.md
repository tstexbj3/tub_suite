# 🔐 Custom DocPerm Deployment Guide

**Critical Information for Deploying Role Permissions**

---

## ⚠️ CRITICAL WARNING

**Custom DocPerm fixtures CANNOT be imported using `bench migrate`!**

Unlike other fixtures, Custom DocPerm records are **child table documents** without a unique "name" field. Attempting to import them via standard methods will **FAIL** with:

```
KeyError: 'name'
```

**You MUST use the console import method described below.**

---

## 📋 What is Custom DocPerm?

**Custom DocPerm** stores role-based permissions for DocTypes:
- Links a Role to a DocType (e.g., "Supervisor" → "Asset Repair")
- Defines what the role can do: Read, Write, Create, Delete, Submit, etc.
- Stored as child table rows (no unique name field)

**Roles vs Permissions:**
- **Role** = Just a name/label (e.g., "Supervisor")
- **Custom DocPerm** = Actual permissions (e.g., "Supervisor can read/write Asset Repair")
- Both must exist for roles to work!

---

## 🔧 How to Change Permissions (DEV)

### Method 1: Role Permission Manager (RECOMMENDED)

1. Go to: **Settings → Role Permission Manager**
2. **Document Type:** Select the DocType (e.g., "Asset Repair")
3. **Role:** Select the role (e.g., "Supervisor")
4. Check/uncheck permissions:
   - ☑ Read - View list and documents
   - ☑ Write - Edit existing documents
   - ☑ Create - Create new documents
   - ☑ Delete - Delete documents
   - ☑ Submit - Submit to workflow
   - ☑ Cancel - Cancel submitted documents
5. Click **"Update"** - Saves immediately ✅

### Method 2: Customize Form

1. Go to: **Customization → Customize Form**
2. **Enter Form Type:** e.g., "Asset Repair"
3. Scroll to: **"Permission Rules"** section
4. Click **"Add Row"** to add new permission
5. Fill in: Role, Level, and check permission boxes
6. Click **"Update"** at bottom

---

## 📤 Export Permissions from DEV

After making permission changes in the Desk UI:

```bash
cd /home/user/frappe-bench/apps/tub_suite

# Run export script
bench --site tub execute tub_suite.EXPORT_CUSTOM_DOCPERM.export_custom_docperm
```

**What this does:**
- Exports all Custom DocPerm for maintenance roles
- Writes to `tub_suite/fixtures/custom_docperm.json`
- Includes: Maintenance User, Supervisor, Maintenance Supervisor, Maintenance Manager, Engineering Supervisor, Engineering Team

**Expected output:**
```
Exported 56 Custom DocPerm records to:
   /home/user/frappe-bench/apps/tub_suite/tub_suite/fixtures/custom_docperm.json
   File size: 18,751 bytes
```

---

## 💾 Commit Changes

```bash
cd /home/user/frappe-bench/apps/tub_suite

# Check what changed
git diff tub_suite/fixtures/custom_docperm.json

# Stage and commit
git add tub_suite/fixtures/custom_docperm.json
git commit -m "fix: Update permissions for [role] on [doctype]

- Added [permission] for [role]
- Removed [permission] from [role]
- etc.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Tag new version
git tag v2.1.x

# Push to GitHub
git push origin v2.1.x
```

---

## 🚀 Deploy to Production

### Step 1: Checkout New Version

```bash
cd ~/frappe-bench/apps/tub_suite
git fetch --all --tags
git checkout v2.1.x
```

### Step 2: Run Migration (Imports Other Fixtures)

```bash
cd ~/frappe-bench
bench --site tub.x-desk.tech migrate
```

**Note:** This will import roles, workflow, custom fields, etc. but will **FAIL** when trying to import Custom DocPerm. That's expected!

### Step 3: Extract Custom DocPerm from Git

```bash
cd ~/frappe-bench/apps/tub_suite

# Extract directly from git (bypasses filesystem)
git show v2.1.x:tub_suite/fixtures/custom_docperm.json > /tmp/custom_docperm_v2.1.x.json

# Verify file exists
wc -l /tmp/custom_docperm_v2.1.x.json
```

### Step 4: Import via Console (CRITICAL STEP)

```bash
cd ~/frappe-bench
bench --site tub.x-desk.tech console
```

**Paste this code in the console:**

```python
import json

# Load the fixture file
with open('/tmp/custom_docperm_v2.1.x.json', 'r') as f:
    perms = json.load(f)

print(f"Importing {len(perms)} permissions from fixture...")
added = 0
updated = 0
skipped = 0

for perm_data in perms:
    parent = perm_data.get('parent')
    role = perm_data.get('role')
    permlevel = perm_data.get('permlevel', 0)

    # Check if exists
    existing = frappe.db.get_value("Custom DocPerm", {
        "parent": parent,
        "role": role,
        "permlevel": permlevel
    }, "name")

    if existing:
        # Check if needs update
        needs_update = False
        for field in ["read", "write", "create", "delete", "submit", "cancel"]:
            current_val = frappe.db.get_value("Custom DocPerm", existing, field)
            new_val = perm_data.get(field, 0)
            if current_val != new_val:
                needs_update = True
                break

        if needs_update:
            # Update existing
            doc = frappe.get_doc("Custom DocPerm", existing)
            for field, value in perm_data.items():
                if field not in ["doctype", "parent", "parenttype", "parentfield"]:
                    setattr(doc, field, value)
            doc.save(ignore_permissions=True)
            updated += 1
            print(f"  🔄 {parent:<30} {role:<25} (updated)")
        else:
            skipped += 1
    else:
        # Create new
        try:
            doc = frappe.get_doc({"doctype": "Custom DocPerm", **perm_data})
            doc.insert(ignore_permissions=True)
            added += 1
            print(f"  ✅ {parent:<30} {role:<25} (added)")
        except Exception as e:
            print(f"  ❌ {parent:<30} {role:<25} ERROR: {e}")

# Commit changes
frappe.db.commit()

print(f"\n{'='*80}")
print("SUMMARY")
print(f"{'='*80}")
print(f"  ✅ Added: {added}")
print(f"  🔄 Updated: {updated}")
print(f"  ⏭️  Skipped: {skipped} (already correct)")
print(f"  📊 Total: {added + updated + skipped}")

# Clear cache
frappe.clear_cache()
print("\n✅ Cache cleared")
print("✅ IMPORT COMPLETE!")
```

**Expected output:**
```
Importing 56 permissions from fixture...
  ✅ Asset                          Supervisor                (added)
  ✅ Asset Repair                   Supervisor                (added)
  ...
✅ Added: 39
🔄 Updated: 0
⏭️  Skipped: 17 (already correct)
📊 Total: 56
✅ Cache cleared
✅ IMPORT COMPLETE!
```

### Step 5: Clear Cache and Restart

```bash
cd ~/frappe-bench

# Clear cache
bench --site tub.x-desk.tech clear-cache

# Restart services
sudo supervisorctl restart all
```

---

## ✅ Verify Deployment

### Check All Roles Have Permissions

```bash
bench --site tub.x-desk.tech console
```

```python
roles = ["Maintenance User", "Supervisor", "Maintenance Supervisor",
         "Maintenance Manager", "Engineering Supervisor", "Engineering Team"]

for role in roles:
    perms = frappe.get_all("Custom DocPerm",
        filters={"role": role},
        fields=["parent"],
        order_by="parent")

    print(f"\n{role} ({len(perms)} DocTypes):")
    for p in perms:
        print(f"  - {p.parent}")
```

**Expected output:**
```
Maintenance User (10 DocTypes):
  - Asset
  - Asset Repair
  - Asset Maintenance
  - Asset Maintenance Log
  ...

Supervisor (9 DocTypes):
  - Asset
  - Asset Repair
  ...
```

### Test User Access

1. Log in as a user with "Supervisor" role
2. Try to access: **Assets → Asset**
3. Should see the Asset list ✅
4. Try to open an Asset document
5. Should be able to view it ✅

---

## 🐛 Troubleshooting

### Error: "KeyError: 'name'" during migrate

**Cause:** Trying to import Custom DocPerm via `bench migrate`

**Solution:** This is expected! Skip the migrate error and manually import via console (Step 4 above)

### Permissions not working after import

**Fix:**
```bash
# Clear cache
bench --site <site> clear-cache

# Restart services
sudo supervisorctl restart all

# Ask users to log out and log back in (permissions are cached per session)
```

### Permissions still missing for a role

**Check:**
```python
# In console
perms = frappe.get_all("Custom DocPerm",
    filters={"role": "Supervisor"},
    fields=["parent", "read", "write", "create"])

print("Supervisor permissions:")
for p in perms:
    print(f"  {p.parent}: R={p.read} W={p.write} C={p.create}")
```

If missing, re-run the import script from Step 4.

---

## 📚 Reference: Permission Types

| Permission | Description |
|-----------|-------------|
| **Read** | View documents in list and form view |
| **Write** | Edit existing documents |
| **Create** | Create new documents |
| **Delete** | Delete documents |
| **Submit** | Submit documents (for workflow/submittable docs) |
| **Cancel** | Cancel submitted documents |
| **Amend** | Amend cancelled documents |
| **Print** | Print documents to PDF |
| **Email** | Email documents |
| **Report** | Access reports for this DocType |
| **Import** | Import data via Data Import tool |
| **Export** | Export to Excel/CSV |
| **Share** | Share documents with other users |

---

## 📋 Maintenance Role Permission Matrix

| Role | Asset | Asset Repair | Asset Maintenance | Logs | Tasks |
|------|-------|--------------|-------------------|------|-------|
| **Maintenance User** | R | RWC | R | RWC | RW |
| **Supervisor** | R | RWS | R | R | R |
| **Maintenance Supervisor** | R | RWS | RWC | RWC | RWC |
| **Maintenance Manager** | RWCD | RWCDSX | RWCD | RWCD | RWCD |
| **Engineering Supervisor** | R | RW | R | R | R |
| **Engineering Team** | R | RWC | RW | RW | R |

**Legend:** R=Read, W=Write, C=Create, D=Delete, S=Submit, X=Cancel

---

## 🔄 Quick Reference

### Change permissions:
```
Settings → Role Permission Manager → Select DocType & Role → Update
```

### Export from DEV:
```bash
bench --site tub execute tub_suite.EXPORT_CUSTOM_DOCPERM.export_custom_docperm
```

### Import to Production:
```bash
# Extract from git
git show v2.1.x:tub_suite/fixtures/custom_docperm.json > /tmp/custom_docperm.json

# Import via console (see Step 4 above for full script)
bench --site <site> console
# (paste import script)
```

---

**Document Created:** 2026-01-28
**Last Updated:** 2026-01-28
**Version:** v2.1.3
**Author:** TUB Suite Development Team
