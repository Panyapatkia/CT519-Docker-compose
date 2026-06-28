from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
import pandas as pd
import joblib
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# โหลดไฟล์โมเดล
MODEL_PATH = BASE_DIR / "sleep_disorder_model.pkl"
COLUMNS_PATH = BASE_DIR / "model_columns.pkl"
LABELS_PATH = BASE_DIR / "label_classes.pkl"

model = joblib.load(MODEL_PATH)
model_columns = list(joblib.load(COLUMNS_PATH))
label_classes = list(joblib.load(LABELS_PATH))

# จุดที่แก้: เปลี่ยน Request เป็น Body(...) เพื่อให้ Swagger UI สร้างกล่องรับ JSON
@app.post("/predict")
async def predict(data: dict = Body(..., example={
    "gender": "Male",
    "age": 30,
    "occupation": "Software Engineer",
    "sleep_duration": 7.5,
    "quality_of_sleep": 8,
    "physical_activity": 60,
    "stress_level": 5,
    "daily_steps": 8000,
    "heart_rate": 70,
    "bmi_category": "Normal",
    "bp_systolic": 120,
    "bp_diastolic": 80,
    "resolved_occupation": "Software Engineer",
    "normalized_bmi": "Normal"
})):
    try:
        resolved_occupation = data.get("resolved_occupation", "Accountant")
        bmi_category = data.get("normalized_bmi", "Normal")
        
        df_input = pd.DataFrame([{
            "Gender": 1 if data.get("gender") == "Male" else 0,
            "Age": int(data.get("age", 0)),
            "Sleep Duration": float(data.get("sleep_duration", 0)),
            "Quality of Sleep": int(data.get("quality_of_sleep", 0)),
            "Physical Activity Level": int(data.get("physical_activity", 0)),
            "Stress Level": int(data.get("stress_level", 0)),
            "BP_Systolic": int(data.get("bp_systolic", 0)),
            "BP_Diastolic": int(data.get("bp_diastolic", 0)),
            "Heart Rate": int(data.get("heart_rate", 0)),
            "Daily Steps": int(data.get("daily_steps", 0)),
            "Occupation": resolved_occupation,
            "BMI Category": bmi_category,
        }])
        
        df_input = pd.get_dummies(df_input, columns=["Occupation", "BMI Category"], drop_first=True)
        
        for col in model_columns:
            if col not in df_input.columns:
                df_input[col] = 0
                
        df_input = df_input[model_columns]
        
        pred = model.predict(df_input)[0]
        prediction = label_classes[int(pred)]
        
        probabilities = {}
        confidence = 0.0
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(df_input)[0]
            probabilities = {
                label_classes[i]: round(float(probs[i]) * 100, 2)
                for i in range(len(label_classes))
            }
            confidence = round(max(probabilities.values()), 2)
            
        return JSONResponse(content={
            "prediction": prediction,
            "probabilities": probabilities,
            "confidence": confidence
        })
        
    except Exception as e:
        logging.error(f"Prediction error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
