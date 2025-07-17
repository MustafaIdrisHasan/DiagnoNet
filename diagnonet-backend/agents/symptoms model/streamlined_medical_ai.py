#!/usr/bin/env python3
"""
Streamlined Medical AI - Production-Ready ML-Focused System
Clean interface with minimal output, ML-driven predictions
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any

# Suppress verbose logging
logging.getLogger().setLevel(logging.ERROR)

class StreamlinedMedicalAI:
    """Production-ready medical AI with clean interface and ML focus"""
    
    def __init__(self):
        self.nlp_processor = None
        self.ml_predictor = None
        self.groq_client = None
        self.initialized = False
        self._initialize_system()
    
    def _initialize_system(self) -> bool:
        """Initialize system components with robust ML focus"""
        try:
            # Initialize NLP processor (enhanced with fallback)
            try:
                from enhanced_medical_nlp import EnhancedMedicalNLP
                self.nlp_processor = EnhancedMedicalNLP()
            except ImportError:
                from simplified_medical_nlp import SimplifiedMedicalNLP
                self.nlp_processor = SimplifiedMedicalNLP()

            # Initialize ML predictor with robust error handling
            self.ml_predictor = self._initialize_ml_predictor()
            if not self.ml_predictor:
                return False

            # Initialize Groq AI (optional - for enhanced analysis)
            try:
                api_key = os.getenv('GROQ_API_KEY')
                if api_key:
                    from groq import Groq
                    self.groq_client = Groq(api_key=api_key)
                    print("✅ Groq AI enhancement enabled")
                else:
                    print("ℹ️  Groq AI not configured (optional) - using ML-only predictions")
                    print("   To enable enhanced analysis, set GROQ_API_KEY environment variable")
            except ImportError:
                print("ℹ️  Groq package not installed (optional) - using ML-only predictions")
                print("   To install: pip install groq")
            except Exception as e:
                print(f"ℹ️  Groq AI initialization failed (optional): {e}")
                print("   Continuing with ML-only predictions")

            self.initialized = True
            return True

        except Exception as e:
            print(f"System initialization error: {e}")
            return False

    def _initialize_ml_predictor(self):
        """Initialize ML predictor with multiple fallback strategies"""

        # Strategy 1: Try to load existing advanced model
        try:
            from advanced_model_trainer import AdvancedDiseasePredictor
            predictor = AdvancedDiseasePredictor()

            if predictor.load_models('advanced_disease_predictor.pkl'):
                return predictor

            # Strategy 2: Train new advanced ensemble
            if predictor.train_advanced_ensemble():
                return predictor

        except Exception as e:
            print(f"Advanced ML predictor failed: {e}")

        # Strategy 3: Create robust ML predictor from scratch
        try:
            return self._create_robust_ml_predictor()
        except Exception as e:
            print(f"Robust ML predictor creation failed: {e}")
            return None

    def _create_robust_ml_predictor(self):
        """Create a robust ML predictor that always works"""
        import numpy as np
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import LabelEncoder
        import pickle
        import os

        class RobustMLPredictor:
            def __init__(self):
                self.model = RandomForestClassifier(n_estimators=100, random_state=42)
                self.label_encoder = LabelEncoder()
                self.symptom_columns = [
                    'chest_pain', 'shortness_of_breath', 'headache', 'fever', 'nausea',
                    'vomiting', 'cough', 'fatigue', 'dizziness', 'sweating',
                    'joint_pain', 'muscle_pain', 'abdominal_pain', 'back_pain',
                    'sore_throat', 'runny_nose', 'rash', 'itching', 'swelling', 'numbness'
                ]
                self.is_trained = False
                self._train_model()

            def _train_model(self):
                """Train model with synthetic medical data"""
                # Create synthetic training data based on medical knowledge
                training_data = self._generate_medical_training_data()
                X, y = training_data

                # Train the model
                self.label_encoder.fit(y)
                y_encoded = self.label_encoder.transform(y)
                self.model.fit(X, y_encoded)
                self.is_trained = True

            def _generate_medical_training_data(self):
                """Generate medically realistic training data"""
                np.random.seed(42)

                # Define disease patterns based on medical knowledge
                disease_patterns = {
                    'Myocardial Infarction': {
                        'chest_pain': 0.95, 'shortness_of_breath': 0.80, 'sweating': 0.70,
                        'nausea': 0.60, 'fatigue': 0.50
                    },
                    'Pneumonia': {
                        'cough': 0.90, 'fever': 0.85, 'shortness_of_breath': 0.70,
                        'fatigue': 0.60, 'chest_pain': 0.40
                    },
                    'Migraine': {
                        'headache': 0.95, 'nausea': 0.70, 'dizziness': 0.50,
                        'fatigue': 0.40
                    },
                    'Gastroenteritis': {
                        'nausea': 0.90, 'vomiting': 0.80, 'abdominal_pain': 0.85,
                        'fever': 0.40, 'fatigue': 0.50
                    },
                    'Influenza': {
                        'fever': 0.90, 'fatigue': 0.85, 'muscle_pain': 0.80,
                        'headache': 0.70, 'cough': 0.60
                    },
                    'Hypertension': {
                        'headache': 0.60, 'dizziness': 0.50, 'fatigue': 0.40
                    },
                    'Arthritis': {
                        'joint_pain': 0.95, 'muscle_pain': 0.70, 'fatigue': 0.50
                    },
                    'Common Cold': {
                        'runny_nose': 0.90, 'sore_throat': 0.80, 'cough': 0.70,
                        'fatigue': 0.40
                    }
                }

                X = []
                y = []

                # Generate samples for each disease
                for disease, pattern in disease_patterns.items():
                    for _ in range(100):  # 100 samples per disease
                        sample = np.zeros(len(self.symptom_columns))

                        for symptom, probability in pattern.items():
                            if symptom in self.symptom_columns:
                                idx = self.symptom_columns.index(symptom)
                                # Add some noise to make it realistic
                                if np.random.random() < probability:
                                    sample[idx] = 1

                        X.append(sample)
                        y.append(disease)

                return np.array(X), np.array(y)

            def predict_disease(self, symptoms):
                """Predict diseases from symptom list"""
                if not self.is_trained:
                    return []

                # Create feature vector
                feature_vector = np.zeros(len(self.symptom_columns))
                for symptom in symptoms:
                    symptom_clean = symptom.lower().replace(' ', '_')
                    if symptom_clean in self.symptom_columns:
                        idx = self.symptom_columns.index(symptom_clean)
                        feature_vector[idx] = 1

                # Get predictions
                probabilities = self.model.predict_proba([feature_vector])[0]

                # Format results
                results = []
                for i, prob in enumerate(probabilities):
                    disease = self.label_encoder.inverse_transform([i])[0]
                    confidence_percentage = prob * 100

                    results.append({
                        'disease': disease,
                        'confidence_percentage': confidence_percentage,
                        'confidence_level': self._get_confidence_level(prob)
                    })

                # Sort by confidence
                results.sort(key=lambda x: x['confidence_percentage'], reverse=True)
                return results

            def _get_confidence_level(self, confidence):
                """Convert confidence to medical terms"""
                if confidence >= 0.8:
                    return "Very High - Strong diagnostic indication"
                elif confidence >= 0.6:
                    return "High - Significant diagnostic consideration"
                elif confidence >= 0.4:
                    return "Moderate - Possible diagnostic consideration"
                elif confidence >= 0.2:
                    return "Low - Differential diagnosis consideration"
                else:
                    return "Very Low - Remote diagnostic possibility"

        return RobustMLPredictor()
    
    def analyze_symptoms(self, input_text: str) -> Dict[str, Any]:
        """
        Main analysis function: Natural language input → ML predictions
        
        Args:
            input_text: Natural language description of symptoms
            
        Returns:
            Dict containing extracted symptoms and ML predictions
        """
        if not self.initialized:
            return {"error": "System not initialized"}
        
        try:
            # Step 1: Extract symptoms using enhanced NLP
            nlp_result = self.nlp_processor.process_natural_language(input_text)
            extracted_symptoms = nlp_result.get('normalized_symptoms', {})
            
            if not extracted_symptoms:
                return {
                    "symptoms": {},
                    "predictions": [],
                    "confidence": 0.0,
                    "message": "No symptoms detected in input"
                }
            
            # Step 2: Get ML predictions
            symptom_list = list(extracted_symptoms.keys())
            ml_predictions = self.ml_predictor.predict_disease(symptom_list)
            
            # Step 3: Enhance with Groq AI if available
            ai_analysis = None
            if self.groq_client and ml_predictions:
                ai_analysis = self._get_ai_analysis(symptom_list, ml_predictions, input_text)
            
            # Step 4: Format clean response
            return self._format_response(
                symptoms=extracted_symptoms,
                predictions=ml_predictions,
                nlp_confidence=nlp_result.get('overall_confidence', 0.0),
                ai_analysis=ai_analysis
            )
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _get_ai_analysis(self, symptoms: List[str], predictions: List[Dict], input_text: str) -> Optional[str]:
        """Get AI-enhanced clinical analysis"""
        try:
            # Create focused prompt for clinical analysis
            top_prediction = predictions[0] if predictions else None
            
            prompt = f"""
            Clinical Analysis Request:
            
            Symptoms: {', '.join(symptoms)}
            Top ML Prediction: {top_prediction['disease'] if top_prediction else 'None'} ({top_prediction['confidence_percentage']:.1f}% confidence)
            
            Provide a concise clinical assessment focusing on:
            1. Symptom pattern significance
            2. Differential diagnosis considerations
            3. Urgency level (Emergency/Urgent/Routine)
            4. Key clinical recommendations
            
            Keep response under 200 words, professional medical tone.
            """
            
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a medical AI providing concise clinical analysis."},
                    {"role": "user", "content": prompt}
                ],
                model="llama3-70b-8192",
                temperature=0.3,
                max_tokens=250
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception:
            return None
    
    def _format_response(self, symptoms: Dict[str, float], predictions: List[Dict], 
                        nlp_confidence: float, ai_analysis: Optional[str]) -> Dict[str, Any]:
        """Format clean, professional response"""
        
        # Calculate overall confidence
        if predictions:
            ml_confidence = predictions[0]['confidence_percentage'] / 100.0
            overall_confidence = (nlp_confidence + ml_confidence) / 2
        else:
            overall_confidence = nlp_confidence
        
        # Determine urgency level
        urgency = self._assess_urgency(symptoms, predictions)
        
        response = {
            "symptoms": {
                "detected": list(symptoms.keys()),
                "confidence_scores": symptoms,
                "extraction_confidence": round(nlp_confidence, 3)
            },
            "predictions": {
                "primary": predictions[0] if predictions else None,
                "differential": predictions[1:4] if len(predictions) > 1 else [],
                "ml_confidence": round(predictions[0]['confidence_percentage'] / 100.0, 3) if predictions else 0.0
            },
            "assessment": {
                "overall_confidence": round(overall_confidence, 3),
                "urgency_level": urgency,
                "recommendation": self._get_urgency_recommendation(urgency)
            }
        }
        
        # Add AI analysis if available
        if ai_analysis:
            response["ai_analysis"] = ai_analysis
        
        return response
    
    def _assess_urgency(self, symptoms: Dict[str, float], predictions: List[Dict]) -> str:
        """Assess clinical urgency based on symptoms and predictions"""
        
        # Emergency symptoms
        emergency_symptoms = ['chest_pain', 'shortness_of_breath', 'severe_headache', 'confusion']
        emergency_diseases = ['Myocardial Infarction', 'Stroke', 'Pulmonary Embolism']
        
        # Check for emergency indicators
        has_emergency_symptom = any(symptom in symptoms for symptom in emergency_symptoms)
        has_emergency_prediction = any(
            pred['disease'] in emergency_diseases and pred['confidence_percentage'] > 70
            for pred in predictions
        )
        
        if has_emergency_symptom or has_emergency_prediction:
            return "Emergency"
        
        # Check for urgent conditions
        urgent_symptoms = ['fever', 'severe_pain', 'persistent_vomiting']
        has_urgent_symptom = any(symptom in symptoms for symptom in urgent_symptoms)
        
        if has_urgent_symptom or (predictions and predictions[0]['confidence_percentage'] > 80):
            return "Urgent"
        
        return "Routine"
    
    def _get_urgency_recommendation(self, urgency: str) -> str:
        """Get recommendation based on urgency level"""
        recommendations = {
            "Emergency": "Seek immediate emergency medical attention",
            "Urgent": "Schedule urgent medical consultation within 24 hours",
            "Routine": "Schedule routine medical consultation"
        }
        return recommendations.get(urgency, "Consult healthcare provider")
    
    def batch_analyze(self, inputs: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple symptom descriptions"""
        return [self.analyze_symptoms(input_text) for input_text in inputs]
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information and capabilities"""
        return {
            "status": "ready" if self.initialized else "error",
            "components": {
                "nlp_processor": type(self.nlp_processor).__name__ if self.nlp_processor else None,
                "ml_predictor": "AdvancedDiseasePredictor" if self.ml_predictor else None,
                "ai_enhancement": "Groq AI" if self.groq_client else None
            },
            "capabilities": [
                "Natural language symptom extraction",
                "ML-based disease prediction",
                "Clinical urgency assessment",
                "AI-enhanced analysis" if self.groq_client else None
            ]
        }

def main():
    """Interactive command-line interface"""
    # Set up environment - API key should be set externally
    # os.environ['GROQ_API_KEY'] = "your_groq_api_key_here"  # Set this in your environment
    
    # Initialize system
    ai = StreamlinedMedicalAI()
    
    if not ai.initialized:
        print("❌ Error: System initialization failed")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure Python packages are installed: pip install -r requirements.txt")
        print("2. For enhanced analysis, set GROQ_API_KEY environment variable")
        print("3. Check that all required model files are present")
        return

    print("🏥 Medical AI Ready")
    if ai.groq_client:
        print("✨ Enhanced AI analysis enabled")
    else:
        print("📊 ML-only analysis mode (still fully functional)")
    print("\nEnter symptom descriptions (type 'quit' to exit):")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_input:
                continue
            
            # Analyze symptoms
            result = ai.analyze_symptoms(user_input)
            
            if "error" in result:
                print(f"Error: {result['error']}")
                continue
            
            # Display results
            print("\n" + "="*60)
            print("MEDICAL ANALYSIS RESULTS")
            print("="*60)
            
            # Symptoms
            symptoms = result['symptoms']
            print(f"Symptoms Detected: {', '.join(symptoms['detected'])}")
            print(f"Extraction Confidence: {symptoms['extraction_confidence']:.1%}")
            
            # Predictions
            predictions = result['predictions']
            if predictions['primary']:
                primary = predictions['primary']
                print(f"\nPrimary Diagnosis: {primary['disease']}")
                print(f"ML Confidence: {predictions['ml_confidence']:.1%}")
                
                if predictions['differential']:
                    print("\nDifferential Diagnoses:")
                    for i, pred in enumerate(predictions['differential'], 2):
                        print(f"  {i}. {pred['disease']} ({pred['confidence_percentage']:.1f}%)")
            
            # Assessment
            assessment = result['assessment']
            print(f"\nUrgency Level: {assessment['urgency_level']}")
            print(f"Recommendation: {assessment['recommendation']}")
            print(f"Overall Confidence: {assessment['overall_confidence']:.1%}")
            
            # AI Analysis
            if 'ai_analysis' in result:
                print(f"\nAI Clinical Analysis:")
                print(result['ai_analysis'])
            
            print("="*60)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nMedical AI session ended")

if __name__ == "__main__":
    main()
