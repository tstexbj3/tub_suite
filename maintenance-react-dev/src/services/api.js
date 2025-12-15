const API_BASE = '/api/method/tub_suite.api'

const callAPI = async (method, args = {}) => {
  const response = await fetch(`/api/method/${method}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Frappe-CSRF-Token': window.csrf_token || ''
    },
    body: JSON.stringify(args)
  })
  
  const data = await response.json()
  if (data.exc) throw new Error(data.exc)
  return data.message
}

export default {
  searchAssets: (query) => 
    callAPI('asset.search_assets', { query }),

  getMaintenanceTasks: (assetName) => 
    callAPI('maintenance.get_maintenance_by_asset', { asset_name: assetName }),

  submitTask: (params) => 
    callAPI('maintenance.submit_maintenance_task', params),

  getRepairForVerification: (repairName) => 
    callAPI('maintenance.get_repair_for_verification', { repair_name: repairName }),

  verifyRepair: (params) => 
    callAPI('maintenance.verify_repair_completion', params)
}
