# Frontend Updates Required for v2.0.0 Backend

**Status:** Backend complete, React source code not in repository

**Note:** The React 19.2.0 source code is not currently in the repository. This document specifies the frontend changes needed to work with the updated v2.0.0 backend APIs.

---

## Overview

The backend has been updated with:
- ✅ Photo system with timestamps and structured naming
- ✅ Inspector verification workflow
- ✅ Issue severity system (Minor/Major)
- ✅ New API signatures for maintenance submission

The frontend needs to be updated to use these new APIs and features.

---

## 1. API Signature Changes

### `submit_maintenance_task()` - BREAKING CHANGE

**OLD API (v1.x):**
```javascript
frappe.call({
  method: 'tub_suite.api.maintenance.submit_maintenance_task',
  args: {
    maintenance_name: maintenanceName,
    task_name: taskName,
    asset_name: assetName,
    has_issue: 0,
    notes: notes,
    before_photo: photoUrl1,  // ❌ REMOVED
    after_photo: photoUrl2    // ❌ REMOVED
  }
});
```

**NEW API (v2.0.0):**
```javascript
frappe.call({
  method: 'tub_suite.api.maintenance.submit_maintenance_task',
  args: {
    maintenance_name: maintenanceName,
    task_name: taskName,
    asset_name: assetName,
    has_issue: 0,
    notes: notes,
    inspection_photos: [photoUrl1, photoUrl2, photoUrl3]  // ✅ NEW - array of URLs
  }
});
```

**Issue Reporting:**
```javascript
frappe.call({
  method: 'tub_suite.api.maintenance.submit_maintenance_task',
  args: {
    maintenance_name: maintenanceName,
    task_name: taskName,
    asset_name: assetName,
    has_issue: 1,
    issue_description: description,
    notes: notes,
    issue_photos: [photoUrl1, photoUrl2]  // Already existed, keep as-is
  }
});
```

---

## 2. Photo Upload Component Updates

### Current Behavior (Assumed)
- User takes photo
- Photo uploaded to Frappe
- URL returned

### Required Changes

#### A. Add Timestamp Overlay
Before uploading, add timestamp overlay to photo:

```javascript
// Add timestamp to photo before upload
function addTimestampToPhoto(photoFile) {
  return new Promise((resolve) => {
    const img = new Image();
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;

      // Draw original photo
      ctx.drawImage(img, 0, 0);

      // Add timestamp overlay (bottom-right)
      const timestamp = new Date().toLocaleString('th-TH', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });

      ctx.font = 'bold 24px Arial';
      ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
      ctx.fillRect(canvas.width - 220, canvas.height - 40, 210, 35);
      ctx.fillStyle = 'white';
      ctx.fillText(timestamp, canvas.width - 215, canvas.height - 15);

      // Convert canvas to blob
      canvas.toBlob((blob) => {
        resolve(new File([blob], photoFile.name, { type: 'image/jpeg' }));
      }, 'image/jpeg', 0.95);
    };

    img.src = URL.createObjectURL(photoFile);
  });
}
```

#### B. Use Structured Filename

The backend will handle filename generation, but you can prepare metadata:

```javascript
// Upload photo with metadata
async function uploadPhotoWithTimestamp(photoFile, assetName, activityType, sequence) {
  // Add timestamp overlay
  const photoWithTimestamp = await addTimestampToPhoto(photoFile);

  // Upload to Frappe
  const formData = new FormData();
  formData.append('file', photoWithTimestamp);
  formData.append('is_private', 0);
  formData.append('folder', 'Home/Attachments');

  const response = await fetch('/api/method/upload_file', {
    method: 'POST',
    headers: {
      'X-Frappe-CSRF-Token': frappe.csrf_token
    },
    body: formData
  });

  const result = await response.json();
  return result.message.file_url;
}
```

#### C. Update Photo Array Handling

**For Normal Completion:**
```javascript
// Checklist.jsx or TaskCompletion component
const [inspectionPhotos, setInspectionPhotos] = useState([]);

// When user adds photo
const handleAddPhoto = async (photoFile) => {
  const photoUrl = await uploadPhotoWithTimestamp(
    photoFile,
    assetName,
    'INSP',
    inspectionPhotos.length + 1
  );
  setInspectionPhotos([...inspectionPhotos, photoUrl]);
};

// Validation before submit
const handleSubmit = () => {
  if (inspectionPhotos.length === 0) {
    alert('At least 1 inspection photo is required');
    return;
  }

  if (inspectionPhotos.length > 5) {
    alert('Maximum 5 photos allowed');
    return;
  }

  // Submit
  frappe.call({
    method: 'tub_suite.api.maintenance.submit_maintenance_task',
    args: {
      inspection_photos: inspectionPhotos  // Pass array
    }
  });
};
```

**For Issue Reporting:**
```javascript
// IssueReport.jsx component
const [issuePhotos, setIssuePhotos] = useState([]);

// When user adds photo
const handleAddIssuePhoto = async (photoFile) => {
  const photoUrl = await uploadPhotoWithTimestamp(
    photoFile,
    assetName,
    'ISSUE',
    issuePhotos.length + 1
  );
  setIssuePhotos([...issuePhotos, photoUrl]);
};

// Validation before submit
const handleSubmitIssue = () => {
  if (issuePhotos.length === 0) {
    alert('At least 1 issue photo is required');
    return;
  }

  frappe.call({
    method: 'tub_suite.api.maintenance.submit_maintenance_task',
    args: {
      has_issue: 1,
      issue_photos: issuePhotos  // Pass array
    }
  });
};
```

---

## 3. Inspector Verification Page (NEW)

### Required: New Component/Page

Create a new page for inspectors to verify completed repairs.

#### File Structure
```
src/
  components/
    VerifyRepair.jsx  (NEW)
```

#### Component Specification

```javascript
// VerifyRepair.jsx
import React, { useState, useEffect } from 'react';

function VerifyRepair({ repairName }) {
  const [repair, setRepair] = useState(null);
  const [verificationPhotos, setVerificationPhotos] = useState([]);
  const [verificationNotes, setVerificationNotes] = useState('');
  const [verificationStatus, setVerificationStatus] = useState('Verified - Passed');

  useEffect(() => {
    loadRepairDetails();
  }, [repairName]);

  const loadRepairDetails = async () => {
    const response = await frappe.call({
      method: 'tub_suite.api.maintenance.get_repair_for_verification',
      args: { repair_name: repairName }
    });
    setRepair(response.message);
  };

  const handleAddVerificationPhoto = async (photoFile) => {
    const photoUrl = await uploadPhotoWithTimestamp(
      photoFile,
      repair.asset,
      'VERIFY',
      verificationPhotos.length + 1
    );
    setVerificationPhotos([...verificationPhotos, photoUrl]);
  };

  const handleSubmitVerification = async () => {
    if (verificationPhotos.length === 0) {
      alert('At least 1 after-repair photo is required');
      return;
    }

    await frappe.call({
      method: 'tub_suite.api.maintenance.verify_repair_completion',
      args: {
        repair_name: repairName,
        verification_photos: verificationPhotos,
        verification_notes: verificationNotes,
        verification_status: verificationStatus
      }
    });

    alert('Verification submitted successfully');
    // Navigate back to repair list
  };

  return (
    <div className="verify-repair">
      <h2>Verify Repair</h2>

      {/* Repair Details */}
      <div className="repair-info">
        <p><strong>Asset:</strong> {repair?.asset}</p>
        <p><strong>Issue:</strong> {repair?.failure_description}</p>
        <p><strong>Repair Notes:</strong> {repair?.repair_notes}</p>
      </div>

      {/* Issue Photos */}
      <div className="issue-photos">
        <h3>Original Issue Photos</h3>
        {/* Display issue photos */}
      </div>

      {/* Verification Photos Upload */}
      <div className="verification-photos">
        <h3>After-Repair Photos (Min 1, Max 5)</h3>
        <input
          type="file"
          accept="image/*"
          capture="environment"
          onChange={(e) => handleAddVerificationPhoto(e.target.files[0])}
        />
        <div className="photo-preview">
          {verificationPhotos.map((url, idx) => (
            <img key={idx} src={url} alt={`Verification ${idx + 1}`} />
          ))}
        </div>
      </div>

      {/* Verification Status */}
      <div className="verification-status">
        <label>Verification Status:</label>
        <select
          value={verificationStatus}
          onChange={(e) => setVerificationStatus(e.target.value)}
        >
          <option value="Verified - Passed">✅ Passed - Repair Complete</option>
          <option value="Verified - Failed">❌ Failed - Needs Rework</option>
        </select>
      </div>

      {/* Verification Notes */}
      <div className="verification-notes">
        <label>Verification Notes:</label>
        <textarea
          value={verificationNotes}
          onChange={(e) => setVerificationNotes(e.target.value)}
          placeholder="Add notes about the repair verification..."
        />
      </div>

      {/* Submit Button */}
      <button
        onClick={handleSubmitVerification}
        disabled={verificationPhotos.length === 0}
      >
        Submit Verification
      </button>
    </div>
  );
}

export default VerifyRepair;
```

#### Navigation

Add link from repair list to verification page:

```javascript
// RepairList.jsx
{repairs.map(repair => (
  <div key={repair.name} className="repair-item">
    <p>{repair.asset} - {repair.failure_description}</p>

    {repair.verification_status === 'Pending Verification' &&
     repair.reported_by === currentUser && (
      <button onClick={() => navigate(`/verify-repair/${repair.name}`)}>
        Verify Repair
      </button>
    )}
  </div>
))}
```

---

## 4. Checklist Component Changes

### File: `Checklist.jsx` (or similar)

**Find and Replace:**

❌ **Remove:**
```javascript
const [beforePhoto, setBeforePhoto] = useState(null);
const [afterPhoto, setAfterPhoto] = useState(null);
```

✅ **Replace with:**
```javascript
const [inspectionPhotos, setInspectionPhotos] = useState([]);
```

**Update Submit Function:**

❌ **Old:**
```javascript
frappe.call({
  args: {
    before_photo: beforePhoto,
    after_photo: afterPhoto
  }
});
```

✅ **New:**
```javascript
frappe.call({
  args: {
    inspection_photos: inspectionPhotos  // Array
  }
});
```

---

## 5. Photo Validation

Add client-side validation before API calls:

```javascript
// PhotoValidator.js utility
export function validatePhotos(photos, activityType) {
  const errors = [];

  // Minimum 1 photo required
  if (!photos || photos.length === 0) {
    errors.push('At least 1 photo is required');
  }

  // Maximum 5 photos
  if (photos.length > 5) {
    errors.push('Maximum 5 photos allowed');
  }

  // Check if photos are URLs
  photos.forEach((photo, idx) => {
    if (!photo || typeof photo !== 'string') {
      errors.push(`Photo ${idx + 1} is invalid`);
    }
  });

  return {
    valid: errors.length === 0,
    errors: errors
  };
}
```

Usage:
```javascript
const validation = validatePhotos(inspectionPhotos, 'INSP');
if (!validation.valid) {
  alert(validation.errors.join('\n'));
  return;
}
```

---

## 6. UI/UX Improvements

### Photo Count Display
```javascript
<div className="photo-counter">
  {inspectionPhotos.length} / 5 photos
  {inspectionPhotos.length === 0 && (
    <span className="required">* At least 1 required</span>
  )}
</div>
```

### Photo Preview with Remove
```javascript
<div className="photo-gallery">
  {inspectionPhotos.map((photoUrl, idx) => (
    <div key={idx} className="photo-item">
      <img src={photoUrl} alt={`Inspection ${idx + 1}`} />
      <button onClick={() => {
        setInspectionPhotos(inspectionPhotos.filter((_, i) => i !== idx));
      }}>
        Remove
      </button>
    </div>
  ))}
</div>
```

---

## 7. Translation Updates (i18next)

Add new translation keys:

**en.json:**
```json
{
  "inspection_photos": "Inspection Photos",
  "verification_photos": "After-Repair Photos",
  "min_one_photo_required": "At least 1 photo is required",
  "max_five_photos": "Maximum 5 photos allowed",
  "verify_repair": "Verify Repair",
  "verification_passed": "Repair Verified - Passed",
  "verification_failed": "Repair Needs Rework",
  "add_photo": "Add Photo",
  "photo_count": "{{count}} / 5 photos"
}
```

**th.json:**
```json
{
  "inspection_photos": "รูปภาพการตรวจสอบ",
  "verification_photos": "รูปภาพหลังการซ่อม",
  "min_one_photo_required": "ต้องการรูปภาพอย่างน้อย 1 รูป",
  "max_five_photos": "อนุญาตสูงสุด 5 รูปเท่านั้น",
  "verify_repair": "ยืนยันการซ่อม",
  "verification_passed": "การซ่อมผ่าน",
  "verification_failed": "การซ่อมไม่ผ่าน ต้องทำใหม่",
  "add_photo": "เพิ่มรูปภาพ",
  "photo_count": "{{count}} / 5 รูป"
}
```

---

## 8. Testing Checklist

### Before Building
- [ ] Update all API calls to use `inspection_photos` instead of `before_photo/after_photo`
- [ ] Add timestamp overlay function
- [ ] Create VerifyRepair component
- [ ] Add photo validation (min 1, max 5)
- [ ] Update translations
- [ ] Test photo upload flow
- [ ] Test issue reporting flow
- [ ] Test verification flow

### After Building
- [ ] Test normal maintenance completion with 1-5 photos
- [ ] Test issue reporting with 1-5 photos
- [ ] Test verification page (only original reporter can access)
- [ ] Test photo validation (reject 0 photos, reject 6+ photos)
- [ ] Verify timestamps appear on photos
- [ ] Verify photos display correctly in manager view

---

## 9. Build Commands

Once frontend source code is available:

```bash
cd maintenance-react-dev

# Install dependencies
npm install

# Development mode (with hot reload)
npm run dev

# Production build
npm run build

# After build, restart bench
bench restart
```

---

## Summary of Changes

| Component | Change Type | Priority |
|-----------|-------------|----------|
| API Calls | Breaking Change | 🔴 Critical |
| Photo Upload | Enhancement | 🔴 Critical |
| VerifyRepair.jsx | New Component | 🔴 Critical |
| Photo Validation | New Feature | 🟡 Important |
| Translations | Enhancement | 🟢 Nice to Have |

---

## Status

**Backend:** ✅ Complete and Ready

**Frontend:** ⚠️ Needs Updates (source code not in repo)

**Action Required:** Obtain React source code to implement these changes

---

**Document Version:** 1.0.0
**Last Updated:** 2025-12-15
**Author:** TUB Suite Development Team
