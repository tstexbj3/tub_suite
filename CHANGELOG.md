# Changelog

All notable changes to TUB Suite will be documented in this file.

## [1.1.0] - 2025-12-04

### Added
- Multiple photo upload (up to 5 photos per report)
- Client-side photo compression (80% quality)
- Same-day grace period for maintenance tasks
- Custom QR generation without port number
- Enhanced QR scanner supporting multiple URL formats
- Auto-load asset from QR scan URL parameter

### Fixed
- QR URLs no longer include :8000 port
- QR scanner now extracts asset ID from various URL formats
- Phone camera QR scanning now works correctly
- Blank screen issue when scanning from Line app

### Changed
- Improved error handling in photo upload
- Enhanced mobile UI for multiple photos
- Updated QR generation to use site_config.json

## [1.0.0] - 2025-12-02

### Added
- Initial release
- Mobile maintenance portal at /maintenance
- QR code scanning with jsQR
- Asset search (case-insensitive, multi-result)
- Maintenance checklist with due date tracking
- Problem reporting with single photo
- Email notifications to maintenance team
- Security features (rate limiting, audit logging)
- Thai language support
- Role-based access control
- Approval workflow for Asset Repair
