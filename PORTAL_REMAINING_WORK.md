# Portal Reporter Confirmation - Remaining Work

## ✅ DONE
1. Backend API implemented: `get_repairs_for_confirmation()` and `submit_reporter_confirmation()`
2. Database fixed: `reporter_confirmation_section` depends_on changed to "Finished"
3. Home.jsx partially updated:
   - Added state: `const [finishedRepairs, setFinishedRepairs] = useState([])`
   - Added fetch call in useEffect: `fetchFinishedRepairs()`
   - Added fetch function: `fetchFinishedRepairs()` calls the API

## ❌ TODO
1. **Add UI section in Home.jsx** to display finished repairs (after line 126, before `<div className="home-grid">`):
   ```jsx
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
   ```

2. **Create ConfirmRepair.jsx page** (copy VerifyRepair.jsx and modify):
   - Load repair using `api.getRepairForConfirmation(repairName)`
   - Submit using `api.submitReporterConfirmation()`
   - Fields: confirmation_photos, confirmation_notes, reporter_signature

3. **Add route** in App.jsx:
   ```jsx
   <Route path="/confirm/:repairName" element={<ConfirmRepair />} />
   ```

4. **Add API methods** in services/api.js:
   ```javascript
   getRepairForConfirmation: async (repairName) => {
     // Similar to getRepairForVerification but for Finished state
   }

   submitReporterConfirmation: async (data) => {
     return apiCall('tub_suite.api.maintenance.submit_reporter_confirmation', data)
   }
   ```

5. **Rebuild portal**: `cd maintenance-react-dev && npm run build`

6. **Copy build to www**: The build process should copy to `tub_suite/www/maintenance/`

## Quick Commands
```bash
# Edit Home.jsx manually and add the UI section
nano maintenance-react-dev/src/pages/Home.jsx

# Copy VerifyRepair.jsx to ConfirmRepair.jsx
cp maintenance-react-dev/src/pages/VerifyRepair.jsx maintenance-react-dev/src/pages/ConfirmRepair.jsx

# Edit ConfirmRepair.jsx to use reporter confirmation fields
nano maintenance-react-dev/src/pages/ConfirmRepair.jsx

# Build
cd maintenance-react-dev && npm run build

# Restart bench
bench start
```
