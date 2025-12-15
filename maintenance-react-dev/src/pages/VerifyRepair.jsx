import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import api from '../services/api'
import PhotoUpload from '../components/PhotoUpload'

export default function VerifyRepair() {
  const { repairName } = useParams()
  const [repair, setRepair] = useState(null)
  const [photos, setPhotos] = useState([])
  const [notes, setNotes] = useState('')
  const [status, setStatus] = useState('Verified - Passed')
  const { t } = useTranslation()

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

    await api.verifyRepair({
      repair_name: repairName,
      verification_photos: photos,
      verification_notes: notes,
      verification_status: status
    })

    alert('Verification submitted!')
  }

  if (!repair) return <div>Loading...</div>

  return (
    <div className="container">
      <div className="card">
        <h2>{t('verify_repair')}</h2>
        <p><strong>Asset:</strong> {repair.asset}</p>
        <p><strong>Issue:</strong> {repair.failure_description}</p>

        <h3>{t('verification_photos')}</h3>
        <PhotoUpload 
          photos={photos} 
          setPhotos={setPhotos}
          activityType="VERIFY"
        />

        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="Verified - Passed">{t('verified_passed')}</option>
          <option value="Verified - Failed">{t('verified_failed')}</option>
        </select>

        <textarea
          placeholder={t('notes')}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />

        <button className="primary" onClick={handleSubmit} disabled={photos.length === 0}>
          {t('submit')}
        </button>
      </div>
    </div>
  )
}
