# Photo Upload System - Timestamp & Naming Convention

Complete guide for photo upload, timestamp embedding, and structured file naming in TUB Suite.

---

## Overview

**Requirements:**
1. ✅ Photos required for ALL maintenance activities (with/without issues)
2. ✅ Timestamp embedded in every photo (proof of presence)
3. ✅ Structured file naming (easy identification and ordering)
4. ✅ Photo metadata preserved (datetime, user, asset)

---

## Photo Requirements by Workflow

### Path A: Normal Completion (No Issues)

**Photos Required:**
- **Minimum:** 1 photo
- **Maximum:** 5 photos
- **Type:** Inspection photos (general condition of asset)

**Purpose:**
- Prove inspector was physically at asset
- Document asset condition
- Timestamp verifies inspection time

### Path B: Issue Reported

**Photos Required:**
- **Issue Photos:** 1-5 photos showing the problem
- **Verification Photos:** 1-5 photos after engineer fixes (taken by inspector)

**Purpose:**
- Document problem clearly
- Show repair work completed
- Compare before/after

---

## Photo Naming Convention

### Format Structure

```
{asset_code}_{activity}_{timestamp}_{sequence}_{user_id}.jpg

Example:
PUMP-001_INSP_20251215_143052_1_INSP001.jpg
PUMP-001_ISSUE_20251215_143105_1_INSP001.jpg
PUMP-001_VERIFY_20251215_173042_1_INSP001.jpg
```

### Components

| Component | Description | Example |
|-----------|-------------|---------|
| `{asset_code}` | Asset item code or name | `PUMP-001` |
| `{activity}` | Activity type | `INSP`, `ISSUE`, `VERIFY` |
| `{timestamp}` | YYYYMMDD_HHMMSS | `20251215_143052` |
| `{sequence}` | Photo number (1-5) | `1`, `2`, `3` |
| `{user_id}` | User short ID | `INSP001`, `ENG002` |

### Activity Codes

| Code | Activity | When Used |
|------|----------|-----------|
| `INSP` | Normal Inspection | Path A - No issues found |
| `ISSUE` | Issue Reported | Path B - Problem photos |
| `VERIFY` | Repair Verification | Path B - After-repair photos |
| `REPAIR` | Repair Work | Engineer's work-in-progress photos (optional) |

---

## Implementation

### Backend: File Naming Function

Create in `tub_suite/api/file_utils.py`:

```python
import frappe
from frappe.utils import now_datetime, cstr
import re

def generate_photo_filename(asset_name, activity_type, sequence, user=None):
    """
    Generate structured filename for maintenance photos

    Args:
        asset_name: Asset name/code (e.g., "ASSET-00001")
        activity_type: "INSP", "ISSUE", "VERIFY", "REPAIR"
        sequence: Photo number (1-5)
        user: User email (defaults to current user)

    Returns:
        str: Formatted filename
    """
    if not user:
        user = frappe.session.user

    # Get asset item code (cleaner than full name)
    asset = frappe.get_cached_value("Asset", asset_name, "item_code")
    if not asset:
        asset = asset_name

    # Clean asset code (remove special chars)
    asset_clean = re.sub(r'[^A-Z0-9]', '', asset.upper())

    # Generate timestamp
    timestamp = now_datetime().strftime("%Y%m%d_%H%M%S")

    # Get user short ID (first 8 chars of email or custom ID)
    user_short = user.split("@")[0].upper()[:8]

    # Build filename
    filename = f"{asset_clean}_{activity_type}_{timestamp}_{sequence}_{user_short}.jpg"

    return filename


def attach_photo_with_metadata(doctype, docname, file_content, asset_name,
                                activity_type, sequence, metadata=None):
    """
    Upload photo with structured naming and metadata

    Args:
        doctype: Parent doctype (e.g., "Asset Maintenance Log")
        docname: Parent document name
        file_content: Base64 or file data
        asset_name: Asset being photographed
        activity_type: INSP/ISSUE/VERIFY/REPAIR
        sequence: Photo number
        metadata: Dict with timestamp, gps, etc.

    Returns:
        str: File URL
    """
    from frappe.utils.file_manager import save_file
    import json

    # Generate filename
    filename = generate_photo_filename(asset_name, activity_type, sequence)

    # Add metadata to description
    description = json.dumps({
        "asset": asset_name,
        "activity": activity_type,
        "sequence": sequence,
        "user": frappe.session.user,
        "timestamp": cstr(now_datetime()),
        "metadata": metadata or {}
    })

    # Save file
    file_doc = save_file(
        fname=filename,
        content=file_content,
        dt=doctype,
        dn=docname,
        is_private=0,
        decode=True  # If base64
    )

    # Update file description with metadata
    frappe.db.set_value("File", file_doc.name, "description", description)

    return file_doc.file_url
```

---

### Frontend: Photo Capture with Timestamp

Create in React frontend:

```javascript
// src/services/photoCapture.js

export const capturePhotoWithTimestamp = async (activityType, sequence) => {
  try {
    // Force camera capture (not gallery upload)
    const photo = await new Promise((resolve, reject) => {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = 'image/*';
      input.capture = 'environment'; // Use back camera

      input.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
          resolve(file);
        } else {
          reject(new Error('No file selected'));
        }
      };

      input.click();
    });

    // Read file as base64
    const reader = new FileReader();
    const base64 = await new Promise((resolve, reject) => {
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(photo);
    });

    // Get current timestamp
    const timestamp = new Date().toISOString();

    // Get geolocation (optional)
    let gps = null;
    if (navigator.geolocation) {
      try {
        const position = await new Promise((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject, {
            enableHighAccuracy: true,
            timeout: 5000,
            maximumAge: 0
          });
        });

        gps = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          timestamp: position.timestamp
        };
      } catch (gpsError) {
        console.warn('GPS not available:', gpsError);
      }
    }

    return {
      data: base64,
      filename: photo.name,
      timestamp,
      gps,
      activityType,
      sequence,
      size: photo.size,
      type: photo.type
    };
  } catch (error) {
    console.error('Photo capture error:', error);
    throw error;
  }
};

// Upload photo with metadata
export const uploadPhotoWithMetadata = async (assetName, photo, doctype, docname) => {
  const response = await frappe.call({
    method: 'tub_suite.api.file_utils.attach_photo_with_metadata',
    args: {
      doctype,
      docname,
      file_content: photo.data,
      asset_name: assetName,
      activity_type: photo.activityType,
      sequence: photo.sequence,
      metadata: {
        timestamp: photo.timestamp,
        gps: photo.gps,
        filename_original: photo.filename,
        size: photo.size
      }
    }
  });

  return response.message; // Returns file URL
};
```

---

### React Component: PhotoUploader

```javascript
// src/components/PhotoUploader.jsx

import React, { useState } from 'react';
import { Camera, X, Clock } from 'lucide-react';
import { capturePhotoWithTimestamp, uploadPhotoWithMetadata } from '../services/photoCapture';

const PhotoUploader = ({ assetName, activityType, maxPhotos = 5, required = false }) => {
  const [photos, setPhotos] = useState([]);
  const [uploading, setUploading] = useState(false);

  const handleCapture = async () => {
    if (photos.length >= maxPhotos) {
      alert(`Maximum ${maxPhotos} photos allowed`);
      return;
    }

    try {
      const sequence = photos.length + 1;
      const photo = await capturePhotoWithTimestamp(activityType, sequence);

      setPhotos([...photos, photo]);
    } catch (error) {
      console.error('Failed to capture photo:', error);
      alert('Failed to capture photo. Please try again.');
    }
  };

  const removePhoto = (index) => {
    setPhotos(photos.filter((_, i) => i !== index));
  };

  return (
    <div className="photo-uploader">
      <div className="photo-grid">
        {photos.map((photo, index) => (
          <div key={index} className="photo-preview">
            <img src={photo.data} alt={`Photo ${index + 1}`} />
            <button
              className="remove-btn"
              onClick={() => removePhoto(index)}
            >
              <X size={16} />
            </button>
            <div className="photo-metadata">
              <Clock size={12} />
              <span>{new Date(photo.timestamp).toLocaleString()}</span>
            </div>
          </div>
        ))}
      </div>

      {photos.length < maxPhotos && (
        <button
          className="capture-btn"
          onClick={handleCapture}
          disabled={uploading}
        >
          <Camera size={20} />
          Take Photo ({photos.length}/{maxPhotos})
        </button>
      )}

      {required && photos.length === 0 && (
        <p className="error-text">At least 1 photo is required</p>
      )}
    </div>
  );
};

export default PhotoUploader;
```

---

## Photo Display & Viewing

### Backend: Get Photos by Activity

```python
@frappe.whitelist()
def get_maintenance_photos(doctype, docname, activity_type=None):
    """
    Get all photos for a maintenance record, grouped by activity

    Args:
        doctype: Asset Maintenance Log or Asset Repair
        docname: Document name
        activity_type: Filter by INSP/ISSUE/VERIFY (optional)

    Returns:
        dict: Photos grouped by activity type
    """
    import json

    filters = {
        "attached_to_doctype": doctype,
        "attached_to_name": docname,
        "file_url": ["like", "%.jpg%"]
    }

    files = frappe.get_all("File",
        filters=filters,
        fields=["name", "file_name", "file_url", "description", "creation"],
        order_by="creation asc"
    )

    photos_by_activity = {}

    for file in files:
        try:
            # Parse metadata from description
            metadata = json.loads(file.description or "{}")
            activity = metadata.get("activity", "UNKNOWN")

            if activity_type and activity != activity_type:
                continue

            if activity not in photos_by_activity:
                photos_by_activity[activity] = []

            photos_by_activity[activity].append({
                "file_name": file.file_name,
                "file_url": file.file_url,
                "sequence": metadata.get("sequence"),
                "user": metadata.get("user"),
                "timestamp": metadata.get("timestamp"),
                "gps": metadata.get("metadata", {}).get("gps"),
                "creation": file.creation
            })
        except:
            # Handle photos without metadata
            if "UNKNOWN" not in photos_by_activity:
                photos_by_activity["UNKNOWN"] = []
            photos_by_activity["UNKNOWN"].append({
                "file_name": file.file_name,
                "file_url": file.file_url
            })

    # Sort photos by sequence within each activity
    for activity in photos_by_activity:
        photos_by_activity[activity].sort(key=lambda x: x.get("sequence", 0))

    return photos_by_activity
```

---

### Frontend: Photo Gallery

```javascript
// src/components/PhotoGallery.jsx

import React, { useState, useEffect } from 'react';
import { Clock, MapPin, User } from 'lucide-react';

const PhotoGallery = ({ doctype, docname, showMetadata = true }) => {
  const [photos, setPhotos] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPhotos();
  }, [doctype, docname]);

  const loadPhotos = async () => {
    try {
      const response = await frappe.call({
        method: 'tub_suite.api.file_utils.get_maintenance_photos',
        args: { doctype, docname }
      });
      setPhotos(response.message);
    } catch (error) {
      console.error('Failed to load photos:', error);
    } finally {
      setLoading(false);
    }
  };

  const activityLabels = {
    'INSP': 'Inspection Photos',
    'ISSUE': 'Issue Photos',
    'VERIFY': 'Verification Photos',
    'REPAIR': 'Repair Work Photos'
  };

  if (loading) return <div>Loading photos...</div>;

  return (
    <div className="photo-gallery">
      {Object.entries(photos).map(([activity, photoList]) => (
        <div key={activity} className="activity-section">
          <h3>{activityLabels[activity] || activity}</h3>

          <div className="photo-grid">
            {photoList.map((photo, index) => (
              <div key={index} className="photo-card">
                <img
                  src={photo.file_url}
                  alt={photo.file_name}
                  onClick={() => window.open(photo.file_url, '_blank')}
                />

                {showMetadata && (
                  <div className="photo-info">
                    {photo.timestamp && (
                      <div className="metadata-item">
                        <Clock size={14} />
                        <span>{new Date(photo.timestamp).toLocaleString()}</span>
                      </div>
                    )}

                    {photo.user && (
                      <div className="metadata-item">
                        <User size={14} />
                        <span>{photo.user}</span>
                      </div>
                    )}

                    {photo.gps && (
                      <div className="metadata-item">
                        <MapPin size={14} />
                        <span>
                          {photo.gps.latitude.toFixed(6)},
                          {photo.gps.longitude.toFixed(6)}
                        </span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}

      {Object.keys(photos).length === 0 && (
        <p className="no-photos">No photos uploaded yet</p>
      )}
    </div>
  );
};

export default PhotoGallery;
```

---

## File Storage & Organization

### Directory Structure

```
sites/[site-name]/public/files/
├── 2025/
│   └── 12/
│       ├── PUMP-001_INSP_20251215_143052_1_INSP001.jpg
│       ├── PUMP-001_INSP_20251215_143052_2_INSP001.jpg
│       ├── PUMP-001_ISSUE_20251215_143105_1_INSP001.jpg
│       └── PUMP-001_VERIFY_20251215_173042_1_INSP001.jpg
```

Frappe automatically organizes by year/month.

### Database Records

**File DocType:**
```json
{
  "file_name": "PUMP-001_INSP_20251215_143052_1_INSP001.jpg",
  "file_url": "/files/2025/12/PUMP-001_INSP_20251215_143052_1_INSP001.jpg",
  "attached_to_doctype": "Asset Maintenance Log",
  "attached_to_name": "MLOG-00001",
  "description": "{\"asset\":\"PUMP-001\",\"activity\":\"INSP\",\"sequence\":1,\"user\":\"inspector@example.com\",\"timestamp\":\"2025-12-15T14:30:52\",\"metadata\":{\"gps\":{\"latitude\":13.7563,\"longitude\":100.5018}}}",
  "is_private": 0
}
```

---

## Validation & Security

### Backend Validation

```python
def validate_photo_upload(photo_count, activity_type, has_issue):
    """Validate photo requirements before saving"""

    if activity_type == "INSP" and photo_count < 1:
        frappe.throw("At least 1 inspection photo is required")

    if activity_type == "ISSUE" and photo_count < 1:
        frappe.throw("At least 1 issue photo is required when reporting problems")

    if activity_type == "VERIFY" and photo_count < 1:
        frappe.throw("At least 1 verification photo is required")

    if photo_count > 5:
        frappe.throw("Maximum 5 photos allowed per activity")

    return True
```

---

## Manager Dashboard: Photo Audit

```python
@frappe.whitelist()
def get_photos_without_timestamp():
    """Find maintenance records missing photo timestamps (suspicious)"""

    sql = """
        SELECT
            ml.name as log_name,
            ml.asset_name,
            ml.owner as inspector,
            ml.completion_date,
            COUNT(f.name) as photo_count
        FROM `tabAsset Maintenance Log` ml
        LEFT JOIN `tabFile` f ON (
            f.attached_to_doctype = 'Asset Maintenance Log'
            AND f.attached_to_name = ml.name
        )
        WHERE ml.completion_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY ml.name
        HAVING photo_count = 0
        ORDER BY ml.completion_date DESC
    """

    return frappe.db.sql(sql, as_dict=True)
```

---

## Quick Reference

### Photo Requirements

| Workflow | Activity | Min Photos | Max Photos | Required |
|----------|----------|-----------|-----------|----------|
| Normal Completion | INSP | 1 | 5 | ✅ Yes |
| Issue Reported | ISSUE | 1 | 5 | ✅ Yes |
| Repair Verification | VERIFY | 1 | 5 | ✅ Yes |

### Filename Pattern

```
{ASSET}_{ACTIVITY}_{YYYYMMDD}_{HHMMSS}_{SEQ}_{USER}.jpg
```

### Activity Codes

- `INSP` = Inspection
- `ISSUE` = Problem Report
- `VERIFY` = Repair Verification
- `REPAIR` = Engineer Work Photos

---

**Last Updated:** 2025-12-15
**TUB Suite Version:** 2.0.0
