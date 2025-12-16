import config from '../config'
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import api from '../services/api'

export default function AssetSearch() {
  const [search, setSearch] = useState('')
  const [assets, setAssets] = useState([])
  const [loading, setLoading] = useState(false)
  const [userRoles, setUserRoles] = useState([])
  const [checkingAccess, setCheckingAccess] = useState(true)
  const navigate = useNavigate()
  const { t } = useTranslation()

  // Check access permission on mount
  useEffect(() => {
    checkAccess()
  }, [])

  const checkAccess = async () => {
    try {
      // Fetch user roles
      const response = await fetch('/api/method/tub_suite.api.maintenance.get_user_roles', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Frappe-CSRF-Token': window.csrf_token || ''
        }
      })
      const data = await response.json()
      const roles = data.message || []
      setUserRoles(roles)

      // Fetch portal settings
      const settings = await config.getSettings()

      // Check if user has permission
      const hasAccess = settings.ENABLE_SEARCH_FOR_ALL ||
                       settings.SEARCH_ALLOWED_ROLES.some(role => roles.includes(role))

      if (!hasAccess) {
        alert('Access Denied: Only Maintenance Managers can access search function')
        navigate('/')
        return
      }
    } catch (error) {
      console.error('Error checking access:', error)
      navigate('/')
    } finally {
      setCheckingAccess(false)
    }
  }

  const handleSearch = async () => {
    if (!search.trim()) return
    setLoading(true)
    try {
      const results = await api.searchAssets(search)
      setAssets(results.assets || [])
    } catch (error) {
      console.error('Search failed:', error)
      setAssets([])
    } finally {
      setLoading(false)
    }
  }

  // Show loading while checking access
  if (checkingAccess) {
    return (
      <div className="container">
        <p>Checking access...</p>
      </div>
    )
  }

  return (
    <div className="container">
      <button
        className="back-button"
        onClick={() => navigate('/')}
      >
        ← {t('back')}
      </button>

      <div className="search-card">
        <h2>{t('search_asset')}</h2>
        <div className="search-box">
          <input
            type="text"
            placeholder={t('search_placeholder')}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button
            className="primary"
            onClick={handleSearch}
            disabled={loading}
          >
            {loading ? t('searching') : t('search')}
          </button>
        </div>

        <div className="asset-grid">
          {assets.map((asset) => (
            <div
              key={asset.name}
              className="asset-card"
              onClick={() => navigate(`/checklist/${asset.name}`)}
            >
              <div className="asset-header">
                <h3>{asset.asset_name}</h3>
                <span className={`status-badge status-${asset.status?.toLowerCase() || 'draft'}`}>
                  {asset.status || 'Draft'}
                </span>
              </div>
              <div className="asset-details">
                <p className="asset-code">{asset.item_code}</p>
                <p className="location">📍 {asset.location}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
