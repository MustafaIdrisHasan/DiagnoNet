"""
Random Forest Classifier for Disease Prediction based on Symptoms
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
import os
from data_loader import DatasetLoader

class DiseasePredictor:
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.symptom_columns = []
        self.disease_column = None
        self.is_trained = False
        
    def preprocess_data(self, data):
        """Preprocess the dataset for training"""
        print("Preprocessing data...")
        
        # Assuming the first column is the disease and rest are symptoms
        self.disease_column = data.columns[0]
        self.symptom_columns = data.columns[1:].tolist()
        
        print(f"Disease column: {self.disease_column}")
        print(f"Number of symptom columns: {len(self.symptom_columns)}")
        
        # Prepare features (symptoms) and target (disease)
        X = data[self.symptom_columns]
        y = data[self.disease_column]
        
        # Handle missing values
        X = X.fillna(0)
        
        # Convert symptoms to binary (1 if symptom present, 0 if not)
        # Assuming symptoms are marked with 1 for present, 0 for absent
        X = X.astype(int)
        
        # Encode disease labels
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)
        
        print(f"Number of unique diseases: {len(self.label_encoder.classes_)}")
        print(f"Feature matrix shape: {X.shape}")
        
        return X, y_encoded
    
    def train_model(self, data):
        """Train the Random Forest Classifier"""
        print("Training Random Forest Classifier...")
        
        # Preprocess data
        X, y = self.preprocess_data(data)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Initialize Random Forest with optimized parameters
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        # Train the model
        self.model.fit(X_train, y_train)
        
        # Evaluate the model
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Model trained successfully!")
        print(f"Test Accuracy: {accuracy:.4f}")
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X, y, cv=5)
        print(f"Cross-validation scores: {cv_scores}")
        print(f"Mean CV accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        self.is_trained = True
        return accuracy
    
    def predict_disease(self, symptoms_input):
        """Predict disease based on input symptoms"""
        if not self.is_trained:
            raise ValueError("Model not trained yet!")
        
        # Create feature vector
        feature_vector = np.zeros(len(self.symptom_columns))
        
        # Convert symptoms_input to lowercase for matching
        symptoms_lower = [symptom.lower().strip() for symptom in symptoms_input]
        
        # Mark symptoms as present (1) in the feature vector
        for i, symptom_col in enumerate(self.symptom_columns):
            symptom_name = symptom_col.lower().replace('_', ' ').strip()
            if any(symptom in symptom_name or symptom_name in symptom for symptom in symptoms_lower):
                feature_vector[i] = 1
        
        # Get prediction probabilities
        probabilities = self.model.predict_proba([feature_vector])[0]
        
        # Get top predictions with confidence scores
        top_indices = np.argsort(probabilities)[::-1][:5]  # Top 5 predictions
        
        predictions = []
        for idx in top_indices:
            disease = self.label_encoder.inverse_transform([idx])[0]
            confidence = probabilities[idx]
            if confidence > 0.01:  # Only include predictions with >1% confidence
                predictions.append({
                    'disease': disease,
                    'confidence': float(confidence),
                    'confidence_percentage': float(confidence * 100)
                })
        
        return predictions
    
    def get_feature_importance(self):
        """Get feature importance from the trained model"""
        if not self.is_trained:
            return None
        
        importance_scores = self.model.feature_importances_
        feature_importance = list(zip(self.symptom_columns, importance_scores))
        feature_importance.sort(key=lambda x: x[1], reverse=True)
        
        return feature_importance[:20]  # Top 20 most important features
    
    def save_model(self, filepath='disease_predictor_model.pkl'):
        """Save the trained model"""
        if not self.is_trained:
            raise ValueError("No trained model to save!")
        
        model_data = {
            'model': self.model,
            'label_encoder': self.label_encoder,
            'symptom_columns': self.symptom_columns,
            'disease_column': self.disease_column
        }
        
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath='disease_predictor_model.pkl'):
        """Load a pre-trained model"""
        if os.path.exists(filepath):
            model_data = joblib.load(filepath)
            self.model = model_data['model']
            self.label_encoder = model_data['label_encoder']
            self.symptom_columns = model_data['symptom_columns']
            self.disease_column = model_data['disease_column']
            self.is_trained = True
            print(f"Model loaded from {filepath}")
            return True
        return False

if __name__ == "__main__":
    # Load data and train model
    loader = DatasetLoader()
    data = loader.load_data()
    
    if data is not None:
        predictor = DiseasePredictor()
        accuracy = predictor.train_model(data)
        
        # Save the model
        predictor.save_model()
        
        # Test prediction
        test_symptoms = ["fever", "cough", "headache"]
        predictions = predictor.predict_disease(test_symptoms)
        print(f"\nTest prediction for symptoms {test_symptoms}:")
        for pred in predictions:
            print(f"  {pred['disease']}: {pred['confidence_percentage']:.2f}%")
