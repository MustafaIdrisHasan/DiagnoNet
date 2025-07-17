#!/usr/bin/env python3
"""
Optimized Medical AI - Production-Ready System
Clean interface, ML-focused, minimal output
"""

import os
from medical_ai_api import MedicalAIAPI

def main():
    """Main interface for medical AI system"""
    # Set up environment - API key should be set externally
    # os.environ['GROQ_API_KEY'] = "your_groq_api_key_here"  # Set this in your environment
    
    # Initialize API
    api = MedicalAIAPI()
    
    if not api.ready:
        print("Error: Medical AI system not available")
        return
    
    print("Medical AI System Ready")
    print("Enter symptom descriptions (type 'quit' to exit):")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_input:
                continue
            
            # Analyze symptoms
            result = api.analyze(user_input)
            
            if "error" in result:
                print(f"Error: {result['error']}")
                continue
            
            # Display clean results
            symptoms = result['symptoms']['detected']
            predictions = result['predictions']
            assessment = result['assessment']
            
            print(f"\nSymptoms: {', '.join(symptoms)}")
            print(f"Confidence: {assessment['overall_confidence']:.1%}")
            
            if predictions['primary']:
                primary = predictions['primary']
                print(f"Diagnosis: {primary['disease']} ({predictions['ml_confidence']:.1%})")
                
                if predictions['differential']:
                    print("Alternatives:")
                    for pred in predictions['differential'][:2]:
                        print(f"  • {pred['disease']} ({pred['confidence_percentage']:.1f}%)")
            
            print(f"Urgency: {assessment['urgency_level']}")
            print(f"Recommendation: {assessment['recommendation']}")
            
            if 'ai_analysis' in result:
                print(f"\nClinical Analysis:\n{result['ai_analysis']}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nSession ended")

if __name__ == "__main__":
    main()
