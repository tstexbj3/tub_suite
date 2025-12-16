# TUB Suite - Deployment Guide

**Version:** 2.0.1
**Last Updated:** 2025-12-16
**Target:** Production & Development Environments

---

## Quick Deploy (Development)

```bash
cd /home/user/frappe-bench/apps/tub_suite/maintenance-react-dev
bash deploy.sh
# Restart bench (Ctrl+C then bench start)
```

That's it! The `deploy.sh` script handles everything.

---

## What `deploy.sh` Does

1. **Builds React app** with Vite (`npm run build`)
2. **Auto-updates template hash** in `tub_suite/www/maintenance.html`
3. **Outputs next steps** (restart bench, refresh browser)

### Manual Build (Not Recommended)

```bash
cd /home/user/frappe-bench/apps/tub_suite/maintenance-react-dev
npm run build
bash update-hash.sh  # CRITICAL - Updates template with new asset hashes
```

---

## Production Deployment

### First Time Setup

```bash
# 1. Install app
cd ~/frappe-bench
bench get-app https://github.com/tstexbj3/tub_suite.git
bench --site YOUR_SITE install-app tub_suite

# 2. Build frontend
cd apps/tub_suite/maintenance-react-dev
npm install
bash deploy.sh

# 3. Setup permissions
bench --site YOUR_SITE execute tub_suite.setup.asset_repair_setup.run_production_setup

# 4. Restart
bench --site YOUR_SITE clear-cache
bench restart
```

### Updating Existing Installation

```bash
# 1. Pull latest code
cd ~/frappe-bench/apps/tub_suite
git pull origin main

# 2. Rebuild frontend
cd maintenance-react-dev
bash deploy.sh

# 3. Migrate database (if needed)
bench --site YOUR_SITE migrate

# 4. Clear cache and restart
bench --site YOUR_SITE clear-cache
bench restart
```

---

## Asset Hash Management

### Why Hash Updates Are Required

Vite generates unique hashes for each build:
```
index-Ckwp7CKQ.js  ← Changes every build
index-GoYVPehZ.css ← Changes every build
```

The HTML template must reference the correct hash:
```html
<script src="/assets/tub_suite/maintenance/assets/index-Ckwp7CKQ.js"></script>
```

### Automated Hash Update (Recommended)

```bash
bash deploy.sh  # Handles everything
```

### Manual Hash Update (If Needed)

```bash
# 1. Build
npm run build

# 2. Check new hashes
ls ../tub_suite/public/maintenance/assets/

# Output:
# index-NewHash123.js
# index-NewHash456.css

# 3. Update template
bash update-hash.sh

# Or manually edit: tub_suite/www/maintenance.html
# Update lines 22-23 with new hashes
```

---

## File Structure

```
tub_suite/
├── maintenance-react-dev/           # React source code
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.jsx            # Portal home with verification alerts
│   │   │   ├── VerifyRepair.jsx    # Verification page
│   │   │   ├── Checklist.jsx       # Maintenance checklist
│   │   │   └── AssetSearch.jsx     # Asset search
│   │   ├── components/
│   │   ├── services/
│   │   │   └── api.js              # API service layer
│   │   └── index.css               # Styles
│   ├── deploy.sh                    # ONE-COMMAND DEPLOY
│   ├── update-hash.sh              # Auto hash updater
│   ├── package.json
│   └── vite.config.js
│
├── tub_suite/
│   ├── www/
│   │   ├── maintenance.html        # Template (hash must match build)
│   │   └── maintenance.py          # Route handler
│   ├── public/maintenance/         # Build output (auto-generated)
│   │   ├── index.html
│   │   └── assets/
│   │       ├── index-[hash].js
│   │       └── index-[hash].css
│   ├── api/
│   │   ├── maintenance.py          # Main API endpoints
│   │   └── file_utils.py           # Photo upload utilities
│   ├── overrides/
│   │   └── asset_repair_override.py  # Custom Asset Repair logic
│   └── hooks.py
```

---

## Build Process Details

### Development Build

```bash
npm run dev  # Hot reload on http://localhost:5173
```

- Vite dev server with HMR
- Changes reflect immediately
- No hash management needed

### Production Build

```bash
npm run build
```

**Output:**
```
../tub_suite/public/maintenance/
├── index.html
└── assets/
    ├── index-[hash].js    # Minified, tree-shaken
    └── index-[hash].css   # Minified
```

**Build Config:** `vite.config.js`
```javascript
export default {
  base: '/assets/tub_suite/maintenance/',
  build: {
    outDir: '../tub_suite/public/maintenance',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        entryFileNames: 'assets/[name]-[hash].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    }
  }
}
```

---

## Troubleshooting

### 404 Not Found on JS/CSS

**Symptoms:**
```
GET /assets/tub_suite/maintenance/assets/index-OldHash.js 404 (NOT FOUND)
```

**Cause:** Template has old hash, doesn't match build output

**Fix:**
```bash
cd maintenance-react-dev
bash update-hash.sh
# Restart bench
```

### Permission Denied on deploy.sh

**Symptoms:**
```bash
bash: ./deploy.sh: Permission denied
```

**Fix:**
```bash
bash deploy.sh  # Use bash prefix instead of ./
```

Or:
```bash
chmod +x deploy.sh update-hash.sh
./deploy.sh
```

### Build Succeeds But Browser Shows Old Version

**Cause:** Browser cache or server cache

**Fix:**
```bash
# 1. Clear ERPNext cache
bench --site YOUR_SITE clear-cache
bench --site YOUR_SITE clear-website-cache

# 2. Restart bench
bench restart

# 3. Hard refresh browser
# Windows: Ctrl + Shift + R
# Mac: Cmd + Shift + R
```

### React App Not Loading (Blank Screen)

**Check:**
1. Browser console for errors
2. Network tab - Are assets loading?
3. Template hash matches build output:
   ```bash
   # Check template
   grep "index-" tub_suite/www/maintenance.html

   # Check build
   ls tub_suite/public/maintenance/assets/
   ```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'

      - name: Build Frontend
        run: |
          cd maintenance-react-dev
          npm install
          bash deploy.sh

      - name: Deploy to Production
        run: |
          ssh user@production-server << 'EOF'
            cd ~/frappe-bench/apps/tub_suite
            git pull origin main
            cd maintenance-react-dev
            bash deploy.sh
            bench --site YOUR_SITE clear-cache
            bench restart
          EOF
```

---

## Version Control Best Practices

### What to Commit

```
✅ maintenance-react-dev/src/       # React source
✅ maintenance-react-dev/deploy.sh
✅ maintenance-react-dev/update-hash.sh
✅ maintenance-react-dev/package.json
✅ tub_suite/www/maintenance.html   # Template (with current hash)
```

### What to Ignore

```
❌ tub_suite/public/maintenance/    # Build output (auto-generated)
❌ maintenance-react-dev/node_modules/
❌ maintenance-react-dev/dist/
```

**.gitignore:**
```
tub_suite/public/maintenance/
maintenance-react-dev/node_modules/
maintenance-react-dev/dist/
*.log
```

---

## Performance Optimization

### Current Build Size

```
index-[hash].js:  617.97 kB (minified)  → 189.31 kB (gzipped)
index-[hash].css:  10.10 kB (minified)  →   2.52 kB (gzipped)
```

### Reducing Bundle Size (Future)

If bundle size becomes an issue:

```javascript
// Use dynamic imports for code splitting
const VerifyRepair = lazy(() => import('./pages/VerifyRepair'))
const Checklist = lazy(() => import('./pages/Checklist'))
```

---

## Security Checklist

- [x] CSRF token validation in all API calls
- [x] Permission checks on backend
- [x] Reporter verification (only original reporter can verify)
- [x] File upload validation
- [x] Rate limiting on API endpoints
- [x] No desk access for Maintenance User role

---

## Rollback Procedure

If deployment fails:

```bash
# 1. Revert to previous commit
cd ~/frappe-bench/apps/tub_suite
git log --oneline  # Find previous commit hash
git checkout <previous-commit-hash>

# 2. Rebuild
cd maintenance-react-dev
bash deploy.sh

# 3. Restart
bench restart
```

---

## Support

**Issues:** https://github.com/tstexbj3/tub_suite/issues
**Docs:** README.md, TECHNICAL.md, WORKFLOW.md

