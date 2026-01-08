# Asset Repair Log - Mobile-First Design

## Overview
When a QR code is scanned, inspectors/engineers should see a complete repair history for that asset before creating a new repair request. This provides context and helps identify recurring issues.

---

## User Flow

```
QR Scan → Asset Info Page → View History OR Report New Issue
```

### Current Flow (Before)
1. Scan QR → Goes to `/maintenance?asset=ACC-ASS-2025-00019`
2. Redirects to `/checklist/{asset}` (maintenance tasks only)
3. No repair history visible

### Proposed Flow (After)
1. Scan QR → Goes to `/maintenance?asset=ACC-ASS-2025-00019`
2. Shows **Asset Overview** page at `/asset/{asset_name}`
3. Displays:
   - Asset info (name, location, status)
   - **Repair History** (recent repairs)
   - Action buttons (Report Issue / View All History / Do Maintenance)

---

## Page Design: Asset Overview (`/asset/{asset_name}`)

### Mobile Layout (320px - 768px)

```
┌─────────────────────────────────────┐
│  TUB Maintenance Portal    [ไทย/EN] │
│  ← Back                              │
├─────────────────────────────────────┤
│                                      │
│  🏭 Asset Information                │
│  ┌─────────────────────────────────┐│
│  │ เครื่อง Load กระป๋องเข้าตะกร้า  ││
│  │ ACC-ASS-2025-00019              ││
│  │ 📍 ห้อง Retort                  ││
│  │ ⚙️  Status: Active               ││
│  └─────────────────────────────────┘│
│                                      │
│  📋 Recent Repairs (Last 30 Days)    │
│  ┌─────────────────────────────────┐│
│  │ 🔴 OPEN - Waiting Engineer       ││
│  │ Motor overheating               ││
│  │ Reported: 2 Jan 2026 | Inspect  ││
│  │ Priority: High                  ││
│  └─────────────────────────────────┘│
│                                      │
│  ┌─────────────────────────────────┐│
│  │ ✅ COMPLETED                     ││
│  │ Belt replacement                ││
│  │ 28 Dec 2025 → 30 Dec 2025       ││
│  │ Engineer: ช่าง A                ││
│  └─────────────────────────────────┘│
│                                      │
│  ┌─────────────────────────────────┐│
│  │ ✅ COMPLETED                     ││
│  │ Lubrication service             ││
│  │ 15 Dec 2025 → 16 Dec 2025       ││
│  │ Engineer: ช่าง B                ││
│  └─────────────────────────────────┘│
│                                      │
│  [View All Repair History (12)]     │
│                                      │
│  ┌─────────────────────────────────┐│
│  │    🚨 REPORT NEW ISSUE           ││
│  │    (Red button - 56px height)   ││
│  └─────────────────────────────────┘│
│                                      │
│  ┌─────────────────────────────────┐│
│  │    ✓ DO SCHEDULED MAINTENANCE   ││
│  │    (Blue button - 56px height)  ││
│  └─────────────────────────────────┘│
│                                      │
└─────────────────────────────────────┘
```

---

## Component Breakdown

### 1. Asset Info Card
**Purpose:** Quick asset identification
**Height:** ~140px

```jsx
<div className="asset-info-card">
  <h2>{asset.asset_name}</h2>
  <div className="asset-code">{asset.name}</div>
  <div className="asset-meta">
    <span>📍 {asset.location}</span>
    <span className={`status-badge ${statusClass}`}>
      {asset.status}
    </span>
  </div>
</div>
```

**Touch Target:** Full card tappable → goes to full asset details

---

### 2. Repair History List
**Purpose:** Show recent repair context
**Default:** Last 30 days, max 5 items
**Item Height:** ~100px each

#### Repair Card States

**🔴 OPEN (Pending/In Progress)**
```
┌───────────────────────────────────────┐
│ 🔴 OPEN - Waiting Engineer            │
│ Motor overheating - smoke detected    │
│ Reported: 2 Jan 2026 14:30            │
│ Inspector: สมชาย ใจดี                 │
│ Priority: High | Photos: 3            │
│                                        │
│ [View Details →]                      │
└───────────────────────────────────────┘
```

**✅ COMPLETED**
```
┌───────────────────────────────────────┐
│ ✅ COMPLETED                           │
│ Belt replacement and alignment        │
│ 28 Dec 2025 → 30 Dec 2025 (2 days)    │
│ Engineer: ช่าง A                      │
│                                        │
│ [View Details →]                      │
└───────────────────────────────────────┘
```

**❌ REJECTED**
```
┌───────────────────────────────────────┐
│ ❌ REJECTED                            │
│ Noise complaint - normal operation    │
│ Rejected: 25 Dec 2025                 │
│ Manager note: "Within spec"           │
│                                        │
│ [View Details →]                      │
└───────────────────────────────────────┘
```

---

### 3. Action Buttons (Fixed Bottom)

**Design Specs:**
- Min height: 56px (iOS/Android standard)
- Min width: 48px (WCAG AAA touch target)
- Spacing: 16px between buttons
- Fixed position on scroll (sticky bottom)

```jsx
<div className="action-buttons-sticky">
  <button className="btn-report-issue">
    🚨 REPORT NEW ISSUE
  </button>

  <button className="btn-do-maintenance">
    ✓ DO SCHEDULED MAINTENANCE
  </button>
</div>
```

**CSS:**
```css
.action-buttons-sticky {
  position: sticky;
  bottom: 0;
  padding: 16px;
  background: white;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
  gap: 12px;
  display: flex;
  flex-direction: column;
}

.btn-report-issue,
.btn-do-maintenance {
  min-height: 56px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  transition: transform 0.1s;
}

.btn-report-issue {
  background: #dc2626;
  color: white;
}

.btn-report-issue:active {
  transform: scale(0.98);
  background: #b91c1c;
}

.btn-do-maintenance {
  background: #2563eb;
  color: white;
}

.btn-do-maintenance:active {
  transform: scale(0.98);
  background: #1d4ed8;
}
```

---

## Full Repair History Page (`/asset/{asset_name}/repairs`)

### Features
- Infinite scroll (load 20 at a time)
- Filter by status: All / Open / Completed / Rejected
- Search by description
- Export to PDF (for managers)

```
┌─────────────────────────────────────┐
│  ← Repair History                    │
│  ACC-ASS-2025-00019                  │
├─────────────────────────────────────┤
│  [All] [Open] [Completed] [Rejected] │
│  🔍 Search repairs...                 │
├─────────────────────────────────────┤
│  Total: 47 repairs | Showing: 20     │
│                                      │
│  January 2026 (3)                    │
│  ┌─────────────────────────────────┐│
│  │ 🔴 Motor overheating             ││
│  │ 2 Jan 2026 | Open                ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │ ✅ Belt replacement              ││
│  │ 28-30 Dec 2025 | Completed       ││
│  └─────────────────────────────────┘│
│                                      │
│  December 2025 (8)                   │
│  ... (grouped by month)              │
│                                      │
│  [Load More...]                      │
└─────────────────────────────────────┘
```

---

## Repair Detail Modal (`/asset/{asset_name}/repair/{repair_id}`)

**Opens as:** Full-screen modal (mobile) or side panel (tablet+)

```
┌─────────────────────────────────────┐
│  ✕ Close                             │
│                                      │
│  Repair #REP-00234                   │
│  🔴 OPEN - Waiting Engineer          │
│                                      │
│  📋 Problem Description              │
│  ┌─────────────────────────────────┐│
│  │ Motor overheating after 2 hours  ││
│  │ of operation. Smoke detected     ││
│  │ from rear bearing.               ││
│  └─────────────────────────────────┘│
│                                      │
│  📸 Inspector Photos (3)             │
│  [🖼️] [🖼️] [🖼️]                     │
│                                      │
│  👤 Reported By                      │
│  สมชาย ใจดี (Inspector)              │
│  2 Jan 2026, 14:30                   │
│                                      │
│  🔧 Engineering Notes                │
│  ┌─────────────────────────────────┐│
│  │ Bearing replacement required.    ││
│  │ Ordered new SKF 6205 bearing.    ││
│  │ ETA: 5 Jan 2026                  ││
│  └─────────────────────────────────┘│
│                                      │
│  ⏱️  Timeline                         │
│  • Reported: 2 Jan 14:30            │
│  • Acknowledged: 2 Jan 15:00        │
│  • Parts Ordered: 2 Jan 16:00       │
│  • In Progress: (pending)           │
│                                      │
│  [Inspector: Mark Complete]          │
│  or                                  │
│  [Engineer: Update Status]           │
└─────────────────────────────────────┘
```

---

## API Endpoints Required

### 1. Get Asset with Recent Repairs
```python
@frappe.whitelist()
def get_asset_repair_overview(asset_name, days=30):
    """
    Get asset info + recent repairs for overview page

    Returns:
    {
        "asset": {
            "name": "ACC-ASS-2025-00019",
            "asset_name": "เครื่อง Load...",
            "location": "ห้อง Retort",
            "status": "Active",
            "has_scheduled_maintenance": True
        },
        "repairs": [
            {
                "name": "REP-00234",
                "status": "Open",
                "problem_description": "Motor overheating",
                "creation": "2026-01-02 14:30:00",
                "priority": "High",
                "inspector_name": "สมชาย ใจดี",
                "photo_count": 3,
                "workflow_state": "Waiting Engineer"
            },
            ...
        ],
        "total_repairs": 47,
        "open_repairs": 2,
        "completed_last_30_days": 5
    }
    ```

### 2. Get All Repairs (Paginated)
```python
@frappe.whitelist()
def get_asset_repairs(asset_name, start=0, limit=20, status_filter=None):
    """
    Paginated repair history
    """
```

### 3. Get Repair Detail
```python
@frappe.whitelist()
def get_repair_detail(repair_name):
    """
    Full repair info including timeline, photos, notes
    """
```

---

## Mobile Optimization Checklist

### Touch Targets
- ✅ Min 48x48px (WCAG AAA)
- ✅ Recommended 56x56px for primary actions
- ✅ 16px spacing between tappable elements

### Typography
- ✅ Min 16px body text (prevents iOS zoom on input)
- ✅ 18-20px for buttons
- ✅ 24px+ for headings

### Performance
- ✅ Lazy load repair history (only visible items)
- ✅ Optimize images (thumbnail → full resolution on tap)
- ✅ Cache asset info (localStorage + 5min TTL)

### Accessibility
- ✅ High contrast (4.5:1 minimum)
- ✅ Focus indicators
- ✅ Screen reader labels (aria-label)
- ✅ Semantic HTML (nav, main, article)

### Network Resilience
- ✅ Loading states (skeleton screens)
- ✅ Error states with retry
- ✅ Offline detection
- ✅ Optimistic UI updates

---

## QR Scan Flow Testing

### Test Scenarios

#### Scenario 1: First-time scan (no history)
1. Scan QR → `/asset/ACC-NEW-001`
2. Shows: "No repair history"
3. Prominent: **"REPORT FIRST ISSUE"** button
4. Secondary: "Do Maintenance" button

#### Scenario 2: Scan with open issue
1. Scan QR → `/asset/ACC-ASS-2025-00019`
2. Shows: 🔴 **1 OPEN ISSUE** alert banner
3. Auto-expanded repair card showing current issue
4. Option: "Report Another Issue" or "Update This Issue"

#### Scenario 3: Scan with recent completion
1. Scan QR → `/asset/ACC-ASS-2025-00050`
2. Shows: ✅ **Last repaired 2 days ago**
3. Recent history collapsed by default
4. Normal action buttons

---

## Responsive Breakpoints

```css
/* Mobile First (default) */
.asset-overview {
  padding: 16px;
}

/* Tablet (768px+) */
@media (min-width: 768px) {
  .asset-overview {
    max-width: 600px;
    margin: 0 auto;
    padding: 24px;
  }

  .action-buttons-sticky {
    flex-direction: row;
  }
}

/* Desktop (1024px+) */
@media (min-width: 1024px) {
  .asset-overview {
    display: grid;
    grid-template-columns: 400px 1fr;
    max-width: 1200px;
    gap: 32px;
  }

  .repair-list {
    max-height: calc(100vh - 200px);
    overflow-y: auto;
  }
}
```

---

## Implementation Priority

### Phase 1: Core Functionality (Week 1)
1. Create `/asset/{asset_name}` route
2. Implement `get_asset_repair_overview` API
3. Build AssetOverview component
4. Update QR scan redirect logic
5. Mobile-first CSS

### Phase 2: History & Details (Week 2)
1. Repair history page `/asset/{asset_name}/repairs`
2. Repair detail modal
3. Filter/search functionality
4. Pagination

### Phase 3: Polish & Testing (Week 3)
1. Loading states & animations
2. Error handling
3. Offline detection
4. Real device testing (iOS/Android)
5. Touch target audit
6. Performance optimization

---

## Testing Devices

### Minimum Test Coverage
- iPhone SE (375px - smallest modern iOS)
- iPhone 14 Pro (393px)
- Samsung Galaxy S21 (360px)
- iPad Mini (768px)
- Desktop Chrome (1920px)

### QR Scanner Testing
- Test with actual Niimbot printed labels
- Various lighting conditions
- Different camera qualities
- Test from 10cm, 20cm, 30cm distances

---

## Success Metrics

### User Experience
- Time to report issue: < 30 seconds from QR scan
- Touch success rate: > 95% (no mis-taps)
- Page load time: < 2 seconds on 3G

### Business Impact
- Reduce duplicate repair reports by 40%
- Increase context awareness (inspector sees history)
- Faster engineer response (full info at glance)

---

## Design System Colors

```css
:root {
  /* Status Colors */
  --status-open: #dc2626;      /* Red 600 */
  --status-completed: #16a34a; /* Green 600 */
  --status-rejected: #6b7280;  /* Gray 500 */
  --status-in-progress: #f59e0b; /* Amber 500 */

  /* Priority */
  --priority-high: #dc2626;
  --priority-medium: #f59e0b;
  --priority-low: #3b82f6;

  /* Touch Feedback */
  --touch-active: rgba(0, 0, 0, 0.1);

  /* Spacing */
  --touch-spacing: 16px;
  --touch-target: 56px;
}
```

---

## Next Steps

1. **Review this design** with actual users (inspectors/engineers)
2. **Prototype in Figma** (optional - or go straight to code)
3. **Implement Phase 1** (core overview page)
4. **Test on real devices** with printed QR labels
5. **Iterate based on feedback**

Would you like me to start implementing the AssetOverview component?
