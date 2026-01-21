# FM-EN-04 Print Format Updates (2026-01-21)

## Optimizations for A4 Fit

All changes made to ensure the entire print format fits on a single A4 page:

### Header Section
- Changed from full border to bottom underline only: `border-bottom: 1px solid #333`
- Reduced padding: `3px 0 5px 0` (was `8px` all sides)
- Reduced margin-bottom: `5px` (was `10px`)
- Right-aligned title section (ใบแจ้งซ่อม/ติดตั้งใหม่, FM-EN-04, document number)

### Tables
- Font size: `8px` (was `10px`)
- Cell padding: `1px 2px` (was `3px 4px`)
- Table margin: `1px 0` (was `5px 0`)

### Section Titles
- Font size: `12px` (was `14px`)
- Padding: `3px` (was `5px`)
- Margin: `5px 0 3px 0` (was `12px 0 8px 0`)

### Signature Boxes (Three-box layout)
- Signature image size: `100px × 50px` (was `80px × 35px`)
- Signature line margin-top: `10px` (was `20px`)
- Box margin: `3px 0` (was `5px 0`)
- Font size: `9px` (was `10px`)

### Two-Column Layout
- Row margin: `1px 0` (was `8px 0`)
- Added `align-items: center` for vertical centering of signature boxes

### Spacing Adjustments
- Added `5px` margin-bottom to Subject line
- Reduced spare parts label margin-top: `2px` (was `5px`)
- Reduced duration line margin-top: `2px` (was `5px`)

### Signature Field Names
Fixed to use correct database field names with fallbacks:
- ตัวแทนผู้แจ้ง: `supervisor_section1_signature` → fallback to `reporter_signature`
- ผู้อนุมัติ(GM): `custom_gm_signature` → `gm_section1_signature` → `approval_signature`

## Result
✅ All content now fits on single A4 page without overflow
✅ Maintains readability with 8px table font
✅ Proper signature field mapping to database
