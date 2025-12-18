# ⚙️ คู่มือผู้ดูแลระบบ
**บทบาท:** ผู้จัดการระบบ / ผู้ดูแล IT
**แพลตฟอร์ม:** ERPNext Desktop + คอนโซลเซิร์ฟเวอร์
**เวอร์ชัน:** v2.1.0

---

## สารบัญ
1. [ภาพรวม](#ภาพรวม)
2. [สถาปัตยกรรมระบบ](#สถาปัตยกรรมระบบ)
3. [การติดตั้งและการตั้งค่า](#การติดตั้งและการตั้งค่า)
4. [การจัดการผู้ใช้](#การจัดการผู้ใช้)
5. [การจัดการการปรับแต่ง](#การจัดการการปรับแต่ง)
6. [การสำรองและกู้คืนข้อมูล](#การสำรองและกู้คืนข้อมูล)
7. [การติดตามและบำรุงรักษา](#การติดตามและบำรุงรักษา)
8. [การแก้ไขปัญหา](#การแก้ไขปัญหา)
9. [ความปลอดภัยและการปฏิบัติตาม](#ความปลอดภัยและการปฏิบัติตาม)
10. [ขั้นตอนการอัปเกรด](#ขั้นตอนการอัปเกรด)

---

## ภาพรวม

### ความรับผิดชอบของคุณ
ในฐานะ **ผู้ดูแลระบบ** คุณมีหน้าที่:
- ✅ ติดตั้งและกำหนดค่าแอป tub_suite
- ✅ จัดการบัญชีผู้ใช้และบทบาท
- ✅ รักษาประสิทธิภาพระบบ
- ✅ ทำการสำรองและกู้คืนข้อมูล
- ✅ แก้ไขปัญหาทางเทคนิค
- ✅ ใช้การอัปเดตและแพตช์
- ✅ รับประกันความปลอดภัยข้อมูล
- ✅ ฝึกอบรมผู้ใช้และสร้างเอกสาร

### ส่วนประกอบระบบ
```
┌─────────────────────────────────────────┐
│         แพลตฟอร์ม ERPNext v15           │
│  (Frappe Framework v15)                 │
├─────────────────────────────────────────┤
│         แอปปรับแต่ง tub_suite           │
│  - ขั้นตอนการซ่อม Asset Repair          │
│  - พอร์ทัลมือถือพนักงานตรวจสอบ          │
│  - ระบบการอนุมัติ                       │
│  - การจัดการรูปภาพ                      │
│  - การแจ้งเตือน                         │
├─────────────────────────────────────────┤
│         React Frontend                  │
│  - maintenance-react-dev                │
│  - เครื่องสแกน QR                       │
│  - การจับภาพรูปภาพ                      │
├─────────────────────────────────────────┤
│         บริการ Backend                  │
│  - Python API (Frappe)                  │
│  - ฐานข้อมูล MariaDB                    │
│  - Redis Cache                          │
│  - เว็บเซิร์ฟเวอร์ Nginx                 │
│  - Supervisor Process Manager           │
└─────────────────────────────────────────┘
```

---

## สถาปัตยกรรมระบบ

### สภาพแวดล้อมการใช้งานจริง
**เซิร์ฟเวอร์:** tub.x-desk.tech
**ระบบปฏิบัติการ:** Ubuntu 24.04 LTS
**ผู้ใช้:**
- ผู้ใช้เซิร์ฟเวอร์: `taynaja`
- ฐานข้อมูล: MariaDB
- ไซต์: `tub.x-desk.tech`

### โครงสร้างไดเรกทอรี
```
/home/user/frappe-bench/
├── apps/
│   ├── frappe/              # เฟรมเวิร์กหลัก
│   ├── erpnext/             # แอป ERPNext
│   └── tub_suite/           # แอปบำรุงรักษาปรับแต่ง
│       ├── tub_suite/
│       │   ├── api/         # Backend APIs
│       │   ├── overrides/   # DocType overrides
│       │   ├── fixtures/    # ช่องปรับแต่ง workflows
│       │   ├── www/         # เว็บเนื้อหา
│       │   │   └── maintenance/  # ผลลัพธ์ React build
│       │   └── setup/       # สคริปต์ติดตั้ง
│       ├── maintenance-react-dev/  # โค้ดต้นฉบับ React
│       └── docs/            # เอกสาร
├── sites/
│   └── tub.x-desk.tech/
│       ├── private/         # ไฟล์ที่อัปโหลด
│       ├── public/          # ไฟล์เว็บที่เข้าถึงได้
│       └── site_config.json # การกำหนดค่าไซต์
└── logs/                    # บันทึกแอปพลิเคชัน
```

**[ภาพหน้าจอ 1: โครงสร้างไดเรกทอรีผ่าน SSH]**

### สถาปัตยกรรมเครือข่าย
```
อินเทอร์เน็ต
   ↓
HTTPS (443) → Nginx Reverse Proxy
   ↓
ERPNext (พอร์ต 8000) → Gunicorn Workers
   ↓
MariaDB (พอร์ต 3306) → ฐานข้อมูล
   ↓
Redis (พอร์ต 6379) → แคช
```

**[ภาพหน้าจอ 2: การตรวจสอบสถานะพอร์ต]**

---

## การติดตั้งและการตั้งค่า

### การติดตั้งเริ่มต้น (การใช้งานจริง)
**อ้างอิง:** `DEPLOYMENT_GUIDE_v2.1.0.md`

### การตั้งค่าหลังการติดตั้ง

#### ขั้นตอนที่ 1: ติดตั้งช่องปรับแต่งและ Workflows
```bash
bench --site tub.x-desk.tech execute tub_suite.setup.asset_repair_setup.run_production_setup
```

**สิ่งนี้ทำ:**
- ติดตั้งช่องปรับแต่งบน Asset Repair
- สร้าง workflow (Draft → รออนุมัติ → อนุมัติแล้ว → เสร็จสิ้น)
- ตั้งค่า Client Script สำหรับการล็อกช่อง
- กำหนดค่า Property Setters

**[ภาพหน้าจอ 3: รันการตั้งค่าการใช้งานจริง]**

#### ขั้นตอนที่ 2: สร้างบทบาทผู้ใช้
```bash
bench --site tub.x-desk.tech console
```

จากนั้นในคอนโซล:
```python
# สร้างบทบาทปรับแต่ง (ถ้าไม่อยู่ใน fixtures)
from frappe import get_doc

roles = ["Maintenance Inspector", "Maintenance Engineer"]
for role_name in roles:
    if not frappe.db.exists("Role", role_name):
        role = get_doc({
            "doctype": "Role",
            "role_name": role_name,
            "desk_access": 0 if "Inspector" in role_name else 1
        })
        role.insert()
        print(f"✓ สร้างบทบาท: {role_name}")
```

**[ภาพหน้าจอ 4: สร้างบทบาทในคอนโซล]**

#### ขั้นตอนที่ 3: กำหนดค่าสิทธิ์
ไปที่: **Setup → Permissions → Role Permissions Manager**

**สิทธิ์ Asset Repair:**

| บทบาท | อ่าน | เขียน | สร้าง | ส่ง | อนุมัติ |
|---|---|---|---|---|---|
| Maintenance User | ✅ | ✅ | ✅ | ❌ | ❌ |
| Engineering Team | ✅ | ✅ | ❌ | ✅ | ❌ |
| Maintenance Manager | ✅ | ✅ | ❌ | ❌ | ✅ |
| System Manager | ✅ | ✅ | ✅ | ✅ | ✅ |

**[ภาพหน้าจอ 5: Role Permissions Manager]**

#### ขั้นตอนที่ 4: สร้าง React Frontend
```bash
cd ~/frappe-bench/apps/tub_suite/maintenance-react-dev
npm install
npm run build
```

ผลลัพธ์สร้างไปที่: `tub_suite/www/maintenance/assets/`

**[ภาพหน้าจอ 6: ผลลัพธ์ React build]**

#### ขั้นตอนที่ 5: ล้างแคชและรีสตาร์ท
```bash
bench --site tub.x-desk.tech clear-cache
bench restart
```

**[ภาพหน้าจอ 7: ผลลัพธ์ Bench restart]**

---

## การจัดการผู้ใช้

### การสร้างผู้ใช้ใหม่

#### ผู้ใช้พนักงานตรวจสอบ (พอร์ทัลมือถืออย่างเดียว)
1. ไปที่: **Setup → Users → User**
2. คลิก **New**
3. กรอกรายละเอียด:
   - **อีเมล:** inspector1@tipubon.com
   - **ชื่อ:** ชื่อพนักงานตรวจสอบ
   - **ส่งอีเมลต้อนรับ:** ใช่
   - **บทบาท:** เพิ่ม "Maintenance User"
   - **ประเภทผู้ใช้:** Website User (ไม่มีการเข้าถึง desk)

**[ภาพหน้าจอ 8: สร้างผู้ใช้พนักงานตรวจสอบ]**

#### ผู้ใช้ช่าง (การเข้าถึง Desktop)
1. สร้างผู้ใช้ตามข้างบน
2. **บทบาท:** เพิ่ม "Engineering Team"
3. **ประเภทผู้ใช้:** System User (การเข้าถึง desk)

**[ภาพหน้าจอ 9: สร้างผู้ใช้ช่าง]**

#### ผู้ใช้ผู้จัดการ (การเข้าถึง Desktop)
1. สร้างผู้ใช้ตามข้างบน
2. **บทบาท:** เพิ่ม "Maintenance Manager" + "Engineering Team" (ถ้าต้องการ)
3. **ประเภทผู้ใช้:** System User

**[ภาพหน้าจอ 10: สร้างผู้ใช้ผู้จัดการ]**

### การควบคุมการเข้าถึงผู้ใช้

#### จำกัดพนักงานตรวจสอบให้ใช้มือถืออย่างเดียว
ในโปรไฟล์ผู้ใช้:
- **การเข้าถึงโมดูล:** ปิดโมดูลทั้งหมด
- **บทบาท:** เฉพาะ "Maintenance User"
- **ประเภทผู้ใช้:** Website User

พนักงานตรวจสอบควรเข้าถึง: `https://tub.x-desk.tech/maintenance` เท่านั้น

**[ภาพหน้าจอ 11: ข้อจำกัดบทบาทพนักงานตรวจสอบ]**

#### การเข้าถึง Desktop ของช่าง
- **การเข้าถึงโมดูล:** เปิด "Assets" โมดูล
- **บทบาท:** "Engineering Team"
- **จำกัดที่ DocTypes:** Asset Repair เท่านั้น (ผ่าน Role Permissions)

**[ภาพหน้าจอ 12: การเข้าถึงโมดูลของช่าง]**

### การรีเซ็ตรหัสผ่าน
**วิธีที่ 1: รีเซ็ตโดยผู้ดูแล**
1. ไปที่รายการ User
2. คลิกผู้ใช้
3. คลิก **รีเซ็ตรหัสผ่าน**
4. อีเมลส่งไปยังผู้ใช้

**[ภาพหน้าจอ 13: ปุ่มรีเซ็ตรหัสผ่าน]**

**วิธีที่ 2: คอนโซล (ฉุกเฉิน)**
```bash
bench --site tub.x-desk.tech console
```
```python
frappe.set_value("User", "user@example.com", "new_password", "TempPass123!")
frappe.db.commit()
```

---

## การจัดการการปรับแต่ง

### การจัดการช่องปรับแต่ง

#### ดูช่องปรับแต่งปัจจุบัน
```bash
bench --site tub.x-desk.tech console
```
```python
fields = frappe.get_all("Custom Field",
    filters={"dt": "Asset Repair"},
    fields=["fieldname", "label", "fieldtype", "insert_after"]
)
for f in fields:
    print(f)
```

**[ภาพหน้าจอ 14: ผลลัพธ์คอนโซลของช่องปรับแต่ง]**

#### การส่งออก Fixtures ที่สะอาด
**อ้างอิง:** `FIXTURE_MANAGEMENT.md`

```bash
cd ~/frappe-bench/apps/tub_suite
bench --site tub.x-desk.tech export-fixtures
git add tub_suite/fixtures/
git commit -m "อัปเดต fixtures จากการใช้งานจริง"
git push origin v2.1.0
```

**[ภาพหน้าจอ 15: คำสั่งส่งออก fixtures]**

#### การลบช่องปรับแต่ง (คอนโซล)
```python
# ลบช่องปรับแต่งเฉพาะ
field = frappe.get_doc("Custom Field", {"dt": "Asset Repair", "fieldname": "old_field"})
field.delete()
frappe.db.commit()
```

**[ภาพหน้าจอ 16: ลบช่องปรับแต่งในคอนโซล]**

---

## การสำรองและกู้คืนข้อมูล

### การสำรองด้วยตนเอง

#### การสำรองทั้งหมดพร้อมไฟล์
```bash
bench --site tub.x-desk.tech backup --with-files
```

ตำแหน่งการสำรอง: `~/frappe-bench/sites/tub.x-desk.tech/private/backups/`

**[ภาพหน้าจอ 19: ผลลัพธ์คำสั่งสำรอง]**

#### การสำรองฐานข้อมูลอย่างเดียว
```bash
bench --site tub.x-desk.tech backup
```

เร็วกว่า เล็กกว่า ไม่รวมไฟล์ที่อัปโหลด

### การสำรองอัตโนมัติ

#### กำหนดค่า Cron Job
```bash
crontab -e
```

เพิ่ม:
```cron
# การสำรองรายวันเวลา 2 นาฬิกาพร้อมไฟล์
0 2 * * * cd /home/user/frappe-bench && /home/user/.local/bin/bench --site tub.x-desk.tech backup --with-files >> /home/user/backup.log 2>&1

# การล้างรายสัปดาห์ (เก็บ 14 วันล่าสุด)
0 3 * * 0 find /home/user/frappe-bench/sites/tub.x-desk.tech/private/backups/ -name "*.sql.gz" -mtime +14 -delete
```

**[ภาพหน้าจอ 20: การกำหนดค่า Crontab]**

### กู้คืนจากการสำรอง

#### ขั้นตอนที่ 1: แสดงรายการการสำรองที่มี
```bash
ls -lh ~/frappe-bench/sites/tub.x-desk.tech/private/backups/
```

**[ภาพหน้าจอ 21: แสดงรายการไฟล์สำรอง]**

#### ขั้นตอนที่ 2: กู้คืนฐานข้อมูล
```bash
bench --site tub.x-desk.tech restore \
  ~/frappe-bench/sites/tub.x-desk.tech/private/backups/20251218_023000-tub_x_desk_tech-database.sql.gz
```

**[ภาพหน้าจอ 22: คำสั่งกู้คืน]**

#### ขั้นตอนที่ 3: กู้คืนไฟล์ (ถ้าจำเป็น)
```bash
bench --site tub.x-desk.tech restore \
  ~/frappe-bench/sites/tub.x-desk.tech/private/backups/20251218_023000-tub_x_desk_tech-files.tar
```

#### ขั้นตอนที่ 4: ล้างแคชและรีสตาร์ท
```bash
bench --site tub.x-desk.tech clear-cache
bench restart
```

---

## การติดตามและบำรุงรักษา

### การตรวจสอบสุขภาพระบบ

#### ตรวจสอบสถานะ Bench
```bash
bench status
```

ผลลัพธ์แสดง:
- Nginx: ทำงาน/ไม่ทำงาน
- Redis: ทำงาน/หยุด
- Worker: ทำงาน/หยุด

**[ภาพหน้าจอ 23: ผลลัพธ์สถานะ Bench]**

#### ตรวจสอบสถานะ Supervisor
```bash
sudo supervisorctl status
```

**[ภาพหน้าจอ 24: สถานะ Supervisor]**

#### ตรวจสอบการใช้ดิสก์
```bash
df -h
du -sh ~/frappe-bench/sites/tub.x-desk.tech/private/files/
du -sh ~/frappe-bench/sites/tub.x-desk.tech/private/backups/
```

**[ภาพหน้าจอ 25: การตรวจสอบการใช้ดิสก์]**

#### ตรวจสอบขนาดฐานข้อมูล
```bash
bench --site tub.x-desk.tech mariadb
```
```sql
SELECT table_schema "ฐานข้อมูล",
       ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) "ขนาด (MB)"
FROM information_schema.tables
WHERE table_schema = 'bab1fc02fa2ff81c'
GROUP BY table_schema;
```

**[ภาพหน้าจอ 26: คำสั่งขนาดฐานข้อมูล]**

### การติดตามบันทึก

#### บันทึกแอปพลิเคชัน
```bash
tail -f ~/frappe-bench/logs/web.log
tail -f ~/frappe-bench/logs/worker.log
tail -f ~/frappe-bench/logs/console.log
```

**[ภาพหน้าจอ 27: บันทึกแบบ Tailing]**

#### การวิเคราะห์บันทึกข้อผิดพลาด
```bash
grep "ERROR" ~/frappe-bench/logs/*.log | tail -20
```

**[ภาพหน้าจอ 28: ข้อผิดพลาดล่าสุด]**

---

## การแก้ไขปัญหา

### ปัญหาทั่วไป

#### ปัญหา 1: พอร์ทัลมือถือไม่โหลด
**อาการ:** `/maintenance` คืนค่า 404 หรือหน้าว่าง

**การวินิจฉัย:**
```bash
# ตรวจสอบว่า React build มีอยู่
ls -lh ~/frappe-bench/apps/tub_suite/tub_suite/www/maintenance/assets/

# ตรวจสอบการกำหนดเส้นทาง web.py
cat ~/frappe-bench/apps/tub_suite/tub_suite/www/maintenance/index.py
```

**วิธีแก้:**
```bash
cd ~/frappe-bench/apps/tub_suite/maintenance-react-dev
npm run build
bench restart
```

**[ภาพหน้าจอ 32: สร้าง React frontend ใหม่]**

---

#### ปัญหา 2: ข้อผิดพลาด "ต้องการลายเซ็นช่าง"
**สาเหตุ:** Client Script ไม่โหลดหรือถูกแคช

**วิธีแก้:**
```bash
# ติดตั้ง client script ใหม่
bench --site tub.x-desk.tech execute tub_suite.setup.asset_repair_setup.run_production_setup

# ล้างแคช
bench --site tub.x-desk.tech clear-cache
bench restart
```

**[ภาพหน้าจอ 33: คำสั่งติดตั้งการตั้งค่าใหม่]**

---

#### ปัญหา 3: ปุ่ม Workflow หายไป
**อาการ:** ผู้ใช้ไม่เห็นปุ่ม "ส่งขออนุมัติ" หรือ "อนุมัติ"

**การวินิจฉัย:**
1. ตรวจสอบบทบาทผู้ใช้
2. ตรวจสอบสิทธิ์ workflow
3. ตรวจสอบสถานะเอกสาร

**วิธีแก้:**
```bash
bench --site tub.x-desk.tech console
```
```python
# ตรวจสอบสถานะ workflow
doc = frappe.get_doc("Asset Repair", "MAT-REP-2025-00123")
print(f"สถานะ Workflow: {doc.workflow_state}")

# ตรวจสอบบทบาทผู้ใช้
user_roles = frappe.get_roles("user@example.com")
print(f"บทบาท: {user_roles}")
```

**[ภาพหน้าจอ 34: การดีบัก workflow ในคอนโซล]**

---

## ความปลอดภัยและการปฏิบัติตาม

### การควบคุมการเข้าถึง

#### ตรวจสอบสิทธิ์ผู้ใช้
```bash
bench --site tub.x-desk.tech console
```
```python
# แสดงรายการผู้ใช้ทั้งหมดและบทบาท
users = frappe.get_all("User",
    filters={"enabled": 1, "name": ["not in", ["Administrator", "Guest"]]},
    fields=["name", "full_name", "last_login"]
)

for user in users:
    roles = frappe.get_roles(user.name)
    print(f"{user.full_name}: {', '.join(roles)}")
```

**[ภาพหน้าจอ 39: การตรวจสอบบทบาทผู้ใช้]**

### การตรวจสอบย้อนกลับ

#### ดูประวัติเอกสาร
1. เปิด Asset Repair ใดๆ
2. คลิก **เมนู (3 จุด)** → **ประวัติเวอร์ชัน**
3. ดูการเปลี่ยนแปลงทั้งหมดพร้อมเวลาประทับ

**[ภาพหน้าจอ 40: มุมมองประวัติเวอร์ชัน]**

---

## ขั้นตอนการอัปเกรด

### การอัปเกรดแอป tub_suite

#### ขั้นตอนที่ 1: สำรองก่อน (เสมอ)
```bash
bench --site tub.x-desk.tech backup --with-files
```

#### ขั้นตอนที่ 2: ดึงโค้ดล่าสุด
```bash
cd ~/frappe-bench/apps/tub_suite
git fetch origin
git checkout v2.1.0  # หรือเวอร์ชันเฉพาะ
git pull origin v2.1.0
```

**[ภาพหน้าจอ 43: ผลลัพธ์ Git pull]**

#### ขั้นตอนที่ 3: สร้าง React Frontend ใหม่
```bash
cd ~/frappe-bench/apps/tub_suite/maintenance-react-dev
npm install  # อัปเดต dependencies ถ้าจำเป็น
npm run build
```

#### ขั้นตอนที่ 4: รัน Migration
```bash
cd ~/frappe-bench
bench --site tub.x-desk.tech migrate
```

**[ภาพหน้าจอ 44: ผลลัพธ์ Migration]**

#### ขั้นตอนที่ 5: ล้างแคชและรีสตาร์ท
```bash
bench --site tub.x-desk.tech clear-cache
bench restart
```

#### ขั้นตอนที่ 6: ตรวจสอบการอัปเกรด
1. ตรวจสอบเวอร์ชัน:
```bash
bench --site tub.x-desk.tech console
```
```python
app_version = frappe.get_attr("tub_suite.__version__")
print(f"เวอร์ชัน tub_suite: {app_version}")
```

2. ทดสอบการทำงาน:
   - เข้าสู่ระบบเป็นพนักงานตรวจสอบ → ทดสอบพอร์ทัลมือถือ
   - เข้าสู่ระบบเป็นช่าง → ทดสอบการส่งซ่อม
   - เข้าสู่ระบบเป็นผู้จัดการ → ทดสอบการอนุมัติ

**[ภาพหน้าจอ 45: การตรวจสอบเวอร์ชัน]**

---

## ภาคผนวก A: อ้างอิงคำสั่ง

### คำสั่ง Bench
```bash
# การจัดการไซต์
bench new-site site_name
bench drop-site site_name
bench migrate
bench clear-cache
bench restart

# การจัดการแอป
bench get-app app_name
bench install-app app_name --site site_name
bench uninstall-app app_name --site site_name

# สำรอง/กู้คืน
bench backup
bench backup --with-files
bench restore backup_file.sql.gz

# คอนโซล
bench console
bench mariadb

# สร้าง
bench build
bench build --app tub_suite

# อัปเดต
bench update --patch
bench update --reset
```

### การจัดการ Fixture
```bash
# ส่งออก fixtures
bench export-fixtures

# นำเข้า fixture เฉพาะ
bench import-doc fixtures/custom_field.json
```

### คำสั่งคอนโซลที่มีประโยชน์
```python
# โหลด doctype ใหม่
frappe.reload_doctype("Asset Repair")

# ล้างแคชเฉพาะ
frappe.cache().delete_key("key_name")

# รับเอกสาร
doc = frappe.get_doc("Asset Repair", "name")

# คำสั่ง SQL
data = frappe.db.sql("SELECT * FROM `tabAsset Repair` LIMIT 10", as_dict=True)

# คอมมิตการเปลี่ยนแปลงฐานข้อมูล
frappe.db.commit()
```

---

## ภาคผนวก B: รายการภาพหน้าจอ

| # | ภาพหน้าจอที่ต้องการ | สถานะ |
|---|---|---|
| 1-46 | [ดูคู่มือภาษาอังกฤษสำหรับรายการเต็ม] | ⬜ รอดำเนินการ |

---

## ภาคผนวก C: ตำแหน่งไฟล์

### ไฟล์กำหนดค่า
```
~/frappe-bench/sites/tub.x-desk.tech/site_config.json - การตั้งค่าไซต์
/etc/nginx/nginx.conf - การกำหนดค่าเว็บเซิร์ฟเวอร์
/etc/supervisor/conf.d/frappe-bench.conf - ผู้จัดการกระบวนการ
```

### ไฟล์แอปพลิเคชัน
```
~/frappe-bench/apps/tub_suite/tub_suite/hooks.py - การกำหนดค่าแอป
~/frappe-bench/apps/tub_suite/tub_suite/fixtures/ - ช่องปรับแต่ง, workflows
~/frappe-bench/apps/tub_suite/tub_suite/api/ - Backend APIs
~/frappe-bench/apps/tub_suite/tub_suite/overrides/ - DocType overrides
```

### ไฟล์ข้อมูล
```
~/frappe-bench/sites/tub.x-desk.tech/private/files/ - ไฟล์แนบที่อัปโหลด
~/frappe-bench/sites/tub.x-desk.tech/private/backups/ - การสำรองฐานข้อมูล
~/frappe-bench/sites/tub.x-desk.tech/public/files/ - ไฟล์สาธารณะ
```

### ไฟล์บันทึก
```
~/frappe-bench/logs/web.log - คำขอเว็บ
~/frappe-bench/logs/worker.log - งานพื้นหลัง
~/frappe-bench/logs/console.log - ผลลัพธ์คอนโซล
~/frappe-bench/logs/bench.log - การดำเนินการ Bench
```

---

## ติดต่อและการสนับสนุน

### การส่งต่อภายใน
- **ทีมพัฒนา:** [ติดต่อทีมพัฒนา]
- **การสนับสนุน Frappe:** https://discuss.erpnext.com
- **ติดต่อฉุกเฉิน:** [หมายเลขฉุกเฉิน]

### แหล่งข้อมูลภายนอก
- **เอกสาร ERPNext:** https://docs.erpnext.com
- **Frappe Framework:** https://frappeframework.com/docs
- **ที่เก็บ tub_suite:** https://github.com/tstexbj3/tub_suite

---

**เวอร์ชันเอกสาร:** 1.0
**อัปเดตล่าสุด:** 2025-12-18
**ทบทวนครั้งถัดไป:** 2026-01-18
