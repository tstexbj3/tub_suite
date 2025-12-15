#!/bin/bash
echo "Creating all React components and pages..."

# AssetSearch Page
cat > src/pages/AssetSearch.jsx << 'EOF'
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
EOF

# Checklist Page
cat > src/pages/Checklist.jsx << 'EOF'
import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import api from '../services/api'
import PhotoUpload from '../components/PhotoUpload'

export default function Checklist() {
  const { assetName } = useParams()
  const [tasks, setTasks] = useState([])
  const [selectedTask, setSelectedTask] = useState(null)
  const [photos, setPhotos] = useState([])
  const [notes, setNotes] = useState('')
  const [hasIssue, setHasIssue] = useState(false)
  const [issueDesc, setIssueDesc] = useState('')
  const { t } = useTranslation()

  useEffect(() => {
    loadTasks()
  }, [assetName])

  const loadTasks = async () => {
    const data = await api.getMaintenanceTasks(assetName)
    setTasks(data)
  }

  const handleSubmit = async () => {
    if (photos.length === 0) {
      alert(t('min_photos_required'))
      return
    }

    await api.submitTask({
      maintenance_name: selectedTask.maintenance_name,
      task_name: selectedTask.name,
      asset_name: assetName,
      has_issue: hasIssue ? 1 : 0,
      notes,
      issue_description: issueDesc,
      inspection_photos: hasIssue ? [] : photos,
      issue_photos: hasIssue ? photos : []
    })

    alert('Task submitted!')
    setSelectedTask(null)
    setPhotos([])
    setNotes('')
    loadTasks()
  }

  if (!selectedTask) {
    return (
      <div className="container">
        <h2>{t('maintenance_tasks')}</h2>
        <div className="task-list">
          {tasks.map(task => (
            <div key={task.name} className="task-item" onClick={() => setSelectedTask(task)}>
              <h3>{task.task_name}</h3>
              <p>{task.description}</p>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      <div className="card">
        <h2>{selectedTask.task_name}</h2>
        
        <label>
          <input 
            type="checkbox" 
            checked={hasIssue} 
            onChange={(e) => setHasIssue(e.target.checked)} 
          />
          {t('report_issue')}
        </label>

        {hasIssue && (
          <textarea
            placeholder={t('issue_description')}
            value={issueDesc}
            onChange={(e) => setIssueDesc(e.target.value)}
          />
        )}

        <h3>{hasIssue ? t('issue_photos') : t('inspection_photos')}</h3>
        <PhotoUpload 
          photos={photos} 
          setPhotos={setPhotos}
          activityType={hasIssue ? 'ISSUE' : 'INSP'}
        />

        <textarea
          placeholder={t('notes')}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />

        <button className="primary" onClick={handleSubmit} disabled={photos.length === 0}>
          {t('submit')}
        </button>
        <button onClick={() => setSelectedTask(null)}>{t('cancel')}</button>
      </div>
    </div>
  )
}
EOF

# VerifyRepair Page
cat > src/pages/VerifyRepair.jsx << 'EOF'
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
EOF

echo "✅ All pages created!"
echo "Creating components..."

