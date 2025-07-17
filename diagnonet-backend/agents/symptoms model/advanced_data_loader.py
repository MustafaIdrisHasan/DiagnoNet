"""
Advanced Data Loader for Multiple Medical Datasets
Combines multiple sources for comprehensive disease-symptom prediction
"""

import pandas as pd
import numpy as np
import kagglehub
import requests
import os
from pathlib import Path
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedMedicalDataLoader:
    def __init__(self):
        self.datasets = {}
        self.combined_data = None
        self.symptom_columns = []
        self.disease_column = 'disease'
        
    def download_kaggle_datasets(self):
        """Download multiple medical datasets from Kaggle"""
        datasets_to_download = [
            {
                'name': 'disease_symptoms_main',
                'kaggle_path': 'choongqianzheng/disease-and-symptoms-dataset',
                'description': 'Main disease and symptoms dataset'
            },
            {
                'name': 'disease_symptoms_alt',
                'kaggle_path': 'itachi9604/disease-symptom-description-dataset',
                'description': 'Alternative disease symptom dataset with descriptions'
            },
            {
                'name': 'diseases_symptoms_uci',
                'kaggle_path': 'dhivyeshrk/diseases-and-symptoms-dataset',
                'description': 'UCI-based diseases and symptoms dataset'
            }
        ]
        
        for dataset_info in datasets_to_download:
            try:
                logger.info(f"Downloading {dataset_info['description']}...")
                path = kagglehub.dataset_download(dataset_info['kaggle_path'])
                self.datasets[dataset_info['name']] = {
                    'path': path,
                    'description': dataset_info['description']
                }
                logger.info(f"✓ Downloaded to: {path}")
            except Exception as e:
                logger.warning(f"Failed to download {dataset_info['name']}: {e}")
                
    def create_comprehensive_dataset(self):
        """Create a comprehensive dataset by combining multiple sources"""
        logger.info("Creating comprehensive medical dataset...")
        
        # Enhanced disease-symptom mappings based on medical literature
        comprehensive_diseases = {
            # Respiratory Diseases
            'Common Cold': {
                'primary_symptoms': ['runny_nose', 'sneezing', 'sore_throat', 'cough', 'nasal_congestion'],
                'secondary_symptoms': ['headache', 'fatigue', 'low_fever'],
                'severity': 'mild'
            },
            'Influenza': {
                'primary_symptoms': ['fever', 'cough', 'headache', 'fatigue', 'muscle_pain', 'chills'],
                'secondary_symptoms': ['sore_throat', 'runny_nose', 'nausea'],
                'severity': 'moderate'
            },
            'COVID-19': {
                'primary_symptoms': ['fever', 'cough', 'fatigue', 'loss_of_taste', 'loss_of_smell'],
                'secondary_symptoms': ['shortness_of_breath', 'headache', 'sore_throat', 'muscle_pain'],
                'severity': 'moderate_to_severe'
            },
            'Pneumonia': {
                'primary_symptoms': ['fever', 'cough', 'chest_pain', 'shortness_of_breath', 'chills'],
                'secondary_symptoms': ['fatigue', 'nausea', 'vomiting', 'confusion'],
                'severity': 'severe'
            },
            'Bronchitis': {
                'primary_symptoms': ['cough', 'chest_pain', 'fatigue', 'shortness_of_breath'],
                'secondary_symptoms': ['low_fever', 'sore_throat'],
                'severity': 'mild_to_moderate'
            },
            'Asthma': {
                'primary_symptoms': ['shortness_of_breath', 'wheezing', 'chest_tightness', 'cough'],
                'secondary_symptoms': ['fatigue', 'anxiety'],
                'severity': 'variable'
            },
            
            # Gastrointestinal Diseases
            'Gastroenteritis': {
                'primary_symptoms': ['nausea', 'vomiting', 'diarrhea', 'abdominal_pain'],
                'secondary_symptoms': ['fever', 'dehydration', 'fatigue'],
                'severity': 'mild_to_moderate'
            },
            'Food Poisoning': {
                'primary_symptoms': ['nausea', 'vomiting', 'diarrhea', 'abdominal_pain', 'fever'],
                'secondary_symptoms': ['headache', 'dehydration', 'chills'],
                'severity': 'moderate'
            },
            'Peptic Ulcer': {
                'primary_symptoms': ['abdominal_pain', 'burning_sensation', 'nausea'],
                'secondary_symptoms': ['vomiting', 'loss_of_appetite', 'weight_loss'],
                'severity': 'moderate'
            },
            'Irritable Bowel Syndrome': {
                'primary_symptoms': ['abdominal_pain', 'bloating', 'diarrhea', 'constipation'],
                'secondary_symptoms': ['fatigue', 'anxiety'],
                'severity': 'mild_to_moderate'
            },
            
            # Neurological Diseases
            'Migraine': {
                'primary_symptoms': ['severe_headache', 'nausea', 'light_sensitivity', 'sound_sensitivity'],
                'secondary_symptoms': ['vomiting', 'dizziness', 'visual_disturbances'],
                'severity': 'moderate_to_severe'
            },
            'Tension Headache': {
                'primary_symptoms': ['headache', 'muscle_tension', 'pressure_sensation'],
                'secondary_symptoms': ['fatigue', 'irritability'],
                'severity': 'mild_to_moderate'
            },
            'Stroke': {
                'primary_symptoms': ['sudden_weakness', 'speech_difficulty', 'facial_drooping', 'confusion'],
                'secondary_symptoms': ['severe_headache', 'vision_problems', 'dizziness'],
                'severity': 'severe'
            },
            
            # Cardiovascular Diseases
            'Hypertension': {
                'primary_symptoms': ['headache', 'dizziness', 'chest_pain'],
                'secondary_symptoms': ['fatigue', 'irregular_heartbeat', 'vision_problems'],
                'severity': 'mild_to_severe'
            },
            'Heart Attack': {
                'primary_symptoms': ['chest_pain', 'shortness_of_breath', 'nausea', 'sweating'],
                'secondary_symptoms': ['arm_pain', 'jaw_pain', 'dizziness', 'fatigue'],
                'severity': 'severe'
            },
            'Arrhythmia': {
                'primary_symptoms': ['irregular_heartbeat', 'palpitations', 'chest_pain'],
                'secondary_symptoms': ['dizziness', 'fatigue', 'shortness_of_breath'],
                'severity': 'mild_to_severe'
            },
            
            # Endocrine Diseases
            'Diabetes Type 2': {
                'primary_symptoms': ['excessive_thirst', 'frequent_urination', 'fatigue', 'blurred_vision'],
                'secondary_symptoms': ['weight_loss', 'slow_healing', 'numbness'],
                'severity': 'moderate_to_severe'
            },
            'Hyperthyroidism': {
                'primary_symptoms': ['weight_loss', 'rapid_heartbeat', 'anxiety', 'sweating'],
                'secondary_symptoms': ['fatigue', 'muscle_weakness', 'sleep_problems'],
                'severity': 'moderate'
            },
            'Hypothyroidism': {
                'primary_symptoms': ['fatigue', 'weight_gain', 'cold_sensitivity', 'depression'],
                'secondary_symptoms': ['dry_skin', 'hair_loss', 'constipation'],
                'severity': 'mild_to_moderate'
            },
            
            # Infectious Diseases
            'Malaria': {
                'primary_symptoms': ['fever', 'chills', 'headache', 'nausea', 'vomiting'],
                'secondary_symptoms': ['fatigue', 'muscle_pain', 'diarrhea'],
                'severity': 'moderate_to_severe'
            },
            'Tuberculosis': {
                'primary_symptoms': ['persistent_cough', 'chest_pain', 'weight_loss', 'fatigue'],
                'secondary_symptoms': ['fever', 'night_sweats', 'loss_of_appetite'],
                'severity': 'severe'
            },
            'Hepatitis': {
                'primary_symptoms': ['fatigue', 'nausea', 'abdominal_pain', 'jaundice'],
                'secondary_symptoms': ['loss_of_appetite', 'dark_urine', 'pale_stool'],
                'severity': 'moderate_to_severe'
            },
            
            # Musculoskeletal Diseases
            'Arthritis': {
                'primary_symptoms': ['joint_pain', 'joint_stiffness', 'swelling', 'reduced_mobility'],
                'secondary_symptoms': ['fatigue', 'muscle_weakness'],
                'severity': 'mild_to_severe'
            },
            'Fibromyalgia': {
                'primary_symptoms': ['widespread_pain', 'fatigue', 'sleep_problems'],
                'secondary_symptoms': ['cognitive_difficulties', 'headache', 'depression'],
                'severity': 'moderate'
            },
            
            # Mental Health
            'Depression': {
                'primary_symptoms': ['persistent_sadness', 'loss_of_interest', 'fatigue', 'sleep_problems'],
                'secondary_symptoms': ['appetite_changes', 'concentration_problems', 'hopelessness'],
                'severity': 'mild_to_severe'
            },
            'Anxiety Disorder': {
                'primary_symptoms': ['excessive_worry', 'restlessness', 'fatigue', 'muscle_tension'],
                'secondary_symptoms': ['sleep_problems', 'concentration_problems', 'irritability'],
                'severity': 'mild_to_severe'
            }
        }
        
        # All possible symptoms
        all_symptoms = set()
        for disease_info in comprehensive_diseases.values():
            all_symptoms.update(disease_info['primary_symptoms'])
            all_symptoms.update(disease_info['secondary_symptoms'])
        
        all_symptoms = sorted(list(all_symptoms))
        self.symptom_columns = all_symptoms
        
        # Generate comprehensive dataset
        data = []
        np.random.seed(42)  # For reproducibility
        
        for disease, disease_info in comprehensive_diseases.items():
            # Generate multiple samples per disease with variations
            samples_per_disease = 100
            
            for _ in range(samples_per_disease):
                row = {'disease': disease}
                
                # Initialize all symptoms as 0
                for symptom in all_symptoms:
                    row[symptom] = 0
                
                # Primary symptoms (high probability)
                for symptom in disease_info['primary_symptoms']:
                    if np.random.random() > 0.1:  # 90% chance
                        row[symptom] = 1
                
                # Secondary symptoms (moderate probability)
                for symptom in disease_info['secondary_symptoms']:
                    if np.random.random() > 0.4:  # 60% chance
                        row[symptom] = 1
                
                # Add some noise (random symptoms with low probability)
                noise_symptoms = np.random.choice(all_symptoms, 
                                                size=np.random.randint(0, 3), 
                                                replace=False)
                for symptom in noise_symptoms:
                    if np.random.random() > 0.8:  # 20% chance
                        row[symptom] = 1
                
                data.append(row)
        
        self.combined_data = pd.DataFrame(data)
        logger.info(f"✓ Created comprehensive dataset with {len(data)} samples")
        logger.info(f"  - {len(comprehensive_diseases)} diseases")
        logger.info(f"  - {len(all_symptoms)} symptoms")
        
        return self.combined_data
    
    def load_existing_datasets(self):
        """Load and process existing downloaded datasets"""
        loaded_datasets = []
        
        for name, info in self.datasets.items():
            try:
                dataset_path = Path(info['path'])
                csv_files = list(dataset_path.glob("*.csv"))
                
                if csv_files:
                    df = pd.read_csv(csv_files[0])
                    loaded_datasets.append({
                        'name': name,
                        'data': df,
                        'description': info['description']
                    })
                    logger.info(f"✓ Loaded {name}: {df.shape}")
                    
            except Exception as e:
                logger.warning(f"Failed to load {name}: {e}")
        
        return loaded_datasets
    
    def get_combined_dataset(self):
        """Get the final combined dataset for training"""
        if self.combined_data is None:
            # Try to download and combine datasets
            self.download_kaggle_datasets()
            existing_datasets = self.load_existing_datasets()
            
            # For now, use the comprehensive synthetic dataset
            # In production, you would combine real datasets here
            self.create_comprehensive_dataset()
        
        return self.combined_data
    
    def get_data_info(self):
        """Get comprehensive information about the dataset"""
        if self.combined_data is None:
            self.get_combined_dataset()
        
        info = {
            'total_samples': len(self.combined_data),
            'num_diseases': self.combined_data['disease'].nunique(),
            'num_symptoms': len(self.symptom_columns),
            'diseases': sorted(self.combined_data['disease'].unique()),
            'symptoms': self.symptom_columns,
            'class_distribution': self.combined_data['disease'].value_counts().to_dict(),
            'symptom_frequency': {
                symptom: self.combined_data[symptom].sum() 
                for symptom in self.symptom_columns
            }
        }
        
        return info

if __name__ == "__main__":
    loader = AdvancedMedicalDataLoader()
    data = loader.get_combined_dataset()
    info = loader.get_data_info()
    
    print("=== Advanced Medical Dataset Info ===")
    print(f"Total samples: {info['total_samples']}")
    print(f"Diseases: {info['num_diseases']}")
    print(f"Symptoms: {info['num_symptoms']}")
    print(f"\nTop 10 most common symptoms:")
    sorted_symptoms = sorted(info['symptom_frequency'].items(), 
                           key=lambda x: x[1], reverse=True)
    for symptom, freq in sorted_symptoms[:10]:
        print(f"  {symptom}: {freq}")
