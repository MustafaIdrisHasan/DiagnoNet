import os, json
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI router
router = APIRouter()

class AgentOutput(BaseModel):
    """Schema for the vitals agent output only"""
    diagnosis: str = Field(..., description="Primary diagnosis from vitals agent")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    explanation: str = Field(..., description="Detailed reasoning from vitals agent")

class MLDiagnosis(BaseModel):
    """Schema for ML disease prediction output"""
    disease: str = Field(..., description="Primary disease prediction from ML model")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")

class SupervisorInput(BaseModel):
    """Input for supervisor agent with optional ML disease prediction"""
    vitals: AgentOutput = Field(..., description="Vitals agent output")
    ml: Optional[MLDiagnosis] = Field(None, description="Optional ML disease prediction")

class SupervisorOutput(BaseModel):
    """Complete medical analysis output with detailed vitals information"""
    final_diagnosis: str = Field(..., description="Primary medical diagnosis")
    confidence: float = Field(..., description="Confidence score (0-1)")
    model_used: str = Field(..., description="Name of the AI model used")
    reasoning: str = Field(..., description="Detailed medical reasoning")
    agent_agreement: str = Field(..., description="Agent consensus information")
    recommendations: list[str] = Field(..., description="Medical recommendations")
    severity: str = Field(..., description="Severity level (LOW, MODERATE, HIGH, CRITICAL)")
    vitals_details: dict | None = Field(None, description="Detailed vitals analysis breakdown")
    xray_details: dict | None = Field(None, description="X-ray analysis details if available")

class SupervisorAgent:
    """
    Supervisor agent that produces a natural-language briefing
    based solely on the vitals agent output using BioGPT.
    """

    def __init__(self):
        self.model_name = os.getenv("BIOGPT_MODEL", "microsoft/biogpt")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model()

    def _load_model(self):
        logger.info(f"Loading BioGPT model: {self.model_name} on {self.device}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None
        )
        self.generator = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if self.device == "cuda" else -1
        )
        logger.info("BioGPT loaded successfully")

    def analyze(self, payload: SupervisorInput) -> SupervisorOutput:
        try:
            vitals = payload.vitals

            # Prioritize ML disease prediction over vitals condition
            if payload.ml:
                primary_diagnosis = payload.ml.disease
                primary_confidence = payload.ml.confidence
                source = "ML ensemble"

                prompt = (
                    "You are a senior medical supervisor. "
                    "Please provide a concise, human-readable briefing summarizing the medical analysis below, "
                    "highlight key findings, confidence, and next-step recommendations.\n\n"
                    f"Primary Diagnosis: {primary_diagnosis}\n"
                    f"Confidence: {primary_confidence:.2f}\n"
                    f"Source: {source}\n"
                    f"Supporting Vitals Condition: {vitals.diagnosis} ({vitals.confidence:.2f})\n"
                    f"Clinical Context: {vitals.explanation}\n\n"
                    "Briefing:"
                )
            else:
                primary_diagnosis = vitals.diagnosis
                primary_confidence = vitals.confidence
                source = "Vitals agent"

                prompt = (
                    "You are a senior medical supervisor. "
                    "Please provide a concise, human-readable briefing summarizing the vitals analysis below, "
                    "highlight key findings, confidence, and next-step recommendations.\n\n"
                    f"Diagnosis: {primary_diagnosis}\n"
                    f"Confidence: {primary_confidence:.2f}\n"
                    f"Source: {source}\n"
                    f"Explanation: {vitals.explanation}\n\n"
                    "Briefing:"
                )
            # Generate summary
            response = self.generator(
                prompt,
                max_length=200,
                temperature=0.2,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id
            )
            text = response[0]["generated_text"].strip()
            # Strip prompt prefix if echoed
            summary = text[len(prompt):].strip() if text.startswith(prompt) else text

            # Determine severity based on diagnosis
            severity = self._assess_severity(primary_diagnosis, primary_confidence)

            # Generate recommendations
            recommendations = self._generate_recommendations(primary_diagnosis, vitals.explanation)

            # Create agent agreement message
            if payload.ml:
                agent_agreement = f"ML prediction ({source}) supported by vitals analysis"
            else:
                agent_agreement = f"Vitals-only analysis ({source})"

            return SupervisorOutput(
                final_diagnosis=primary_diagnosis,
                confidence=primary_confidence,
                model_used=self.model_name,
                reasoning=summary,
                agent_agreement=agent_agreement,
                recommendations=recommendations,
                severity=severity,
                vitals_details=None,  # Can be populated later if needed
                xray_details=None     # Can be populated later if needed
            )
        except Exception as e:
            logger.error(f"SupervisorAgent failed: {e}")
            # Fallback: return raw explanation
            fallback_diagnosis = payload.ml.disease if payload.ml else payload.vitals.diagnosis
            fallback_confidence = payload.ml.confidence if payload.ml else payload.vitals.confidence

            return SupervisorOutput(
                final_diagnosis=fallback_diagnosis,
                confidence=fallback_confidence,
                model_used="fallback",
                reasoning=f"Supervisor fallback summary based on vitals: {payload.vitals.explanation}",
                agent_agreement="Fallback mode due to processing error",
                recommendations=["Consult healthcare provider", "Monitor symptoms"],
                severity="MODERATE",
                vitals_details=None,
                xray_details=None
            )

    def _assess_severity(self, diagnosis: str, confidence: float) -> str:
        """Assess severity based on diagnosis and confidence"""
        # Emergency conditions
        emergency_conditions = [
            "Myocardial Infarction", "Heart Attack", "Stroke", "Pulmonary Embolism",
            "Severe Respiratory Distress", "Cardiac Arrest"
        ]

        # High severity conditions
        high_severity_conditions = [
            "Pneumonia", "Hypertension", "Respiratory_Distress", "Tachycardia",
            "Bradycardia", "Hypotension"
        ]

        diagnosis_lower = diagnosis.lower()

        if any(condition.lower() in diagnosis_lower for condition in emergency_conditions):
            return "CRITICAL"
        elif any(condition.lower() in diagnosis_lower for condition in high_severity_conditions):
            return "HIGH" if confidence > 0.7 else "MODERATE"
        elif confidence > 0.8:
            return "MODERATE"
        else:
            return "LOW"

    def _generate_recommendations(self, diagnosis: str, explanation: str) -> list[str]:
        """Generate medical recommendations based on diagnosis"""
        recommendations = []
        diagnosis_lower = diagnosis.lower()

        # Emergency recommendations
        if any(term in diagnosis_lower for term in ["myocardial", "heart attack", "stroke"]):
            recommendations.extend([
                "Seek immediate emergency medical attention",
                "Call emergency services (911)",
                "Do not delay treatment"
            ])
        # Respiratory conditions
        elif any(term in diagnosis_lower for term in ["pneumonia", "respiratory", "breathing"]):
            recommendations.extend([
                "Monitor oxygen saturation levels",
                "Consider chest imaging if not already done",
                "Evaluate for antibiotic therapy",
                "Monitor for worsening symptoms"
            ])
        # Cardiovascular conditions
        elif any(term in diagnosis_lower for term in ["hypertension", "tachycardia", "bradycardia"]):
            recommendations.extend([
                "Monitor blood pressure regularly",
                "Consider cardiovascular evaluation",
                "Review current medications",
                "Lifestyle modifications may be beneficial"
            ])
        # General recommendations
        else:
            recommendations.extend([
                "Continue monitoring symptoms",
                "Follow up with healthcare provider",
                "Maintain healthy lifestyle"
            ])

        return recommendations

# FastAPI endpoint
@router.post("/supervisor", response_model=SupervisorOutput)
def supervisor_endpoint(input: SupervisorInput):
    agent = SupervisorAgent()
    return agent.analyze(input)
