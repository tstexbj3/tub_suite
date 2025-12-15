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
