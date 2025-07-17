#!/usr/bin/env python3
"""
Simplified Enhanced Medical NLP - Works without heavy dependencies
Provides professional medical symptom extraction with validation
"""

import re
import json
import logging
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimplifiedMedicalNLP:
    """Simplified medical NLP processor with enhanced validation"""
    
    def __init__(self):
        self.medical_entities = self._load_medical_knowledge()
        self.symptom_weights = self._load_symptom_weights()
        self.validation_rules = self._load_validation_rules()
        logger.info("✓ Simplified Medical NLP initialized")
    
    def _load_medical_knowledge(self) -> Dict:
        """Load medical knowledge base"""
        return {
            'symptoms': {
                'chest_pain': ['chest pain', 'chest discomfort', 'chest pressure', 'substernal pain', 'precordial pain'],
                'shortness_of_breath': ['shortness of breath', 'dyspnea', 'difficulty breathing', 'breathlessness', 'sob'],
                'headache': ['headache', 'head pain', 'cephalgia', 'migraine', 'head ache'],
                'fever': ['fever', 'high temperature', 'pyrexia', 'febrile', 'hot'],
                'nausea': ['nausea', 'feeling sick', 'queasy', 'sick to stomach'],
                'vomiting': ['vomiting', 'throwing up', 'emesis', 'puking'],
                'cough': ['cough', 'coughing', 'hacking', 'productive cough', 'dry cough'],
                'fatigue': ['fatigue', 'tired', 'exhausted', 'weakness', 'lethargy'],
                'dizziness': ['dizziness', 'dizzy', 'lightheaded', 'vertigo', 'unsteady'],
                'sweating': ['sweating', 'diaphoresis', 'perspiration', 'sweaty'],
                'joint_pain': ['joint pain', 'arthralgia', 'joint ache', 'joint stiffness'],
                'muscle_pain': ['muscle pain', 'myalgia', 'muscle ache', 'muscle soreness'],
                'abdominal_pain': ['abdominal pain', 'stomach pain', 'belly pain', 'tummy ache'],
                'back_pain': ['back pain', 'backache', 'spine pain', 'lower back pain'],
                'sore_throat': ['sore throat', 'throat pain', 'pharyngitis', 'throat irritation'],
                'runny_nose': ['runny nose', 'nasal discharge', 'rhinorrhea', 'stuffy nose'],
                'rash': ['rash', 'skin rash', 'eruption', 'skin irritation'],
                'itching': ['itching', 'pruritus', 'scratching', 'itchy'],
                'swelling': ['swelling', 'edema', 'puffiness', 'inflammation'],
                'numbness': ['numbness', 'tingling', 'pins and needles', 'loss of sensation']
            },
            'severity_terms': {
                'severe': ['severe', 'intense', 'excruciating', 'unbearable', 'worst'],
                'moderate': ['moderate', 'significant', 'noticeable', 'considerable'],
                'mild': ['mild', 'slight', 'minor', 'little', 'small'],
                'acute': ['acute', 'sudden', 'sharp', 'immediate'],
                'chronic': ['chronic', 'persistent', 'ongoing', 'long-term', 'constant']
            },
            'temporal_terms': {
                'duration': ['for', 'since', 'over', 'during', 'lasting'],
                'frequency': ['often', 'sometimes', 'rarely', 'always', 'never'],
                'timing': ['morning', 'evening', 'night', 'day', 'after', 'before']
            }
        }
    
    def _load_symptom_weights(self) -> Dict:
        """Load clinical importance weights for symptoms"""
        return {
            'chest_pain': 1.5,
            'shortness_of_breath': 1.4,
            'fever': 1.3,
            'headache': 1.2,
            'nausea': 1.1,
            'vomiting': 1.1,
            'cough': 1.2,
            'fatigue': 0.9,
            'dizziness': 1.0,
            'sweating': 1.0,
            'joint_pain': 0.8,
            'muscle_pain': 0.8,
            'abdominal_pain': 1.2,
            'back_pain': 0.7,
            'sore_throat': 0.8,
            'runny_nose': 0.6,
            'rash': 0.9,
            'itching': 0.7,
            'swelling': 1.0,
            'numbness': 1.1
        }
    
    def _load_validation_rules(self) -> Dict:
        """Load symptom validation rules"""
        return {
            'exclusions': {
                'fever': ['hypothermia', 'cold'],
                'diarrhea': ['constipation'],
                'hypertension': ['hypotension']
            },
            'co_occurrence': {
                ('chest_pain', 'shortness_of_breath'): 0.9,
                ('chest_pain', 'nausea'): 0.7,
                ('fever', 'cough'): 0.8,
                ('nausea', 'vomiting'): 0.9,
                ('headache', 'dizziness'): 0.7
            },
            'negation_words': ['no', 'not', 'never', 'without', 'absent', 'denies', 'negative', 'none']
        }
    
    def process_natural_language(self, text: str, session_id: str = None) -> Dict:
        """Process natural language input for medical symptoms"""
        
        # Clean and prepare text
        text_lower = text.lower().strip()
        
        # Extract symptoms with enhanced validation
        extracted_symptoms = self._extract_symptoms_with_validation(text_lower)
        
        # Extract context
        severity_context = self._extract_severity_context(text_lower)
        temporal_context = self._extract_temporal_context(text_lower)
        
        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(extracted_symptoms, text_lower)
        
        # Assess clinical coherence
        clinical_coherence = self._assess_clinical_coherence(extracted_symptoms)
        
        # Determine follow-up needs
        follow_up_analysis = self._analyze_follow_up_needs(extracted_symptoms, overall_confidence)
        
        return {
            'normalized_symptoms': extracted_symptoms,
            'confidence_scores': extracted_symptoms,
            'severity_context': severity_context,
            'temporal_context': temporal_context,
            'overall_confidence': overall_confidence,
            'clinical_coherence': clinical_coherence,
            'extraction_method': 'simplified_medical_nlp',
            'follow_up_needed': follow_up_analysis['needed'],
            'follow_up_questions': follow_up_analysis['questions'],
            'symptom_completeness': follow_up_analysis['completeness']
        }
    
    def _extract_symptoms_with_validation(self, text: str) -> Dict[str, float]:
        """Extract symptoms with enhanced pattern matching for diverse inputs"""
        extracted_symptoms = {}

        # Normalize text for better matching
        normalized_text = self._normalize_text(text)

        # Check for negation context
        negated_symptoms = self._detect_negated_symptoms(normalized_text)

        # Extract symptoms using enhanced pattern matching
        for symptom_key, variations in self.medical_entities['symptoms'].items():
            best_match_score = 0.0

            # Check exact matches
            for variation in variations:
                if variation in normalized_text:
                    if symptom_key not in negated_symptoms:
                        confidence = self._calculate_symptom_confidence(variation, normalized_text, symptom_key)
                        if confidence > best_match_score:
                            best_match_score = confidence

            # Check fuzzy matches for informal language
            if best_match_score == 0.0:
                fuzzy_score = self._fuzzy_match_symptom(symptom_key, variations, normalized_text)
                if fuzzy_score > 0.7:
                    best_match_score = fuzzy_score

            if best_match_score > 0.6:  # Minimum confidence threshold
                extracted_symptoms[symptom_key] = best_match_score

        # Apply clinical validation
        validated_symptoms = self._apply_clinical_validation(extracted_symptoms)

        return validated_symptoms

    def _normalize_text(self, text: str) -> str:
        """Normalize text for better symptom extraction"""
        # Convert to lowercase
        normalized = text.lower()

        # Handle common informal expressions
        informal_mappings = {
            'tummy': 'stomach',
            'belly': 'stomach',
            'hurts': 'pain',
            'aches': 'pain',
            'sore': 'pain',
            'really bad': 'severe',
            'terrible': 'severe',
            'awful': 'severe',
            'can\'t breathe': 'shortness of breath',
            'hard to breathe': 'shortness of breath',
            'throwing up': 'vomiting',
            'puking': 'vomiting'
        }

        for informal, formal in informal_mappings.items():
            normalized = normalized.replace(informal, formal)

        # Handle medical terminology
        medical_mappings = {
            'substernal': 'chest',
            'precordial': 'chest',
            'cephalgia': 'headache',
            'pyrexia': 'fever',
            'dyspnea': 'shortness of breath',
            'emesis': 'vomiting',
            'diaphoresis': 'sweating'
        }

        for medical, common in medical_mappings.items():
            normalized = normalized.replace(medical, common)

        return normalized

    def _fuzzy_match_symptom(self, symptom_key: str, variations: List[str], text: str) -> float:
        """Fuzzy matching for informal symptom descriptions"""

        # Define fuzzy patterns for common symptoms
        fuzzy_patterns = {
            'chest_pain': [
                r'chest.*hurt', r'chest.*ache', r'heart.*pain', r'chest.*tight',
                r'pressure.*chest', r'squeezing.*chest'
            ],
            'headache': [
                r'head.*hurt', r'head.*ache', r'head.*pain', r'migraine'
            ],
            'abdominal_pain': [
                r'stomach.*hurt', r'belly.*pain', r'tummy.*ache', r'gut.*pain'
            ],
            'nausea': [
                r'feel.*sick', r'queasy', r'sick.*stomach'
            ],
            'fatigue': [
                r'really.*tired', r'exhausted', r'worn.*out', r'no.*energy'
            ],
            'fever': [
                r'hot', r'burning.*up', r'high.*temperature'
            ]
        }

        import re
        patterns = fuzzy_patterns.get(symptom_key, [])

        for pattern in patterns:
            if re.search(pattern, text):
                return 0.8  # High confidence for pattern match

        return 0.0
    
    def _detect_negated_symptoms(self, text: str) -> List[str]:
        """Detect symptoms that are explicitly negated"""
        negated_symptoms = []
        negation_words = self.validation_rules['negation_words']
        
        for symptom_key, variations in self.medical_entities['symptoms'].items():
            for variation in variations:
                if variation in text:
                    # Check for negation within 5 words before the symptom
                    symptom_pos = text.find(variation)
                    context_start = max(0, symptom_pos - 50)
                    context = text[context_start:symptom_pos + len(variation)]
                    
                    if any(neg_word in context for neg_word in negation_words):
                        negated_symptoms.append(symptom_key)
                        break
        
        return negated_symptoms
    
    def _calculate_symptom_confidence(self, variation: str, text: str, symptom_key: str) -> float:
        """Calculate confidence score for symptom extraction"""
        base_confidence = 0.8  # Base confidence for exact match
        
        # Boost for clinical importance
        clinical_weight = self.symptom_weights.get(symptom_key, 1.0)
        confidence = base_confidence * min(clinical_weight, 1.2)
        
        # Boost for severity indicators
        severity_boost = 0.0
        for severity_level, terms in self.medical_entities['severity_terms'].items():
            if any(term in text for term in terms):
                severity_boost = 0.1
                break
        
        # Boost for temporal indicators
        temporal_boost = 0.0
        for temporal_type, terms in self.medical_entities['temporal_terms'].items():
            if any(term in text for term in terms):
                temporal_boost = 0.05
                break
        
        final_confidence = min(confidence + severity_boost + temporal_boost, 1.0)
        return final_confidence
    
    def _apply_clinical_validation(self, symptoms: Dict[str, float]) -> Dict[str, float]:
        """Apply clinical validation rules"""
        validated_symptoms = {}
        
        for symptom, confidence in symptoms.items():
            # Check exclusion rules
            should_exclude = False
            exclusions = self.validation_rules['exclusions'].get(symptom, [])
            
            for other_symptom in symptoms:
                if other_symptom in exclusions:
                    # If both conflicting symptoms are present, keep the one with higher confidence
                    if symptoms[other_symptom] > confidence:
                        should_exclude = True
                        break
            
            if not should_exclude:
                # Apply co-occurrence boosting
                boosted_confidence = confidence
                for other_symptom in symptoms:
                    if other_symptom != symptom:
                        cooccur_key = tuple(sorted([symptom, other_symptom]))
                        if cooccur_key in self.validation_rules['co_occurrence']:
                            boost_factor = self.validation_rules['co_occurrence'][cooccur_key]
                            boosted_confidence = min(confidence * (1 + boost_factor * 0.1), 1.0)
                
                validated_symptoms[symptom] = boosted_confidence
        
        return validated_symptoms
    
    def _extract_severity_context(self, text: str) -> Dict[str, float]:
        """Extract severity context from text"""
        severity_scores = {}
        
        for severity_level, terms in self.medical_entities['severity_terms'].items():
            score = 0.0
            for term in terms:
                if term in text:
                    score = 1.0
                    break
            severity_scores[severity_level] = score
        
        return severity_scores
    
    def _extract_temporal_context(self, text: str) -> Dict[str, str]:
        """Extract temporal context from text"""
        temporal_context = {}
        
        # Simple pattern matching for duration
        duration_patterns = [
            r'for (\d+) (day|days|hour|hours|week|weeks)',
            r'since (\w+)',
            r'over (\d+) (day|days|week|weeks)'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, text)
            if match:
                temporal_context['duration'] = match.group(0)
                break
        
        return temporal_context
    
    def _calculate_overall_confidence(self, symptoms: Dict[str, float], text: str) -> float:
        """Calculate overall confidence score"""
        if not symptoms:
            return 0.0
        
        # Weight by clinical importance
        weighted_sum = sum(conf * self.symptom_weights.get(symptom, 1.0) 
                          for symptom, conf in symptoms.items())
        total_weight = sum(self.symptom_weights.get(symptom, 1.0) for symptom in symptoms)
        
        base_confidence = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        # Adjust for text length (longer descriptions = more confidence)
        text_length_factor = min(len(text.split()) / 15.0, 1.0)
        
        return min(base_confidence * (0.8 + 0.2 * text_length_factor), 1.0)
    
    def _assess_clinical_coherence(self, symptoms: Dict[str, float]) -> float:
        """Assess clinical coherence of symptom combination"""
        if len(symptoms) < 2:
            return 1.0
        
        coherence_score = 1.0
        symptom_list = list(symptoms.keys())
        
        # Check co-occurrence patterns
        for i, symptom1 in enumerate(symptom_list):
            for symptom2 in symptom_list[i+1:]:
                cooccur_key = tuple(sorted([symptom1, symptom2]))
                if cooccur_key in self.validation_rules['co_occurrence']:
                    coherence_score *= (1 + self.validation_rules['co_occurrence'][cooccur_key] * 0.1)
        
        return min(coherence_score, 1.0)
    
    def _analyze_follow_up_needs(self, symptoms: Dict[str, float], overall_confidence: float) -> Dict:
        """Analyze if follow-up questions are needed"""
        follow_up_needed = False
        questions = []
        completeness_score = 1.0
        
        # Check if we have too few symptoms
        if len(symptoms) < 2:
            follow_up_needed = True
            completeness_score *= 0.6
            questions.append("Can you describe any additional symptoms you're experiencing?")
        
        # Check if confidence is low
        if overall_confidence < 0.7:
            follow_up_needed = True
            completeness_score *= 0.8
            questions.append("Could you provide more details about your main symptoms?")
        
        # Add severity question if no severity context
        if not any('severe' in str(symptoms) or 'mild' in str(symptoms) for _ in [1]):
            questions.append("How would you rate the severity of your symptoms?")
        
        return {
            'needed': follow_up_needed,
            'questions': questions[:3],  # Maximum 3 questions
            'completeness': completeness_score
        }
