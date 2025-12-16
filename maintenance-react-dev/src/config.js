// Portal Configuration
// Settings are now managed from ERPNext Desk
// Go to: Maintenance Portal Settings

let cachedSettings = null
let lastFetchTime = 0
const CACHE_DURATION = 60000 // Cache for 1 minute

const fetchSettings = async () => {
  const now = Date.now()

  // Return cached settings if still valid
  if (cachedSettings && (now - lastFetchTime) < CACHE_DURATION) {
    return cachedSettings
  }

  try {
    const response = await fetch('/api/method/tub_suite.api.maintenance.get_portal_settings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.csrf_token || ''
      }
    })
    const data = await response.json()

    if (data.message) {
      cachedSettings = {
        ENABLE_SEARCH_FOR_ALL: data.message.enable_search_for_all === 1,
        SEARCH_ALLOWED_ROLES: data.message.search_allowed_roles || []
      }
      lastFetchTime = now
      return cachedSettings
    }
  } catch (error) {
    console.error('Error fetching portal settings:', error)
  }

  // Fallback to default settings
  return {
    ENABLE_SEARCH_FOR_ALL: false,
    SEARCH_ALLOWED_ROLES: ['Maintenance Manager', 'System Manager', 'Administrator']
  }
}

const config = {
  getSettings: fetchSettings,

  // Legacy support - will fetch from API
  get ENABLE_SEARCH_FOR_ALL() {
    return false // Default, will be overridden by async fetch
  },

  get SEARCH_ALLOWED_ROLES() {
    return ['Maintenance Manager', 'System Manager', 'Administrator']
  }
}

export default config
