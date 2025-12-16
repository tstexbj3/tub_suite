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
    callAPI('tub_suite.api.asset.search_assets', { query }),

  getMaintenanceTasks: (assetName) => 
    callAPI('tub_suite.api.maintenance.get_maintenance_by_asset', { asset_name: assetName }),

  submitTask: (params) => 
    callAPI('tub_suite.api.maintenance.submit_maintenance_task', params),

  getRepairForVerification: (repairName) => 
    callAPI('tub_suite.api.maintenance.get_repair_for_verification', { repair_name: repairName }),

  verifyRepair: (params) => 
    callAPI('tub_suite.api.maintenance.verify_repair_completion', params)
}
