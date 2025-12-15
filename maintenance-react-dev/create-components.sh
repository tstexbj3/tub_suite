#!/bin/bash

# QR Scanner Component
cat > src/components/QRScanner.jsx << 'EOF'
import { useEffect, useRef } from 'react'
import { Html5Qrcode } from 'html5-qrcode'

export default function QRScanner({ onScan }) {
  const qrRef = useRef(null)

  useEffect(() => {
    const scanner = new Html5Qrcode("qr-reader")
    
    scanner.start(
      { facingMode: "environment" },
      { fps: 10, qrbox: 250 },
      (decodedText) => {
        const assetName = extractAssetName(decodedText)
        if (assetName) {
          scanner.stop()
          onScan(assetName)
        }
      }
    )

    return () => {
      scanner.stop().catch(() => {})
    }
  }, [onScan])

  const extractAssetName = (url) => {
    const match = url.match(/asset[=/]([^&\/]+)/)
    return match ? match[1] : url
  }

  return <div id="qr-reader" style={{ width: '100%' }}></div>
}
EOF

# Photo Upload Component with Timestamp
cat > src/components/PhotoUpload.jsx << 'EOF'
import { useTranslation } from 'react-i18next'
import { addTimestampToPhoto, uploadPhoto } from '../services/photoService'

export default function PhotoUpload({ photos, setPhotos, activityType }) {
  const { t } = useTranslation()

  const handlePhotoCapture = async (e) => {
    if (photos.length >= 5) {
      alert(t('max_photos'))
      return
    }

    const file = e.target.files[0]
    if (!file) return

    // Add timestamp overlay
    const photoWithTimestamp = await addTimestampToPhoto(file)
    
    // Upload to Frappe
    const url = await uploadPhoto(photoWithTimestamp)
    
    setPhotos([...photos, url])
  }

  const removePhoto = (index) => {
    setPhotos(photos.filter((_, i) => i !== index))
  }

  return (
    <div>
      <input 
        type="file" 
        accept="image/*" 
        capture="environment"
        onChange={handlePhotoCapture}
        disabled={photos.length >= 5}
      />
      
      <p>{photos.length} / 5 {t('inspection_photos')}</p>
      
      <div className="photo-grid">
        {photos.map((url, index) => (
          <div key={index} className="photo-item">
            <img src={url} alt={`Photo ${index + 1}`} />
            <button onClick={() => removePhoto(index)}>×</button>
          </div>
        ))}
      </div>
    </div>
  )
}
EOF

# API Service
cat > src/services/api.js << 'EOF'
const API_BASE = '/api/method/tub_suite.api'

const callAPI = async (method, args = {}) => {
  const response = await fetch(`/api/method/${method}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Frappe-CSRF-Token': window.csrf_token || ''
    },
    body: JSON.stringify(args)
  })
  
  const data = await response.json()
  if (data.exc) throw new Error(data.exc)
  return data.message
}

export default {
  searchAssets: (query) => 
    callAPI('asset.search_assets', { query }),

  getMaintenanceTasks: (assetName) => 
    callAPI('maintenance.get_maintenance_by_asset', { asset_name: assetName }),

  submitTask: (params) => 
    callAPI('maintenance.submit_maintenance_task', params),

  getRepairForVerification: (repairName) => 
    callAPI('maintenance.get_repair_for_verification', { repair_name: repairName }),

  verifyRepair: (params) => 
    callAPI('maintenance.verify_repair_completion', params)
}
EOF

# Photo Service with Timestamp
cat > src/services/photoService.js << 'EOF'
export const addTimestampToPhoto = (file) => {
  return new Promise((resolve) => {
    const img = new Image()
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')

    img.onload = () => {
      canvas.width = img.width
      canvas.height = img.height

      // Draw photo
      ctx.drawImage(img, 0, 0)

      // Add timestamp
      const timestamp = new Date().toLocaleString('th-TH', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })

      ctx.font = 'bold 24px Arial'
      ctx.fillStyle = 'rgba(0, 0, 0, 0.7)'
      ctx.fillRect(canvas.width - 220, canvas.height - 40, 210, 35)
      ctx.fillStyle = 'white'
      ctx.fillText(timestamp, canvas.width - 215, canvas.height - 15)

      canvas.toBlob((blob) => {
        resolve(new File([blob], file.name, { type: 'image/jpeg' }))
      }, 'image/jpeg', 0.95)
    }

    img.src = URL.createObjectURL(file)
  })
}

export const uploadPhoto = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('is_private', 0)

  const response = await fetch('/api/method/upload_file', {
    method: 'POST',
    headers: {
      'X-Frappe-CSRF-Token': window.csrf_token || ''
    },
    body: formData
  })

  const data = await response.json()
  return data.message.file_url
}
EOF

echo "✅ All components and services created!"

