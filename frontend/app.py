from flask import Flask, render_template, request, jsonify
import requests
from pathlib import Path
import logging
import os

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ดึง URL ของ Backend API จาก Environment Variable (หรือใช้ค่า default ตอนเทสต์)
API_URL = os.environ.get("API_URL", "http://backend-api:8000/predict")

# ย้ายการโหลดโมเดลออกไปทั้งหมด (ลบ joblib.load ออก)
# กำหนด MODEL_INFO เป็นค่าคงที่แทน (เพราะไฟล์ model_info.pkl ย้ายไป Backend แล้ว)
MODEL_INFO = {
    "title": "Sleep Disorder Risk Screening",
    "model_name": "Final Trained Sleep Disorder Model",
    "dataset_size": 374,
    "target": "Sleep Disorder · 3 Classes",
    "deploy_mode": "Microservices (Flask UI -> FastAPI Backend)",
    "best_model": "Loaded in Backend Container",
    "cv_accuracy": "-",
    "cv_macro_f1": "-",
    "final_accuracy": "-",
    "final_precision": "-",
    "final_recall": "-",
    "final_macro_f1": "-",
}

OCCUPATIONS = [
    {"value": "Accountant", "label": "นักบัญชี (Accountant)"},
    {"value": "Doctor", "label": "แพทย์ (Doctor)"},
    {"value": "Engineer", "label": "วิศวกร (Engineer)"},
    {"value": "Lawyer", "label": "นักกฎหมาย / ทนาย (Lawyer)"},
    {"value": "Manager", "label": "ผู้จัดการ / งานบริหาร (Manager)"},
    {"value": "Nurse", "label": "พยาบาล (Nurse)"},
    {"value": "Sales Representative", "label": "พนักงานขายภาคสนาม (Sales Representative)"},
    {"value": "Salesperson", "label": "พนักงานขาย (Salesperson)"},
    {"value": "Scientist", "label": "นักวิทยาศาสตร์ (Scientist)"},
    {"value": "Software Engineer", "label": "วิศวกรซอฟต์แวร์ (Software Engineer)"},
    {"value": "Teacher", "label": "ครู / อาจารย์ (Teacher)"},
]

OCCUPATION_THAI = {
    "Accountant": "นักบัญชี",
    "Doctor": "แพทย์",
    "Engineer": "วิศวกร",
    "Lawyer": "นักกฎหมาย / ทนาย",
    "Manager": "ผู้จัดการ / งานบริหาร",
    "Nurse": "พยาบาล",
    "Sales Representative": "พนักงานขายภาคสนาม",
    "Salesperson": "พนักงานขาย",
    "Scientist": "นักวิทยาศาสตร์",
    "Software Engineer": "วิศวกรซอฟต์แวร์",
    "Teacher": "ครู / อาจารย์",
}

OCCUPATION_GROUPS = [
    ("Accountant", "งานสำนักงาน / เอกสาร / การเงิน"),
    ("Doctor", "งานสายการแพทย์ / สาธารณสุข"),
    ("Nurse", "งานดูแลผู้ป่วย / งานที่เคลื่อนไหวสูง"),
    ("Engineer", "งานด้านเทคนิค / วิศวกรรม"),
    ("Software Engineer", "งาน IT / ซอฟต์แวร์ / นั่งหน้าคอม"),
    ("Scientist", "งานวิจัย / ห้องแล็บ"),
    ("Manager", "งานบริหาร / หัวหน้างาน"),
    ("Lawyer", "งานกฎหมาย / ที่ปรึกษา"),
    ("Teacher", "งานสอน / การศึกษา"),
    ("Salesperson", "งานขาย / บริการลูกค้า"),
    ("Sales Representative", "งานขายภาคสนาม / เดินทางบ่อย"),
]

BMI_OPTIONS = ["Normal", "Overweight", "Obese"]

PREDICTION_INFO = {
    "None": {
        "title": "ผลประเมินเบื้องต้น: ไม่พบความเสี่ยงเด่นชัด",
        "short_label": "ปกติ (None)",
        "description": "จากข้อมูลที่กรอก ระบบยังไม่พบรูปแบบที่เด่นชัดของภาวะผิดปกติการนอนในระดับคัดกรองเบื้องต้น",
        "clinical_note": "รักษาพฤติกรรมการนอน การออกกำลังกาย และการจัดการความเครียดอย่างสม่ำเสมอ",
        "risk_level": "ต่ำ",
        "status": "None",
    },
    "Insomnia": {
        "title": "ผลประเมินเบื้องต้น: มีแนวโน้มภาวะนอนไม่หลับ",
        "short_label": "Insomnia",
        "description": "ระบบพบรูปแบบข้อมูลที่สอดคล้องกับภาวะนอนไม่หลับ เช่น ชั่วโมงการนอนน้อย คุณภาพการนอนต่ำ หรือระดับความเครียดสูง",
        "clinical_note": "ควรปรับพฤติกรรมก่อนนอนและติดตามอาการ หากเป็นต่อเนื่องควรปรึกษาผู้เชี่ยวชาญ",
        "risk_level": "ปานกลาง",
        "status": "Insomnia",
    },
    "Sleep Apnea": {
        "title": "ผลประเมินเบื้องต้น: มีแนวโน้มภาวะหยุดหายใจขณะหลับ",
        "short_label": "Sleep Apnea",
        "description": "ระบบพบรูปแบบข้อมูลที่สอดคล้องกับความเสี่ยง Sleep Apnea เช่น BMI สูง ความดันโลหิตสูง หรืออัตราการเต้นหัวใจขณะพักสูง",
        "clinical_note": "หากมีอาการกรนดัง ง่วงกลางวันมาก หรือสะดุ้งตื่นกลางคืน ควรปรึกษาแพทย์เพื่อประเมินเพิ่มเติม",
        "risk_level": "สูง",
        "status": "Sleep Apnea",
    },
}

BAR_ORDER = ["None", "Insomnia", "Sleep Apnea"]

def normalize_bmi_category(value: str) -> str:
    value = (value or "").strip()
    if value == "Normal Weight":
        return "Normal"
    return value

def valid_occupation_values():
    return [item["value"] for item in OCCUPATIONS]

def resolve_occupation(data: dict) -> str:
    valid_occupations = valid_occupation_values()
    occupation = data.get("occupation", "").strip()

    if occupation == "__other__":
        mapped = data.get("occ_other", "").strip()
        return mapped if mapped in valid_occupations else "Accountant"

    return occupation if occupation in valid_occupations else "Accountant"

# ลบฟังก์ชัน preprocess_input() ออกไป (ย้ายไปทำที่ฝั่ง Backend)

def build_recommendations(data: dict, prediction: str):
    recs = {"priority": [], "monitor": [], "medical": []}

    sleep_duration = float(data.get("sleep_duration", 0))
    quality = int(data.get("quality_of_sleep", 0))
    stress = int(data.get("stress_level", 0))
    activity = int(data.get("physical_activity", 0))
    steps = int(data.get("daily_steps", 0))
    heart_rate = int(data.get("heart_rate", 0))
    bp_sys = int(data.get("bp_systolic", 0))
    bp_dia = int(data.get("bp_diastolic", 0))
    bmi = normalize_bmi_category(data.get("bmi_category", ""))

    if sleep_duration < 7:
        recs["priority"].append("เพิ่มเวลานอนให้เข้าใกล้ 7–9 ชั่วโมงต่อคืน และพยายามนอนให้เป็นเวลา")
    if quality <= 5:
        recs["priority"].append("ลดแสงหน้าจอ คาเฟอีน และกิจกรรมกระตุ้นก่อนนอน เพื่อช่วยเพิ่มคุณภาพการนอน")
    if stress >= 7:
        recs["priority"].append("ระดับความเครียดค่อนข้างสูง ควรเพิ่มกิจกรรมผ่อนคลายก่อนนอน เช่น หายใจลึกหรือทำสมาธิสั้น ๆ")

    if activity < 30:
        recs["monitor"].append("กิจกรรมทางกายค่อนข้างน้อย ลองเพิ่มการเดินหรือออกกำลังกายเบา ๆ อย่างสม่ำเสมอ")
    if steps < 5000:
        recs["monitor"].append("จำนวนก้าวต่อวันค่อนข้างต่ำ ควรเพิ่มการเคลื่อนไหวระหว่างวัน")
    if heart_rate >= 85:
        recs["monitor"].append("อัตราการเต้นหัวใจขณะพักค่อนข้างสูง ควรติดตามร่วมกับความเครียดและการพักผ่อน")
    if bp_sys >= 130 or bp_dia >= 85:
        recs["monitor"].append("ความดันโลหิตค่อนข้างสูง ควรใส่ใจอาหาร การพักผ่อน และการออกกำลังกาย")
    if bmi in {"Overweight", "Obese"}:
        recs["monitor"].append("BMI อยู่ในกลุ่มเสี่ยง การควบคุมน้ำหนักอาจช่วยลดความเสี่ยงด้านการนอน")

    if prediction == "Sleep Apnea":
        recs["medical"].append("หากมีอาการกรนดัง ง่วงกลางวันมาก หรือสะดุ้งตื่นกลางคืน ควรตรวจเพิ่มเติมกับแพทย์")
    elif prediction == "Insomnia":
        recs["medical"].append("หากมีอาการนอนไม่หลับต่อเนื่องหลายสัปดาห์ ควรปรึกษาแพทย์หรือผู้เชี่ยวชาญด้านการนอน")
    elif not any(recs.values()):
        recs["priority"].append("ภาพรวมอยู่ในเกณฑ์ดี ควรรักษาพฤติกรรมการนอนและสุขภาพแบบนี้ต่อไป")

    return recs

@app.route("/")
def home():
    return render_template("home.html", model_info=MODEL_INFO)

@app.route("/assessment")
def assessment():
    return render_template(
        "assessment.html",
        model_info=MODEL_INFO,
        occupations=OCCUPATIONS,
        occupation_groups=OCCUPATION_GROUPS,
        bmi_options=BMI_OPTIONS,
    )

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", model_info=MODEL_INFO)

@app.route("/about")
def about():
    return render_template("about.html", model_info=MODEL_INFO)

@app.route("/health")
def health():
    return jsonify({"status": "ok", "frontend": True, "api_url": API_URL})

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)

        required_fields = [
            "gender", "age", "occupation",
            "sleep_duration", "quality_of_sleep",
            "physical_activity", "stress_level",
            "daily_steps", "heart_rate",
            "bmi_category", "bp_systolic", "bp_diastolic"
        ]

        missing = [f for f in required_fields if f not in data or str(data[f]).strip() == ""]
        if missing:
            return jsonify({"error": f"กรุณากรอกข้อมูลให้ครบ: {', '.join(missing)}"}), 400

        # ทำ Data Validation พื้นฐาน (เหมือนเดิม)
        age = int(data["age"])
        sleep_duration = float(data["sleep_duration"])
        quality = int(data["quality_of_sleep"])
        activity = int(data["physical_activity"])
        stress = int(data["stress_level"])
        steps = int(data["daily_steps"])
        heart_rate = int(data["heart_rate"])
        bp_sys = int(data["bp_systolic"])
        bp_dia = int(data["bp_diastolic"])

        if not (1 <= age <= 120):
            return jsonify({"error": "อายุต้องอยู่ระหว่าง 1 ถึง 120 ปี"}), 400
        if not (0 <= sleep_duration <= 24):
            return jsonify({"error": "ชั่วโมงการนอนต้องอยู่ระหว่าง 0 ถึง 24"}), 400

        # จุดที่เปลี่ยน: ส่ง Request ไปให้ Backend API แทนการโหลดโมเดลตรงๆ
        try:
            # เพิ่มฟิลด์ที่ resolve แล้วส่งไปด้วย
            data['resolved_occupation'] = resolve_occupation(data)
            data['normalized_bmi'] = normalize_bmi_category(data["bmi_category"])
            
            response = requests.post(API_URL, json=data, timeout=5)
            response.raise_for_status()
            api_result = response.json()
            
            prediction = api_result.get("prediction", "None")
            probabilities = api_result.get("probabilities", {})
            confidence = api_result.get("confidence", 0.0)
            
        except requests.exceptions.RequestException as e:
            app.logger.error(f"API Error: {e}")
            return jsonify({"error": "ไม่สามารถเชื่อมต่อกับระบบ AI ได้ในขณะนี้ (API Timeout/Error)"}), 503

        resolved_occ = resolve_occupation(data)
        info = PREDICTION_INFO.get(prediction, {
            "title": prediction,
            "short_label": prediction,
            "description": "",
            "clinical_note": "",
            "risk_level": "-",
            "status": prediction,
        })

        return jsonify({
            "prediction": prediction,
            "title": info["title"],
            "short_label": info["short_label"],
            "description": info["description"],
            "clinical_note": info["clinical_note"],
            "risk_level": info["risk_level"],
            "status": info["status"],
            "confidence": confidence,
            "probabilities": probabilities,
            "recommendations": build_recommendations(data, prediction),
            "resolved_occupation": resolved_occ,
            "resolved_occupation_label": f'{OCCUPATION_THAI.get(resolved_occ, resolved_occ)} ({resolved_occ})',
            "display_order": BAR_ORDER,
        })

    except Exception:
        app.logger.exception("Prediction request failed")
        return jsonify({"error": "เกิดข้อผิดพลาดในการรับ-ส่งข้อมูล"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
