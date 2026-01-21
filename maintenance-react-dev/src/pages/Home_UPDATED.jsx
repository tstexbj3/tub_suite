import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useState, useEffect } from 'react'
import QRScanner from '../components/QRScanner'
import config from '../config'

export default function Home() {
  const navigate = useNavigate()
  const { t, i18n } = useTranslation()
  const [pendingVerifications, setPendingVerifications] = useState([])
  const [finishedRepairs, setFinishedRepairs] = useState([])
  const [loading, setLoading] = useState(true)
  const [userRoles, setUserRoles] = useState([])
  const [showSearch, setShowSearch] = useState(false)

  const handleQRScan = (assetName) => {
    navigate(`/checklist/${assetName}`)
  }

  // Fetch user roles and settings on mount
  useEffect(() => {
    fetchUserRolesAndSettings()
    fetchPendingVerifications()
    fetchFinishedRepairs()
  }, [])

  const fetchUserRolesAndSettings = async () => {
    try {
      // Fetch user roles
      const rolesResponse = await fetch('/api/method/tub_suite.api.maintenance.get_user_roles', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Frappe-CSRF-Token': window.csrf_token || ''
        }
      })
      const rolesData = await rolesResponse.json()
      const roles = rolesData.message || []
      setUserRoles(roles)

      // Fetch portal settings
      const settings = await config.getSettings()

      // Determine if user can see search
      const canSeeSearch = settings.ENABLE_SEARCH_FOR_ALL ||
                          settings.SEARCH_ALLOWED_ROLES.some(role => roles.includes(role))

      setShowSearch(canSeeSearch)

      console.log('User roles:', roles)
      console.log('Portal settings:', settings)
      console.log('Can see search:', canSeeSearch)
    } catch (error) {
      console.error('Error fetching user roles and settings:', error)
      setUserRoles([])
      setShowSearch(false)
    }
  }

  const fetchPendingVerifications = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/method/tub_suite.api.maintenance.get_repairs_needing_verification', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Frappe-CSRF-Token': window.csrf_token || ''
        }
      })
      const data = await response.json()
      setPendingVerifications(data.message || [])
    } catch (error) {
      console.error('Error fetching pending verifications:', error)
      setPendingVerifications([])
    } finally {
      setLoading(false)
    }
  }

  const fetchFinishedRepairs = async () => {
    try {
      const response = await fetch('/api/method/tub_suite.api.maintenance.get_repairs_for_confirmation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Frappe-CSRF-Token': window.csrf_token || ''
        }
      })
      const data = await response.json()
      setFinishedRepairs(data.message || [])
    } catch (error) {
      console.error('Error fetching finished repairs:', error)
      setFinishedRepairs([])
    }
  }

  return (
    <div className="container">
      <div className="welcome-section">
        <h1 className="welcome-title">🔧 TUB Maintenance Portal</h1>
        <p className="welcome-subtitle">
          {i18n.language === 'th' ? 'เลือกตัวเลือกเพื่อเริ่มต้น' : 'Select an option to get started'}
        </p>
      </div>

      {/* Pending Verifications Alert */}
      {!loading && pendingVerifications.length > 0 && (
        <div className="verification-alert">
          <div className="verification-alert-header">
            <span className="verification-badge">{pendingVerifications.length}</span>
            <h3>
              ⚠️ {i18n.language === 'th' ? 'รอการตรวจสอบ' : 'Pending Verifications'}
            </h3>
          </div>
          <p>
            {i18n.language === 'th'
              ? `คุณมี ${pendingVerifications.length} งานซ่อมที่รอการตรวจสอบจากคุณ`
              : `You have ${pendingVerifications.length} repair(s) waiting for your verification`
            }
          </p>
          <div className="verification-list">
            {pendingVerifications.map((repair) => (
              <div
                key={repair.name}
                className="verification-item"
                onClick={() => navigate(`/verify/${repair.name}`)}
              >
                <div className="verification-item-header">
                  <strong>{repair.asset_name}</strong>
                  <span className="verification-item-badge">
                    {i18n.language === 'th' ? 'ต้องตรวจสอบ' : 'Needs Verification'}
                  </span>
                </div>
                <p className="verification-item-description">{repair.description}</p>
                <p className="verification-item-meta">
                  {repair.location && `📍 ${repair.location} • `}
                  {new Date(repair.completion_date || repair.failure_date).toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Finished Repairs Needing Confirmation */}
      {!loading && finishedRepairs.length > 0 && (
        <div className="verification-alert" style={{borderLeft: '4px solid #10b981'}}>
          <div className="verification-alert-header">
            <span className="verification-badge" style={{backgroundColor: '#10b981'}}>{finishedRepairs.length}</span>
            <h3>
              ✅ {i18n.language === 'th' ? 'รอการยืนยัน' : 'Awaiting Confirmation'}
            </h3>
          </div>
          <p>
            {i18n.language === 'th'
              ? `คุณมี ${finishedRepairs.length} งานซ่อมที่เสร็จแล้ว กรุณายืนยันผลการซ่อม`
              : `You have ${finishedRepairs.length} finished repair(s) awaiting your confirmation`
            }
          </p>
          <div className="verification-list">
            {finishedRepairs.map((repair) => (
              <div
                key={repair.name}
                className="verification-item"
                onClick={() => navigate(`/confirm/${repair.name}`)}
              >
                <div className="verification-item-header">
                  <strong>{repair.asset_name}</strong>
                  <span className="verification-item-badge" style={{backgroundColor: '#10b981'}}>
                    {i18n.language === 'th' ? 'กรุณายืนยัน' : 'Please Confirm'}
                  </span>
                </div>
                <p className="verification-item-description">{repair.description}</p>
                <p className="verification-item-meta">
                  {repair.location && `📍 ${repair.location} • `}
                  {new Date(repair.completion_handover_date || repair.failure_date).toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="home-grid">
        {/* My Tasks Card - ONLY for Maintenance User role */}
        {userRoles.includes('Maintenance User') && (
          <div className="home-card" onClick={() => navigate('/todos')}>
            <div className="home-card-icon">📋</div>
            <h2>{i18n.language === 'th' ? 'งานของฉัน' : 'My Tasks'}</h2>
            <p className="home-card-description">
              {i18n.language === 'th' ? 'ดูงานบำรุงรักษาที่มอบหมายให้คุณ' : 'View maintenance tasks assigned to you'}
            </p>
            <button className="primary home-action-button">
              {i18n.language === 'th' ? 'ดูงาน' : 'View Tasks'} →
            </button>
          </div>
        )}

        <div className="home-card qr-card">
          <div className="home-card-icon">📷</div>
          <h2>{t('scan_qr')}</h2>
          <p className="home-card-description">
            {i18n.language === 'th' ? 'สแกน QR code บนอุปกรณ์เพื่อเริ่มตรวจสอบ' : 'Scan QR code on asset to start inspection'}
          </p>
          <QRScanner onScan={handleQRScan} />
        </div>

        {/* Search Card - Visibility controlled by settings from ERPNext */}
        {showSearch && (
          <div className="home-card search-card-home" onClick={() => navigate('/search')}>
            <div className="home-card-icon">🔍</div>
            <h2>{t('search_asset')}</h2>
            <p className="home-card-description">
              {i18n.language === 'th' ? 'ค้นหาอุปกรณ์ด้วยชื่อหรือรหัส' : 'Search for assets by name or code'}
            </p>
            <button
              className="primary home-action-button"
            >
              {t('search_asset')} →
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
