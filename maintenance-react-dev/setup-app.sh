#!/bin/bash
# TUB Suite React App Setup Script

cd "$(dirname "$0")"

echo "Creating React app structure..."

# i18n configuration
cat > src/i18n.js << 'EOF'
import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import en from './locales/en.json'
import th from './locales/th.json'

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    th: { translation: th }
  },
  lng: 'en',
  fallbackLng: 'en',
  interpolation: { escapeValue: false }
})

export default i18n
EOF

# English translations
cat > src/locales/en.json << 'EOF'
{
  "app_title": "TUB Maintenance Portal",
  "scan_qr": "Scan QR Code",
  "search_asset": "Search Asset",
  "asset_name": "Asset Name",
  "maintenance_tasks": "Maintenance Tasks",
  "complete_task": "Complete Task",
  "report_issue": "Report Issue",
  "take_photo": "Take Photo",
  "inspection_photos": "Inspection Photos",
  "issue_photos": "Issue Photos",
  "verification_photos": "After-Repair Photos",
  "min_photos_required": "At least 1 photo required",
  "max_photos": "Maximum 5 photos",
  "verify_repair": "Verify Repair",
  "verified_passed": "Verified - Passed",
  "verified_failed": "Verified - Failed",
  "submit": "Submit",
  "cancel": "Cancel",
  "notes": "Notes",
  "issue_description": "Issue Description"
}
EOF

# Thai translations
cat > src/locales/th.json << 'EOF'
{
  "app_title": "ระบบบำรุงรักษา TUB",
  "scan_qr": "สแกน QR Code",
  "search_asset": "ค้นหาสินทรัพย์",
  "asset_name": "ชื่อสินทรัพย์",
  "maintenance_tasks": "รายการบำรุงรักษา",
  "complete_task": "ทำงานเสร็จสิ้น",
  "report_issue": "รายงานปัญหา",
  "take_photo": "ถ่ายรูป",
  "inspection_photos": "รูปภาพการตรวจสอบ",
  "issue_photos": "รูปภาพปัญหา",
  "verification_photos": "รูปภาพหลังการซ่อม",
  "min_photos_required": "ต้องมีอย่างน้อย 1 รูป",
  "max_photos": "สูงสุด 5 รูป",
  "verify_repair": "ยืนยันการซ่อม",
  "verified_passed": "ยืนยัน - ผ่าน",
  "verified_failed": "ยืนยัน - ไม่ผ่าน",
  "submit": "ส่ง",
  "cancel": "ยกเลิก",
  "notes": "บันทึก",
  "issue_description": "รายละเอียดปัญหา"
}
EOF

# CSS
cat > src/index.css << 'EOF'
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans Thai', sans-serif;
  background: #f5f5f5;
}

.app {
  min-height: 100vh;
}

header {
  background: #2196F3;
  color: white;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

header h1 {
  font-size: 1.5rem;
}

.lang-toggle {
  background: white;
  color: #2196F3;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
}

.container {
  padding: 1rem;
  max-width: 800px;
  margin: 0 auto;
}

button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
}

button.primary {
  background: #2196F3;
  color: white;
}

button.primary:hover {
  background: #1976D2;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

input, textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  margin: 0.5rem 0;
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.photo-item {
  position: relative;
}

.photo-item img {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 4px;
}

.photo-item button {
  position: absolute;
  top: 5px;
  right: 5px;
  background: red;
  color: white;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.task-list {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  margin: 1rem 0;
}

.task-item {
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.task-item:last-child {
  border-bottom: none;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  margin: 1rem 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
EOF

echo "✅ All configuration files created!"
echo "Next: Creating page components..."

