# CT519 Project: Web-ML with Docker Compose (Sleep Disorder Prediction)

โปรเจกต์นี้เป็นการนำโมเดล Machine Learning จากวิชา CT663 สำหรับทำนายความเสี่ยงภาวะผิดปกติการนอนหลับ (Sleep Disorder) มาให้บริการในรูปแบบ Web Application โดยออกแบบสถาปัตยกรรมระบบเป็นแบบ **Microservices** และบริหารจัดการ Container ทั้งหมดด้วย **Docker Compose** โดยทำการปรับแก้ไขไฟล์

---

## สถาปัตยกรรมระบบ (System Architecture)
ระบบถูกแบ่งการทำงานออกเป็น 2 Services หลักที่แยกออกจากกันอย่างเด็ดขาด (Decoupled) เพื่อให้ระบบเบาและทำงานได้รวดเร็ว ดังนี้:

1. **Frontend Service (`ml_frontend`)**
   * **เทคโนโลยี:** Python (Flask), HTML, CSS, Bootstrap
   * **พอร์ต:** `5000`
   * **หน้าที่:** เป็นส่วนติดต่อผู้ใช้งาน (Web UI) รับข้อมูลปัจจัยเสี่ยงต่างๆ จากผู้ใช้ แพ็กเป็นรูปแบบ JSON และส่ง HTTP Request ไปยัง Backend จากนั้นนำผลลัพธ์ที่ได้มาแสดงผลเป็นกราฟิกให้เข้าใจง่าย (ไม่มีการฝังโค้ด ML หรือไลบรารีขนาดใหญ่ในส่วนนี้)

2. **Backend Service (`ml_backend`)**
   * **เทคโนโลยี:** Python (FastAPI), Pandas, Scikit-learn, Joblib
   * **พอร์ต:** `8000`
   * **หน้าที่:** เป็นสมองประมวลผลหลักของระบบ (API) ทำหน้าที่รับข้อมูล JSON จาก Frontend นำมาแปลงสภาพ (Data Preprocessing) และป้อนเข้าสู่โมเดล Machine Learning (`sleep_disorder_model.pkl`) เพื่อทำนายผลและคืนค่ากลับไปเป็น JSON

---

## 📂 โครงสร้างโฟลเดอร์ (Project Structure)

```text
.
├── backend/                   # ซอร์สโค้ดฝั่ง API
│   ├── Dockerfile
│   ├── main.py                # โค้ด FastAPI
│   ├── requirements.txt       # Dependencies ของ Backend
│   └── *.pkl                  # ไฟล์โมเดล Machine Learning
├── frontend/                  # ซอร์สโค้ดฝั่งหน้าเว็บ
│   ├── Dockerfile
│   ├── app.py                 # โค้ด Flask
│   ├── requirements.txt       # Dependencies ของ Frontend
│   ├── static/                # ไฟล์ CSS, รูปภาพ
│   └── templates/             # ไฟล์ HTML
└── docker-compose.yml         # ไฟล์ตั้งค่าสำหรับรัน Microservices

## วิธีการติดตั้งและรันระบบ (How to Run)
ระบบนี้ถูกตั้งค่า Environment และ Dependencies ทุกอย่างไว้ใน Docker เรียบร้อยแล้ว สามารถรันระบบได้ด้วยคำสั่งเดียว:

1. ตรวจสอบให้แน่ใจว่าติดตั้ง `docker` และ `docker-compose` บนเครื่อง Server แล้ว
2. เปิด Terminal เข้ามาที่โฟลเดอร์หลักของโปรเจกต์
3. รันคำสั่งต่อไปนี้เพื่อสร้างและเปิดใช้งาน Containers:
   ```bash
   docker compose up -d --build
4. หลังจาก Deploy ระบบเรียบร้อยแล้ว สามารถเข้าใช้งานได้ผ่าน URL ดังนี้
• Frontend (ส่วนติดต่อผู้ใช้งาน)
  http://<IP-Server>:5000
• Backend (เอกสาร API และหน้าทดสอบการเรียกใช้งาน Swagger UI)
  http://<IP-Server>:8000/docs
