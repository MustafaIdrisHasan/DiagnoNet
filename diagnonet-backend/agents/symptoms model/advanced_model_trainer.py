"""
Advanced Model Trainer with Multiple ML Algorithms
Implements ensemble methods, hyperparameter tuning, and comprehensive evaluation
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import (
    train_test_split, cross_val_score, GridSearchCV, 
    StratifiedKFold, learning_curve
)
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    classification_report, accuracy_score, confusion_matrix,
    precision_recall_fscore_support, roc_auc_score, roc_curve
)
from sklearn.calibration import CalibratedClassifierCV
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
import warnings
warnings.filterwarnings('ignore')
from typing import List, Dict, Optional, Any

# Try to import advanced ML libraries
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    
try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False

try:
    from catboost import CatBoostClassifier
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedDiseasePredictor:
    def __init__(self):
        self.models = {}
        self.ensemble_model = None
        self.label_encoder = None
        self.scaler = None
        self.symptom_columns = []
        self.disease_column = None
        self.is_trained = False
        self.model_performance = {}
        
    def prepare_data(self, data):
        """Advanced data preparation with feature engineering"""
        logger.info("Preparing data with advanced preprocessing...")
        
        # Basic setup
        self.disease_column = 'disease'
        self.symptom_columns = [col for col in data.columns if col != self.disease_column]
        
        # Features and target
        X = data[self.symptom_columns].copy()
        y = data[self.disease_column].copy()
        
        # Feature engineering
        logger.info("Performing feature engineering...")
        
        # 1. Symptom count features
        X['total_symptoms'] = X.sum(axis=1)
        X['symptom_ratio'] = X['total_symptoms'] / len(self.symptom_columns)
        
        # 2. System-based symptom groups
        respiratory_symptoms = [col for col in self.symptom_columns 
                              if any(term in col.lower() for term in 
                                   ['cough', 'breath', 'chest', 'throat', 'nose'])]
        gi_symptoms = [col for col in self.symptom_columns 
                      if any(term in col.lower() for term in 
                           ['nausea', 'vomit', 'diarrhea', 'abdominal', 'stomach'])]
        neuro_symptoms = [col for col in self.symptom_columns 
                         if any(term in col.lower() for term in 
                              ['headache', 'dizziness', 'confusion', 'memory'])]
        
        if respiratory_symptoms:
            X['respiratory_score'] = X[respiratory_symptoms].sum(axis=1)
        if gi_symptoms:
            X['gi_score'] = X[gi_symptoms].sum(axis=1)
        if neuro_symptoms:
            X['neuro_score'] = X[neuro_symptoms].sum(axis=1)
        
        # 3. Symptom combinations (interaction features)
        common_pairs = [
            ('fever', 'cough'), ('nausea', 'vomiting'), 
            ('headache', 'fatigue'), ('chest_pain', 'shortness_of_breath')
        ]
        
        for symptom1, symptom2 in common_pairs:
            if symptom1 in self.symptom_columns and symptom2 in self.symptom_columns:
                X[f'{symptom1}_{symptom2}_combo'] = X[symptom1] * X[symptom2]
        
        # Update symptom columns to include engineered features
        self.symptom_columns = X.columns.tolist()
        
        # Encode labels
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Scale features for algorithms that need it
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        X_scaled = pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
        
        logger.info(f"✓ Data prepared: {X.shape[0]} samples, {X.shape[1]} features")
        logger.info(f"✓ {len(self.label_encoder.classes_)} disease classes")
        
        return X, X_scaled, y_encoded
    
    def initialize_models(self):
        """Initialize multiple ML models with optimized parameters"""
        logger.info("Initializing advanced ML models...")
        
        self.models = {
            'random_forest': RandomForestClassifier(
                n_estimators=200,
                max_depth=20,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
                class_weight='balanced'
            ),
            
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=150,
                learning_rate=0.1,
                max_depth=8,
                random_state=42
            ),
            
            'logistic_regression': LogisticRegression(
                random_state=42,
                max_iter=1000,
                class_weight='balanced'
            ),
            
            'svm': SVC(
                kernel='rbf',
                probability=True,
                random_state=42,
                class_weight='balanced'
            ),
            
            'neural_network': MLPClassifier(
                hidden_layer_sizes=(100, 50),
                max_iter=500,
                random_state=42,
                early_stopping=True,
                validation_fraction=0.1
            )
        }
        
        # Add advanced models if available
        if XGBOOST_AVAILABLE:
            self.models['xgboost'] = xgb.XGBClassifier(
                n_estimators=150,
                learning_rate=0.1,
                max_depth=8,
                random_state=42,
                eval_metric='mlogloss'
            )
            
        if LIGHTGBM_AVAILABLE:
            self.models['lightgbm'] = lgb.LGBMClassifier(
                n_estimators=150,
                learning_rate=0.1,
                max_depth=8,
                random_state=42,
                verbose=-1
            )
            
        if CATBOOST_AVAILABLE:
            self.models['catboost'] = CatBoostClassifier(
                iterations=150,
                learning_rate=0.1,
                depth=8,
                random_state=42,
                verbose=False
            )
        
        logger.info(f"✓ Initialized {len(self.models)} models")
        return self.models
    
    def train_individual_models(self, X, X_scaled, y):
        """Train individual models and evaluate performance"""
        logger.info("Training individual models...")
        
        # Split data
        X_train, X_test, X_train_scaled, X_test_scaled, y_train, y_test = train_test_split(
            X, X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        
        for name, model in self.models.items():
            logger.info(f"Training {name}...")
            
            try:
                # Choose appropriate data (scaled for some models)
                if name in ['logistic_regression', 'svm', 'neural_network']:
                    train_X, test_X = X_train_scaled, X_test_scaled
                else:
                    train_X, test_X = X_train, X_test
                
                # Train model
                model.fit(train_X, y_train)
                
                # Predictions
                y_pred = model.predict(test_X)
                y_pred_proba = model.predict_proba(test_X)
                
                # Cross-validation scores
                cv_scores = cross_val_score(model, train_X, y_train, cv=cv, scoring='accuracy')
                
                # Calculate metrics
                accuracy = accuracy_score(y_test, y_pred)
                precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')

                # Calculate AUC score for multiclass
                try:
                    # For multiclass, use ovr (one-vs-rest) strategy
                    auc_score = roc_auc_score(y_test, y_pred_proba, multi_class='ovr', average='weighted')
                except Exception as e:
                    logger.warning(f"Could not calculate AUC for {name}: {e}")
                    auc_score = None

                # Store performance
                self.model_performance[name] = {
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'f1_score': f1,
                    'auc_score': auc_score,
                    'cv_mean': cv_scores.mean(),
                    'cv_std': cv_scores.std(),
                    'predictions': y_pred,
                    'probabilities': y_pred_proba
                }
                
                logger.info(f"✓ {name}: Accuracy={accuracy:.4f}, CV={cv_scores.mean():.4f}±{cv_scores.std():.4f}")
                
            except Exception as e:
                logger.warning(f"Failed to train {name}: {e}")
                if name in self.models:
                    del self.models[name]
        
        return X_train, X_test, X_train_scaled, X_test_scaled, y_train, y_test
    
    def create_ensemble_model(self, X_train, X_train_scaled, y_train):
        """Create an ensemble model from the best performing individual models"""
        logger.info("Creating ensemble model...")
        
        # Select top performing models
        sorted_models = sorted(self.model_performance.items(), 
                             key=lambda x: x[1]['cv_mean'], reverse=True)
        
        top_models = []
        for name, performance in sorted_models[:5]:  # Top 5 models
            if name in self.models:
                model = self.models[name]
                
                # Use appropriate data for each model
                if name in ['logistic_regression', 'svm', 'neural_network']:
                    # Retrain on full training data
                    model.fit(X_train_scaled, y_train)
                else:
                    model.fit(X_train, y_train)
                
                top_models.append((name, model))
        
        # Create voting ensemble
        if len(top_models) >= 3:
            self.ensemble_model = VotingClassifier(
                estimators=top_models,
                voting='soft'  # Use probability voting
            )
            
            # For ensemble, we need to handle mixed data types
            # Use original features for simplicity
            self.ensemble_model.fit(X_train, y_train)
            
            logger.info(f"✓ Ensemble created with {len(top_models)} models")
        else:
            logger.warning("Not enough models for ensemble, using best single model")
            best_model_name = sorted_models[0][0]
            self.ensemble_model = self.models[best_model_name]
    
    def train_models(self, data):
        """Main training pipeline"""
        logger.info("Starting advanced model training pipeline...")
        
        # Prepare data
        X, X_scaled, y = self.prepare_data(data)
        
        # Initialize models
        self.initialize_models()
        
        # Train individual models
        X_train, X_test, X_train_scaled, X_test_scaled, y_train, y_test = \
            self.train_individual_models(X, X_scaled, y)
        
        # Create ensemble
        self.create_ensemble_model(X_train, X_train_scaled, y_train)
        
        # Calibrate ensemble for better probability estimates
        if self.ensemble_model is not None:
            logger.info("Calibrating ensemble model...")
            self.ensemble_model = CalibratedClassifierCV(
                self.ensemble_model, 
                method='isotonic', 
                cv=3
            )
            self.ensemble_model.fit(X_train, y_train)
        
        self.is_trained = True
        logger.info("✓ Advanced model training completed!")
        
        return self.get_training_summary()
    
    def get_training_summary(self):
        """Get comprehensive training summary"""
        if not self.model_performance:
            return None
        
        summary = {
            'models_trained': len(self.model_performance),
            'best_model': max(self.model_performance.items(), 
                            key=lambda x: x[1]['cv_mean']),
            'performance_comparison': self.model_performance,
            'ensemble_available': self.ensemble_model is not None,
            'feature_count': len(self.symptom_columns),
            'disease_count': len(self.label_encoder.classes_)
        }
        
        return summary
    
    def predict_disease(self, symptoms_input, return_probabilities=True):
        """Advanced prediction with uncertainty quantification"""
        if not self.is_trained or self.ensemble_model is None:
            raise ValueError("Models not trained yet!")
        
        # Prepare input
        feature_vector = np.zeros(len(self.symptom_columns))
        
        # Handle symptom input
        if isinstance(symptoms_input, str):
            symptoms_list = [s.strip().lower() for s in symptoms_input.split(',')]
        else:
            symptoms_list = [s.lower().strip() for s in symptoms_input]
        
        # Enhanced symptom mapping with clinical validation
        mapped_symptoms = []
        for i, feature in enumerate(self.symptom_columns):
            feature_name = feature.lower().replace('_', ' ')
            if any(symptom in feature_name or feature_name in symptom
                   for symptom in symptoms_list):
                feature_vector[i] = 1
                mapped_symptoms.append(feature)

        # Apply clinical validation
        if not self._validate_symptom_disease_compatibility(mapped_symptoms):
            # Return low-confidence results for incompatible combinations
            return self._create_low_confidence_results("Symptom combination requires clinical review")
        
        # Handle engineered features
        if 'total_symptoms' in self.symptom_columns:
            idx = self.symptom_columns.index('total_symptoms')
            feature_vector[idx] = np.sum(feature_vector[:len([col for col in self.symptom_columns 
                                                            if not col.startswith(('total_', 'symptom_', 
                                                                                  'respiratory_', 'gi_', 
                                                                                  'neuro_'))])])
        
        # Get predictions
        probabilities = self.ensemble_model.predict_proba([feature_vector])[0]
        
        # Get top predictions with confidence scores
        top_indices = np.argsort(probabilities)[::-1][:10]  # Top 10
        
        predictions = []
        for idx in top_indices:
            disease = self.label_encoder.inverse_transform([idx])[0]
            confidence = probabilities[idx]
            
            if confidence > 0.001:  # Only include meaningful predictions
                predictions.append({
                    'disease': disease,
                    'confidence': float(confidence),
                    'confidence_percentage': float(confidence * 100),
                    'confidence_level': self._interpret_confidence(confidence)
                })
        
        return predictions
    
    def _interpret_confidence(self, confidence):
        """Interpret confidence scores in medical terms"""
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

    def _validate_symptom_disease_compatibility(self, symptoms: List[str]) -> bool:
        """Validate if symptoms are compatible with potential diseases"""

        # Define disease-symptom compatibility rules
        disease_symptom_rules = {
            'cardiovascular': {
                'required_symptoms': ['chest_pain', 'shortness_of_breath'],
                'compatible_symptoms': ['nausea', 'sweating', 'dizziness', 'palpitations', 'fatigue'],
                'incompatible_symptoms': ['joint_pain', 'rash', 'diarrhea']
            },
            'respiratory': {
                'required_symptoms': ['cough', 'shortness_of_breath'],
                'compatible_symptoms': ['fever', 'sputum', 'chest_pain', 'wheezing'],
                'incompatible_symptoms': ['joint_pain', 'rash']
            },
            'neurological': {
                'required_symptoms': ['headache', 'dizziness'],
                'compatible_symptoms': ['nausea', 'confusion', 'weakness', 'vision_changes'],
                'incompatible_symptoms': ['cough', 'sputum', 'diarrhea']
            }
        }

        # Check for obvious incompatibilities
        symptom_set = set(symptoms)

        for system, rules in disease_symptom_rules.items():
            has_required = any(req in symptom_set for req in rules['required_symptoms'])
            has_incompatible = any(inc in symptom_set for inc in rules['incompatible_symptoms'])

            if has_required and has_incompatible:
                # Strong incompatibility detected
                return False

        return True

    def _create_low_confidence_results(self, reason: str) -> List[Dict]:
        """Create low-confidence results when validation fails"""
        return [{
            'disease': 'Clinical Review Required',
            'confidence': 0.1,
            'confidence_percentage': 10.0,
            'confidence_level': 'Very Low - Clinical validation needed',
            'validation_note': reason
        }]

    def train_advanced_ensemble(self):
        """Train the advanced ensemble model with synthetic data if needed"""
        try:
            # Create synthetic medical data for training
            logger.info("Creating synthetic medical training data...")

            # Define common symptoms and diseases
            symptoms = [
                'fever', 'cough', 'headache', 'fatigue', 'nausea', 'vomiting',
                'chest_pain', 'shortness_of_breath', 'abdominal_pain', 'diarrhea',
                'muscle_aches', 'sore_throat', 'runny_nose', 'dizziness'
            ]

            diseases = [
                'Common Cold', 'Influenza', 'Pneumonia', 'Gastroenteritis',
                'Migraine', 'Hypertension', 'Diabetes', 'Arthritis',
                'Myocardial Infarction', 'Asthma'
            ]

            # Generate synthetic training data
            import numpy as np
            import pandas as pd

            np.random.seed(42)
            n_samples = 1000

            # Create symptom patterns for each disease
            data = []
            for _ in range(n_samples):
                disease = np.random.choice(diseases)
                symptom_vector = np.zeros(len(symptoms))

                # Define disease-specific symptom patterns
                if disease == 'Common Cold':
                    symptom_vector[[symptoms.index(s) for s in ['cough', 'runny_nose', 'sore_throat'] if s in symptoms]] = 1
                elif disease == 'Influenza':
                    symptom_vector[[symptoms.index(s) for s in ['fever', 'muscle_aches', 'fatigue', 'headache'] if s in symptoms]] = 1
                elif disease == 'Pneumonia':
                    symptom_vector[[symptoms.index(s) for s in ['fever', 'cough', 'chest_pain', 'shortness_of_breath'] if s in symptoms]] = 1
                elif disease == 'Myocardial Infarction':
                    symptom_vector[[symptoms.index(s) for s in ['chest_pain', 'shortness_of_breath', 'nausea'] if s in symptoms]] = 1
                elif disease == 'Gastroenteritis':
                    symptom_vector[[symptoms.index(s) for s in ['nausea', 'vomiting', 'diarrhea', 'abdominal_pain'] if s in symptoms]] = 1

                # Add some random noise
                noise_indices = np.random.choice(len(symptoms), size=np.random.randint(0, 3), replace=False)
                symptom_vector[noise_indices] = np.random.choice([0, 1], size=len(noise_indices), p=[0.8, 0.2])

                row = dict(zip(symptoms, symptom_vector))
                row['disease'] = disease
                data.append(row)

            df = pd.DataFrame(data)

            # Train the model
            logger.info("Training advanced ensemble model...")
            self.prepare_data(df)
            X_train, X_test, y_train, y_test = self.split_data()
            self.train_individual_models(X_train, y_train)
            self.create_ensemble(X_train, y_train)
            self.evaluate_models(X_test, y_test)

            logger.info("✓ Advanced ensemble training completed successfully")
            return True

        except Exception as e:
            logger.error(f"Advanced ensemble training failed: {e}")
            return False

    def save_models(self, filepath='advanced_disease_predictor.pkl'):
        """Save all trained models and components"""
        if not self.is_trained:
            raise ValueError("No trained models to save!")
        
        model_data = {
            'ensemble_model': self.ensemble_model,
            'individual_models': self.models,
            'label_encoder': self.label_encoder,
            'scaler': self.scaler,
            'symptom_columns': self.symptom_columns,
            'disease_column': self.disease_column,
            'model_performance': self.model_performance,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"✓ Advanced models saved to {filepath}")
    
    def load_models(self, filepath='advanced_disease_predictor.pkl'):
        """Load pre-trained models"""
        try:
            model_data = joblib.load(filepath)
            
            self.ensemble_model = model_data['ensemble_model']
            self.models = model_data['individual_models']
            self.label_encoder = model_data['label_encoder']
            self.scaler = model_data['scaler']
            self.symptom_columns = model_data['symptom_columns']
            self.disease_column = model_data['disease_column']
            self.model_performance = model_data['model_performance']
            self.is_trained = model_data['is_trained']
            
            logger.info(f"✓ Advanced models loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            return False

    def generate_model_report(self):
        """Generate comprehensive model evaluation report"""
        if not self.model_performance:
            return None

        report = {
            'summary': {
                'total_models': len(self.model_performance),
                'best_model': max(self.model_performance.items(),
                                key=lambda x: x[1]['cv_mean']),
                'ensemble_available': self.ensemble_model is not None
            },
            'detailed_performance': {},
            'recommendations': []
        }

        # Detailed performance for each model
        for name, perf in self.model_performance.items():
            model_metrics = {
                'accuracy': f"{perf['accuracy']:.4f}",
                'precision': f"{perf['precision']:.4f}",
                'recall': f"{perf['recall']:.4f}",
                'f1_score': f"{perf['f1_score']:.4f}",
                'cv_score': f"{perf['cv_mean']:.4f} ± {perf['cv_std']:.4f}"
            }

            # Add AUC score if available
            if perf.get('auc_score') is not None:
                model_metrics['auc_score'] = f"{perf['auc_score']:.4f}"
            else:
                model_metrics['auc_score'] = "N/A"

            report['detailed_performance'][name] = model_metrics

        # Generate recommendations
        best_accuracy = max(perf['accuracy'] for perf in self.model_performance.values())
        if best_accuracy > 0.9:
            report['recommendations'].append("Excellent model performance achieved")
        elif best_accuracy > 0.8:
            report['recommendations'].append("Good model performance, consider feature engineering")
        else:
            report['recommendations'].append("Model performance needs improvement, consider more data")

        return report

if __name__ == "__main__":
    # Test the advanced model trainer
    from advanced_data_loader import AdvancedMedicalDataLoader

    # Load data
    loader = AdvancedMedicalDataLoader()
    data = loader.get_combined_dataset()

    # Train models
    predictor = AdvancedDiseasePredictor()
    summary = predictor.train_models(data)

    # Print results
    print("\n=== Advanced Model Training Results ===")
    print(f"Models trained: {summary['models_trained']}")
    print(f"Best model: {summary['best_model'][0]} (CV: {summary['best_model'][1]['cv_mean']:.4f})")
    print(f"Ensemble available: {summary['ensemble_available']}")

    # Generate detailed report
    report = predictor.generate_model_report()
    print("\n=== Model Performance Report ===")
    for model_name, metrics in report['detailed_performance'].items():
        print(f"{model_name}:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value}")

    # Test prediction
    test_symptoms = "fever, cough, headache, fatigue"
    predictions = predictor.predict_disease(test_symptoms)

    print(f"\nTest prediction for: {test_symptoms}")
    for i, pred in enumerate(predictions[:5]):
        print(f"{i+1}. {pred['disease']}: {pred['confidence_percentage']:.2f}% ({pred['confidence_level']})")

    # Save models
    predictor.save_models()
