#!/usr/bin/env python3
"""Quick start server for testing"""

import sys
import os

# Prevent problematic imports
sys.dont_write_bytecode = True

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="DiagnoNET Quick Test")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Quick test server running"}

@app.post("/xray-chest-analysis")
async def test_xray_upload(
    xray_image: UploadFile = File(...),
    generate_gradcam: bool = Form(True),
    generate_explanation: bool = Form(True),
    patient_name: str = Form(None),
    patient_age: int = Form(None),
    patient_height: str = Form(None)
):
    """Test X-ray upload endpoint"""
    try:
        # Read file info
        file_size = len(await xray_image.read())
        await xray_image.seek(0)  # Reset file pointer
        
        return {
            "status": "success",
            "message": "File upload working!",
            "file_info": {
                "filename": xray_image.filename,
                "content_type": xray_image.content_type,
                "size_bytes": file_size
            },
            "patient_info": {
                "name": patient_name,
                "age": patient_age,
                "height": patient_height
            },
            "primary_finding": "Test Upload Successful",
            "confidence": 0.95,
            "recommendations": ["File upload is working correctly"]
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Upload failed: {str(e)}"
        }

if __name__ == "__main__":
    print("🚀 Starting Quick Test Server...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
