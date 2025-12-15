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
