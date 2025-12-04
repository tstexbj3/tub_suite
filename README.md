# TUB Suite - Mobile Maintenance Portal for ERPNext

**A mobile-first maintenance inspection system with QR code scanning for Frappe/ERPNext**

[![Frappe](https://img.shields.io/badge/Frappe-v15.81.0-blue)](https://frappeframework.com)
[![ERPNext](https://img.shields.io/badge/ERPNext-v15.78.1-blue)](https://erpnext.com)
[![License](https://img.shields.io/badge/license-Proprietary-red)](LICENSE)

---

## 📱 Overview

TUB Suite is a comprehensive mobile maintenance management system built for **Tipubon International Co., Ltd.** It enables maintenance inspectors to:

- 📷 **Scan QR codes** on assets using mobile devices
- ✅ **Complete maintenance checklists** with due date tracking
- 🔧 **Report problems** with photo attachments
- 📧 **Notify maintenance teams** automatically
- 🔒 **Secure & audit** all maintenance activities

### Key Features

- ✅ **Mobile-first UI** - Optimized for phones and tablets
- ✅ **QR Code Scanner** - Built-in camera scanning with jsQR
- ✅ **Offline-capable** - Works with poor connectivity
- ✅ **Multi-photo uploads** - Up to 5 photos per report
- ✅ **Photo compression** - Client-side compression (80% quality)
- ✅ **Thai language** - Full localization support
- ✅ **Security features** - Rate limiting & audit logging
- ✅ **Approval workflow** - Asset Repair approval with locked fields

---

## 🎯 Use Cases

### For Manufacturing
- Equipment preventive maintenance
- Machine inspection checklists
- Breakdown reporting
- Spare parts tracking

### For Facilities Management
- Building maintenance schedules
- HVAC system inspections
- Safety equipment checks
- Work order management

### For Fleet Management
- Vehicle inspection checklists
- Maintenance schedules
- Defect reporting
- Service history tracking

---

## 📸 Screenshots

### Mobile Portal
- QR Scanner interface
- Asset search
- Maintenance checklist
- Problem reporting with photos

### Desktop Management
- Asset Repair dashboard
- Approval workflow
- Maintenance history
- Analytics & reports

---

## 🚀 Quick Start

### Prerequisites

- Frappe v15+ / ERPNext v15+
- Python 3.10+
- MariaDB 10.6+
- SSL certificate (for camera access)

### Installation

```bash
# 1. Create tub_suite app
cd ~/frappe-bench
bench new-app tub_suite

# 2. Install to site
bench --site your-site install-app tub_suite

# 3. Copy production files
cp production_code/api/asset.py apps/tub_suite/tub_suite/api/
cp production_code/www/maintenance/index.html apps/tub_suite/tub_suite/www/maintenance/
cp production_code/hooks.py apps/tub_suite/tub_suite/

# 4. Install dependencies
source env/bin/activate
pip install qrcode[pil]

# 5. Setup approval fields (one-time)
bench --site your-site execute tub_suite.install_approval_fields.install

# 6. Clear cache & restart
bench --site your-site clear-cache
bench restart
```

### Configuration

```bash
# Set site URL
bench --site your-site set-config host_name "https://your-domain.com"

# Enable CORS (optional, for testing)
bench --site your-site set-config allow_cors "*"
```

---

## 📚 Documentation

### User Guides
- [Inspector Guide](docs/INSPECTOR_GUIDE.md) - How to use mobile portal
- [Manager Guide](docs/MANAGER_GUIDE.md) - Repair approval & management
- [Administrator Guide](docs/ADMIN_GUIDE.md) - System configuration

### Technical Documentation
- [API Reference](docs/API_REFERENCE.md) - API endpoints & security
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) - Production deployment
- [QR Code Setup](docs/QR_SETUP.md) - QR generation & printing
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues & solutions

### Development
- [Architecture](docs/ARCHITECTURE.md) - System design & flow
- [Contributing](CONTRIBUTING.md) - How to contribute
- [Changelog](CHANGELOG.md) - Version history

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│  Mobile Device (Inspector)              │
│  ┌───────────────────────────────────┐  │
│  │  /maintenance Portal              │  │
│  │  - QR Scanner                     │  │
│  │  - Asset Search                   │  │
│  │  - Checklist                      │  │
│  │  - Photo Upload                   │  │
│  └───────────────────────────────────┘  │
└─────────────┬───────────────────────────┘
              │ HTTPS/REST API
              ↓
┌─────────────────────────────────────────┐
│  ERPNext Server                         │
│  ┌───────────────────────────────────┐  │
│  │  TUB Suite API                    │  │
│  │  - search_assets()                │  │
│  │  - get_asset_with_checklist()     │  │
│  │  - submit_checklist()             │  │
│  │  - generate_maintenance_qr()      │  │
│  │  + Security Layer                 │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  ERPNext Core                     │  │
│  │  - Asset                          │  │
│  │  - Asset Maintenance              │  │
│  │  - Asset Maintenance Log          │  │
│  │  - Asset Repair                   │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

---

## 🔐 Security Features

### Rate Limiting
- Search: 50 requests/minute/user
- View: 100 requests/minute/user
- Submit: 20 requests/minute/user

### Audit Logging
- All actions logged to Activity Log
- Security events logged to Error Log
- Includes: User, IP, Timestamp, Action

### Access Control
- Role-based permissions
- Asset-level permissions
- Approval workflow validation

### Data Protection
- Input sanitization
- SQL injection prevention
- XSS protection
- CSRF token validation

---

## 🛠️ Tech Stack

### Frontend
- HTML5, CSS3, JavaScript (ES6)
- jQuery 3.x
- jsQR (QR code scanning)
- Canvas API (image compression)

### Backend
- Python 3.10+
- Frappe Framework v15
- ERPNext v15
- MariaDB 10.6+

### Infrastructure
- Ubuntu 24.04 LTS
- nginx (reverse proxy)
- Supervisor (process management)
- Redis (caching)

---

## 📊 Project Status

| Component | Status | Version |
|-----------|--------|---------|
| Mobile Portal | ✅ Production | 1.1.0 |
| QR Scanner | ✅ Production | 1.1.0 |
| Asset Search | ✅ Production | 1.0.0 |
| Checklist | ✅ Production | 1.1.0 |
| Photo Upload | ✅ Production | 1.1.0 |
| Email Notifications | ✅ Production | 1.0.0 |
| Security | ✅ Production | 1.0.0 |
| Approval Workflow | ✅ Production | 1.1.0 |

---

## 🗺️ Roadmap

### Version 1.2.0 (Planned)
- [ ] Maintenance history view
- [ ] Advanced search filters
- [ ] Offline mode improvements
- [ ] Batch QR generation tool

### Version 1.3.0 (Future)
- [ ] Mobile app (React Native)
- [ ] Barcode support
- [ ] Voice notes
- [ ] Parts inventory integration

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone repository
git clone https://github.com/tipubon/tub-suite.git
cd tub-suite

# Create development environment
cd ~/frappe-bench
bench get-app tub_suite path/to/tub-suite

# Install to dev site
bench --site dev-site install-app tub_suite

# Run development server
bench start
```

### Code Standards
- Python: PEP 8
- JavaScript: ES6+
- Documentation: Markdown
- Commits: Conventional Commits

---

## 📄 License

Proprietary License - Tipubon International Co., Ltd.

This software is proprietary and confidential. Unauthorized copying, distribution, or modification is strictly prohibited.

For licensing inquiries, contact: [email@tipubon.com]

---

## 👥 Team

**Developed by**: Tipubon International Co., Ltd.
**Client**: Internal Use
**Maintained by**: IT Department

### Contributors
- Initial development: December 2025
- Architecture & Design: Tipubon IT Team
- Implementation: Frappe Framework

---

## 📞 Support

### Documentation
- 📖 [Complete Documentation](docs/MAINTENANCE_MODULE_DOCUMENTATION.md)
- 🔧 [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- 💬 [FAQ](docs/FAQ.md)

### Contact
- **Email**: support@tipubon.com
- **Website**: https://tipubon.com
- **ERPNext Site**: https://tub.x-desk.tech

### Resources
- [Frappe Documentation](https://frappeframework.com/docs)
- [ERPNext Documentation](https://docs.erpnext.com)
- [Issue Tracker](https://github.com/tipubon/tub-suite/issues)

---

## 🙏 Acknowledgments

- **Frappe Framework** - Core framework
- **ERPNext** - ERP system
- **jsQR** - QR code scanning library
- **QR Foundry** - QR code generation (optional)

---

## 📈 Statistics

- **Lines of Code**: ~5,000 (Python + JavaScript + HTML)
- **API Endpoints**: 8 core functions
- **Test Coverage**: Manual testing complete
- **Documentation**: 20+ pages
- **Assets Managed**: 170+ (Tipubon production)

---

## 🔄 Version History

### v1.1.0 (December 4, 2025)
- ✅ Multiple photo upload (up to 5)
- ✅ Client-side photo compression
- ✅ Same-day grace period for tasks
- ✅ Asset Repair approval workflow
- ✅ Custom QR generation without port
- ✅ Improved error handling

### v1.0.0 (December 2, 2025)
- ✅ Initial release
- ✅ Mobile maintenance portal
- ✅ QR code scanning
- ✅ Maintenance checklist
- ✅ Problem reporting
- ✅ Email notifications
- ✅ Security features

---

**⭐ Star this repository if you find it useful!**

**🐛 Found a bug? [Report it](https://github.com/tipubon/tub-suite/issues)**

**💡 Have a feature request? [Let us know](https://github.com/tipubon/tub-suite/issues/new)**

---

Made with ❤️ by Tipubon International Co., Ltd.
