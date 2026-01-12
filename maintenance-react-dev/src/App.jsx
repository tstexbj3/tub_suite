import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import Home from './pages/Home'
import AssetSearch from './pages/AssetSearch'
import Checklist from './pages/Checklist'
import VerifyRepair from './pages/VerifyRepair'
import TodoList from './pages/TodoList'
import ReportIssue from './pages/ReportIssue'

function App() {
  const { i18n } = useTranslation()

  const toggleLanguage = () => {
    i18n.changeLanguage(i18n.language === 'en' ? 'th' : 'en')
  }

  return (
    <Router basename="/maintenance">
      <div className="app">
        <header>
          <h1>TUB Maintenance Portal</h1>
          <button onClick={toggleLanguage} className="lang-toggle">
            {i18n.language === 'en' ? 'ไทย' : 'EN'}
          </button>
        </header>
        
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/search" element={<AssetSearch />} />
          <Route path="/todos" element={<TodoList />} />
          <Route path="/report-issue/:assetName" element={<ReportIssue />} />
          <Route path="/checklist/:assetName" element={<Checklist />} />
          <Route path="/verify/:repairName" element={<VerifyRepair />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
