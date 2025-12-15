import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import api from '../services/api'

export default function AssetSearch() {
  const [search, setSearch] = useState('')
  const [assets, setAssets] = useState([])
  const navigate = useNavigate()
  const { t } = useTranslation()

  const handleSearch = async () => {
    if (!search) return
    const results = await api.searchAssets(search)
    setAssets(results)
  }

  return (
    <div className="container">
      <div className="card">
        <h2>{t('search_asset')}</h2>
        <input 
          type="text"
          placeholder={t('asset_name')}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button className="primary" onClick={handleSearch}>
          {t('search_asset')}
        </button>
      </div>

      {assets.length > 0 && (
        <div className="task-list">
          {assets.map(asset => (
            <div key={asset.name} className="task-item" onClick={() => navigate(`/checklist/${asset.name}`)}>
              <h3>{asset.item_name}</h3>
              <p>{asset.name}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
