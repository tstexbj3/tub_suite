import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import api from '../services/api'
import PhotoUpload from '../components/PhotoUpload'

export default function Checklist() {
  const { assetName } = useParams()
  const navigate = useNavigate()
  const [tasks, setTasks] = useState([])
  const [assetInfo, setAssetInfo] = useState(null)
  const [selectedTask, setSelectedTask] = useState(null)
  const [photos, setPhotos] = useState([])
  const [notes, setNotes] = useState('')
  const [hasIssue, setHasIssue] = useState(false)
  const [issueDesc, setIssueDesc] = useState('')
  const [loading, setLoading] = useState(true)
  const { t } = useTranslation()

  useEffect(() => {
    loadTasks()
  }, [assetName])

  const loadTasks = async () => {
    setLoading(true)
    try {
      const data = await api.getMaintenanceTasks(assetName)
      console.log('API returned:', data)

      // API returns array of assets with tasks
      // Find the matching asset and extract tasks
      if (Array.isArray(data) && data.length > 0) {
        const assetData = data.find(item => item.asset && item.asset.name === assetName) || data[0]
        const taskList = assetData.tasks || []
        console.log('Extracted tasks:', taskList)
        setTasks(taskList)
        setAssetInfo(assetData.asset)
      } else {
        setTasks([])
        setAssetInfo(null)
      }
    } catch (error) {
      console.error('Failed to load tasks:', error)
      setTasks([])
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async () => {
    if (photos.length === 0) {
      alert(t('min_photos_required'))
      return
    }

    if (hasIssue && !issueDesc.trim()) {
      alert('Please provide issue description')
      return
    }

    try {
      const response = await api.submitTask({
        maintenance_name: selectedTask.parent,
        task_name: selectedTask.name,
        asset_name: assetName,
        has_issue: hasIssue ? 1 : 0,
        notes,
        issue_description: issueDesc,
        inspection_photos: hasIssue ? [] : photos,
        issue_photos: hasIssue ? photos : []
      })

      alert('Task submitted successfully!')

      // Mark task as completed immediately in local state
      // Use the response from backend to know if issue was reported
      const today = new Date().toISOString().split('T')[0]
      const hasOpenIssue = response.has_issue ? 1 : 0

      setTasks(tasks.map(t =>
        t.name === selectedTask.name
          ? { ...t, last_completion_date: today, has_open_issue: hasOpenIssue }
          : t
      ))

      setSelectedTask(null)
      setPhotos([])
      setNotes('')
      setIssueDesc('')
      setHasIssue(false)

      // Don't reload - trust the immediate state update from backend response
      // User can manually refresh if needed
    } catch (error) {
      console.error('Submit failed:', error)
      alert('Failed to submit task: ' + error.message)
    }
  }

  if (!selectedTask) {
    return (
      <div className="container">
        <div className="page-header">
          <button className="back-button" onClick={() => navigate('/search')}>
            ← {t('back')}
          </button>
          <div>
            <h2>{t('maintenance_tasks')}</h2>
            {assetInfo && (
              <p style={{ margin: '0.5rem 0 0 0', color: '#666', fontSize: '0.95rem' }}>
                {assetInfo.item_name || assetInfo.asset_name} ({assetInfo.item_code}) - {assetInfo.name}
              </p>
            )}
          </div>
        </div>

        {loading ? (
          <div className="loading-state">⏳ Loading tasks...</div>
        ) : tasks.length === 0 ? (
          <div className="no-results">
            <p>📋 No maintenance tasks found for this asset</p>
          </div>
        ) : (
          <div className="task-list">
            {tasks.map(task => {
              // Check if task was completed today or has a pending repair
              const today = new Date().toISOString().split('T')[0]
              const lastCompleted = task.last_completion_date
              const completedToday = lastCompleted === today
              const hasOpenIssue = task.has_open_issue === 1
              const hasPendingRepair = task.pending_repair === 1

              // Lock task if: completed today OR has pending repair
              const isLocked = completedToday || hasPendingRepair

              return (
                <div
                  key={task.name}
                  className={`task-card ${isLocked ? 'task-completed-today' : ''}`}
                  onClick={() => !isLocked && setSelectedTask(task)}
                  style={{ cursor: isLocked ? 'not-allowed' : 'pointer', opacity: isLocked ? 0.6 : 1 }}
                >
                  <div className="task-card-header">
                    <h3>{task.maintenance_task || task.task_name || 'Unnamed Task'}</h3>
                    {hasPendingRepair && !completedToday ? (
                      <span className="status-badge" style={{ background: '#2196F3', color: 'white' }}>
                        🔧 Repair In Progress
                      </span>
                    ) : completedToday && hasOpenIssue ? (
                      <span className="status-badge" style={{ background: '#FF9800', color: 'white' }}>
                        ⚠ Issue Reported
                      </span>
                    ) : completedToday ? (
                      <span className="status-badge" style={{ background: '#4CAF50', color: 'white' }}>
                        ✓ Completed Today
                      </span>
                    ) : task.maintenance_type && (
                      <span className="status-badge status-submitted">
                        {task.maintenance_type}
                      </span>
                    )}
                  </div>
                  <div className="task-meta">
                    {task.periodicity && <span>🔄 {task.periodicity}</span>}
                    {task.next_due_date && <span>📅 Due: {task.next_due_date}</span>}
                    {task.last_completion_date && <span>✓ Last: {task.last_completion_date}</span>}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="container">
      <div className="page-header">
        <button className="back-button" onClick={() => setSelectedTask(null)}>
          ← {t('back')}
        </button>
        <h2>{selectedTask.maintenance_task || selectedTask.task_name}</h2>
      </div>

      <div className="card">
        <div className="form-section">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={hasIssue}
              onChange={(e) => setHasIssue(e.target.checked)}
            />
            <span>{t('report_issue')}</span>
          </label>

          {hasIssue && (
            <div className="form-group">
              <label>{t('issue_description')}</label>
              <textarea
                placeholder={t('issue_description')}
                value={issueDesc}
                onChange={(e) => setIssueDesc(e.target.value)}
                rows="4"
              />
            </div>
          )}

          <div className="form-group">
            <label>{hasIssue ? t('issue_photos') : t('inspection_photos')}</label>
            <PhotoUpload
              photos={photos}
              setPhotos={setPhotos}
              activityType={hasIssue ? 'ISSUE' : 'INSP'}
              assetName={assetName}
            />
          </div>

          <div className="form-group">
            <label>{t('notes')}</label>
            <textarea
              placeholder={t('notes')}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows="3"
            />
          </div>

          <div className="button-group">
            <button
              className="primary"
              onClick={handleSubmit}
              disabled={photos.length === 0 || (hasIssue && !issueDesc.trim())}
            >
              ✓ {t('submit')}
            </button>
            <button className="secondary" onClick={() => setSelectedTask(null)}>
              ✗ {t('cancel')}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
