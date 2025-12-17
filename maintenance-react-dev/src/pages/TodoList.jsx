import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

export default function TodoList() {
  const navigate = useNavigate()
  const { t, i18n } = useTranslation()
  const [todoData, setTodoData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [permissionDenied, setPermissionDenied] = useState(false)

  useEffect(() => {
    fetchTodoList()
  }, [])

  const fetchTodoList = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await fetch('/api/method/tub_suite.api.maintenance.get_inspector_todo_list', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Frappe-CSRF-Token': window.csrf_token || ''
        },
        body: JSON.stringify({
          days_ahead: 7
        })
      })

      const data = await response.json()

      // Check for permission error
      if (data.exc_type === 'PermissionError' ||
          (data._server_messages && data._server_messages.includes('PermissionError'))) {
        setPermissionDenied(true)
        return
      }

      if (data.message) {
        setTodoData(data.message)
      } else {
        throw new Error('Invalid response format')
      }
    } catch (err) {
      console.error('Error fetching todo list:', err)
      // Check if it's a permission error
      if (err.message && err.message.includes('denied')) {
        setPermissionDenied(true)
      } else {
        setError(err.message)
      }
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    return date.toLocaleDateString(i18n.language === 'th' ? 'th-TH' : 'en-US', {
      month: 'short',
      day: 'numeric'
    })
  }

  const TaskCard = ({ task, urgency }) => {
    const daysOverdue = task.days_overdue || 0

    const getBadgeText = () => {
      if (daysOverdue > 0) {
        return i18n.language === 'th'
          ? `เกิน ${daysOverdue} วัน`
          : `${daysOverdue} day${daysOverdue > 1 ? 's' : ''} late`
      } else if (daysOverdue === 0) {
        return i18n.language === 'th' ? 'ครบกำหนดวันนี้' : 'Due Today'
      } else {
        return i18n.language === 'th'
          ? `ถึงกำหนด ${formatDate(task.next_due_date)}`
          : `Due ${formatDate(task.next_due_date)}`
      }
    }

    return (
      <div
        className={`task-card urgency-${urgency}`}
        onClick={() => navigate(`/checklist/${task.asset_name}`)}
      >
        <div className="task-header">
          <div className="task-asset-info">
            <h3>{task.asset_title || task.asset_name}</h3>
            <span className="task-asset-code">{task.asset_name}</span>
          </div>
          <span className={`task-badge badge-${urgency}`}>
            {getBadgeText()}
          </span>
        </div>

        <p className="task-title">{task.maintenance_task}</p>

        {task.description && (
          <p className="task-description">{task.description}</p>
        )}

        <div className="task-meta">
          {task.location && (
            <span className="task-meta-item">
              📍 {task.location}
            </span>
          )}
          {task.periodicity && (
            <span className="task-meta-item">
              🔄 {task.periodicity}
            </span>
          )}
          {task.maintenance_type && (
            <span className="task-meta-item">
              🔧 {task.maintenance_type}
            </span>
          )}
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="container">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>{i18n.language === 'th' ? 'กำลังโหลด...' : 'Loading...'}</p>
        </div>
      </div>
    )
  }

  // Permission denied - ONLY for Maintenance User role
  if (permissionDenied) {
    return (
      <div className="container">
        <div className="error-state">
          <h2>🚫 {i18n.language === 'th' ? 'ไม่มีสิทธิ์เข้าถึง' : 'Access Denied'}</h2>
          <p>
            {i18n.language === 'th'
              ? 'เฉพาะผู้ใช้ที่มีบทบาท "Maintenance User" เท่านั้นที่สามารถดูรายการงานได้'
              : 'Only users with the "Maintenance User" role can view the task list.'}
          </p>
          <p className="error-detail">
            {i18n.language === 'th'
              ? 'หากคุณคิดว่านี่เป็นข้อผิดพลาด กรุณาติดต่อผู้ดูแลระบบ'
              : 'If you believe this is an error, please contact your system administrator.'}
          </p>
          <button onClick={() => navigate('/')} className="btn-primary">
            {i18n.language === 'th' ? 'กลับหน้าหลัก' : 'Back to Home'}
          </button>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container">
        <div className="error-state">
          <h2>❌ {i18n.language === 'th' ? 'เกิดข้อผิดพลาด' : 'Error'}</h2>
          <p>{error}</p>
          <button onClick={fetchTodoList} className="btn-retry">
            {i18n.language === 'th' ? 'ลองอีกครั้ง' : 'Retry'}
          </button>
        </div>
      </div>
    )
  }

  if (!todoData) {
    return (
      <div className="container">
        <div className="empty-state">
          <h2>{i18n.language === 'th' ? 'ไม่พบข้อมูล' : 'No Data'}</h2>
        </div>
      </div>
    )
  }

  const { overdue, due_today, upcoming, summary } = todoData

  return (
    <div className="container todo-container">
      {/* Header with summary */}
      <div className="todo-header">
        <div className="todo-title-section">
          <button
            className="back-button"
            onClick={() => navigate('/')}
          >
            ←
          </button>
          <h1>📋 {i18n.language === 'th' ? 'งานของฉัน' : 'My Tasks'}</h1>
        </div>

        <div className="summary-stats">
          <div className="stat stat-overdue">
            <span className="stat-number">{summary.overdue_count}</span>
            <span className="stat-label">
              {i18n.language === 'th' ? 'เกินกำหนด' : 'Overdue'}
            </span>
          </div>
          <div className="stat stat-due-today">
            <span className="stat-number">{summary.due_today_count}</span>
            <span className="stat-label">
              {i18n.language === 'th' ? 'ครบกำหนดวันนี้' : 'Due Today'}
            </span>
          </div>
          <div className="stat stat-upcoming">
            <span className="stat-number">{summary.upcoming_count}</span>
            <span className="stat-label">
              {i18n.language === 'th' ? 'กำลังจะถึง' : 'Upcoming'}
            </span>
          </div>
        </div>
      </div>

      {/* Empty state */}
      {summary.total === 0 && (
        <div className="empty-todo-state">
          <div className="empty-icon">✅</div>
          <h2>{i18n.language === 'th' ? 'ยินดีด้วย!' : 'All Caught Up!'}</h2>
          <p>
            {i18n.language === 'th'
              ? 'คุณไม่มีงานที่ต้องทำในช่วง 7 วันข้างหน้า'
              : 'You have no tasks due in the next 7 days'
            }
          </p>
          <button
            onClick={() => navigate('/')}
            className="btn-primary"
          >
            {i18n.language === 'th' ? 'กลับหน้าหลัก' : 'Back to Home'}
          </button>
        </div>
      )}

      {/* Overdue Section - High Priority (Red) */}
      {overdue.length > 0 && (
        <section className="todo-section overdue-section">
          <h2 className="section-title">
            🔥 {i18n.language === 'th' ? 'เกินกำหนด' : 'Overdue'} ({overdue.length})
          </h2>
          <div className="task-list">
            {overdue.map((task) => (
              <TaskCard key={task.name} task={task} urgency="high" />
            ))}
          </div>
        </section>
      )}

      {/* Due Today Section - Medium Priority (Orange) */}
      {due_today.length > 0 && (
        <section className="todo-section due-today-section">
          <h2 className="section-title">
            ⚠️ {i18n.language === 'th' ? 'ครบกำหนดวันนี้' : 'Due Today'} ({due_today.length})
          </h2>
          <div className="task-list">
            {due_today.map((task) => (
              <TaskCard key={task.name} task={task} urgency="medium" />
            ))}
          </div>
        </section>
      )}

      {/* Upcoming Section - Low Priority (Blue) */}
      {upcoming.length > 0 && (
        <section className="todo-section upcoming-section">
          <h2 className="section-title">
            📅 {i18n.language === 'th' ? 'กำลังจะถึง' : 'Upcoming'} ({upcoming.length})
          </h2>
          <div className="task-list">
            {upcoming.map((task) => (
              <TaskCard key={task.name} task={task} urgency="low" />
            ))}
          </div>
        </section>
      )}

      {/* Refresh button */}
      <div className="todo-footer">
        <button
          onClick={fetchTodoList}
          className="btn-refresh"
          disabled={loading}
        >
          🔄 {i18n.language === 'th' ? 'รีเฟรช' : 'Refresh'}
        </button>
      </div>
    </div>
  )
}
