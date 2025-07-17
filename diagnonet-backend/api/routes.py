from fastapi import APIRouter, HTTPException, File, UploadFile, Form, BackgroundTasks
from pydantic import BaseModel, Field, ValidationError
from typing import Dict, Optional, List, Any, Union
from agents.vitals_agent import VitalsAgent
from agents.supervisor_agent import SupervisorAgent, SupervisorOutput, SupervisorInput, AgentOutput, MLDiagnosis
# Direct imports from symptoms model folder
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents', 'symptoms model'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents', 'x-ray chest'))

from streamlined_medical_ai import StreamlinedMedicalAI
import run_cxr
import logging
import json
import requests
import time
import shutil
from uuid import uuid4
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize the agents
vitals_agent = VitalsAgent()
symptoms_ai = StreamlinedMedicalAI()
supervisor_agent = SupervisorAgent()

# Enhanced X-ray analysis class
class EnhancedXRayAgent:
    """Enhanced X-ray analysis using run_cxr module"""

    def __init__(self):
        self.initialized = True
        logger.info("Enhanced X-ray agent initialized")

    def analyze_xray_image(self, image_data: bytes, filename: str,
                          topk: int = 18, generate_gradcam: bool = True,
                          generate_explanation: bool = True) -> Dict[str, Any]:
        """Analyze X-ray image using run_cxr module"""
        try:
            import tempfile
            import os
            from PIL import Image
            import io

            # Save image data to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                # Convert and standardize image
                image = Image.open(io.BytesIO(image_data))

                # Convert to grayscale if needed
                if image.mode != 'L':
                    image = image.convert('L')

                # Resize to standard size (512x512) for consistency
                image = image.resize((512, 512), Image.Resampling.LANCZOS)

                # Save as PNG
                image.save(temp_file.name, 'PNG')
                temp_image_path = temp_file.name

            # Run X-ray analysis
            result = run_cxr.analyze_xray(
                image_path=temp_image_path,
                topk=topk,
                mc_dropout=0,  # Disable MC dropout for faster inference
                cam_label=None,  # Use top prediction for GradCAM
                no_cam=not generate_gradcam,
                no_explain=not generate_explanation
            )

            # Clean up temporary file
            try:
                os.unlink(temp_image_path)
            except:
                pass

            # Format the response for DiagnoNet compatibility
            return self._format_for_diagnonet(result, filename)

        except Exception as e:
            logger.error(f"X-ray analysis failed: {str(e)}")
            return {
                "error": f"X-ray analysis failed: {str(e)}",
                "primary_finding": "Analysis failed",
                "confidence": 0.0
            }

    def _format_for_diagnonet(self, cxr_result: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """Format the run_cxr result for DiagnoNet compatibility"""
        try:
            # Extract key information
            pathologies = cxr_result.get('pathologies', [])
            top_label = cxr_result.get('top_label', 'Unknown')
            top_prob = cxr_result.get('top_prob', 0.0)
            clinical_explanation = cxr_result.get('clinical_explanation', '')
            gradcam_b64 = cxr_result.get('gradcam_b64')

            # Format pathology findings
            findings = []
            for label, prob in pathologies:
                findings.append({
                    'pathology': label,
                    'confidence': round(prob, 3),
                    'confidence_percentage': round(prob * 100, 1),
                    'severity': self._assess_pathology_severity(label, prob)
                })

            # Assess overall severity
            overall_severity = self._assess_overall_severity(top_label, top_prob)

            # Generate recommendations
            recommendations = self._generate_recommendations(top_label, top_prob, overall_severity)

            # Create formatted result
            formatted_result = {
                "primary_finding": top_label,
                "confidence": round(top_prob, 3),
                "confidence_percentage": round(top_prob * 100, 1),
                "findings": findings,
                "pathology_count": len(findings),
                "clinical_explanation": clinical_explanation if clinical_explanation else None,
                "severity": overall_severity,
                "recommendations": recommendations,
                "technical_quality": "good",
                "gradcam_visualization": {
                    "available": gradcam_b64 is not None,
                    "base64_image": gradcam_b64,
                    "target_pathology": top_label
                } if gradcam_b64 else None,
                "agent_type": "xray_chest_analysis",
                "image_filename": filename,
                "analysis_parameters": {
                    "model": "TorchXRayVision DenseNet121",
                    "topk_predictions": len(findings),
                    "gradcam_enabled": gradcam_b64 is not None,
                    "clinical_explanation_enabled": clinical_explanation is not None
                },
                "timestamp": self._get_timestamp()
            }

            return formatted_result

        except Exception as e:
            logger.error(f"Error formatting result: {str(e)}")
            return {
                "error": f"Result formatting failed: {str(e)}",
                "primary_finding": "Formatting error",
                "confidence": 0.0
            }

    def _assess_pathology_severity(self, pathology: str, confidence: float) -> str:
        """Assess severity of individual pathology"""
        high_severity = ['Pneumothorax', 'Pneumonia', 'Lung Opacity', 'Consolidation', 'Pleural Effusion']
        medium_severity = ['Cardiomegaly', 'Atelectasis', 'Emphysema', 'Fibrosis']

        if pathology in high_severity and confidence > 0.6:
            return 'HIGH'
        elif pathology in high_severity and confidence > 0.4:
            return 'MODERATE'
        elif pathology in medium_severity and confidence > 0.7:
            return 'MODERATE'
        elif confidence > 0.8:
            return 'MODERATE'
        else:
            return 'LOW'

    def _assess_overall_severity(self, top_finding: str, confidence: float) -> str:
        """Assess overall severity based on top finding"""
        critical_findings = ['Pneumothorax', 'Pneumonia']
        high_findings = ['Lung Opacity', 'Consolidation', 'Pleural Effusion']

        if top_finding in critical_findings and confidence > 0.7:
            return 'CRITICAL'
        elif top_finding in critical_findings and confidence > 0.5:
            return 'HIGH'
        elif top_finding in high_findings and confidence > 0.6:
            return 'HIGH'
        elif confidence > 0.8:
            return 'MODERATE'
        else:
            return 'LOW'

    def _generate_recommendations(self, finding: str, confidence: float, severity: str) -> List[str]:
        """Generate clinical recommendations based on findings"""
        recommendations = []

        if severity == 'CRITICAL':
            recommendations.append('Immediate emergency medical attention required')
            recommendations.append('Consider urgent chest imaging follow-up')
        elif severity == 'HIGH':
            recommendations.append('Urgent medical consultation recommended')
            recommendations.append('Clinical correlation with symptoms advised')
        elif severity == 'MODERATE':
            recommendations.append('Medical evaluation recommended')
            recommendations.append('Follow-up imaging may be indicated')
        else:
            recommendations.append('Routine medical consultation if symptomatic')
            recommendations.append('Continue regular health monitoring')

        # Specific recommendations based on finding
        if 'Pneumonia' in finding:
            recommendations.append('Consider antibiotic therapy evaluation')
        elif 'Cardiomegaly' in finding:
            recommendations.append('Cardiac evaluation recommended')
        elif 'Pneumothorax' in finding:
            recommendations.append('Immediate chest decompression may be needed')

        return recommendations

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

# Initialize enhanced X-ray agent
xray_chest_agent = EnhancedXRayAgent()

class VitalsPayload(BaseModel):
    """Pydantic model for vital signs input"""
    systolic_bp: float = Field(..., ge=50, le=300, description="Systolic blood pressure (mmHg)")
    diastolic_bp: float = Field(..., ge=30, le=200, description="Diastolic blood pressure (mmHg)")
    heart_rate: float = Field(..., ge=30, le=250, description="Heart rate (beats per minute)")
    temperature: float = Field(..., ge=30, le=45, description="Body temperature (Celsius)")
    respiratory_rate: float = Field(..., ge=5, le=50, description="Respiratory rate (breaths per minute)")
    oxygen_saturation: float = Field(..., ge=70, le=100, description="Oxygen saturation (%)")
    
    class Config:
        schema_extra = {
            "example": {
                "systolic_bp": 120,
                "diastolic_bp": 80,
                "heart_rate": 72,
                "temperature": 98.6,
                "respiratory_rate": 16,
                "oxygen_saturation": 98
            }
        }

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    message: str

class MultiAgentSummaryRequest(BaseModel):
    """Request model for multi-agent summary"""
    patient_info: Optional[Dict] = Field(None, description="Patient information and demographics")
    vitals_result: Optional[Dict] = Field(None, description="Results from vitals analysis")
    symptoms_result: Optional[Dict] = Field(None, description="Results from symptoms analysis")
    xray_result: Optional[Dict] = Field(None, description="Results from X-ray analysis")

    class Config:
        schema_extra = {
            "example": {
                "patient_info": {
                    "name": "John Doe",
                    "age": 45,
                    "height": "175 cm",
                    "weight": "80 kg"
                },
                "vitals_result": {
                    "primary_diagnosis": "Hypertension Stage 1",
                    "confidence": 0.85,
                    "severity": "HIGH"
                },
                "symptoms_result": {
                    "symptoms_detected": ["chest_pain", "shortness_of_breath"],
                    "urgency_level": "Urgent"
                },
                "xray_result": {
                    "primary_finding": "Lung Opacity",
                    "confidence": 0.73,
                    "clinical_explanation": "Lung opacity present indicating inflammatory process"
                }
            }
        }

class MultiAgentSummaryResponse(BaseModel):
    """Response model for multi-agent summary"""
    patient_info: Optional[Dict] = Field(None, description="Patient information and demographics")
    clinical_summary: str = Field(..., description="Comprehensive clinical summary")
    overall_assessment: str = Field(..., description="Overall clinical assessment")
    urgency_level: str = Field(..., description="Overall urgency level")
    key_findings: List[str] = Field(..., description="Key findings from all agents")
    confidence_score: float = Field(..., description="Overall confidence score")
    agents_analyzed: List[str] = Field(..., description="List of agents that provided data")
    recommendations: List[str] = Field(..., description="Combined recommendations")

    class Config:
        schema_extra = {
            "example": {
                "patient_info": {
                    "name": "John Doe",
                    "age": 45,
                    "height": "175 cm"
                },
                "clinical_summary": "Patient presents with hypertensive episode accompanied by respiratory symptoms and chest X-ray findings suggestive of lung opacity.",
                "overall_assessment": "Moderate to high clinical concern requiring immediate medical attention",
                "urgency_level": "HIGH",
                "key_findings": ["Hypertension Stage 1", "Respiratory symptoms", "Lung opacity"],
                "confidence_score": 0.78,
                "agents_analyzed": ["vitals", "symptoms", "xray"],
                "recommendations": ["Immediate blood pressure management", "Respiratory evaluation", "Follow-up imaging"]
            }
        }

@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "DiagnoNet BioGPT Medical AI",
        "version": "2.0.0",
        "endpoints": {
            "health": "/health",
            "biogpt_analysis": "/biogpt-analysis",
            "symptoms_analysis": "/symptoms-analysis",
            "xray_chest_analysis": "/xray-chest-analysis",
            "multimodal_analysis": "/multimodal-analysis",
            "multi_agent_summary": "/multi-agent-summary"
        }
    }

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Quick vitals agent test
        test_vitals = {
            "systolic_bp": 120,
            "diastolic_bp": 80,
            "heart_rate": 72,
            "temperature": 98.6,
            "respiratory_rate": 16,
            "oxygen_saturation": 98
        }
        
        vitals_agent.analyze_vitals(test_vitals)
        
        return HealthResponse(
            status="healthy",
            message="BioGPT Medical AI System Operational"
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"System health check failed: {str(e)}"
        )

@router.post("/biogpt-analysis", response_model=SupervisorOutput)
async def biogpt_medical_analysis(
    vitals_data: str = Form(..., description="JSON string of vital signs data"),
    xray_image: Optional[UploadFile] = File(None, description="Optional X-ray image file"),
    symptoms_text: Optional[str] = Form(None, description="Optional symptoms description for ML disease prediction")
):
    """
    Enhanced Medical Analysis Endpoint with ML Disease Prediction

    Analyzes vital signs and optional symptoms to provide comprehensive medical assessment.
    Uses ML disease prediction when symptoms are provided, otherwise falls back to vitals analysis.

    Features:
    - ML-powered disease prediction from symptoms
    - Vitals condition analysis
    - Supervisor agent integration
    - X-ray image analysis
    - Detailed medical reasoning
    - Confidence scoring
    """
    try:
        logger.info(f"BioGPT analysis requested with X-ray: {xray_image is not None}")

        # Parse vitals data from form
        try:
            vitals_dict = json.loads(vitals_data)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid vitals data format. Must be valid JSON."
            )

        # Validate vital signs relationships
        if vitals_dict['systolic_bp'] <= vitals_dict['diastolic_bp']:
            raise HTTPException(
                status_code=400,
                detail="Systolic blood pressure must be higher than diastolic blood pressure"
            )

        # Step 1: Analyze vitals
        vitals_result = vitals_agent.analyze_vitals(vitals_dict)
        logger.info(f"Vitals analysis complete: {vitals_result['primary_diagnosis']}")

        # Step 1.5: Analyze symptoms for ML disease prediction (if provided)
        ml_disease_prediction = None
        if symptoms_text and symptoms_text.strip():
            try:
                symptoms_result = symptoms_ai.analyze_symptoms(symptoms_text)
                if 'predictions' in symptoms_result and symptoms_result['predictions']['primary']:
                    primary_prediction = symptoms_result['predictions']['primary']
                    ml_disease_prediction = {
                        'disease': primary_prediction['disease'],
                        'confidence': primary_prediction['confidence_percentage'] / 100.0
                    }
                    logger.info(f"ML disease prediction: {ml_disease_prediction['disease']} ({ml_disease_prediction['confidence']:.1%})")
                else:
                    logger.info("No ML disease prediction available from symptoms")
            except Exception as e:
                logger.error(f"Symptoms analysis failed: {str(e)}")
                # Continue without ML prediction

        # Step 2: Analyze X-ray if provided (bypassing BioGPT for now)
        xray_result = None
        if xray_image:
            try:
                # Validate file type
                if not xray_image.content_type.startswith('image/'):
                    raise HTTPException(
                        status_code=400,
                        detail="File must be an image (PNG, JPG, or JPEG)"
                    )

                # Read image data
                image_data = await xray_image.read()

                # Analyze X-ray using the new chest agent
                xray_result = xray_chest_agent.analyze_xray_image(image_data, xray_image.filename)

                logger.info(f"X-ray analysis complete: {xray_result['primary_finding']}")

            except Exception as e:
                logger.error(f"X-ray analysis failed: {str(e)}")
                # Create error output for X-ray analysis
                xray_result = {
                    'primary_finding': 'X-ray analysis failed',
                    'findings': [f'Error: {str(e)}'],
                    'confidence': 0.0,
                    'technical_quality': 'error',
                    'agent_type': 'xray_analysis'
                }

        # Step 3: Use supervisor agent with ML disease prediction
        # Prepare vitals agent output (convert vital_analysis dict to string)
        vital_analysis_text = ""
        if isinstance(vitals_result['vital_analysis'], dict):
            for key, value in vitals_result['vital_analysis'].items():
                if isinstance(value, dict):
                    vital_analysis_text += f"{key.replace('_', ' ').title()}: {value.get('status', 'N/A')} ({value.get('value', 'N/A')}); "
                else:
                    vital_analysis_text += f"{key.replace('_', ' ').title()}: {value}; "
        else:
            vital_analysis_text = str(vitals_result['vital_analysis'])

        vitals_agent_output = AgentOutput(
            diagnosis=vitals_result['primary_diagnosis'],
            confidence=vitals_result['confidence'],
            explanation=vital_analysis_text.strip()
        )

        # Prepare supervisor input
        supervisor_input = SupervisorInput(vitals=vitals_agent_output)

        # Add ML diagnosis if available
        if ml_disease_prediction:
            supervisor_input.ml = MLDiagnosis(
                disease=ml_disease_prediction['disease'],
                confidence=ml_disease_prediction['confidence']
            )

        # Get supervisor analysis
        supervisor_result = supervisor_agent.analyze(supervisor_input)

        # Add vitals and X-ray details to the result
        supervisor_result.vitals_details = {
            'diagnosis': vitals_result['primary_diagnosis'],
            'confidence': vitals_result['confidence'],
            'top_conditions': vitals_result['top_conditions'],
            'vital_analysis': vitals_result['vital_analysis'],
            'recommendations': vitals_result['recommendations'],
            'agent_type': 'vitals_analysis'
        }

        if xray_result:
            supervisor_result.xray_details = xray_result

        logger.info(f"Supervisor analysis complete. Final diagnosis: {supervisor_result.final_diagnosis}")

        return supervisor_result

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        logger.error(f"BioGPT analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Medical analysis failed: {str(e)}"
        )

@router.post("/symptoms-analysis")
async def symptoms_analysis(symptoms_text: str = Form(...)):
    """
    Analyze symptoms from natural language description

    Uses the advanced symptoms AI model for:
    - Symptom extraction from natural language
    - Disease prediction with confidence scores
    - Urgency assessment
    - AI-powered clinical analysis
    """
    try:
        logger.info(f"Symptoms analysis requested for: {symptoms_text[:100]}...")

        # Analyze symptoms using the enhanced symptoms AI
        result = symptoms_ai.analyze_symptoms(symptoms_text)

        # Format result for DiagnoNet compatibility
        if 'error' not in result:
            result = _format_symptoms_result(result)

        if 'error' in result:
            logger.error(f"Symptoms analysis failed: {result['error']}")
            raise HTTPException(status_code=500, detail=result['error'])

        logger.info(f"Symptoms analysis complete. Detected: {len(result['symptoms_detected'])} symptoms")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Symptoms analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Symptoms analysis failed: {str(e)}"
        )

@router.post("/xray-chest-analysis")
async def xray_chest_analysis(
    xray_image: UploadFile = File(...),
    generate_gradcam: bool = Form(True),
    generate_explanation: bool = Form(True),
    topk: int = Form(18),
    patient_name: Optional[str] = Form(None),
    patient_age: Optional[int] = Form(None),
    patient_height: Optional[str] = Form(None)
):
    """
    Advanced X-ray chest analysis with GradCAM and Ollama integration

    Features:
    - Advanced pathology detection
    - GradCAM++ visualization
    - Ollama 3.2 clinical explanations
    - Uncertainty quantification
    - Severity assessment
    """
    try:
        logger.info(f"Advanced X-ray analysis requested: {xray_image.filename}")

        # Validate file type
        if not xray_image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image (PNG, JPG, or JPEG)"
            )

        # Read image data
        image_data = await xray_image.read()

        # Analyze X-ray using the advanced chest agent
        result = xray_chest_agent.analyze_xray_image(
            image_data=image_data,
            filename=xray_image.filename,
            topk=topk,
            generate_gradcam=generate_gradcam,
            generate_explanation=generate_explanation
        )

        if 'error' in result:
            logger.error(f"X-ray chest analysis failed: {result['error']}")
            raise HTTPException(status_code=500, detail=result['error'])

        # Add patient demographics to the result if provided
        if patient_name or patient_age or patient_height:
            patient_demographics = {}
            if patient_name:
                patient_demographics['patient_name'] = patient_name
            if patient_age:
                patient_demographics['age'] = patient_age
            if patient_height:
                patient_demographics['height'] = patient_height

            result['patient_demographics'] = patient_demographics

        logger.info(f"X-ray chest analysis complete: {result['primary_finding']} ({result['confidence']:.1%})")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"X-ray chest analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"X-ray chest analysis failed: {str(e)}"
        )

@router.post("/multimodal-analysis")
async def multimodal_analysis(
    vitals_data: str = Form(...),
    symptoms_text: str = Form(None),
    xray_image: UploadFile = File(None)
):
    """
    Complete multimodal medical analysis combining all three agents

    Integrates:
    - Vitals analysis (existing)
    - Symptoms analysis (new)
    - Advanced X-ray analysis (new)
    - Cross-modal insights
    """
    try:
        logger.info("Multimodal analysis requested")

        # Parse vitals data
        vitals_dict = json.loads(vitals_data)
        vitals = VitalsPayload(**vitals_dict)

        results = {}

        # 1. Analyze vitals (existing functionality)
        vitals_result = vitals_agent.analyze_vitals(vitals.model_dump())
        results['vitals'] = vitals_result
        logger.info(f"Vitals analysis: {vitals_result['primary_diagnosis']}")

        # 2. Analyze symptoms if provided
        if symptoms_text and symptoms_text.strip():
            symptoms_result = symptoms_ai.analyze_symptoms(symptoms_text)
            symptoms_result = _format_symptoms_result(symptoms_result)
            results['symptoms'] = symptoms_result
            logger.info(f"Symptoms analysis: {len(symptoms_result.get('symptoms_detected', []))} symptoms detected")

        # 3. Analyze X-ray if provided
        if xray_image:
            if not xray_image.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=400,
                    detail="X-ray file must be an image (PNG, JPG, or JPEG)"
                )

            image_data = await xray_image.read()
            xray_result = xray_chest_agent.analyze_xray_image(
                image_data=image_data,
                filename=xray_image.filename,
                generate_gradcam=True,
                generate_explanation=True
            )
            results['xray'] = xray_result
            logger.info(f"X-ray analysis: {xray_result.get('primary_finding', 'Unknown')}")

        # 4. Create integrated summary
        results['integration'] = {
            'total_modalities': len([k for k in results.keys() if k != 'integration']),
            'analysis_timestamp': vitals_result.get('timestamp', 'unknown'),
            'overall_severity': _assess_overall_severity(results),
            'cross_modal_insights': _generate_cross_modal_insights(results)
        }

        logger.info("Multimodal analysis complete")
        return results

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid vitals data format")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Multimodal analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Multimodal analysis failed: {str(e)}"
        )

def _assess_overall_severity(results: Dict) -> str:
    """Assess overall severity across all modalities"""
    severities = []

    if 'vitals' in results:
        # Map vitals diagnosis to severity
        diagnosis = results['vitals'].get('primary_diagnosis', '').lower()
        if 'normal' in diagnosis:
            severities.append('LOW')
        elif any(term in diagnosis for term in ['hypertension', 'tachycardia']):
            severities.append('HIGH')
        elif any(term in diagnosis for term in ['respiratory', 'critical']):
            severities.append('CRITICAL')
        else:
            severities.append('MODERATE')

    if 'symptoms' in results:
        urgency = results['symptoms'].get('urgency_level', '').lower()
        if urgency == 'emergency':
            severities.append('CRITICAL')
        elif urgency == 'urgent':
            severities.append('HIGH')
        else:
            severities.append('MODERATE')

    if 'xray' in results:
        xray_severity = results['xray'].get('severity', 'MODERATE')
        severities.append(xray_severity)

    # Return highest severity
    if 'CRITICAL' in severities:
        return 'CRITICAL'
    elif 'HIGH' in severities:
        return 'HIGH'
    elif 'MODERATE' in severities:
        return 'MODERATE'
    else:
        return 'LOW'

def _generate_cross_modal_insights(results: Dict) -> List[str]:
    """Generate insights from cross-modal analysis"""
    insights = []

    # Check for consistency between modalities
    if 'vitals' in results and 'symptoms' in results:
        vitals_diagnosis = results['vitals'].get('primary_diagnosis', '').lower()
        symptoms = results['symptoms'].get('symptoms_detected', [])

        if 'respiratory' in vitals_diagnosis and any('breath' in s.lower() for s in symptoms):
            insights.append("🔗 Respiratory findings consistent across vitals and symptoms")

        if 'hypertension' in vitals_diagnosis and any('chest' in s.lower() for s in symptoms):
            insights.append("🔗 Cardiovascular findings suggest hypertensive episode")

    if 'xray' in results and 'symptoms' in results:
        xray_finding = results['xray'].get('primary_finding', '').lower()
        symptoms = results['symptoms'].get('symptoms_detected', [])

        if 'pneumonia' in xray_finding and any('cough' in s.lower() for s in symptoms):
            insights.append("🔗 X-ray pneumonia finding correlates with respiratory symptoms")

    if not insights:
        insights.append("📊 Multi-modal analysis completed - review individual findings")

    return insights

def call_ollama_for_summary(vitals_data, symptoms_data, xray_data):
    """Generate clinical summary using fallback method (Ollama not available)"""
    try:
        logger.info("Generating clinical summary using fallback method...")
        
        # Use fallback summary directly for better reliability
        return _generate_fallback_summary(vitals_data, symptoms_data, xray_data)
        
    except Exception as e:
        logger.error(f"Error generating clinical summary: {str(e)}")
        return _generate_fallback_summary(vitals_data, symptoms_data, xray_data)

def _generate_fallback_summary(vitals_data, symptoms_data, xray_data):
    """Generate a fallback clinical summary when Ollama is unavailable"""
    summary_parts = []

    if vitals_data:
        diagnosis = vitals_data.get('primary_diagnosis', 'Unknown')
        confidence = vitals_data.get('confidence', 0)
        summary_parts.append(f"Patient presents with {diagnosis.lower()} (confidence: {confidence:.1%})")

    if symptoms_data:
        symptoms = symptoms_data.get('symptoms_detected', [])
        urgency = symptoms_data.get('urgency_level', 'Unknown')
        if symptoms:
            summary_parts.append(f"accompanied by {', '.join(symptoms[:3])} with {urgency.lower()} urgency level")

    if xray_data:
        finding = xray_data.get('primary_finding', 'Unknown')
        confidence = xray_data.get('confidence', 0)
        summary_parts.append(f"Imaging reveals {finding.lower()} (confidence: {confidence:.1%})")

    if summary_parts:
        base_summary = ". ".join(summary_parts) + "."
        return f"Multi-agent medical analysis completed. {base_summary} Comprehensive evaluation from multiple diagnostic modalities provides clinical insight for healthcare provider assessment."
    else:
        return "Multi-agent analysis completed across multiple diagnostic modalities. Clinical summary generation requires additional agent data for comprehensive assessment."

def _format_vitals_for_prompt(vitals_data):
    """Format vitals data for Ollama prompt"""
    if not vitals_data:
        return "No vitals data available"

    diagnosis = vitals_data.get('primary_diagnosis', 'Unknown')
    confidence = vitals_data.get('confidence', 0)

    formatted = f"Primary Diagnosis: {diagnosis} (Confidence: {confidence:.1%})"

    if 'top_conditions' in vitals_data:
        conditions = vitals_data['top_conditions'][:3]  # Top 3 conditions
        conditions_text = ', '.join([f"{c.get('condition', 'Unknown')} ({c.get('probability', 0):.1%})" for c in conditions])
        formatted += f"\nTop Conditions: {conditions_text}"

    return formatted

def _format_symptoms_for_prompt(symptoms_data):
    """Format symptoms data for Ollama prompt"""
    if not symptoms_data:
        return "No symptoms data available"

    symptoms = symptoms_data.get('symptoms_detected', [])
    urgency = symptoms_data.get('urgency_level', 'Unknown')

    formatted = f"Detected Symptoms: {', '.join(symptoms) if symptoms else 'None specified'}"
    formatted += f"\nUrgency Level: {urgency}"

    if 'predictions' in symptoms_data:
        predictions = symptoms_data['predictions']
        if isinstance(predictions, list):
            predictions = predictions[:2]  # Top 2 predictions
            if predictions:
                pred_text = ', '.join([f"{p.get('disease', 'Unknown')} ({p.get('confidence', 0):.1%})" for p in predictions])
                formatted += f"\nDisease Predictions: {pred_text}"
        elif isinstance(predictions, dict) and 'primary' in predictions:
            # Handle enhanced format with primary diagnosis
            primary = predictions['primary']
            if isinstance(primary, dict):
                formatted += f"\nPrimary Diagnosis: {primary.get('disease', 'Unknown')} ({primary.get('confidence_percentage', 0):.1f}%)"

    return formatted

def _format_xray_for_prompt(xray_data):
    """Format X-ray data for Ollama prompt"""
    if not xray_data:
        return "No X-ray data available"

    primary_finding = xray_data.get('primary_finding', 'Unknown')
    confidence = xray_data.get('confidence', 0)

    formatted = f"Primary Finding: {primary_finding} (Confidence: {confidence:.1%})"

    if 'clinical_explanation' in xray_data:
        explanation = xray_data['clinical_explanation']
        if explanation and len(explanation) > 10:
            formatted += f"\nClinical Interpretation: {explanation}"

    return formatted

@router.post("/multi-agent-summary", response_model=MultiAgentSummaryResponse)
async def generate_multi_agent_summary(request: MultiAgentSummaryRequest):
    """
    Generate comprehensive multi-agent clinical summary

    Combines outputs from vitals, symptoms, and X-ray analysis agents
    using Ollama's Llama 3.2 model to create a unified clinical assessment.

    Features:
    - Integration of multiple AI agent outputs
    - Ollama-powered clinical summarization
    - Overall urgency assessment
    - Key findings extraction
    - Professional medical language
    """
    try:
        logger.info("Multi-agent summary generation requested")

        # Validate that at least 2 agents have provided data
        available_agents = []
        if request.vitals_result:
            available_agents.append("vitals")
        if request.symptoms_result:
            available_agents.append("symptoms")
        if request.xray_result:
            available_agents.append("xray")

        if len(available_agents) < 2:
            raise HTTPException(
                status_code=400,
                detail="Multi-agent summary requires data from at least 2 agents (vitals, symptoms, or X-ray)"
            )

        logger.info(f"Generating summary from {len(available_agents)} agents: {', '.join(available_agents)}")

        # Generate clinical summary using Ollama
        clinical_summary = call_ollama_for_summary(
            request.vitals_result,
            request.symptoms_result,
            request.xray_result
        )

        # Extract key findings from all agents
        key_findings = []
        if request.vitals_result:
            if isinstance(request.vitals_result, dict):
                vitals_finding = request.vitals_result.get('primary_diagnosis', 'Vitals analysis completed')
            else:
                vitals_finding = 'Vitals analysis completed'
            key_findings.append(f"Vitals: {vitals_finding}")

        if request.symptoms_result:
            if isinstance(request.symptoms_result, dict):
                symptoms = request.symptoms_result.get('symptoms_detected', [])
                if symptoms:
                    key_findings.append(f"Symptoms: {', '.join(symptoms[:3])}")  # Top 3 symptoms
                else:
                    key_findings.append("Symptoms: Analysis completed")
            else:
                key_findings.append("Symptoms: Analysis completed")

        if request.xray_result:
            if isinstance(request.xray_result, dict):
                xray_finding = request.xray_result.get('primary_finding', 'X-ray analysis completed')
            else:
                xray_finding = 'X-ray analysis completed'
            key_findings.append(f"X-ray: {xray_finding}")

        # Determine overall urgency level
        urgency_level = _determine_overall_urgency(request.vitals_result, request.symptoms_result, request.xray_result)

        # Calculate overall confidence score
        confidence_score = _calculate_overall_confidence(request.vitals_result, request.symptoms_result, request.xray_result)

        # Generate overall assessment
        overall_assessment = _generate_overall_assessment(urgency_level, len(available_agents))

        # Combine recommendations from all agents
        recommendations = _combine_recommendations(request.vitals_result, request.symptoms_result, request.xray_result)

        response = MultiAgentSummaryResponse(
            patient_info=request.patient_info,
            clinical_summary=clinical_summary,
            overall_assessment=overall_assessment,
            urgency_level=urgency_level,
            key_findings=key_findings,
            confidence_score=confidence_score,
            agents_analyzed=available_agents,
            recommendations=recommendations
        )

        logger.info(f"Multi-agent summary generated successfully. Urgency: {urgency_level}, Confidence: {confidence_score:.2f}")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Multi-agent summary generation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Multi-agent summary generation failed: {str(e)}"
        )

def _determine_overall_urgency(vitals_data, symptoms_data, xray_data):
    """Determine overall urgency level from all agent outputs"""
    urgency_scores = []

    # Vitals urgency assessment
    if vitals_data and isinstance(vitals_data, dict):
        diagnosis = vitals_data.get('primary_diagnosis', '').lower()
        if any(term in diagnosis for term in ['critical', 'emergency', 'severe']):
            urgency_scores.append(4)  # CRITICAL
        elif any(term in diagnosis for term in ['hypertension', 'tachycardia', 'high']):
            urgency_scores.append(3)  # HIGH
        elif 'normal' in diagnosis:
            urgency_scores.append(1)  # LOW
        else:
            urgency_scores.append(2)  # MODERATE

    # Symptoms urgency assessment
    if symptoms_data and isinstance(symptoms_data, dict):
        urgency = symptoms_data.get('urgency_level', '').lower()
        if urgency == 'emergency':
            urgency_scores.append(4)  # CRITICAL
        elif urgency == 'urgent':
            urgency_scores.append(3)  # HIGH
        else:
            urgency_scores.append(2)  # MODERATE

    # X-ray urgency assessment
    if xray_data and isinstance(xray_data, dict):
        finding = xray_data.get('primary_finding', '').lower()
        confidence = xray_data.get('confidence', 0)

        if any(term in finding for term in ['pneumonia', 'pneumothorax', 'effusion']) and confidence > 0.7:
            urgency_scores.append(3)  # HIGH
        elif any(term in finding for term in ['opacity', 'infiltrate']) and confidence > 0.6:
            urgency_scores.append(2)  # MODERATE
        else:
            urgency_scores.append(1)  # LOW

    # Return highest urgency level
    if not urgency_scores:
        return "MODERATE"

    max_urgency = max(urgency_scores)
    if max_urgency >= 4:
        return "CRITICAL"
    elif max_urgency >= 3:
        return "HIGH"
    elif max_urgency >= 2:
        return "MODERATE"
    else:
        return "LOW"

def _calculate_overall_confidence(vitals_data, symptoms_data, xray_data):
    """Calculate overall confidence score from all agent outputs"""
    confidences = []

    if vitals_data and isinstance(vitals_data, dict) and 'confidence' in vitals_data:
        confidences.append(vitals_data['confidence'])

    if symptoms_data and isinstance(symptoms_data, dict):
        # Try different confidence fields
        if 'confidence' in symptoms_data:
            confidences.append(symptoms_data['confidence'])
        elif 'overall_confidence' in symptoms_data:
            confidences.append(symptoms_data['overall_confidence'])
        elif 'predictions' in symptoms_data:
            predictions = symptoms_data['predictions']
            if isinstance(predictions, list) and predictions:
                max_conf = max([p.get('confidence', 0) for p in predictions])
                confidences.append(max_conf)
            elif isinstance(predictions, dict) and 'ml_confidence' in predictions:
                confidences.append(predictions['ml_confidence'])

    if xray_data and isinstance(xray_data, dict) and 'confidence' in xray_data:
        confidences.append(xray_data['confidence'])

    # Return average confidence or default
    if confidences:
        return sum(confidences) / len(confidences)
    else:
        return 0.75  # Default moderate confidence

def _generate_overall_assessment(urgency_level, num_agents):
    """Generate overall clinical assessment based on urgency and number of agents"""
    agent_text = f"{num_agents} diagnostic modalities"

    if urgency_level == "CRITICAL":
        return f"Critical clinical findings requiring immediate medical intervention based on {agent_text}"
    elif urgency_level == "HIGH":
        return f"Significant clinical concerns requiring prompt medical attention based on {agent_text}"
    elif urgency_level == "MODERATE":
        return f"Moderate clinical findings requiring medical evaluation based on {agent_text}"
    else:
        return f"Low-priority clinical findings with routine follow-up recommended based on {agent_text}"

def _combine_recommendations(vitals_data, symptoms_data, xray_data):
    """Combine recommendations from all agents"""
    recommendations = []

    # Vitals recommendations - handle both dict and string inputs
    if vitals_data:
        if isinstance(vitals_data, dict) and 'recommendations' in vitals_data:
            vitals_recs = vitals_data['recommendations']
            if isinstance(vitals_recs, list):
                recommendations.extend(vitals_recs[:2])  # Top 2 recommendations
            elif isinstance(vitals_recs, str):
                recommendations.append(vitals_recs)

    # Symptoms recommendations - handle both dict and string inputs
    if symptoms_data:
        if isinstance(symptoms_data, dict):
            # Try multiple possible recommendation fields
            for field in ['urgency_recommendation', 'recommendations', 'clinical_recommendation']:
                if field in symptoms_data:
                    symptoms_rec = symptoms_data[field]
                    if isinstance(symptoms_rec, str) and symptoms_rec not in recommendations:
                        recommendations.append(symptoms_rec)
                    elif isinstance(symptoms_rec, list):
                        for rec in symptoms_rec[:2]:
                            if rec not in recommendations:
                                recommendations.append(rec)
                    break

    # X-ray recommendations - handle both dict and string inputs
    if xray_data:
        if isinstance(xray_data, dict) and 'recommendations' in xray_data:
            xray_recs = xray_data['recommendations']
            if isinstance(xray_recs, list):
                for rec in xray_recs[:2]:  # Top 2 recommendations
                    if rec not in recommendations:
                        recommendations.append(rec)
            elif isinstance(xray_recs, str):
                recommendations.append(xray_recs)

    # Add general multi-agent recommendation
    if len(recommendations) > 1:
        recommendations.append("Correlate findings across all diagnostic modalities for comprehensive assessment")

    # Ensure we have at least some recommendations
    if not recommendations:
        recommendations = [
            "Continue monitoring patient condition",
            "Follow up with healthcare provider as appropriate"
        ]

    return recommendations[:5]  # Limit to 5 recommendations

def _format_symptoms_result(ai_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the StreamlinedMedicalAI result for DiagnoNet compatibility

    Args:
        ai_result: Result from the streamlined medical AI

    Returns:
        Formatted result for DiagnoNet with enhanced structure
    """
    try:
        # Extract key information from AI result
        symptoms = ai_result.get('symptoms', {})
        predictions = ai_result.get('predictions', {})
        assessment = ai_result.get('assessment', {})

        # Get detected symptoms
        symptoms_detected = symptoms.get('detected', [])

        # Get primary diagnosis
        primary_prediction = predictions.get('primary')
        primary_diagnosis = primary_prediction['disease'] if primary_prediction else "No clear diagnosis"
        primary_confidence = predictions.get('ml_confidence', 0.0)

        # Get urgency level
        urgency_level = assessment.get('urgency_level', 'Routine')

        # Get overall confidence
        overall_confidence = assessment.get('overall_confidence', 0.0)

        # Get differential diagnoses
        differential_diagnoses = []
        for diff in predictions.get('differential', []):
            differential_diagnoses.append({
                'condition': diff['disease'],
                'confidence': diff['confidence_percentage'] / 100.0,
                'confidence_percentage': diff['confidence_percentage'],
                'description': diff.get('confidence_level', '')
            })

        # Get AI analysis if available
        ai_analysis = ai_result.get('ai_analysis', '')

        # Create enhanced formatted result
        formatted_result = {
            # Core symptoms information
            "symptoms_detected": symptoms_detected,
            "symptom_analysis": {
                "extracted_symptoms": symptoms.get('confidence_scores', {}),
                "extraction_confidence": symptoms.get('extraction_confidence', 0.0),
                "total_symptoms": len(symptoms_detected),
                "extraction_method": "enhanced_medical_nlp"
            },

            # Disease predictions
            "primary_diagnosis": primary_diagnosis,
            "confidence": primary_confidence,
            "differential_diagnoses": differential_diagnoses,
            "predictions": {
                "primary": primary_prediction,
                "differential": differential_diagnoses,
                "ml_confidence": primary_confidence
            },

            # Clinical assessment
            "urgency_level": urgency_level,
            "overall_confidence": overall_confidence,
            "clinical_assessment": {
                "urgency": urgency_level,
                "recommendation": assessment.get('recommendation', 'Consult healthcare provider'),
                "severity_assessment": _map_urgency_to_severity(urgency_level),
                "clinical_coherence": ai_result.get('clinical_coherence', 0.8)
            },

            # Enhanced recommendations
            "recommendations": _generate_symptoms_recommendations(urgency_level, primary_diagnosis, symptoms_detected),
            "urgency_recommendation": assessment.get('recommendation', 'Consult healthcare provider'),

            # AI analysis and metadata
            "ai_analysis": ai_analysis if ai_analysis else None,
            "agent_type": "symptoms_analysis",
            "analysis_metadata": {
                "follow_up_needed": ai_result.get('follow_up_needed', False),
                "follow_up_questions": ai_result.get('follow_up_questions', []),
                "symptom_completeness": ai_result.get('symptom_completeness', 1.0),
                "extraction_method": ai_result.get('extraction_method', 'enhanced_medical_nlp_v2')
            },
            "timestamp": _get_current_timestamp()
        }

        return formatted_result

    except Exception as e:
        logger.error(f"Error formatting symptoms result: {str(e)}")
        return {
            "error": f"Symptoms result formatting failed: {str(e)}",
            "symptoms_detected": [],
            "urgency_level": "Unknown",
            "confidence": 0.0
        }

def _map_urgency_to_severity(urgency_level: str) -> str:
    """Map urgency level to severity assessment"""
    urgency_mapping = {
        "Emergency": "CRITICAL",
        "Urgent": "HIGH",
        "Routine": "LOW"
    }
    return urgency_mapping.get(urgency_level, "MODERATE")

def _generate_symptoms_recommendations(urgency_level: str, primary_diagnosis: str, symptoms: List[str]) -> List[str]:
    """Generate enhanced recommendations based on symptoms analysis"""
    recommendations = []

    # Base recommendations by urgency
    if urgency_level == "Emergency":
        recommendations.extend([
            "Seek immediate emergency medical attention",
            "Do not delay medical care",
            "Consider calling emergency services if symptoms worsen"
        ])
    elif urgency_level == "Urgent":
        recommendations.extend([
            "Schedule urgent medical consultation within 24 hours",
            "Monitor symptoms closely for any worsening",
            "Seek immediate care if symptoms become severe"
        ])
    else:
        recommendations.extend([
            "Schedule routine medical consultation",
            "Continue monitoring symptoms",
            "Maintain symptom diary for healthcare provider"
        ])

    # Specific recommendations based on primary diagnosis
    if "Myocardial Infarction" in primary_diagnosis or "Heart" in primary_diagnosis:
        recommendations.append("Avoid strenuous activity until medical evaluation")
    elif "Pneumonia" in primary_diagnosis or "Respiratory" in primary_diagnosis:
        recommendations.append("Monitor breathing and oxygen levels")
    elif "Migraine" in primary_diagnosis or "Headache" in primary_diagnosis:
        recommendations.append("Rest in quiet, dark environment")

    # Symptom-specific recommendations
    if any("chest" in s.lower() for s in symptoms):
        recommendations.append("Avoid physical exertion until medical clearance")
    if any("fever" in s.lower() for s in symptoms):
        recommendations.append("Stay hydrated and monitor temperature")

    return list(set(recommendations))  # Remove duplicates

def _get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    from datetime import datetime
    return datetime.now().isoformat()

# New Upload & Analyze endpoints
@router.post("/analyze")
async def analyze_medical_case(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """Upload and queue medical file for AI analysis"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        # Validate file type
        allowed_extensions = {'.pdf', '.json', '.csv', '.png', '.jpg', '.jpeg', '.dcm'}
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )

        job_id = uuid4().hex
        os.makedirs("storage", exist_ok=True)
        save_path = f"storage/{job_id}_{file.filename}"

        # Save uploaded file
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Queue analysis task
        if background_tasks:
            background_tasks.add_task(run_analysis_pipeline, job_id, save_path)
        else:
            # Fallback: run synchronously for testing
            run_analysis_pipeline(job_id, save_path)

        logger.info(f"Analysis queued for job {job_id}: {file.filename}")
        return {"job_id": job_id, "status": "queued", "filename": file.filename}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"File upload failed: {str(e)}"
        )

@router.get("/results/{job_id}")
async def get_analysis_results(job_id: str):
    """Get analysis results by job ID"""
    try:
        result_path = Path(f"storage/{job_id}_result.json")
        if not result_path.exists():
            return {"status": "processing", "job_id": job_id}

        with open(result_path, "r") as f:
            result = json.load(f)

        return {"status": "complete", "job_id": job_id, "result": result}

    except Exception as e:
        logger.error(f"Results retrieval error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve results: {str(e)}"
        )

def run_analysis_pipeline(job_id: str, file_path: str):
    """Execute the complete medical analysis pipeline"""
    try:
        logger.info(f"Starting analysis pipeline for job {job_id}")

        # Parse uploaded file based on extension
        parsed_data = parse_medical_file(Path(file_path))

        # Initialize results
        results = {
            "job_id": job_id,
            "filename": Path(file_path).name,
            "analysis_timestamp": _get_current_timestamp(),
            "status": "completed"
        }

        # Add patient information if available
        if parsed_data.get("patient_info"):
            results["patient_info"] = parsed_data["patient_info"]

        # Run individual analysis agents
        vitals_result = None
        if parsed_data.get("vitals"):
            logger.info(f"Running vitals analysis for job {job_id}")
            vitals_result = vitals_agent.analyze_vitals(parsed_data["vitals"])
            results["vitals_analysis"] = vitals_result

        xray_result = None
        if parsed_data.get("image_data"):
            logger.info(f"Running X-ray analysis for job {job_id}")
            xray_result = xray_chest_agent.analyze_xray_image(
                image_data=parsed_data["image_data"],
                filename=parsed_data.get("image_filename", "uploaded_image"),
                topk=18,
                generate_gradcam=True,
                generate_explanation=True
            )
            results["xray_analysis"] = xray_result

        symptom_result = None
        if parsed_data.get("symptoms_text"):
            logger.info(f"Running symptoms analysis for job {job_id}")
            symptom_result = symptoms_ai.analyze_symptoms(parsed_data["symptoms_text"])
            results["symptoms_analysis"] = _format_symptoms_result(symptom_result)

        # Generate multi-agent summary if we have multiple results
        analysis_count = sum(1 for x in [vitals_result, xray_result, symptom_result] if x is not None)
        if analysis_count >= 2:
            logger.info(f"Generating multi-agent summary for job {job_id}")
            clinical_summary = call_ollama_for_summary(
                vitals_result,
                results.get("symptoms_analysis"),
                xray_result
            )

            # Calculate overall metrics
            urgency_level = _determine_overall_urgency(vitals_result, results.get("symptoms_analysis"), xray_result)
            confidence_score = _calculate_overall_confidence(vitals_result, results.get("symptoms_analysis"), xray_result)

            results["multi_agent_summary"] = {
                "clinical_summary": clinical_summary,
                "urgency_level": urgency_level,
                "confidence_score": confidence_score,
                "agents_analyzed": analysis_count,
                "overall_assessment": _generate_overall_assessment(urgency_level, analysis_count)
            }

        # Save results
        result_path = f"storage/{job_id}_result.json"
        with open(result_path, "w") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"Analysis pipeline completed successfully for job {job_id}")

    except Exception as e:
        logger.error(f"Analysis pipeline failed for job {job_id}: {str(e)}")
        # Save error result
        error_result = {
            "job_id": job_id,
            "status": "failed",
            "error": str(e),
            "timestamp": _get_current_timestamp()
        }
        with open(f"storage/{job_id}_result.json", "w") as f:
            json.dump(error_result, f, indent=2)

def parse_medical_file(file_path: Path):
    """Parse different medical file formats"""
    try:
        file_ext = file_path.suffix.lower()
        parsed_data = {}

        if file_ext == '.json':
            # Parse JSON files (FHIR, vitals data, etc.)
            with open(file_path, 'r') as f:
                data = json.load(f)

            # Try to extract vitals data
            if 'vitals' in data:
                parsed_data['vitals'] = data['vitals']
            elif all(key in data for key in ['systolic_bp', 'diastolic_bp', 'heart_rate']):
                parsed_data['vitals'] = data

            # Try to extract symptoms
            if 'symptoms' in data:
                parsed_data['symptoms_text'] = data['symptoms']
            elif 'symptoms_text' in data:
                parsed_data['symptoms_text'] = data['symptoms_text']

            # Extract patient information
            patient_info = {}
            patient_fields = ['patient_id', 'name', 'age', 'gender', 'height', 'weight',
                            'medical_history', 'medications', 'allergies', 'emergency_contact']

            for field in patient_fields:
                if field in data:
                    patient_info[field] = data[field]

            # Also check for nested patient object
            if 'patient' in data:
                patient_data = data['patient']
                for field in patient_fields:
                    if field in patient_data:
                        patient_info[field] = patient_data[field]

            if patient_info:
                parsed_data['patient_info'] = patient_info

        elif file_ext == '.csv':
            # Parse CSV files (vitals data)
            import pandas as pd
            df = pd.read_csv(file_path)

            # Try to extract vitals from CSV
            vitals_columns = ['systolic_bp', 'diastolic_bp', 'heart_rate', 'temperature', 'respiratory_rate', 'oxygen_saturation']
            if any(col in df.columns for col in vitals_columns):
                # Use the last row of data
                last_row = df.iloc[-1]
                vitals = {}
                for col in vitals_columns:
                    if col in df.columns:
                        vitals[col] = float(last_row[col])
                parsed_data['vitals'] = vitals

        elif file_ext in ['.png', '.jpg', '.jpeg', '.dcm']:
            # Parse image files
            with open(file_path, 'rb') as f:
                image_data = f.read()
            parsed_data['image_data'] = image_data
            parsed_data['image_filename'] = file_path.name

        elif file_ext == '.pdf':
            # For PDF files, extract text and try to find symptoms
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                parsed_data['symptoms_text'] = text
            except ImportError:
                logger.warning("PyPDF2 not available for PDF parsing")
                parsed_data['symptoms_text'] = "PDF content could not be extracted"

        logger.info(f"Parsed file {file_path.name}: {list(parsed_data.keys())}")
        return parsed_data

    except Exception as e:
        logger.error(f"File parsing error for {file_path}: {str(e)}")
        return {"error": f"Failed to parse file: {str(e)}"}
