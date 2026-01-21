import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import PhotoUpload from '../components/PhotoUpload'

export default function ConfirmRepair() {
  const { repairName } = useParams()
  const navigate = useNavigate()
  const [repair, setRepair] = useState(null)
  const [photos, setPhotos] = useState([])
  const [notes, setNotes] = useState('')
  const [confirmed, setConfirmed] = useState(false)
  const { t, i18n } = useTranslation()

  useEffect(() => {
    loadRepair()
  }, [repairName])

  const loadRepair = async () => {
    try {
      const response = await fetch(`/api/method/frappe.client.get?doctype=Asset Repair&name=${repairName}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Frappe-CSRF-Token': window.csrf_token || ''
        }
      })
      const data = await response.json()
      setRepair(data.message)
    } catch (error) {
      console.error('Error loading repair:', error)
      alert('Error loading repair details')
      navigate('/')
    }
  }

  const handleSubmit = async () => {
    if (!confirmed) {
      alert(i18n.language === 'th'
        ? 'กรุณายืนยันว่าคุณได้ตรวจสอบการซ่อมแล้ว'
        : 'Please confirm that you have verified the repair')
      return
    }

    try {
      const response = await fetch('/api/method/tub_suite.api.maintenance.submit_reporter_confirmation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Frappe-CSRF-Token': window.csrf_token || ''
        },
        body: JSON.stringify({
          repair_name: repairName,
          confirmation_photos: JSON.stringify(photos),
          confirmation_notes: notes
        })
      })

      const data = await response.json()

      if (data.message && data.message.success) {
        alert(i18n.language === 'th'
          ? 'ยืนยันการซ่อมเรียบร้อยแล้ว'
          : 'Repair confirmation submitted successfully!')
        navigate('/')
      } else {
        throw new Error(data.exception || 'Submission failed')
      }
    } catch (error) {
      console.error('Error submitting confirmation:', error)
      alert(i18n.language === 'th'
        ? 'เกิดข้อผิดพลาดในการส่งข้อมูล: ' + error.message
        : 'Error submitting confirmation: ' + error.message)
    }
  }

  if (!repair) return <div className="container"><div>Loading...</div></div>

  return (
    <div className="container">
      <div className="page-header">
        <button className="back-button" onClick={() => navigate('/')}>
          ← {t('back')}
        </button>
        <h2>{i18n.language === 'th' ? 'ยืนยันการซ่อม' : 'Confirm Repair'}</h2>
      </div>

      <div className="card">
        <div className="info-section-large">
          <div className="info-row">
            <span className="info-label">Asset:</span>
            <span className="info-value">{repair.asset_name || repair.asset}</span>
          </div>
          {repair.location && (
            <div className="info-row">
              <span className="info-label">Location:</span>
              <span className="info-value">{repair.location}</span>
            </div>
          )}
          <div className="info-row">
            <span className="info-label">Issue:</span>
            <span className="info-value">{repair.description}</span>
          </div>
          {repair.repair_result_status && (
            <div className="info-row">
              <span className="info-label">Repair Result:</span>
              <span className="info-value">{repair.repair_result_status}</span>
            </div>
          )}
        </div>

        <h3>{i18n.language === 'th' ? 'รูปถ่ายยืนยัน (ถ้ามี)' : 'Confirmation Photo (Optional)'}</h3>
        <PhotoUpload
          photos={photos}
          setPhotos={setPhotos}
          activityType="CONFIRM"
          assetName={repair.asset || 'ASSET'}
          maxPhotos={1}
        />

        <label className="form-label">{i18n.language === 'th' ? 'หมายเหตุเพิ่มเติม (ถ้ามี)' : 'Additional Notes (Optional)'}</label>
        <textarea
          className="verify-textarea"
          placeholder={i18n.language === 'th' ? 'ความคิดเห็นหรือข้อสังเกต...' : 'Any comments or observations...'}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows="4"
        />

        <div className="confirmation-section">
          <div className="disclaimer-box">
            <h4>
              ⚠️ {i18n.language === 'th' ? 'ประกาศสำคัญ' : 'Important Notice'}
            </h4>
            {i18n.language === 'th' ? (
              <>
                <p>การยืนยันนี้ คุณรับทราบและยอมรับว่า:</p>
                <ul>
                  <li>คุณได้ตรวจสอบการซ่อมด้วยตนเอง</li>
                  <li>งานซ่อมแซมเสร็จสมบูรณ์และถูกต้อง</li>
                  <li>อุปกรณ์ทำงานได้ตามปกติ</li>
                </ul>
              </>
            ) : (
              <>
                <p>By confirming, you acknowledge that:</p>
                <ul>
                  <li>You have personally verified the repair</li>
                  <li>The repair work has been completed satisfactorily</li>
                  <li>The asset is functioning properly</li>
                </ul>
              </>
            )}
          </div>

          <label className="confirmation-checkbox">
            <input
              type="checkbox"
              checked={confirmed}
              onChange={(e) => setConfirmed(e.target.checked)}
            />
            <span>
              {i18n.language === 'th'
                ? 'ฉันยืนยันว่าได้ตรวจสอบการซ่อมแล้วและอุปกรณ์ทำงานได้ตามปกติ'
                : 'I confirm that I have verified the repair and the asset is working properly'
              }
            </span>
          </label>
        </div>

        <button
          className="primary"
          onClick={handleSubmit}
          disabled={!confirmed}
        >
          {i18n.language === 'th' ? '✓ ยืนยันการซ่อม' : '✓ Confirm Repair'}
        </button>
      </div>
    </div>
  )
}
