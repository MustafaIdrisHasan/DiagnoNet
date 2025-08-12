#!/usr/bin/env python3
"""Presentation-ready DiagnoNET server"""

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import random

app = FastAPI(title="DiagnoNET 2.0 - Presentation Demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "DiagnoNET 2.0 - AI Medical Diagnosis Platform", "status": "ready"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "DiagnoNET 2.0 Operational"}

@app.post("/biogpt-analysis")
async def vitals_analysis(
    vitals_data: str = Form(...),
    symptoms_text: str = Form(None),
    patient_name: str = Form(None),
    patient_age: int = Form(None),
    patient_height: str = Form(None),
    patient_weight: str = Form(None)
):
    """Vitals and symptoms analysis"""
    vitals = json.loads(vitals_data)
    
    # Demo vitals analysis
    conditions = ["Hypertension", "Tachycardia", "Normal", "Fever"]
    diagnosis = random.choice(conditions)
    
    return {
        "status": "success",
        "final_diagnosis": diagnosis,
        "confidence": 0.85,
        "patient_info": {
            "name": patient_name,
            "age": patient_age,
            "height": patient_height,
            "weight": patient_weight
        },
        "vitals_analysis": {
            "systolic_bp": vitals.get("systolic_bp"),
            "diastolic_bp": vitals.get("diastolic_bp"),
            "heart_rate": vitals.get("heart_rate"),
            "assessment": "Analyzed successfully"
        },
        "recommendations": [
            "Monitor blood pressure regularly",
            "Follow up with healthcare provider",
            "Maintain healthy lifestyle"
        ],
        "urgency_level": "MODERATE",
        "agent_agreement": "Vitals Agent + ML Analysis"
    }

@app.post("/xray-chest-analysis")
async def xray_analysis(
    xray_image: UploadFile = File(...),
    generate_gradcam: bool = Form(True),
    patient_name: str = Form(None),
    patient_age: int = Form(None),
    patient_height: str = Form(None)
):
    """X-ray analysis demo"""
    content = await xray_image.read()
    
    findings = ["Normal", "Pneumonia", "Pleural Effusion", "Cardiomegaly"]
    primary_finding = random.choice(findings)
    
    return {
        "status": "success",
        "primary_finding": primary_finding,
        "confidence": 0.92,
        "patient_info": {
            "name": patient_name,
            "age": patient_age,
            "height": patient_height
        },
        "file_info": {
            "filename": xray_image.filename,
            "size": len(content),
            "type": xray_image.content_type
        },
        "analysis_results": {
            "pathology_detected": primary_finding != "Normal",
            "urgency": "MODERATE" if primary_finding != "Normal" else "LOW"
        },
        "recommendations": [
            "Clinical correlation recommended",
            "Follow-up imaging if symptoms persist",
            "Consult radiologist for detailed interpretation"
        ],
        "gradcam_available": generate_gradcam
    }

@app.post("/symptoms-analysis")
async def symptoms_analysis(symptoms_text: str = Form(...)):
    """Symptoms analysis demo"""
    diseases = ["Influenza", "Common Cold", "Pneumonia", "Bronchitis"]
    disease = random.choice(diseases)
    
    return {
        "status": "success",
        "primary_diagnosis": disease,
        "confidence": 0.78,
        "symptoms_detected": symptoms_text.split()[:3],
        "urgency_level": "MODERATE",
        "recommendations": [
            "Rest and hydration",
            "Monitor symptoms",
            "Seek medical attention if worsening"
        ]
    }

@app.post("/file-upload-analysis")
async def file_upload_analysis(
    file: UploadFile = File(...),
    patient_name: str = Form(None),
    patient_age: int = Form(None),
    patient_height: str = Form(None),
    patient_weight: str = Form(None)
):
    """File upload analysis for presentation"""
    content = await file.read()
    
    return {
        "status": "success",
        "message": "✅ File Upload Working Perfectly!",
        "analysis_complete": True,
        "patient_demographics": {
            "name": patient_name,
            "age": patient_age,
            "height": patient_height,
            "weight": patient_weight
        },
        "file_details": {
            "filename": file.filename,
            "size_mb": round(len(content) / 1024 / 1024, 2),
            "type": file.content_type
        },
        "ai_analysis": {
            "primary_finding": "Analysis Complete",
            "confidence": 0.95,
            "recommendations": [
                "File processed successfully",
                "All patient demographics captured",
                "Ready for clinical review"
            ]
        }
    }

if __name__ == "__main__":
    print("🚀 Starting DiagnoNET 2.0 Presentation Server...")
    print("✅ All agents ready for demo!")
    uvicorn.run(app, host="0.0.0.0", port=8001)
