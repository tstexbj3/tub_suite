# GitHub Update Guide - TUB Suite v2.0.0

## Overview
Update existing repo (https://github.com/tstexbj3/tub_suite) from v1.1.0 (jQuery) to v2.0.0 (React)

## ⚠️ IMPORTANT: Run these commands in WSL terminal

```bash
# Open WSL terminal and navigate to project
cd ~/frappe-bench/apps/tub_suite
```

---

## Step 1: Configure Git Remote

```bash
# Add remote if not already configured
git remote add origin https://github.com/tstexbj3/tub_suite.git

# Or update if it exists
git remote set-url origin https://github.com/tstexbj3/tub_suite.git

# Verify
git remote -v
```

---

## Step 2: Fetch Existing Repo

```bash
# Fetch all branches from GitHub
git fetch origin

# Check what branches exist on GitHub
git branch -a
```

---

## Step 3: Create Backup Branch (Preserve v1.x)

```bash
# If main/master exists on GitHub, create backup branch from it
git checkout -b v1-jquery-legacy origin/main
# OR if it's 'master'
git checkout -b v1-jquery-legacy origin/master

# Push backup branch
git push origin v1-jquery-legacy

# Go back to your local branch
git checkout main
# OR
git checkout master
```

**If you get an error about branches not existing:**
```bash
# Just create the backup from your current state
git checkout -b v1-jquery-legacy
git push origin v1-jquery-legacy
git checkout main
```

---

## Step 4: Check Current Changes

```bash
# See what files have changed
git status

# See what's different
git diff
```

---

## Step 5: Stage All Changes

```bash
# Add all changes
git add .

# Verify what will be committed
git status
```

---

## Step 6: Commit as v2.0.0

```bash
git commit -m "v2.0.0: Major rewrite - jQuery to React migration

🚀 Major Changes:
- Complete frontend rewrite in React 19.2.0
- Modern build system with Vite
- Bilingual support (EN/TH) with i18next
- Improved mobile UX and component architecture

✨ New Features:
- Multi-photo upload for issue reporting
- Auto-calculation of next due dates
- Duplicate submission prevention
- Better task ordering (respects Asset Maintenance idx)
- Recently completed task protection

🔧 Fixes:
- Notes now save to correct field (actions_performed)
- 417 file upload errors resolved
- Task completion logic improved

⚠️ Breaking Changes:
- jQuery dependencies removed
- Requires frontend rebuild
- API endpoints enhanced with new features

📝 Migration:
- Old v1.x jQuery version preserved in 'v1-jquery-legacy' branch
- See CHANGELOG.md for full details
"
```

---

## Step 7: Push to GitHub

```bash
# Push to main branch
git push origin main

# OR if you use master
git push origin master

# If you get "rejected" error (diverged history):
git push origin main --force-with-lease

# ⚠️ Only use --force if you're sure you want to replace GitHub version
```

---

## Step 8: Create Git Tag

```bash
# Create version tag
git tag -a v2.0.0 -m "Version 2.0.0 - React Migration"

# Push tag
git push origin v2.0.0
```

---

## Step 9: Verify on GitHub

1. Go to: https://github.com/tstexbj3/tub_suite
2. Check that:
   - ✅ Main branch has new React code
   - ✅ Branch `v1-jquery-legacy` exists with old jQuery code
   - ✅ Tag `v2.0.0` is visible
   - ✅ README.md shows updated content

---

## Troubleshooting

### "Authentication failed"
```bash
# Use personal access token
# GitHub Settings → Developer settings → Personal access tokens
# Create token with 'repo' scope
# Use token as password when prompted
```

### "Diverged history"
```bash
# If you want to completely replace GitHub version:
git push origin main --force-with-lease
```

### "No such branch"
```bash
# Check what your local branch is called
git branch

# Use that name instead of 'main' or 'master'
```

### Git config needed
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## Next Steps After Push

1. **Create GitHub Release**
   - Go to Releases → Draft new release
   - Tag: v2.0.0
   - Title: "v2.0.0 - React Migration"
   - Description: Copy from CHANGELOG.md

2. **Update Repository Settings**
   - Set default branch to `main` (if needed)
   - Add topics: `frappe`, `erpnext`, `react`, `maintenance`, `qr-code`

3. **Documentation**
   - Ensure README.md is clear about v2.0.0
   - Add installation instructions for React version
   - Link to migration guide

---

## Quick Command Summary

```bash
# All commands in sequence
cd ~/frappe-bench/apps/tub_suite
git remote add origin https://github.com/tstexbj3/tub_suite.git
git fetch origin
git checkout -b v1-jquery-legacy
git push origin v1-jquery-legacy
git checkout main
git add .
git commit -m "v2.0.0: Major rewrite - jQuery to React migration"
git push origin main
git tag -a v2.0.0 -m "Version 2.0.0 - React Migration"
git push origin v2.0.0
```

---

**Created:** 2025-12-15
**Purpose:** Update TUB Suite GitHub repo to v2.0.0
