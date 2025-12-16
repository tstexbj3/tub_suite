import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import api from '../services/api'
import PhotoUpload from '../components/PhotoUpload'

export default function VerifyRepair() {
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
    const data = await api.getRepairForVerification(repairName)
    setRepair(data)
  }

  const handleSubmit = async () => {
    if (photos.length === 0) {
      alert(t('min_photos_required'))
      return
    }

    if (!confirmed) {
      alert('Please confirm that you have checked the asset and it is working properly')
      return
    }

    await api.verifyRepair({
      repair_name: repairName,
      verification_photos: photos,
      verification_notes: notes,
      verification_status: 'Verified - Passed'
    })

    alert('Verification submitted! Asset will be restored to service.')
    navigate('/')
  }

  if (!repair) return <div>Loading...</div>

  return (
    <div className="container">
      <div className="page-header">
        <button className="back-button" onClick={() => navigate('/')}>
          ← {t('back')}
        </button>
        <h2>{t('verify_repair')}</h2>
      </div>

      <div className="card">
        <div className="info-section-large">
          <div className="info-row">
            <span className="info-label">Asset:</span>
            <span className="info-value">{repair.repair?.asset_name || repair.repair?.asset}</span>
          </div>
          <div className="info-row">
            <span className="info-label">Location:</span>
            <span className="info-value">{repair.repair?.location || 'N/A'}</span>
          </div>
          <div className="info-row">
            <span className="info-label">Issue:</span>
            <span className="info-value">{repair.repair?.description}</span>
          </div>
          {repair.repair?.actions_performed && (
            <div className="info-row">
              <span className="info-label">Actions Performed:</span>
              <span className="info-value">{repair.repair.actions_performed}</span>
            </div>
          )}
        </div>

        <h3>{t('verification_photos')}</h3>
        <PhotoUpload
          photos={photos}
          setPhotos={setPhotos}
          activityType="VERIFY"
          assetName={repair.repair?.asset || 'ASSET'}
        />

        <label className="form-label">Additional Notes (Optional)</label>
        <textarea
          className="verify-textarea"
          placeholder="Any additional comments or observations..."
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
                <p>การยืนยันการตรวจสอบนี้ คุณรับทราบและยอมรับว่า:</p>
                <ul>
                  <li>คุณได้ตรวจสอบอุปกรณ์ด้วยตนเอง</li>
                  <li>งานซ่อมแซมเสร็จสมบูรณ์และถูกต้อง</li>
                  <li>อุปกรณ์ทำงานได้ตามปกติ</li>
                  <li>
                    <strong>
                      หากปัญหาเดิมเกิดขึ้นอีกภายใน 7 วัน คุณจะต้องรับผิดชอบในการรายงานปัญหาอีกครั้ง
                      และอาจถูกตั้งคำถามถึงความรอบคอบในการตรวจสอบครั้งนี้
                    </strong>
                  </li>
                </ul>
              </>
            ) : (
              <>
                <p>By confirming this verification, you acknowledge that:</p>
                <ul>
                  <li>You have personally inspected the asset</li>
                  <li>The repair work has been completed satisfactorily</li>
                  <li>The asset is functioning properly</li>
                  <li>
                    <strong>
                      If the same issue occurs again within 7 days, you will be responsible
                      for re-reporting it and your verification thoroughness may be questioned
                    </strong>
                  </li>
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
                ? 'ฉันยืนยันว่าได้ตรวจสอบอุปกรณ์แล้วและทำงานได้ตามปกติ ฉันเข้าใจความรับผิดชอบของฉันหากปัญหาเกิดขึ้นอีกภายใน 7 วัน'
                : 'I confirm that I have checked the asset and it is working properly. I understand my responsibility if the issue recurs within 7 days.'
              }
            </span>
          </label>
        </div>

        <button
          className="primary"
          onClick={handleSubmit}
          disabled={photos.length === 0 || !confirmed}
        >
          {i18n.language === 'th' ? '✓ ยืนยันการตรวจสอบ' : '✓ Confirm Verification'}
        </button>
      </div>
    </div>
  )
}
