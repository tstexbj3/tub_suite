import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import PhotoUpload from '../components/PhotoUpload'

export default function ReportIssue() {
  const navigate = useNavigate()
  const { assetName } = useParams()
  const { i18n } = useTranslation()
  const [loading, setLoading] = useState(false)
  const [assetInfo, setAssetInfo] = useState(null)
  const [departments, setDepartments] = useState([])
  const [photos, setPhotos] = useState([])
  const [formData, setFormData] = useState({
    asset_name: assetName || '',
    repair_subject: '',
    repair_source: '',
    repair_type: '',
    failure_date: new Date().toISOString().split('T')[0],
    failure_description: '',
    reporter_name: '',
    reporter_department: ''
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    if (assetName) {
      fetchAssetInfo()
    }
    fetchDepartments()
    fetchUserInfo()
  }, [assetName])

  const fetchAssetInfo = async () => {
    try {
      const response = await fetch('/api/method/frappe.client.get', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Frappe-CSRF-Token': window.csrf_token || ''
        },
        body: JSON.stringify({
          doctype: 'Asset',
          name: assetName
        })
      })
      const data = await response.json()
      setAssetInfo(data.message)
    } catch (error) {
      console.error('Error fetching asset info:', error)
    }
  }

  const fetchDepartments = async () => {
    try {
      const response = await fetch('/api/method/frappe.client.get_list', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Frappe-CSRF-Token': window.csrf_token || ''
        },
        body: JSON.stringify({
          doctype: 'Department',
          fields: ['name'],
          limit_page_length: 1000,
          order_by: 'name asc'
        })
      })
      const data = await response.json()
      setDepartments(data.message || [])
    } catch (error) {
      console.error('Error fetching departments:', error)
    }
  }

  const fetchUserInfo = async () => {
    try {
      const response = await fetch('/api/method/frappe.auth.get_logged_user', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Frappe-CSRF-Token': window.csrf_token || ''
        }
      })
      const data = await response.json()
      const userEmail = data.message

      const userResponse = await fetch('/api/method/frappe.client.get', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Frappe-CSRF-Token': window.csrf_token || ''
        },
        body: JSON.stringify({
          doctype: 'User',
          name: userEmail
        })
      })
      const userData = await userResponse.json()

      setFormData(prev => ({
        ...prev,
        reporter_name: userData.message.full_name || userEmail
      }))
    } catch (error) {
      console.error('Error fetching user info:', error)
    }
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      if (!formData.asset_name) {
        throw new Error(i18n.language === 'th' ? 'กรุณาเลือกอุปกรณ์' : 'Please select an asset')
      }
      if (!formData.repair_subject) {
        throw new Error(i18n.language === 'th' ? 'กรุณาระบุเรื่องที่แจ้ง' : 'Please enter subject')
      }
      if (!formData.repair_source) {
        throw new Error(i18n.language === 'th' ? 'กรุณาเลือกที่มาของการแจ้ง' : 'Please select repair source')
      }
      if (!formData.repair_type) {
        throw new Error(i18n.language === 'th' ? 'กรุณาเลือกประเภทการซ่อม' : 'Please select repair type')
      }
      if (photos.length === 0) {
        throw new Error(i18n.language === 'th' ? 'กรุณาแนบรูปถ่ายอย่างน้อย 1 รูป' : 'Please attach at least 1 photo')
      }

      const response = await fetch('/api/method/tub_suite.api.maintenance.create_operator_repair_request', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Frappe-CSRF-Token': window.csrf_token || ''
        },
        body: JSON.stringify({
          asset_name: formData.asset_name,
          repair_subject: formData.repair_subject,
          repair_source: formData.repair_source,
          repair_type: formData.repair_type,
          failure_date: formData.failure_date,
          failure_description: formData.failure_description,
          reporter_name: formData.reporter_name,
          reporter_department: formData.reporter_department || null,
          issue_photos: photos
        })
      })

      const data = await response.json()

      if (data.message && data.message.success) {
        setSuccess(
          i18n.language === 'th'
            ? `✅ แจ้งซ่อมสำเร็จ! เลขที่: ${data.message.repair_name}`
            : `✅ Repair request submitted! Reference: ${data.message.repair_name}`
        )

        setTimeout(() => {
          navigate(-1)
        }, 2000)
      } else {
        throw new Error(data.message || 'Failed to submit repair request')
      }
    } catch (error) {
      console.error('Error submitting repair:', error)
      setError(error.message || (i18n.language === 'th' ? 'เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง' : 'An error occurred. Please try again.'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <div className="page-header">
        <button className="back-button" onClick={() => navigate(-1)}>
          ← {i18n.language === 'th' ? 'กลับ' : 'Back'}
        </button>
        <h1>🔧 {i18n.language === 'th' ? 'แจ้งซ่อม/ติดตั้งใหม่' : 'Report Issue'}</h1>
        {assetInfo && (
          <p className="page-subtitle">
            {assetInfo.asset_name || assetInfo.item_name} ({assetInfo.item_code})
          </p>
        )}
      </div>

      {error && (
        <div className="alert alert-error">
          ❌ {error}
        </div>
      )}

      {success && (
        <div className="alert alert-success">
          {success}
        </div>
      )}

      <form onSubmit={handleSubmit} className="report-issue-form">
        <div className="form-section">
          <h2 className="form-section-title">
            📋 {i18n.language === 'th' ? 'ข้อมูลพื้นฐาน' : 'Basic Information'}
          </h2>

          <div className="form-group">
            <label className="required">
              {i18n.language === 'th' ? 'ที่มาของการแจ้ง' : 'Repair Source'}
            </label>
            <select
              name="repair_source"
              value={formData.repair_source}
              onChange={handleInputChange}
              required
            >
              <option value="">{i18n.language === 'th' ? '-- เลือก --' : '-- Select --'}</option>
              <option value="Portal (แจ้งผ่านระบบ)">
                {i18n.language === 'th' ? 'แจ้งผ่านระบบ' : 'Portal'}
              </option>
              <option value="Manual (แจ้งด้วยตนเอง)">
                {i18n.language === 'th' ? 'แจ้งด้วยตนเอง' : 'Manual'}
              </option>
              <option value="Planned Maintenance (ตามแผน)">
                {i18n.language === 'th' ? 'ตามแผน' : 'Planned Maintenance'}
              </option>
            </select>
          </div>

          <div className="form-group">
            <label className="required">
              {i18n.language === 'th' ? 'ประเภทการซ่อม' : 'Repair Type'}
            </label>
            <select
              name="repair_type"
              value={formData.repair_type}
              onChange={handleInputChange}
              required
            >
              <option value="">{i18n.language === 'th' ? '-- เลือก --' : '-- Select --'}</option>
              <option value="ซ่อม (Repair)">{i18n.language === 'th' ? 'ซ่อม' : 'Repair'}</option>
              <option value="แก้ไข (Fix/Correction)">{i18n.language === 'th' ? 'แก้ไข' : 'Fix/Correction'}</option>
              <option value="ติดตั้งใหม่ (New Installation)">{i18n.language === 'th' ? 'ติดตั้งใหม่' : 'New Installation'}</option>
              <option value="ปรับปรุง (Improvement)">{i18n.language === 'th' ? 'ปรับปรุง' : 'Improvement'}</option>
              <option value="ซ่อมบำรุงตามแผน (Planned Maintenance)">{i18n.language === 'th' ? 'ซ่อมบำรุงตามแผน' : 'Planned Maintenance'}</option>
              <option value="อื่นๆ (Other)">{i18n.language === 'th' ? 'อื่นๆ' : 'Other'}</option>
            </select>
          </div>
        </div>

        <div className="form-section">
          <h2 className="form-section-title">
            🏭 {i18n.language === 'th' ? 'รายละเอียดปัญหา' : 'Issue Details'}
          </h2>

          <div className="form-group">
            <label className="required">
              {i18n.language === 'th' ? 'เรื่องที่แจ้ง' : 'Subject'}
            </label>
            <input
              type="text"
              name="repair_subject"
              value={formData.repair_subject}
              onChange={handleInputChange}
              placeholder={i18n.language === 'th' ? 'เช่น: มอเตอร์ไม่ทำงาน' : 'e.g., Motor not working'}
              required
            />
          </div>

          {assetInfo && (
            <div className="form-group">
              <label>
                {i18n.language === 'th' ? 'อุปกรณ์' : 'Asset'}
              </label>
              <div style={{
                padding: '0.75rem',
                backgroundColor: '#f5f5f5',
                borderRadius: '6px',
                border: '1px solid #ddd',
                fontSize: '1rem',
                color: '#333'
              }}>
                <strong>{assetInfo.asset_name || assetInfo.item_name}</strong>
                <br />
                <small style={{ color: '#666' }}>
                  {assetInfo.item_code} {assetInfo.location ? `• ${assetInfo.location}` : ''}
                </small>
              </div>
              <small className="form-help-text">
                {i18n.language === 'th' ? 'ดึงข้อมูลจากอุปกรณ์ที่เลือก' : 'From selected asset'}
              </small>
            </div>
          )}

          <div className="form-group">
            <label className="required">
              {i18n.language === 'th' ? 'วันที่เกิดปัญหา' : 'Failure Date'}
            </label>
            <input
              type="date"
              name="failure_date"
              value={formData.failure_date}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-group">
            <label className="required">
              {i18n.language === 'th' ? 'อาการเสีย / รายละเอียด' : 'Problem Description'}
            </label>
            <textarea
              name="failure_description"
              value={formData.failure_description}
              onChange={handleInputChange}
              rows="4"
              placeholder={i18n.language === 'th' ? 'อธิบายปัญหาโดยละเอียด...' : 'Describe the problem in detail...'}
              required
            />
          </div>

          <div className="form-group">
            <label className="required">
              📷 {i18n.language === 'th' ? 'รูปถ่ายปัญหา' : 'Issue Photos'}
            </label>
            <PhotoUpload
              photos={photos}
              setPhotos={setPhotos}
              activityType="REPORT"
              assetName={formData.asset_name || 'ASSET'}
            />
            <small className="form-help-text">
              {i18n.language === 'th' ? 'แนบรูปถ่ายปัญหาอย่างน้อย 1 รูป (สูงสุด 5 รูป)' : 'Attach at least 1 photo of the issue (max 5)'}
            </small>
          </div>
        </div>

        <div className="form-section">
          <h2 className="form-section-title">
            👤 {i18n.language === 'th' ? 'ข้อมูลผู้แจ้ง' : 'Reporter Information'}
          </h2>

          <div className="form-group">
            <label>
              {i18n.language === 'th' ? 'ชื่อผู้แจ้ง' : 'Reporter Name'}
            </label>
            <input
              type="text"
              name="reporter_name"
              value={formData.reporter_name}
              readOnly
              style={{ backgroundColor: '#f5f5f5', cursor: 'not-allowed' }}
            />
            <small className="form-help-text">
              {i18n.language === 'th' ? 'ดึงข้อมูลจากบัญชีผู้ใช้' : 'Auto-filled from user account'}
            </small>
          </div>

          <div className="form-group">
            <label>
              {i18n.language === 'th' ? 'แผนก' : 'Department'}
            </label>
            <select
              name="reporter_department"
              value={formData.reporter_department}
              onChange={handleInputChange}
            >
              <option value="">{i18n.language === 'th' ? '-- เลือกแผนก (ไม่บังคับ) --' : '-- Select Department (Optional) --'}</option>
              {departments.map(dept => (
                <option key={dept.name} value={dept.name}>
                  {dept.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-actions">
          <button
            type="button"
            className="secondary"
            onClick={() => navigate(-1)}
            disabled={loading}
          >
            {i18n.language === 'th' ? 'ยกเลิก' : 'Cancel'}
          </button>
          <button
            type="submit"
            className="primary"
            disabled={loading}
          >
            {loading
              ? (i18n.language === 'th' ? 'กำลังส่ง...' : 'Submitting...')
              : (i18n.language === 'th' ? '✅ ส่งการแจ้งซ่อม' : '✅ Submit Repair Request')
            }
          </button>
        </div>
      </form>
    </div>
  )
}
