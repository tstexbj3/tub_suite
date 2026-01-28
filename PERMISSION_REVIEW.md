# 🔐 Maintenance Role Permissions Review

**IMPORTANT:** Please review these permissions CAREFULLY before applying them to DEV.

---

## Permission Legend
- **R** = Read (view list and documents)
- **W** = Write (edit existing documents)
- **C** = Create (create new documents)
- **D** = Delete (delete documents)
- **S** = Submit (submit documents to workflow)
- **X** = Cancel (cancel submitted documents)

---

## 1. Maintenance User (Field Technicians, Reporters)

**Role Purpose:** Front-line maintenance workers who report issues and log maintenance work

| DocType | Permissions | Justification |
|---------|------------|---------------|
| Asset | R | View assets to report issues |
| Asset Repair | RWC | Create and edit repair requests they reported |
| Asset Maintenance | R | View PM schedules |
| Asset Maintenance Log | RWC | Log maintenance work performed |
| Asset Maintenance Task | RW | Update tasks assigned to them |
| Location | R | View locations for reporting |
| Asset Category | R | View categories for reporting |
| Item | R | View spare parts |

**✅ CORRECT** - Users can report issues and log work but cannot manage schedules

---

## 2. Supervisor (Portal Repair Verifier)

**Role Purpose:** Verifies Portal-reported repairs only (not PM)

| DocType | Permissions | Justification |
|---------|------------|---------------|
| Asset | R | View assets being repaired |
| Asset Repair | RWS | Edit repair details and SUBMIT (verify/approve) |
| Asset Maintenance | R | View PM schedules (read-only) |
| Asset Maintenance Log | R | View maintenance logs (read-only) |
| Asset Maintenance Task | R | View tasks (read-only) |
| Location | R | View locations |
| Asset Category | R | View categories |
| Item | R | View spare parts |

**❓ QUESTION:** Should Supervisor have SUBMIT permission on Asset Repair?
- **YES** - They need to approve workflow transitions (Supervisor Verify action)
- This matches the workflow logic in asset_repair_override.py

**✅ CORRECT**

---

## 3. Maintenance Supervisor (PM Repair Verifier + PM Manager)

**Role Purpose:** Verifies PM repairs AND manages PM schedules/tasks

| DocType | Permissions | Justification |
|---------|------------|---------------|
| Asset | R | View assets being maintained |
| Asset Repair | RWS | Edit PM repairs and SUBMIT (verify/approve) |
| Asset Maintenance | RWC | Manage PM schedules (create, edit) |
| Asset Maintenance Log | RWC | Create and edit maintenance logs |
| Asset Maintenance Task | RWC | Create and assign PM tasks |
| Location | R | View locations |
| Asset Category | R | View categories |
| Item | R | View spare parts |

**✅ CORRECT** - Has full PM management + repair verification powers

---

## 4. Maintenance Manager (GM Level)

**Role Purpose:** Top-level management, approves budgets, has full control

| DocType | Permissions | Justification |
|---------|------------|---------------|
| Asset | RWCD | Full asset management |
| Asset Repair | RWCDSX | Full repair control including cancel |
| Asset Maintenance | RWCD | Full PM schedule control |
| Asset Maintenance Log | RWCD | Full log control |
| Asset Maintenance Task | RWCD | Full task control |
| Location | RWC | Can create/edit locations |
| Asset Category | RWC | Can create/edit categories |
| Item | R | View spare parts (don't manage inventory) |

**✅ CORRECT** - Full control except inventory management

---

## 5. Engineering Supervisor

**Role Purpose:** Reviews engineering assessments in workflow

| DocType | Permissions | Justification |
|---------|------------|---------------|
| Asset | R | View assets being assessed |
| Asset Repair | RW | Edit engineering assessment fields |
| Asset Maintenance | R | View PM schedules |
| Asset Maintenance Log | R | View logs |
| Asset Maintenance Task | R | View tasks |
| Location | R | View locations |
| Asset Category | R | View categories |
| Item | R | View spare parts |

**❓ QUESTION:** Should Engineering Supervisor have SUBMIT permission?
- **NO** - Looking at workflow, Engineering Supervisor doesn't submit
- Engineering Team fills in data, then Engineering Supervisor reviews and transitions
- Workflow action "Supervisor Review Complete" moves it forward but doesn't require submit permission

**✅ CORRECT** - No submit needed

---

## 6. Engineering Team

**Role Purpose:** Performs engineering assessments and repairs

| DocType | Permissions | Justification |
|---------|------------|---------------|
| Asset | R | View assets being repaired |
| Asset Repair | RWC | Create repair records and edit assessment fields |
| Asset Maintenance | RW | Edit PM records (assist with repairs) |
| Asset Maintenance Log | RW | Edit maintenance logs |
| Asset Maintenance Task | R | View assigned tasks |
| Location | R | View locations |
| Asset Category | R | View categories |
| Item | R | View spare parts |

**❓ QUESTION:** Should Engineering Team have CREATE on Asset Repair?
- **YES** - They may need to create repair records for discovered issues
- Current production shows they have RWC, which makes sense

**✅ CORRECT**

---

## 🚨 CRITICAL REVIEW QUESTIONS

### Question 1: Asset Repair Submit Permission
**Who should have SUBMIT permission on Asset Repair?**

Current workflow requires these roles to submit:
- ✅ Supervisor (Line 30: submit=1) - For workflow transitions
- ✅ Maintenance Supervisor (Line 40: submit=1) - For workflow transitions
- ✅ Maintenance Manager (Line 50: submit=1) - For workflow transitions
- ❌ Maintenance User (Line 20: submit=0) - Cannot submit, only report
- ❌ Engineering Supervisor (Line 60: submit=0) - Reviews but doesn't submit
- ❌ Engineering Team (Line 70: submit=0) - Works but doesn't submit

**✅ THIS IS CORRECT** - Matches workflow logic

### Question 2: Missing DocTypes?
Are there other DocTypes we should add permissions for?
- ⏭️ **Serial No** - For tracking asset serial numbers?
- ⏭️ **Warehouse** - For spare parts location?
- ⏭️ **Stock Entry** - For spare parts usage?
- ⏭️ **Purchase Order** - For ordering spare parts?

**Decision:** Let's start with the 8 core DocTypes. Add more later if needed.

### Question 3: Report Permission?
All roles with READ should have REPORT permission (for reports/exports)
**✅ Script sets report=1 for all read permissions (Line 137)**

### Question 4: Export Permission?
All roles with READ should have EXPORT permission (for Excel exports)
**✅ Script sets export=1 for all read permissions (Line 138)**

---

## ✅ FINAL VERDICT

**The permissions are CORRECT and safe to apply.**

**Rationale:**
1. ✅ Maintenance User can report issues but not manage
2. ✅ Supervisor can verify Portal repairs (submit permission needed for workflow)
3. ✅ Maintenance Supervisor can verify PM repairs AND manage PM
4. ✅ Maintenance Manager has full control (GM level)
5. ✅ Engineering Supervisor can review assessments
6. ✅ Engineering Team can perform repairs and assessments
7. ✅ Submit permissions match workflow requirements
8. ✅ No dangerous permissions (delete/cancel) given to low-level roles

---

## 🎯 Next Steps

1. ✅ **APPROVED** - Run the permission script on DEV
2. Update hooks.py to export Custom DocPerm
3. Export custom_docperm.json fixture
4. Commit as v2.1.3
5. Deploy to production

---

**Reviewed by:** AI Assistant
**Date:** 2026-01-28
**Status:** APPROVED FOR DEV APPLICATION
