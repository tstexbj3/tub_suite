# Section 5 Visibility Control - CRITICAL DOCUMENTATION

**IMPORTANT**: Read this before touching Section 5 visibility!

---

## THE PROBLEM WE KEPT HAVING

Section 5 kept showing in ALL workflow states when it should only show in specific states.

---

## HOW SECTION 5 VISIBILITY ACTUALLY WORKS

**Section 5 (`fm_en_04_section_5`) has NO `depends_on` rule itself.**

Instead, visibility is controlled by **THE FIELDS INSIDE IT**:

### On DEV (CORRECT Behavior):

- **Draft state**: Section 5 doesn't show at all
- **Pending Supervisor Verification**: Shows ONLY signature box
- **Finished**: Shows Section 5 heading + signature + verification date

### Fields Inside Section 5:

1. **`supervisor_signature`** (Signature field)
   - Shows in: "Pending Supervisor Verification" + "Finished"
   - This is what makes Section 5 appear in those states

2. **`supervisor_verification_date`** (Datetime field)
   - Shows in: "Finished" only (after signature is filled)
   - Auto-filled when signature is created

3. **`supervisor_verified_by`** (Link to User)
   - Auto-filled when supervisor signs

4. **`confirmation_date`** (Datetime)
   - Custom field, exact visibility TBD

### Fields We DELETED (not needed):

- **`final_remarks`** - Text field that was not being used

---

## WHY THIS WAS CONFUSING

We kept looking for:
1. ❌ `depends_on` rule on Section 5 itself (it's EMPTY)
2. ❌ Client Script controlling Section 5 (doesn't exist)
3. ❌ Server Script controlling Section 5 (doesn't exist)
4. ❌ Override class controlling Section 5 (doesn't exist)

**The actual mechanism**: When ALL fields inside a section have `depends_on` rules that evaluate to false, the section appears empty/hidden. When at least ONE field shows, the section appears.

---

## THE CORRECT CONFIGURATION

### Section 5 Break Field:
```
Name: Asset Repair-fm_en_04_section_5
Label: Section 5: Final Remarks (หมายเหตุเพิ่มเติม)
Fieldtype: Section Break
depends_on: (EMPTY - this is correct!)
hidden: 0
```

### supervisor_signature Field:
```
Name: Asset Repair-supervisor_signature
Label: Supervisor Signature (ลายเซ็น)
Fieldtype: Signature
depends_on: eval:["Pending Supervisor Verification", "Finished"].includes(doc.workflow_state)
```

### supervisor_verification_date Field:
```
Name: Asset Repair-supervisor_verification_date
Label: Verification Date (วันที่ตรวจรับ)
Fieldtype: Datetime
depends_on: eval:doc.workflow_state=="Finished"
(OR it might be: eval:doc.supervisor_signature)
```

---

## HOW TO CHECK IF IT'S WORKING

1. **On DEV**, open an Asset Repair document
2. Check each workflow state:
   - **Draft**: Section 5 should NOT appear
   - **Pending Supervisor Verification**: Section 5 should show with ONLY signature field
   - **Finished**: Section 5 should show signature + verification date

3. **On PROD**, do the same test after deployment

---

## DEPLOYMENT PROCEDURE

When deploying Section 5 changes:

1. **DO NOT** set `depends_on` on the Section 5 field itself
2. **DO** ensure the fields INSIDE Section 5 have correct `depends_on` rules
3. **TEST** on DEV first in all workflow states
4. **EXPORT** the correct Custom Field configuration from DEV
5. **USE MEGA-SYNC** to apply to PROD (don't edit manually)

---

## MEGA-SYNC COMMANDS

### On DEV - Generate patch:
```bash
cd ~/frappe-bench
bench --site tub execute tub_suite.tub_suite.patches.generate_prod_sync.generate_python_patch
```

### Copy to app:
```bash
cp /tmp/mega_sync_patch_*.py ~/frappe-bench/apps/tub_suite/tub_suite/patches/v2_1/mega_sync_all_config.py
```

### On PROD - Apply patch:
```bash
# Fix JSON syntax (null → None, true → True, false → False)
cd ~/frappe-bench/apps/tub_suite
sed -i 's/: null/: None/g' tub_suite/patches/v2_1/mega_sync_all_config.py
sed -i 's/: true/: True/g' tub_suite/patches/v2_1/mega_sync_all_config.py
sed -i 's/: false/: False/g' tub_suite/patches/v2_1/mega_sync_all_config.py

# Run the patch
cd ~/frappe-bench
bench --site tub.x-desk.tech execute tub_suite.patches.v2_1.mega_sync_all_config.execute

# Clear cache
bench --site tub.x-desk.tech clear-cache
```

---

## NEVER FORGET

- Section visibility is controlled by **individual field visibility**, NOT the section field itself
- DEV is the source of truth - always check DEV first
- Use mega-sync to deploy, don't manually edit Custom Fields on PROD
- Test in ALL workflow states before saying it's fixed

---

**Last Updated**: 2026-01-31
**Working Version**: DEV (site: tub)
**Status**: Section 5 works correctly on DEV, needs to be synced to PROD
