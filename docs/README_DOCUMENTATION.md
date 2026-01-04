# 📚 Documentation Index
**tub_suite - Maintenance Management System**
**Version:** v2.1.0
**Last Updated:** 2025-12-18

---

## Quick Access by Role

### 👤 I am a...

#### 📱 **Maintenance Inspector / User**
**Your manual:** [USER_MANUAL_INSPECTOR.md](USER_MANUAL_INSPECTOR.md)

**What you do:**
- Use mobile portal to perform inspections
- Scan QR codes on assets
- Take photos during maintenance
- Report issues when found
- Verify completed repairs

**Platform:** Mobile web browser only (`/maintenance` portal)

---

#### 🔧 **Engineering Team Member**
**Your manual:** [USER_MANUAL_ENGINEER.md](USER_MANUAL_ENGINEER.md)

**What you do:**
- Receive repair notifications
- Review issue reports from inspectors
- Perform actual repairs
- Document work with photos and notes
- Submit work for manager approval

**Platform:** ERPNext desktop (web browser)

---

#### 👔 **Maintenance Manager / Quality Manager**
**Your manual:** [USER_MANUAL_MANAGER.md](USER_MANUAL_MANAGER.md)

**What you do:**
- Review engineer-submitted repairs
- Approve quality work
- Reject incomplete/unsafe work
- Provide feedback to engineers
- Monitor system performance

**Platform:** ERPNext desktop (web browser)

---

#### ⚙️ **System Administrator / IT**
**Your manual:** [USER_MANUAL_ADMINISTRATOR.md](USER_MANUAL_ADMINISTRATOR.md)

**What you do:**
- Install and configure system
- Manage users and permissions
- Perform backups and updates
- Troubleshoot technical issues
- Train users and create documentation

**Platform:** ERPNext desktop + Server console

---

## Technical Documentation

### For Developers and IT Staff

#### Deployment and Setup
- **[DEPLOYMENT_GUIDE_v2.1.0.md](DEPLOYMENT_GUIDE_v2.1.0.md)** - Production deployment steps for v2.1.0
- **[FIXTURE_MANAGEMENT.md](FIXTURE_MANAGEMENT.md)** - Managing custom fields and workflows across environments
- **[ASSET_QR_PRINTING_GUIDE.md](ASSET_QR_PRINTING_GUIDE.md)** - Print QR labels for assets using Niimbot B1 printer

#### System Architecture
- **Frontend:** React 19 with QR scanner and camera integration
- **Backend:** ERPNext v15 / Frappe Framework v15
- **Database:** MariaDB
- **Caching:** Redis
- **Web Server:** Nginx

#### Key Features
- ✅ Mobile-first inspector portal with QR scanning
- ✅ Photo capture with automatic timestamping and geolocation
- ✅ Multi-stage approval workflow (Draft → Pending → Approved → Finished)
- ✅ Role-based field locking (engineers can't edit manager fields)
- ✅ Automatic notifications at each workflow stage
- ✅ Asset status management (Out of Order / In Maintenance)
- ✅ Inspector verification loop (closed-loop quality assurance)
- ✅ **NEW: Asset QR label printing** (Niimbot B1 thermal printer support)

---

## Documentation Structure

```
tub_suite/docs/
├── README_DOCUMENTATION.md          ← You are here (index)
│
├── USER_MANUAL_INSPECTOR.md         ← Mobile portal user guide
├── USER_MANUAL_ENGINEER.md          ← Desktop engineer guide
├── USER_MANUAL_MANAGER.md           ← Manager approval guide
├── USER_MANUAL_ADMINISTRATOR.md     ← IT/Admin technical guide
│
├── DEPLOYMENT_GUIDE_v2.1.0.md       ← Production deployment steps
├── FIXTURE_MANAGEMENT.md            ← Custom field management
└── ASSET_QR_PRINTING_GUIDE.md       ← QR label printing (Niimbot B1)
```

---

## Workflow Overview

### Complete Maintenance Cycle

```
┌─────────────────────────────────────────────────────────┐
│  1. INSPECTOR: Scans asset QR code                      │
│     └─ Views maintenance checklist                      │
│     └─ Performs inspection                              │
│     └─ Takes before/after photos                        │
│     └─ Submits task                                     │
├─────────────────────────────────────────────────────────┤
│  2a. NO ISSUE: Task marked completed ✅                 │
│      └─ Task card locks until next schedule            │
│      └─ Photos attached to maintenance log              │
├─────────────────────────────────────────────────────────┤
│  2b. ISSUE FOUND: Inspector reports problem ⚠️          │
│      └─ Takes issue photos                              │
│      └─ Writes description                              │
│      └─ Asset status → Out of Order (if Major)          │
│      └─ OR In Maintenance (if Minor)                    │
├─────────────────────────────────────────────────────────┤
│  3. ENGINEER: Receives notification 🔔                  │
│     └─ Reviews issue photos and description             │
│     └─ Plans repair (Engineering Details table)         │
│     └─ Performs repair work                             │
│     └─ Documents in Actions Performed                   │
│     └─ Attaches completion photos                       │
│     └─ Signs engineer signature                         │
│     └─ Submits for Approval                             │
│        └─ State: Draft → Pending Approval               │
├─────────────────────────────────────────────────────────┤
│  4. MANAGER: Receives notification 🔔                   │
│     └─ Reviews documentation and photos                 │
│     └─ Evaluates work quality                           │
│     └─ Decision:                                        │
│        ├─ APPROVE ✅                                     │
│        │  └─ Adds approval notes and signature          │
│        │  └─ State: Pending Approval → Approved         │
│        │  └─ Engineer notified                          │
│        │                                                 │
│        └─ REJECT ❌                                      │
│           └─ Adds rejection reason                      │
│           └─ State: Pending Approval → Rejected         │
│           └─ Maintenance log → Completed (false alarm)  │
│           └─ Engineer can rework or abandon             │
├─────────────────────────────────────────────────────────┤
│  5. ENGINEER: Marks repair as Finished                  │
│     └─ State: Approved → Finished                       │
│     └─ Inspector notified for verification 🔔           │
├─────────────────────────────────────────────────────────┤
│  6. INSPECTOR: Verifies completed repair                │
│     └─ Scans asset QR code again                        │
│     └─ Tests the repair                                 │
│     └─ Decision:                                        │
│        ├─ VERIFIED - PASSED ✅                           │
│        │  └─ Asset status → Submitted (operational)     │
│        │  └─ Task card unlocks for regular inspections  │
│        │                                                 │
│        └─ VERIFIED - FAILED ❌                           │
│           └─ Takes photos of remaining issues           │
│           └─ Adds notes                                 │
│           └─ Engineer re-notified                       │
└─────────────────────────────────────────────────────────┘
```

---

## Role Permissions Summary

### Asset Repair DocType Permissions

| Action | Inspector | Engineer | Manager | Admin |
|---|---|---|---|---|
| **View repairs** | Own only | All | All | All |
| **Create draft** | Via portal | ❌ | ❌ | ✅ |
| **Edit in Draft** | ❌ | ✅ | ✅ | ✅ |
| **Submit for Approval** | ❌ | ✅ | ❌ | ✅ |
| **Edit in Pending** | ❌ | ❌ | ❌ | ❌ |
| **Approve/Reject** | ❌ | ❌ | ✅ | ✅ |
| **Mark as Finished** | ❌ | ✅ | ❌ | ✅ |
| **Verify repair** | ✅ | ❌ | ❌ | ✅ |
| **Edit manager fields** | ❌ | ❌ | ✅ | ✅ |
| **Edit inspector fields** | ❌ | ❌ | ❌ | ❌ (locked) |

### Field Access Control

**Inspector Fields (Always Locked):**
- Failure Date
- Description
- Reported By
- Maintenance Task

**Engineer Fields (Locked after Submit):**
- Engineering Details table
- Actions Performed
- Engineer Signature

**Manager Fields (Manager Only):**
- Approval Notes
- Approval Signature
- Approval Timestamp

---

## System Requirements

### Production Server
- **OS:** Ubuntu 24.04 LTS (or similar)
- **RAM:** 4GB minimum, 8GB recommended
- **Disk:** 50GB minimum (for database, files, backups)
- **Python:** 3.11+
- **Node.js:** 18+
- **Database:** MariaDB 10.6+
- **Cache:** Redis 7+

### Client Devices

#### Inspectors (Mobile)
- **Device:** Smartphone or tablet
- **OS:** iOS 14+ or Android 10+
- **Browser:** Chrome, Safari, Edge (latest versions)
- **Camera:** Required for photo capture
- **Internet:** WiFi or 4G/5G cellular

#### Engineers/Managers (Desktop)
- **Device:** Laptop or desktop computer
- **OS:** Windows, macOS, Linux
- **Browser:** Chrome, Firefox, Edge (latest versions)
- **Screen:** 1280x720 minimum, 1920x1080 recommended

---

## Common Questions

### For Inspectors

**Q: Can I use this on my phone?**
A: Yes! The inspector portal is designed for mobile devices. Use `/maintenance` portal.

**Q: Do I need an app?**
A: No app needed. Use your mobile web browser (Chrome, Safari, etc.).

**Q: What if QR code is damaged?**
A: Use the search bar to type the asset code manually.

**Q: How many photos do I need?**
A: Normal inspection: 2 minimum (before/after). Issue reporting: 1 minimum (issue photo).

### For Engineers

**Q: Can I edit a repair after submitting for approval?**
A: No. After submission, the form is locked until manager approves/rejects.

**Q: What if manager rejects my work?**
A: Review the rejection notes, make corrections, and resubmit.

**Q: Can I approve my own repairs?**
A: No. Manager approval is required for all repairs.

### For Managers

**Q: Can I edit engineer's work documentation?**
A: No. Engineer fields are locked for audit trail. You can only approve/reject and add your notes.

**Q: How quickly should I review pending approvals?**
A: Major severity: Within 2-4 hours (asset down). Minor severity: Same day.

**Q: Can I undo an approval?**
A: No. Workflow doesn't allow state reversal. You can edit your approval notes afterward.

### For Administrators

**Q: How do I upgrade to new version?**
A: See [DEPLOYMENT_GUIDE_v2.1.0.md](DEPLOYMENT_GUIDE_v2.1.0.md) - Always backup first!

**Q: Where are uploaded photos stored?**
A: `~/frappe-bench/sites/tub.x-desk.tech/private/files/`

**Q: How do I export custom fields?**
A: See [FIXTURE_MANAGEMENT.md](FIXTURE_MANAGEMENT.md)

---

## Getting Help

### By Role

**Inspectors:**
- Check your manual: [USER_MANUAL_INSPECTOR.md](USER_MANUAL_INSPECTOR.md)
- Contact: Your supervisor or IT support

**Engineers:**
- Check your manual: [USER_MANUAL_ENGINEER.md](USER_MANUAL_ENGINEER.md)
- Contact: Your manager or IT support

**Managers:**
- Check your manual: [USER_MANUAL_MANAGER.md](USER_MANUAL_MANAGER.md)
- Contact: IT support or operations manager

**Administrators:**
- Check: [USER_MANUAL_ADMINISTRATOR.md](USER_MANUAL_ADMINISTRATOR.md)
- Community: https://discuss.erpnext.com
- Repository: https://github.com/tstexbj3/tub_suite

### Support Contacts
- **IT Support:** it@tipubon.com
- **System Issues:** [PHONE NUMBER]
- **Emergency:** [EMERGENCY CONTACT]

---

## Version History

### v2.1.0 (Current) - 2025-12-18
**New Features:**
- Fixed failure_date to capture exact timestamp (not just date)
- Fixed maintenance log stuck in "Planned" when repair rejected
- Enhanced engineer field locking (prevent editing manager approval fields)

### v2.0.0 - 2025-12-15
**Major Release:**
- Complete verification workflow (inspector verifies completed repairs)
- Portal settings configuration
- Enhanced photo requirements
- Badge count for verification tasks
- Comprehensive documentation

### v1.0 - Initial Release
**Core Features:**
- Basic maintenance workflow
- Mobile portal for inspections
- Asset repair tracking

---

## License and Credits

**Developed by:** Tipubon Development Team
**Built on:** ERPNext (GPLv3) / Frappe Framework (MIT)
**Repository:** https://github.com/tstexbj3/tub_suite

---

## Document Maintenance

**Documentation Owner:** IT Team
**Review Frequency:** Quarterly
**Last Review:** 2025-12-18
**Next Review:** 2026-03-18

**Contributors:**
- User feedback from inspectors, engineers, managers
- IT observations during support
- Security and compliance team requirements

---

## Quick Links

- 📱 [Inspector Manual](USER_MANUAL_INSPECTOR.md) - Mobile portal guide
- 🔧 [Engineer Manual](USER_MANUAL_ENGINEER.md) - Desktop repair workflow
- 👔 [Manager Manual](USER_MANUAL_MANAGER.md) - Approval and monitoring
- ⚙️ [Administrator Manual](USER_MANUAL_ADMINISTRATOR.md) - IT technical guide
- 🚀 [Deployment Guide](DEPLOYMENT_GUIDE_v2.1.0.md) - Production setup
- 📋 [Fixture Management](FIXTURE_MANAGEMENT.md) - Custom field management
- 🏷️ [QR Printing Guide](ASSET_QR_PRINTING_GUIDE.md) - Asset label printing (Niimbot B1)

---

**Need immediate help?**
1. Find your role above
2. Click your manual link
3. Check Table of Contents
4. Jump to relevant section
5. Follow step-by-step screenshots (when added)

**For screenshot documentation team:** Each manual has an appendix listing all needed screenshots with checkboxes.
