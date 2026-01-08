
---

## UPDATES (Based on User Feedback - January 2026)

### 1. CORRECTED WORKFLOW

**Updated Flow:**
```
Asset User scans QR
→ Reports issue via /maintenance portal
→ Creates Asset Repair (source: "User Report")
→ Auto-assign to Maintenance Engineer
→ Engineer inspects issue and fills assessment
→ Engineer submits to Manager for approval
→ Manager Approves/Rejects
→ (If Approved) Engineer performs repair
→ Asset User confirms completion
→ Status: Finished
```

### 2. COMPLETE FM-EN-04 STRUCTURE (All 5 Sections + Section 0)

**Section 0: Document Header** (NEW - ส่วนหัวเอกสาร)
- Repair Type: ซ่อม / แก้ไข / ติดตั้งใหม่ / ปรับปรุง
- Date (วันที่)
- Repair ID (เลขที่ใบแจ้ง)

**Section 1: Asset Info & Reporter** (ข้อมูลเครื่องจักรและผู้แจ้งซ่อม)
- ชื่อแผนก (Department)
- ชื่อเครื่องจักร/อุปกรณ์ (Asset Name)
- รหัสเครื่องจักร/อุปกรณ์ (Item Code)
- เลขที่เครื่องจักร (Asset ID)
- รายละเอียด/สิ่งที่ดำเนินการ (Problem Description)
- ต้นสังกัดผู้แจ้งอนุมัติ (Reporter's Head Approval + Date)
- ผู้อนุมัติ (Manager Approval + Date)

**Section 2: For Engineering Department** (สำหรับฝ่ายวิศวกรรม)
- การดำเนินการ (Action Type): ช่างภายใน/ช่างภายนอก/มีค่าใช้จ่าย/ไม่มีค่าใช้จ่าย
- รายการ/สิ่งที่ต้องทำ (Todo List) + การแก้ไข/การดำเนินงาน (Procedure) + ผู้ดำเนินงาน (Responsible)
- รายการอะไหล่ที่ใช้ (Spare Parts Used):
  - ลำดับ (Item No)
  - รายการ (Description)
  - ใบขอซื้อ/เลขที่ (PO Number)
  - จำนวน (Quantity)
  - หมายเหตุ (Remarks)
- ระยะเวลาดำเนินการ (Expected Duration) + วันที่เริ่มต้น + วันที่สิ้นสุด

**Section 3: Post-Repair Verification** (ตรวจสอบหลังการซ่อม)
- ผู้ประเมิน (Evaluator Signature + Date)
- ผู้ควบคุมตรวจสอบ (Head of Engineering Signature + Date)
- ผู้อนุมัติ (Manager Signature + Date)
- ตรวจรับงาน (Inspector Verification):
  - ผลการดำเนินการ (Result): เรียบร้อย / ไม่เรียบร้อย / อื่นๆ
  - วันที่ส่งมอบงาน (Completion Handover Date)

**Section 4: Hygiene & Safety** (บันทึกสุขลักษณะ/ความปลอดภัย)
- สถานะ: เรียบร้อย/สะอาดไม่เสี่ยงต่อการปนเปื้อน OR ไม่เรียบร้อย/ต้องแก้ไข
- ความสะอาดเครื่องจักรก่อนซ่อม (สะอาด/ไม่สะอาด)
- ความสะอาดเครื่องจักรหลังซ่อม (สะอาด/ไม่สะอาด)
- ความสะอาดสถานที่ก่อนซ่อม (สะอาด/ไม่สะอาด)
- ความสะอาดสถานที่หลังซ่อม (สะอาด/ไม่สะอาด)
- อุปกรณ์ที่นำเข้า (Parts Inserted List)
- อุปกรณ์ที่นำออก (Parts Removed List)

**Section 5: Final Remarks** (หมายเหตุ + Signatures)
- หมายเหตุเพิ่มเติม (Additional Remarks)
- ต้นสังกัดผู้แจ้งตรวจรับงาน (Reporter's Head Final Approval + Date)
- วันที่เริ่มใช้แบบฟอร์ม FM-EN-04 และผู้อนุมัติ (Form Usage Start Date + Approval Signature)

### 3. SPARE PARTS TRACKING

**New Child Table: Repair Spare Part**
Fields:
- item_no (ลำดับ)
- item_code (รหัสอะไหล่) - Link to Item
- item_name (รายการ) - Auto-fetched
- purchase_order (ใบขอซื้อ/เลขที่) - Link to Purchase Order
- qty (จำนวน) - Float
- uom (หน่วย) - Link to UOM
- warehouse (คลังสินค้า) - Link to Warehouse
- remarks (หมายเหตุ) - Small Text

**Auto Stock Entry Creation:**
- When repair is completed, auto-create Stock Entry (Material Issue)
- Links spare parts to inventory system
- Tracks consumption against Asset Repair

**Availability Check:**
- Before manager approves, check if spare parts are available
- Alert if stock is insufficient
- Link to Purchase Order if parts need ordering

### 4. MOBILE OPTIMIZATION

**Issues to Fix:**
- Text sizes inconsistent (too big/too small)
- Elements not aligned on mobile screens
- Touch targets too small
- Images not responsive

**Solution: Mobile-First CSS Framework**
```css
:root {
    --font-xs: 12px;
    --font-sm: 14px;
    --font-base: 16px;
    --font-lg: 18px;
    --font-xl: 20px;
    --font-2xl: 24px;
    --touch-target: 56px;
    --spacing-md: 16px;
    --border-radius: 8px;
}

body {
    font-size: var(--font-base);
    line-height: 1.5;
}

h1 { font-size: var(--font-2xl); }
h2 { font-size: var(--font-xl); }
h3 { font-size: var(--font-lg); }

button, .btn {
    min-height: var(--touch-target);
    padding: var(--spacing-md);
    font-size: var(--font-base);
}

.grid {
    display: grid;
    gap: var(--spacing-md);
    grid-template-columns: 1fr;
}

@media (min-width: 768px) {
    .grid { grid-template-columns: repeat(2, 1fr); }
}
```

Apply to all /maintenance portal pages for consistency.

### 5. UPDATED WORKFLOW STATES

```
Draft (ร่าง)
  → Pending Engineering Assessment (รอช่างตรวจสอบ) [NEW STATE]
    → Pending Manager Approval (รอผู้จัดการอนุมัติ)
      → Approved (อนุมัติ - กำลังซ่อม)
        → Pending Verification (รอตรวจรับงาน)
          → Finished (เสร็จสิ้น) [LOCKED - No Edit]
      → Rejected (ปฏิเสธ) [LOCKED - No Edit]
```

**Key Changes:**
- Added "Pending Engineering Assessment" state (Engineer fills assessment before manager sees it)
- Finished state: allow_edit = "No One" (completely locked)
- Auto-assign engineer when repair is created

### 6. CHILD DOCTYPES TO CREATE

1. **Engineering Todo Item**
   - task_no, task_description, status, completed_by

2. **Repair Spare Part**
   - item_no, item_code, item_name, purchase_order, qty, uom, warehouse, remarks

3. **Parts Inserted Item**
   - item_code, item_name, qty, serial_no

4. **Parts Removed Item**
   - item_code, item_name, qty, serial_no, disposal_method

### 7. IMPLEMENTATION PHASES (UPDATED)

**Phase 1 (Week 1): Critical Structure**
1. Add Section 0 (Repair Type header fields)
2. Add all missing fields from FM-EN-04 Sections 1-5
3. Create 4 child doctypes
4. Reorder fields to match form
5. Lock editing after Finished state

**Phase 2 (Week 2): Workflow & Integration**
6. Add "Pending Engineering Assessment" workflow state
7. Update workflow transitions
8. Implement spare parts Stock Entry auto-creation
9. Add spare parts availability check
10. Test approval flow end-to-end

**Phase 3 (Week 3): Mobile & Portal**
11. Apply mobile CSS framework to all portal pages
12. Fix text alignment and sizing issues
13. Test on iPhone SE, Samsung Galaxy
14. Update Report Issue page
15. Test QR scan → Report → Approve flow

**Phase 4 (Week 4): Testing & Deploy**
16. User acceptance testing
17. Update print format to match FM-EN-04 exactly
18. Update Thai documentation
19. Deploy to production VPS

---

**ALL CORRECTIONS APPLIED ✅**
- Workflow corrected (Engineer → Manager → Repair → User)
- Complete FM-EN-04 structure (Sections 0-5)
- Spare parts tracking designed
- Mobile optimization planned

**Next Step:** Review this updated design, then proceed with Phase 1 implementation.
