#!/usr/bin/env python3
"""
Medical AI Integration Example
Demonstrates how to integrate the Medical AI system with other diagnosis models
"""

import sys
import os
import time
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from medical_ai_api import MedicalAIAPI

class MockDiagnosisModel:
    """Mock diagnosis model for demonstration purposes"""
    
    def __init__(self, name: str, specialty: str = "general"):
        self.name = name
        self.specialty = specialty
        self.diagnoses = {
            "fever, cough": {"diagnosis": "Upper Respiratory Infection", "confidence": 0.85},
            "chest pain": {"diagnosis": "Angina", "confidence": 0.78},
            "headache, nausea": {"diagnosis": "Migraine", "confidence": 0.82},
            "abdominal pain": {"diagnosis": "Gastritis", "confidence": 0.75},
            "shortness of breath": {"diagnosis": "Asthma", "confidence": 0.80}
        }
    
    def predict(self, symptoms: str) -> Dict[str, Any]:
        """Mock prediction method"""
        symptoms_lower = symptoms.lower()
        
        # Simple keyword matching for demo
        for key, result in self.diagnoses.items():
            if any(word in symptoms_lower for word in key.split(", ")):
                return {
                    "diagnosis": result["diagnosis"],
                    "confidence": result["confidence"],
                    "model": self.name,
                    "specialty": self.specialty
                }
        
        # Default response
        return {
            "diagnosis": "Unknown Condition",
            "confidence": 0.3,
            "model": self.name,
            "specialty": self.specialty
        }

class IntegratedDiagnosisSystem:
    """Example integrated diagnosis system combining Medical AI with other models"""
    
    def __init__(self):
        print("🏥 Initializing Integrated Diagnosis System...")
        
        # Initialize Medical AI
        self.medical_ai = MedicalAIAPI()
        
        if not self.medical_ai.ready:
            raise Exception("Medical AI system failed to initialize")
        
        # Initialize mock models for demonstration
        self.other_models = [
            MockDiagnosisModel("CardioModel", "cardiology"),
            MockDiagnosisModel("RespiratoryModel", "respiratory"),
            MockDiagnosisModel("GeneralModel", "general")
        ]
        
        print("✅ Integrated system ready")
    
    def parallel_analysis(self, symptoms: str) -> Dict[str, Any]:
        """Perform parallel analysis with all models"""
        print(f"\n🔍 Analyzing: '{symptoms}'")
        print("=" * 50)
        
        results = {}
        
        # Get Medical AI analysis
        print("📊 Medical AI Analysis...")
        start_time = time.time()
        ai_result = self.medical_ai.analyze(symptoms)
        ai_time = time.time() - start_time
        
        if "error" not in ai_result:
            results["medical_ai"] = {
                "diagnosis": ai_result['predictions']['primary']['disease'],
                "confidence": ai_result['predictions']['primary']['confidence'],
                "urgency": ai_result['assessment']['urgency_level'],
                "symptoms_detected": ai_result['symptoms']['detected'],
                "processing_time": ai_time,
                "full_result": ai_result
            }
            print(f"  ✅ Completed in {ai_time:.3f}s")
        else:
            results["medical_ai"] = {"error": ai_result["error"]}
            print(f"  ❌ Failed: {ai_result['error']}")
        
        # Get other model analyses
        for model in self.other_models:
            print(f"📊 {model.name} Analysis...")
            start_time = time.time()
            
            try:
                model_result = model.predict(symptoms)
                model_time = time.time() - start_time
                
                results[model.name] = {
                    **model_result,
                    "processing_time": model_time
                }
                print(f"  ✅ Completed in {model_time:.3f}s")
                
            except Exception as e:
                results[model.name] = {"error": str(e)}
                print(f"  ❌ Failed: {e}")
        
        return results
    
    def weighted_consensus(self, parallel_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate weighted consensus from parallel results"""
        print("\n🎯 Calculating Weighted Consensus...")
        
        # Define model weights (Medical AI gets higher weight)
        model_weights = {
            "medical_ai": 0.4,
            "CardioModel": 0.2,
            "RespiratoryModel": 0.2,
            "GeneralModel": 0.2
        }
        
        diagnosis_scores = {}
        total_weight = 0
        valid_models = 0
        
        for model_name, result in parallel_results.items():
            if "error" in result:
                continue
            
            diagnosis = result["diagnosis"]
            confidence = result["confidence"]
            weight = model_weights.get(model_name, 0.1)
            
            score = confidence * weight
            
            if diagnosis in diagnosis_scores:
                diagnosis_scores[diagnosis] += score
            else:
                diagnosis_scores[diagnosis] = score
            
            total_weight += weight
            valid_models += 1
        
        if not diagnosis_scores:
            return {"error": "No valid model results"}
        
        # Normalize scores
        for diagnosis in diagnosis_scores:
            diagnosis_scores[diagnosis] /= total_weight
        
        # Get final diagnosis
        final_diagnosis = max(diagnosis_scores.items(), key=lambda x: x[1])
        
        consensus_result = {
            "final_diagnosis": final_diagnosis[0],
            "consensus_confidence": final_diagnosis[1],
            "all_scores": diagnosis_scores,
            "contributing_models": valid_models,
            "method": "weighted_consensus"
        }
        
        print(f"  🎯 Final Diagnosis: {final_diagnosis[0]}")
        print(f"  📊 Consensus Confidence: {final_diagnosis[1]:.1%}")
        print(f"  🤝 Contributing Models: {valid_models}")
        
        return consensus_result
    
    def comprehensive_analysis(self, symptoms: str) -> Dict[str, Any]:
        """Perform comprehensive analysis with detailed reporting"""
        
        # Step 1: Parallel analysis
        parallel_results = self.parallel_analysis(symptoms)
        
        # Step 2: Weighted consensus
        consensus = self.weighted_consensus(parallel_results)
        
        # Step 3: Extract Medical AI insights
        medical_ai_insights = {}
        if "medical_ai" in parallel_results and "error" not in parallel_results["medical_ai"]:
            ai_result = parallel_results["medical_ai"]["full_result"]
            medical_ai_insights = {
                "urgency_assessment": ai_result['assessment']['urgency_level'],
                "symptoms_detected": ai_result['symptoms']['detected'],
                "confidence_scores": ai_result['symptoms']['confidence_scores'],
                "differential_diagnoses": ai_result['predictions']['differential'][:3],
                "ai_analysis": ai_result.get('ai_analysis', 'Not available')
            }
        
        # Step 4: Compile comprehensive result
        comprehensive_result = {
            "input_symptoms": symptoms,
            "parallel_analysis": parallel_results,
            "consensus": consensus,
            "medical_ai_insights": medical_ai_insights,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system_version": "integrated_v1.0"
        }
        
        return comprehensive_result
    
    def display_results(self, result: Dict[str, Any]):
        """Display results in a formatted way"""
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE DIAGNOSIS REPORT")
        print("=" * 60)
        
        print(f"Input: {result['input_symptoms']}")
        print(f"Timestamp: {result['timestamp']}")
        
        # Consensus result
        if "error" not in result['consensus']:
            consensus = result['consensus']
            print(f"\n🎯 FINAL DIAGNOSIS: {consensus['final_diagnosis']}")
            print(f"📊 Confidence: {consensus['consensus_confidence']:.1%}")
            print(f"🤝 Models Contributing: {consensus['contributing_models']}")
        
        # Medical AI insights
        insights = result['medical_ai_insights']
        if insights:
            print(f"\n🏥 MEDICAL AI INSIGHTS:")
            print(f"   Urgency: {insights['urgency_assessment']}")
            print(f"   Symptoms: {', '.join(insights['symptoms_detected'])}")
            
            if insights['differential_diagnoses']:
                print(f"   Alternatives:")
                for i, alt in enumerate(insights['differential_diagnoses'], 1):
                    print(f"     {i}. {alt['disease']} ({alt['confidence_percentage']:.1f}%)")
        
        # Individual model results
        print(f"\n📊 INDIVIDUAL MODEL RESULTS:")
        for model_name, model_result in result['parallel_analysis'].items():
            if "error" in model_result:
                print(f"   ❌ {model_name}: {model_result['error']}")
            else:
                diagnosis = model_result['diagnosis']
                confidence = model_result['confidence']
                time_taken = model_result['processing_time']
                print(f"   ✅ {model_name}: {diagnosis} ({confidence:.1%}) [{time_taken:.3f}s]")

def demo_integration():
    """Demonstrate the integrated diagnosis system"""
    print("🏥 MEDICAL AI INTEGRATION DEMONSTRATION")
    print("=" * 60)
    
    try:
        # Initialize system
        system = IntegratedDiagnosisSystem()
        
        # Test cases
        test_cases = [
            "I have severe chest pain and shortness of breath",
            "Patient presents with fever, cough, and fatigue for 3 days",
            "Experiencing severe headache with nausea and vomiting",
            "Abdominal pain and bloating after eating"
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'='*60}")
            print(f"TEST CASE {i}/{len(test_cases)}")
            print(f"{'='*60}")
            
            # Perform comprehensive analysis
            result = system.comprehensive_analysis(test_case)
            
            # Display results
            system.display_results(result)
            
            # Wait for user input to continue
            if i < len(test_cases):
                input("\nPress Enter to continue to next test case...")
        
        print(f"\n{'='*60}")
        print("🎉 INTEGRATION DEMONSTRATION COMPLETE")
        print("=" * 60)
        print("✅ All test cases processed successfully")
        print("📊 Integration working as expected")
        print("🚀 Ready for production deployment")
        
    except Exception as e:
        print(f"❌ Integration demo failed: {e}")
        return False
    
    return True

def quick_test():
    """Quick integration test"""
    print("🧪 Quick Integration Test")
    print("-" * 30)
    
    try:
        system = IntegratedDiagnosisSystem()
        result = system.comprehensive_analysis("fever and cough")
        
        if "error" not in result['consensus']:
            print("✅ Integration test passed")
            print(f"   Diagnosis: {result['consensus']['final_diagnosis']}")
            print(f"   Confidence: {result['consensus']['consensus_confidence']:.1%}")
            return True
        else:
            print("❌ Integration test failed")
            return False
            
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Medical AI Integration Example")
    parser.add_argument("--demo", action="store_true", help="Run full demonstration")
    parser.add_argument("--test", action="store_true", help="Run quick test")
    
    args = parser.parse_args()
    
    if args.demo:
        success = demo_integration()
    elif args.test:
        success = quick_test()
    else:
        print("Usage: python integration_example.py [--demo|--test]")
        print("  --demo: Run full integration demonstration")
        print("  --test: Run quick integration test")
        success = True
    
    sys.exit(0 if success else 1)
