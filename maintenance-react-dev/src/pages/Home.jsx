import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import QRScanner from '../components/QRScanner'

export default function Home() {
  const navigate = useNavigate()
  const { t } = useTranslation()

  const handleQRScan = (assetName) => {
    navigate(`/checklist/${assetName}`)
  }

  return (
    <div className="container">
      <div className="card">
        <h2>{t('scan_qr')}</h2>
        <QRScanner onScan={handleQRScan} />
      </div>
      
      <div className="card">
        <h2>{t('search_asset')}</h2>
        <button 
          className="primary" 
          onClick={() => navigate('/search')}
          style={{width: '100%'}}
        >
          {t('search_asset')}
        </button>
      </div>
    </div>
  )
}
