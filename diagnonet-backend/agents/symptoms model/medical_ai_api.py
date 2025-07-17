#!/usr/bin/env python3
"""
Medical AI API - Clean interface for symptom analysis
Provides simple function calls for medical AI functionality
"""

import os
import json
from typing import Dict, List, Any, Optional
from streamlined_medical_ai import StreamlinedMedicalAI

class MedicalAIAPI:
    """Clean API interface for medical AI functionality"""
    
    def __init__(self, groq_api_key: Optional[str] = None):
        """
        Initialize Medical AI API
        
        Args:
            groq_api_key: Optional Groq API key for enhanced analysis
        """
        if groq_api_key:
            os.environ['GROQ_API_KEY'] = groq_api_key
        
        self.ai = StreamlinedMedicalAI()
        self.ready = self.ai.initialized
    
    def analyze(self, symptoms_description: str) -> Dict[str, Any]:
        """
        Analyze symptoms from natural language description
        
        Args:
            symptoms_description: Natural language description of symptoms
            
        Returns:
            Dictionary containing analysis results
            
        Example:
            >>> api = MedicalAIAPI()
            >>> result = api.analyze("I have severe chest pain and shortness of breath")
            >>> print(result['predictions']['primary']['disease'])
            'Myocardial Infarction'
        """
        if not self.ready:
            return {"error": "Medical AI not initialized"}
        
        return self.ai.analyze_symptoms(symptoms_description)
    
    def extract_symptoms(self, text: str) -> Dict[str, float]:
        """
        Extract symptoms only (no predictions)
        
        Args:
            text: Natural language text
            
        Returns:
            Dictionary of symptoms with confidence scores
        """
        if not self.ready:
            return {}
        
        result = self.ai.analyze_symptoms(text)
        return result.get('symptoms', {}).get('confidence_scores', {})
    
    def predict_diseases(self, symptoms: List[str]) -> List[Dict[str, Any]]:
        """
        Get disease predictions for given symptoms
        
        Args:
            symptoms: List of symptom names
            
        Returns:
            List of disease predictions with confidence scores
        """
        if not self.ready:
            return []
        
        try:
            predictions = self.ai.ml_predictor.predict_disease(symptoms)
            return predictions
        except:
            return []
    
    def assess_urgency(self, symptoms_description: str) -> Dict[str, str]:
        """
        Assess urgency level for symptoms
        
        Args:
            symptoms_description: Natural language description
            
        Returns:
            Dictionary with urgency level and recommendation
        """
        if not self.ready:
            return {"urgency": "unknown", "recommendation": "System unavailable"}
        
        result = self.ai.analyze_symptoms(symptoms_description)
        assessment = result.get('assessment', {})
        
        return {
            "urgency": assessment.get('urgency_level', 'unknown'),
            "recommendation": assessment.get('recommendation', 'Consult healthcare provider')
        }
    
    def batch_analyze(self, descriptions: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze multiple symptom descriptions
        
        Args:
            descriptions: List of natural language descriptions
            
        Returns:
            List of analysis results
        """
        if not self.ready:
            return [{"error": "Medical AI not initialized"} for _ in descriptions]
        
        return self.ai.batch_analyze(descriptions)
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status and capabilities"""
        return self.ai.get_system_info()

# Convenience functions for direct use
def analyze_symptoms(description: str, groq_api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Quick function to analyze symptoms
    
    Args:
        description: Natural language symptom description
        groq_api_key: Optional Groq API key
        
    Returns:
        Analysis results
    """
    api = MedicalAIAPI(groq_api_key)
    return api.analyze(description)

def extract_symptoms_only(text: str) -> Dict[str, float]:
    """
    Quick function to extract symptoms only
    
    Args:
        text: Natural language text
        
    Returns:
        Symptoms with confidence scores
    """
    api = MedicalAIAPI()
    return api.extract_symptoms(text)

def predict_from_symptoms(symptoms: List[str]) -> List[Dict[str, Any]]:
    """
    Quick function to get predictions from symptom list
    
    Args:
        symptoms: List of symptom names
        
    Returns:
        Disease predictions
    """
    api = MedicalAIAPI()
    return api.predict_diseases(symptoms)

def check_urgency(description: str) -> str:
    """
    Quick function to check urgency level
    
    Args:
        description: Symptom description
        
    Returns:
        Urgency level (Emergency/Urgent/Routine)
    """
    api = MedicalAIAPI()
    result = api.assess_urgency(description)
    return result.get('urgency', 'unknown')

# Example usage and testing
def demo():
    """Demonstrate API functionality"""
    print("Medical AI API Demo")
    print("="*50)
    
    # Set up API with Groq key from environment
    api = MedicalAIAPI()  # API key should be set in environment variable GROQ_API_KEY
    
    if not api.ready:
        print("Error: Medical AI not ready")
        return
    
    # Test cases
    test_cases = [
        "I have severe chest pain radiating to my left arm",
        "My stomach hurts really bad and I feel sick",
        "Patient presents with substernal chest discomfort and dyspnea",
        "I've been feeling tired and have a headache for 3 days"
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {case}")
        print("-" * 40)
        
        # Full analysis
        result = api.analyze(case)
        
        if "error" in result:
            print(f"Error: {result['error']}")
            continue
        
        # Display key results
        symptoms = result['symptoms']['detected']
        primary = result['predictions']['primary']
        urgency = result['assessment']['urgency_level']
        
        print(f"Symptoms: {', '.join(symptoms)}")
        if primary:
            print(f"Primary Diagnosis: {primary['disease']} ({primary['confidence_percentage']:.1f}%)")
        print(f"Urgency: {urgency}")
        
        # Show AI analysis if available
        if 'ai_analysis' in result:
            print(f"AI Analysis: {result['ai_analysis'][:100]}...")
    
    print("\n" + "="*50)
    print("Demo completed")

if __name__ == "__main__":
    demo()
