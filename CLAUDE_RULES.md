# RULES FOR CLAUDE AI - READ THIS FIRST

#Read CLAUDE_RULES.md and WORKFLOW_AND_FIELDS.md first.

**Priority Level:** CRITICAL - READ BEFORE ANY ACTION

---

## 🚨 RULE #1: DOCUMENTATION

### ONLY ONE SOURCE OF TRUTH:
- **WORKFLOW_AND_FIELDS.md** - Everything about Asset Repair workflow and fields

### NEVER DO:
- ❌ Create new .md documentation files
- ❌ Create DESIGN_*.md, ANALYSIS_*.md, GUIDE_*.md files
- ❌ Write documentation in comments and forget to update main file

### ALWAYS DO:
- ✅ Read WORKFLOW_AND_FIELDS.md FIRST before making ANY change
- ✅ Update WORKFLOW_AND_FIELDS.md when making changes
- ✅ If confused, read WORKFLOW_AND_FIELDS.md again, don't guess

---

## 🚨 RULE #2: BEFORE MAKING ANY CHANGE

### REQUIRED STEPS (IN ORDER):
1. **Read** WORKFLOW_AND_FIELDS.md to understand current state
2. **Check** database/code to verify actual current state
3. **Compare** what documentation says vs what actually exists
4. **Explain** to user what you found and what needs to change
5. **Wait** for user approval (don't assume)
6. **Make** the change
7. **Update** WORKFLOW_AND_FIELDS.md if needed
8. **Clear** cache
9. **Confirm** to user it's done

### NEVER:
- ❌ Make changes without checking current state first
- ❌ Assume documentation is up to date
- ❌ Guess field names or state names
- ❌ Create new fields without checking if they exist

---

## 🚨 RULE #3: WORKFLOW FACTS (MEMORIZE THIS)

### Current Workflow:
- **Type:** Supervisor-Only (NO OPERATORS)
- **States:** 9 states (Draft → Pending GM Approval Section 1 → Pending Engineering Assessment → Pending Engineering Supervisor Review → Pending GM Final Approval → Approved for Repair → Pending Supervisor Verification → Finished → Rejected)

### Critical State Names:
- ✅ "Pending Supervisor Verification" (CORRECT)
- ❌ "Pending Reporter Supervisor Verification" (OLD - DON'T USE)
- ❌ "Pending Reporter Confirmation" (DELETED - DOESN'T EXIST)

### Section 3B: Hygiene & Safety
- **Fieldname:** `section_3b_break`
- **Shows in:** "Pending Supervisor Verification" state ONLY
- **Filled by:** Supervisor (who originally reported the issue)
- **Contains:** Hygiene checklist, cleanliness checks, supervisor signature

### Engineering Sections:
- **Section 1:** action_type, cost_type, todo_items, spare_parts (Custom Fields)
- **Section 2:** expected_duration_days, dates, signatures (Standard ERPNext Fields - DON'T DELETE)
- **Section 3:** completion_handover_date (auto-fill), repair_result_status (editable)

### Field Behavior:
- `completion_handover_date`: AUTO-FILLED when clicking "Finish Repair" (Approved for Repair → Pending Supervisor Verification)
- `repair_result_status`: EDITABLE in "Approved for Repair" state (engineer fills this)
- `repair_subject`: EDITABLE in Draft state only, locked after
- `description`: EDITABLE in Draft state only, locked after

---

## 🚨 RULE #4: WHEN USER REPORTS "FIELD NOT SHOWING"

### DEBUG CHECKLIST (DO IN ORDER):
1. **Check field exists:**
   ```python
   frappe.db.exists("Custom Field", {"dt": "Asset Repair", "fieldname": "FIELDNAME"})
   ```

2. **Check depends_on condition:**
   ```python
   field = frappe.get_doc("Custom Field", {"dt": "Asset Repair", "fieldname": "FIELDNAME"})
   print(field.depends_on)
   ```

3. **Check for typos in state name:**
   - Wrong: "Pending Reporter Supervisor Verification"
   - Correct: "Pending Supervisor Verification"

4. **Check field not hidden:**
   ```python
   print(field.hidden)  # Should be 0
   ```

5. **Check if field has value:**
   ```python
   doc = frappe.get_doc("Asset Repair", "ACC-ASR-XXXX")
   print(doc.get("FIELDNAME"))
   ```

6. **Clear cache:**
   ```bash
   bench --site tub clear-cache
   ```

---

## 🚨 RULE #5: WHEN USER REPORTS "FIELD NOT EDITABLE"

### CHECK THESE (IN ORDER):
1. **Custom Field read_only property:**
   ```python
   field = frappe.get_doc("Custom Field", {"dt": "Asset Repair", "fieldname": "FIELDNAME"})
   print(field.read_only)
   ```

2. **Property Setter overriding read_only:**
   ```python
   frappe.db.exists("Property Setter", {"doc_type": "Asset Repair", "field_name": "FIELDNAME", "property": "read_only"})
   ```

3. **Client Script forcing read_only:**
   - Check "Asset Repair - Field Locking UI" client script
   - Look for `frm.set_df_property('FIELDNAME', 'read_only', 1)`

4. **Server-side validation:**
   - Check asset_repair_override.py validate_asset_repair() function

---

## 🚨 RULE #6: WHEN FIXING FIELD VISIBILITY

### CORRECT PATTERN:
```python
# For supervisor-only workflow
depends_on = 'eval:doc.workflow_state=="Pending Supervisor Verification"'
```

### WRONG PATTERNS (DON'T USE):
```python
# ❌ Old state name
depends_on = 'eval:doc.workflow_state=="Pending Reporter Supervisor Verification"'

# ❌ Checking non-existent field
depends_on = 'eval:doc.reporter_confirmed==1'

# ❌ Old operator-based condition
depends_on = 'eval:doc.workflow_state=="Pending Reporter Confirmation"'
```

---

## 🚨 RULE #7: NEVER DO THESE THINGS

1. ❌ Create new documentation files (UPDATE WORKFLOW_AND_FIELDS.md instead - UNLESS user specifically requests it)
2. ❌ Delete Section 2 (it contains standard ERPNext fields)
3. ❌ Make completion_handover_date editable (it's auto-filled)
4. ❌ Assume field names without checking database first
5. ❌ Use old state name "Pending Reporter Supervisor Verification"
6. ❌ Check for reporter_confirmed field (it doesn't exist anymore)
7. ❌ Give operators access (workflow is supervisor-only)
8. ❌ Forget to clear cache after making changes
9. ❌ Make changes without reading WORKFLOW_AND_FIELDS.md first
10. ❌ Create fixes without understanding the problem first

---

## 🚨 RULE #8: AFTER CONTEXT COMPACTION

**When you lose memory and session continues:**

1. **IMMEDIATELY** read these files:
   - CLAUDE_RULES.md (this file)
   - WORKFLOW_AND_FIELDS.md (workflow and field structure)

2. **ASK USER** what they were working on (don't guess from context)

3. **CHECK DATABASE** to see current state, don't rely on old memory

4. **DON'T CREATE** new documentation - update existing

---

## 🚨 RULE #9: WHEN USER IS FRUSTRATED

**User will be frustrated when:**
- You forget the workflow structure
- You ask the same questions repeatedly
- You create new docs instead of updating existing
- You guess instead of checking
- You use old state names
- You make assumptions

**When this happens:**
1. **STOP** what you're doing
2. **READ** WORKFLOW_AND_FIELDS.md completely
3. **APOLOGIZE** briefly (1 sentence max)
4. **CHECK** database for actual current state
5. **FIX** the issue correctly based on facts
6. **DON'T** make excuses or long explanations

---

## 🚨 RULE #10: STANDARD WORKFLOW FOR ANY TASK

```
1. User requests change
2. Read WORKFLOW_AND_FIELDS.md
3. Check database/code current state
4. Explain what you found
5. Propose solution
6. Get approval
7. Make change
8. Update WORKFLOW_AND_FIELDS.md
9. Clear cache
10. Confirm done
```

**NO SHORTCUTS. FOLLOW THIS EVERY TIME.**

---

## 📝 Quick Reference

### Files to Read:
1. **CLAUDE_RULES.md** (this file) - How to work
2. **WORKFLOW_AND_FIELDS.md** - What the workflow is

### Files to Keep:
- ✅ README.md (project overview)
- ✅ CHANGELOG.md (version history)
- ✅ DEPLOYMENT_GUIDE_v2.1.0.md (deployment)
- ✅ FIXTURE_MANAGEMENT.md (technical)
- ✅ MIGRATION_GUIDE.md (upgrades)

### Files to NEVER Create:
- ❌ DESIGN_*.md
- ❌ ANALYSIS_*.md
- ❌ IMPLEMENTATION_*.md
- ❌ GUIDE_*.md
- ❌ PLAN_*.md
- ❌ Any new documentation

---

## 🎯 Success Criteria

**You're doing it right when:**
- ✅ You read WORKFLOW_AND_FIELDS.md before making changes
- ✅ You check database before answering questions
- ✅ You use correct state name "Pending Supervisor Verification"
- ✅ You update WORKFLOW_AND_FIELDS.md when making changes
- ✅ You don't create new documentation files
- ✅ User doesn't have to repeat themselves
- ✅ You fix issues correctly on first try

**You're doing it wrong when:**
- ❌ User says "I ALREADY TOLD YOU THIS"
- ❌ User says "READ THE DOCUMENTATION"
- ❌ User says "YOU'RE CREATING NEW FILES AGAIN"
- ❌ User is frustrated or angry
- ❌ You make the same mistake twice

---

**REMEMBER: User has to deal with context loss frustration. Your job is to minimize this by:**
1. Reading these rules EVERY session
2. Checking facts before acting
3. Not making assumptions
4. Following the standard workflow above

**IF YOU BREAK THESE RULES, USER WILL BE VERY ANGRY.**
