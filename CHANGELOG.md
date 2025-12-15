# Changelog

All notable changes to the TUB Suite project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2025-12-15

### 🚀 Major Rewrite - React Migration

**This is a BREAKING CHANGE release. The frontend has been completely rewritten in React 19.2.0.**

#### Breaking Changes

- **Frontend Stack Migration:**
  - Removed jQuery dependencies
  - Migrated from HTML5/JavaScript to React 19.2.0
  - New build system using Vite 6.0.3
  - Modern component architecture with React hooks

- **Build Process:**
  - Requires `npm install` and `npm run build` for production
  - Development server: `npm run dev`
  - Assets now built to `tub_suite/public/maintenance/` and `tub_suite/www/maintenance/`

- **API Changes:**
  - Enhanced `get_maintenance_by_asset` endpoint
  - Improved error handling and response formats
  - Added security features (rate limiting, audit logging)

#### ✨ New Features

**Frontend:**
- ✅ Bilingual support (English/Thai) with i18next
- ✅ Modern, responsive UI with better mobile experience
- ✅ Multi-photo upload for issue reporting (up to 5 photos)
- ✅ Photo preview and removal before submission
- ✅ Real-time validation and user feedback
- ✅ Loading states and error boundaries
- ✅ Recently completed task badges and protection
- ✅ Task status badges (overdue, due today, completed today)
- ✅ Improved search with debouncing
- ✅ Asset selection from search results

**Backend:**
- ✅ Enhanced maintenance API with repair workflow
- ✅ Auto-calculation of next due dates based on periodicity
- ✅ Duplicate submission prevention (same-day grace period)
- ✅ Task ordering now respects Asset Maintenance idx
- ✅ Security features:
  - Rate limiting on API endpoints
  - Permission validation
  - Input sanitization
  - Audit logging
- ✅ Asset status management (Out of Order detection)
- ✅ Active repair tracking
- ✅ **Issue Severity System** ⭐ NEW
  - Minor issues: Asset keeps running
  - Major issues: Asset automatically goes Out of Order
  - Engineer sets severity when assessing repairs
- ✅ **Inspector Verification Workflow** ⭐ NEW
  - Original reporter must verify repairs with after-photos
  - Verification required before manager approval
  - Manager can override verification if needed
- ✅ **Photo System with Timestamps** ⭐ NEW
  - Structured filename format: `ASSET_ACTIVITY_TIMESTAMP_SEQ_USER.jpg`
  - All photos require timestamps (proof of presence)
  - Metadata embedded in photo uploads
  - Audit trail for compliance

#### 🔧 Fixed

- **Task Ordering:** Tasks now display in correct order from Asset Maintenance (respects idx field)
- **Notes Field:** Maintenance notes now correctly save to `actions_performed` field
- **File Uploads:** Fixed 417 Expectation Failed errors on photo uploads
- **Task Completion:** Recently completed tasks (same day) cannot be resubmitted
- **Due Date Calculation:** Next due dates properly calculated based on task periodicity
- **Asset Search:** Multi-field search (name, item_code, item_name) working correctly

#### 🏗️ Technical Improvements

**Frontend Architecture:**
- Component-based structure (Home, AssetSearch, Checklist, TaskList, etc.)
- Custom hooks for data fetching and state management
- Centralized API client with error handling
- Responsive design with mobile-first approach
- Modern CSS with flexbox/grid layouts

**Backend Architecture:**
- Modular API structure (maintenance.py, asset.py, qr_scanner.py, file_utils.py)
- Photo utilities with timestamp and structured naming
- Verification workflow APIs
- Asset Repair override with severity-based status management
- Security utilities (rate limiting, input sanitization)
- Helper functions for asset history and repairs
- Role-based access control
- Transaction safety and rollback support

#### 📝 Migration Guide

**For Developers:**
1. Old v1.x jQuery version preserved in `v1-jquery-legacy` branch
2. React source code in `maintenance-react-dev/` (if preserved in repo)
3. Build artifacts in `tub_suite/public/maintenance/` and `tub_suite/www/maintenance/`

**Installation:**
```bash
# Install dependencies
cd apps/tub_suite
npm install  # (if React source included)

# Build for production
npm run build  # (if React source included)

# Clear Frappe cache
bench --site [site-name] clear-cache

# Restart bench
bench restart
```

**Breaking API Changes:**
- `get_maintenance_by_asset` now returns array of assets (not single asset)
- Response format includes `task_count` and structured asset info
- New fields: `is_checkable`, `status_badge`, `completed_by`, `completed_time`

#### 🔐 Security Enhancements

- Rate limiting on all API endpoints
- User role validation (Maintenance Inspector, Manager, Engineer)
- Input sanitization (max lengths, XSS prevention)
- Permission checks on asset access
- Audit logging for security events
- CSRF token handling in React app

#### 📦 Dependencies

**Frontend:**
- React 19.2.0
- React Router 7.1.1
- i18next 24.2.0 (internationalization)
- Lucide React 0.468.0 (icons)
- Vite 6.0.3 (build tool)

**Backend:**
- ERPNext v15
- Frappe Framework v15
- Python 3.12+

#### 🎨 UI/UX Improvements

- Clean, modern interface
- Better error messages (bilingual)
- Loading indicators
- Success/error notifications
- Photo upload with preview
- Task status visual indicators
- Responsive layout for mobile/tablet/desktop
- Improved touch targets for mobile

---

## [1.1.0] - 2024-12-04

### Added
- Basic maintenance checklist functionality
- QR code scanning for asset identification
- jQuery-based frontend
- Asset Maintenance Log creation
- Repair request workflow

### Fixed
- Various bug fixes and improvements

---

## [1.0.0] - 2024-11-30

### Added
- Initial release
- Basic TUB Suite structure
- Custom DocTypes (Maintenance Schedule, Maintenance Log, Checklist Item)
- Integration with ERPNext Assets
- Basic mobile interface

---

## Version Comparison

| Feature | v1.x (jQuery) | v2.0.0 (React) |
|---------|---------------|----------------|
| Frontend | jQuery/HTML5 | React 19.2.0 |
| Build Tool | None | Vite |
| i18n | Hardcoded | i18next |
| Mobile UX | Basic | Enhanced |
| Photo Upload | Single | Multiple (5) |
| Task Protection | No | Yes (same-day) |
| Status Badges | No | Yes |
| API Security | Basic | Enhanced |
| Type Safety | No | PropTypes |

---

## Links

- **Repository:** https://github.com/tstexbj3/tub_suite
- **Legacy Version:** Branch `v1-jquery-legacy`
- **Issues:** https://github.com/tstexbj3/tub_suite/issues

---

## Acknowledgments

- Built for Tipubon International Co., Ltd.
- Developed for ERPNext v15 / Frappe Framework v15
- React migration completed December 2024

---

**Note:** For questions about migrating from v1.x to v2.0.0, please open an issue on GitHub.
