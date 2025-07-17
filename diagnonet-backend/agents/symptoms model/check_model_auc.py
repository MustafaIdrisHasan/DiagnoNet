#!/usr/bin/env python3
"""
Script to check the AUC and other performance metrics of the trained medical AI model
"""

import joblib
import pandas as pd
import numpy as np
from pathlib import Path

def load_and_display_model_performance():
    """Load the trained model and display its performance metrics including AUC"""
    
    # Try to load the advanced model first
    model_files = [
        'advanced_disease_predictor.pkl',
        'disease_predictor_model.pkl',
        'backend/disease_predictor_model.pkl'
    ]
    
    model_data = None
    model_file_used = None
    
    for model_file in model_files:
        if Path(model_file).exists():
            try:
                print(f"Loading model from: {model_file}")
                model_data = joblib.load(model_file)
                model_file_used = model_file
                break
            except Exception as e:
                print(f"Failed to load {model_file}: {e}")
                continue
    
    if model_data is None:
        print("❌ No trained model found!")
        print("Available model files to check:")
        for model_file in model_files:
            exists = "✅" if Path(model_file).exists() else "❌"
            print(f"  {exists} {model_file}")
        return
    
    print(f"✅ Successfully loaded model from: {model_file_used}")
    print("=" * 60)
    
    # Check if this is an advanced model with performance metrics
    if 'model_performance' in model_data:
        print("🎯 ADVANCED MODEL PERFORMANCE METRICS")
        print("=" * 60)
        
        performance = model_data['model_performance']
        
        if not performance:
            print("❌ No performance metrics found in the model file")
            return
        
        # Display performance for each algorithm
        print(f"📊 Individual Model Performance ({len(performance)} algorithms):")
        print("-" * 60)
        
        best_auc = 0
        best_model = None
        
        for model_name, metrics in performance.items():
            print(f"\n🔬 {model_name.upper()}:")
            print(f"   Accuracy:    {metrics['accuracy']:.4f}")
            print(f"   Precision:   {metrics['precision']:.4f}")
            print(f"   Recall:      {metrics['recall']:.4f}")
            print(f"   F1-Score:    {metrics['f1_score']:.4f}")
            print(f"   CV Score:    {metrics['cv_mean']:.4f} ± {metrics['cv_std']:.4f}")
            
            # Display AUC if available
            if 'auc_score' in metrics and metrics['auc_score'] is not None:
                auc = metrics['auc_score']
                print(f"   AUC Score:   {auc:.4f}")
                if auc > best_auc:
                    best_auc = auc
                    best_model = model_name
            else:
                print(f"   AUC Score:   Not calculated")
        
        # Summary
        print("\n" + "=" * 60)
        print("📈 PERFORMANCE SUMMARY")
        print("=" * 60)
        
        if best_auc > 0:
            print(f"🏆 Best AUC Score: {best_auc:.4f} ({best_model})")
            
            # Interpret AUC score
            if best_auc >= 0.9:
                interpretation = "Excellent - Outstanding discriminative ability"
            elif best_auc >= 0.8:
                interpretation = "Good - Strong discriminative ability"
            elif best_auc >= 0.7:
                interpretation = "Fair - Acceptable discriminative ability"
            elif best_auc >= 0.6:
                interpretation = "Poor - Limited discriminative ability"
            else:
                interpretation = "Very Poor - No discriminative ability"
            
            print(f"📊 AUC Interpretation: {interpretation}")
        else:
            print("❌ No AUC scores available")
        
        # Best overall model
        best_cv_model = max(performance.items(), key=lambda x: x[1]['cv_mean'])
        print(f"🎯 Best CV Score: {best_cv_model[1]['cv_mean']:.4f} ({best_cv_model[0]})")
        
        # Model details
        print(f"\n🔧 Model Configuration:")
        if 'symptom_columns' in model_data:
            print(f"   Features: {len(model_data['symptom_columns'])} symptoms")
        if 'label_encoder' in model_data:
            print(f"   Diseases: {len(model_data['label_encoder'].classes_)} conditions")
        
        ensemble_available = 'ensemble_model' in model_data and model_data['ensemble_model'] is not None
        print(f"   Ensemble: {'✅ Available' if ensemble_available else '❌ Not available'}")
        
    else:
        # Basic model without detailed performance metrics
        print("📊 BASIC MODEL INFORMATION")
        print("=" * 60)
        print("❌ This model doesn't contain detailed performance metrics including AUC")
        print("💡 To get AUC scores, retrain the model using advanced_model_trainer.py")
        
        if 'symptom_columns' in model_data:
            print(f"   Features: {len(model_data['symptom_columns'])} symptoms")
        if 'label_encoder' in model_data:
            print(f"   Diseases: {len(model_data['label_encoder'].classes_)} conditions")

def retrain_with_auc():
    """Retrain the model to get AUC scores"""
    print("\n" + "=" * 60)
    print("🔄 RETRAINING MODEL TO GET AUC SCORES")
    print("=" * 60)
    
    try:
        from advanced_model_trainer import AdvancedDiseasePredictor
        from advanced_data_loader import AdvancedMedicalDataLoader
        
        print("📥 Loading training data...")
        loader = AdvancedMedicalDataLoader()
        data = loader.get_combined_dataset()
        
        print("🎯 Training advanced models with AUC calculation...")
        predictor = AdvancedDiseasePredictor()
        summary = predictor.train_models(data)
        
        print("💾 Saving updated model...")
        predictor.save_models()
        
        print("✅ Model retrained successfully!")
        print("\n🔄 Checking updated performance...")
        load_and_display_model_performance()
        
    except Exception as e:
        print(f"❌ Failed to retrain model: {e}")
        print("💡 Make sure all dependencies are installed and data is available")

if __name__ == "__main__":
    print("🏥 MEDICAL AI MODEL PERFORMANCE CHECKER")
    print("=" * 60)
    
    load_and_display_model_performance()
    
    # Ask if user wants to retrain for AUC if not available
    print("\n" + "=" * 60)
    response = input("🔄 Retrain model to calculate AUC scores? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        retrain_with_auc()
    else:
        print("✅ Performance check completed!")
