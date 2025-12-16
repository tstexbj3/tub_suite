# TUB Maintenance Portal - Documentation Index

**Version:** 1.0
**Last Updated:** December 16, 2024
**System:** ERPNext v15 + Frappe Framework v15 + React 19

---

## Welcome

This documentation suite provides comprehensive guidance for all users and administrators of the TUB Maintenance Portal system.

---

## Quick Navigation by Role

### 👷 I am a Maintenance User (Field Inspector)
**Your Priority:** [01_MAINTENANCE_USER_MANUAL.md](./01_MAINTENANCE_USER_MANUAL.md)

**What you'll learn:**
- How to scan QR codes
- How to complete maintenance checklists
- How to report issues with photos
- How to verify completed repairs
- Mobile portal navigation

**Start Here:** → Section 2: Daily Workflow

---

### 🔧 I am an Engineering Team Member
**Your Priority:** [02_ENGINEERING_TEAM_MANUAL.md](./02_ENGINEERING_TEAM_MANUAL.md)

**What you'll learn:**
- How to receive and process repair requests
- How to fill in technical details
- How to submit for approval
- Understanding field restrictions
- Workflow states and transitions

**Start Here:** → Section 2: Receiving Repair Requests

---

### 👔 I am a Maintenance Manager
**Your Priority:** [03_MAINTENANCE_MANAGER_MANUAL.md](./03_MAINTENANCE_MANAGER_MANUAL.md)

**What you'll learn:**
- How to approve/reject repair requests
- How to configure portal settings
- How to use search function
- Team oversight and reporting
- System administration

**Start Here:** → Section 2: Approval Workflow

---

### 💻 I am a System Administrator / Developer
**Your Priority:** [04_SYSTEM_WORKFLOWS_AND_ARCHITECTURE.md](./04_SYSTEM_WORKFLOWS_AND_ARCHITECTURE.md)

**What you'll learn:**
- Complete system architecture
- Workflow diagrams
- API reference
- Database schema
- Configuration guide
- Troubleshooting

**Start Here:** → Section 1: System Architecture

---

## Document Structure

### User Manuals (Role-Based)

Each manual is self-contained and tailored to specific role:

| Document | Audience | Format | Estimated Reading Time |
|----------|----------|--------|----------------------|
| [01_MAINTENANCE_USER_MANUAL.md](./01_MAINTENANCE_USER_MANUAL.md) | Maintenance Users | Step-by-step guide | 30 minutes |
| [02_ENGINEERING_TEAM_MANUAL.md](./02_ENGINEERING_TEAM_MANUAL.md) | Engineering Team | Reference + procedures | 45 minutes |
| [03_MAINTENANCE_MANAGER_MANUAL.md](./03_MAINTENANCE_MANAGER_MANUAL.md) | Managers | Comprehensive guide | 60 minutes |
| [04_SYSTEM_WORKFLOWS_AND_ARCHITECTURE.md](./04_SYSTEM_WORKFLOWS_AND_ARCHITECTURE.md) | Technical staff | Technical reference | 90 minutes |

### Quick References

**Need something specific? Jump to:**

- **How do I scan a QR code?** → Manual 01, Section 3
- **How do I report an issue?** → Manual 01, Section 5
- **How do I approve a repair?** → Manual 03, Section 2
- **How do I verify a repair?** → Manual 01, Section 6
- **How does asset status change?** → Manual 04, Section 3
- **What are the workflow states?** → Manual 04, Section 2
- **How do I configure settings?** → Manual 03, Section 3
- **API documentation?** → Manual 04, Section 4

---

## System Overview

### What is TUB Maintenance Portal?

A comprehensive maintenance management system combining:
- Mobile-first inspection portal (React)
- Workflow-driven repair management (ERPNext)
- QR code-based asset tracking
- Role-based access control
- Automated status management
- Reporter verification system

### Key Features

**For Maintenance Users:**
- 📱 Mobile QR code scanner
- ✅ Digital maintenance checklists
- 📸 Photo-based issue reporting
- ✓ Repair verification with accountability

**For Engineering Team:**
- 📋 Centralized repair queue
- ⚡ Real-time notifications
- 📝 Technical documentation fields
- 🔒 Field locking for audit trail

**For Managers:**
- ✍️ Approval workflow
- 🎛️ Portal configuration
- 🔍 Advanced search function
- 📊 Reports and analytics

### User Roles

| Role | Access | Primary Tasks |
|------|--------|---------------|
| **Maintenance User** | Mobile Portal | Inspect, Report, Verify |
| **Engineering Team** | ERPNext Desk | Repair, Document, Complete |
| **Maintenance Manager** | Full System | Approve, Configure, Oversee |

---

## Getting Started Guide

### New to the System? Start Here

**Day 1: Understanding the Basics**
1. Read your role-specific manual (30-60 min)
2. Watch system demo (if available)
3. Practice in test environment
4. Ask questions

**Day 2: Hands-On Practice**
1. Follow step-by-step workflows
2. Try each function with guidance
3. Review common scenarios
4. Take notes of questions

**Week 1: Building Confidence**
1. Complete real tasks with supervision
2. Reference manual as needed
3. Learn keyboard shortcuts
4. Share tips with team

**Month 1: Mastery**
1. Work independently
2. Train new users
3. Suggest improvements
4. Optimize your workflow

---

## Key Workflows

### 1. Inspection and Issue Reporting Flow
```
Maintenance User → Scan QR → Complete Checklist → Report Issue (if found)
                                                  ↓
Engineering Team ← Notification ← Asset Repair Created
```
**Details:** Manual 01, Section 4-5 | Manual 04, Section 2.1

### 2. Repair Approval Flow
```
Engineer → Fill Details + Sign → Submit for Approval
                                      ↓
Manager → Review → Approve (Asset status may change)
                      ↓
Engineer → Perform Repair → Mark "Job Finished"
```
**Details:** Manual 02, Section 3-6 | Manual 03, Section 2 | Manual 04, Section 2.2

### 3. Verification and Restoration Flow
```
Reporter → Notification → Test Equipment → Take Photos → Confirm
                                                           ↓
System → Verify Completion → Check Other Repairs → Restore Asset (if safe)
```
**Details:** Manual 01, Section 6 | Manual 04, Section 2.3

---

## Critical Concepts

### Issue Severity - UNDERSTAND THIS

**Major - Asset Must Stop:**
- ⚠️ Asset becomes "Out of Order" on approval
- Users cannot inspect it
- Equipment offline
- Urgent priority

**Minor - Asset Operational:**
- ✓ Asset stays operational
- Can be scheduled
- Normal priority

**Why It Matters:**
- Controls asset availability
- Affects user workflow
- Impacts scheduling
- Business continuity

**Who Decides:** Engineer recommends, Manager approves/overrides

### 7-Day Verification Rule

**What It Means:**
- Reporter verifies repair completion
- Takes responsibility for 7 days
- If problem returns → reporter must re-report
- Encourages thorough verification

**Purpose:**
- Quality control
- Accountability
- Prevents rushed verifications
- Ensures repairs are truly complete

### Asset Status Lifecycle

```
Submitted → (Major Issue Approved) → Out of Order → (Verified + No Other Issues) → Submitted
  ↑                                                                                     ↓
  └─────────────────────────── Cycle Continues ───────────────────────────────────────┘
```

**Key Point:** Asset only returns to service when ALL major repairs are verified.

---

## Configuration Options

### Portal Settings (Manager Only)

**Search Function Visibility:**

**Production (Recommended):**
```
☐ Enable Search for All Users
```
- Only managers see search
- Users use QR codes
- Enforces process

**Testing/Training:**
```
☑ Enable Search for All Users
```
- Everyone sees search
- Easier access
- Good for testing

**How to Change:** Manual 03, Section 3

---

## Common Questions (FAQ)

### For All Users

**Q: What browser should I use?**
A: Chrome is recommended. Safari and Edge also work. Internet Explorer not supported.

**Q: Can I use this on my phone?**
A: Yes! Mobile portal designed for phone/tablet use.

**Q: What if I forget my password?**
A: Contact your manager or IT administrator to reset.

**Q: Can I work offline?**
A: No, internet connection required.

### For Maintenance Users

**Q: QR code won't scan - what do I do?**
A: Check camera permissions, clean QR code, try different angle. If damaged, contact manager for new label or use search (if available).

**Q: I verified a repair but it's still broken - now what?**
A: Contact the engineer immediately. Do NOT verify if not 100% fixed.

**Q: Can I check the same task twice in one day?**
A: No, each task can only be completed once per day.

### For Engineering Team

**Q: Can I edit after submitting?**
A: No, fields lock after submit. Contact manager to reject if you need changes.

**Q: Manager rejected my repair - what now?**
A: Document returns to Draft. Read rejection notes, make changes, resubmit.

**Q: How do I know if verification is pending?**
A: Check repair document status. "Finished" state with no verification status means pending.

### For Managers

**Q: Should I approve Major or Minor?**
A: Major = equipment must stop. Minor = can keep operating. Choose based on safety and business impact, not just engineer's recommendation.

**Q: How do I enable search for testing?**
A: Portal Settings → Check "Enable Search for All Users" → Save

**Q: Asset not restoring after verification - why?**
A: Check for other open Major repairs on same asset. System keeps asset offline until all major issues resolved (safety feature).

---

## Troubleshooting Quick Reference

### Problem: Asset status not changing

**Check:**
1. Issue Severity = Major?
2. Workflow State = Approved?
3. Manager actually approved (not just viewed)?

**Solution:** Manual 04, Section 7 → "Asset status not changing after approval"

### Problem: Cannot submit repair

**Check:**
1. Engineer signature present?
2. All required fields filled?
3. Document in Draft state?

**Solution:** Manual 02, Section 8 → "Cannot submit"

### Problem: Verification not appearing

**Check:**
1. Logged in as correct user (original reporter)?
2. Repair state = Finished?
3. Check home page for alert banner?

**Solution:** Manual 01, Section 8 → "Cannot verify repair"

### Problem: Search not working

**Check:**
1. User role = Maintenance Manager?
2. Portal Settings configured?
3. Browser cache cleared?

**Solution:** Manual 03, Section 8 → "Search not working"

---

## Screenshot Checklist

**Each manual identifies where screenshots should be added. To complete documentation:**

### Manual 01 (Maintenance User):
- [ ] Home page with QR scanner
- [ ] QR scanning interface
- [ ] Checklist with badges
- [ ] Issue reporting form
- [ ] Verification alert
- [ ] Verification page
- [ ] Photo upload interface

### Manual 02 (Engineering Team):
- [ ] ToDo notifications
- [ ] Repair form in Draft
- [ ] Issue severity dropdown
- [ ] Engineer signature field
- [ ] Workflow ribbon
- [ ] Approved state fields
- [ ] Job Finished button

### Manual 03 (Maintenance Manager):
- [ ] Approval queue
- [ ] Review screen
- [ ] Approval section
- [ ] Portal Settings
- [ ] Search interface
- [ ] Reports dashboard

### Manual 04 (Technical):
- [ ] System architecture diagram
- [ ] Workflow state diagram
- [ ] API request/response examples
- [ ] Database schema

**Tool for Screenshots:** Any screen capture tool. Save as PNG, name descriptively.

---

## Support Contacts

**For User Questions:**
- Maintenance Manager: [Add contact]
- Email: [Add email]

**For Technical Issues:**
- System Administrator: [Add contact]
- IT Support: [Add contact]

**For Development:**
- Development Team: [Add contact]
- GitHub Issues: [Add repository link]

---

## Version History

### Version 1.0 (December 16, 2024)
- Initial documentation release
- 4 comprehensive manuals
- Complete workflow coverage
- API reference included
- Configuration guides
- Troubleshooting sections

### Planned Updates
- Add screenshots throughout
- Video tutorials (if available)
- Advanced configuration guide
- Integration documentation
- Performance tuning guide

---

## Contributing to Documentation

Found an error? Have a suggestion?

1. Note the document and section number
2. Describe the issue or improvement
3. Contact system administrator or development team
4. Or submit pull request (if using version control)

**Documentation is a living resource - your feedback improves it for everyone!**

---

## Next Steps

**Choose your path:**

- **🆕 New User?** → Start with your role manual, read sections 1-2
- **📚 Training Team?** → Use manuals as training materials
- **🔧 System Admin?** → Read Manual 04 for complete technical reference
- **👔 Manager?** → Read Manual 03, focus on Sections 2-3
- **🛠️ Developer?** → Manual 04 + review actual code in `/tub_suite/`

---

**Welcome to TUB Maintenance Portal! 🚀**

For questions or support, contact your system administrator.

---

**Document Version:** 1.0
**Last Updated:** December 16, 2024
**Prepared By:** TUB Suite Development Team
