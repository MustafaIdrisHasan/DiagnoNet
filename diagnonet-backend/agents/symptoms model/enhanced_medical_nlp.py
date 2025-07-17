#!/usr/bin/env python3
"""
Enhanced Medical NLP Processor
Professional medical-grade NLP without ScispaCy dependency
Optimized for Python 3.13 compatibility
"""

import re
import spacy
import sqlite3
import logging
import numpy as np
from typing import Dict, List, Tuple, Optional, Set
from fuzzywuzzy import fuzz, process
from datetime import datetime
import json
from collections import defaultdict
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedMedicalNLP:
    def __init__(self):
        self.nlp = None
        self.medical_entities = {}
        self.symptom_patterns = {}
        self.medical_abbreviations = {}
        self.severity_indicators = {}
        self.temporal_patterns = {}
        self.db_path = 'enhanced_medical_conversations.db'
        self.initialize_nlp()
        self.load_medical_knowledge()
        self.setup_database()
    
    def initialize_nlp(self):
        """Initialize spaCy with the best available model"""
        try:
            # Try to load the medium model first
            self.nlp = spacy.load("en_core_web_md")
            logger.info("✓ Enhanced spaCy model (en_core_web_md) loaded")
        except OSError:
            try:
                # Fallback to small model
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("✓ Standard spaCy model (en_core_web_sm) loaded")
            except OSError:
                logger.error("❌ No spaCy model found. Install with: python -m spacy download en_core_web_sm")
                raise
    
    def load_medical_knowledge(self):
        """Load comprehensive medical knowledge base with medical ontologies"""

        # Enhanced medical entities with UMLS/SNOMED CT inspired structure
        self.medical_entities = {
            'symptoms': {
                # Cardiovascular
                'chest_pain': ['chest pain', 'chest discomfort', 'angina', 'crushing pain', 'substernal pain'],
                'shortness_of_breath': ['shortness of breath', 'dyspnea', 'breathlessness', 'difficulty breathing', 'sob'],
                'palpitations': ['palpitations', 'heart racing', 'irregular heartbeat', 'heart pounding'],
                'syncope': ['syncope', 'fainting', 'loss of consciousness', 'blackout', 'passing out'],
                'edema': ['swelling', 'edema', 'fluid retention', 'puffy', 'bloated'],
                
                # Respiratory
                'cough': ['cough', 'coughing', 'productive cough', 'dry cough', 'hacking cough'],
                'sputum': ['sputum', 'phlegm', 'mucus', 'expectoration'],
                'wheezing': ['wheezing', 'whistling breath', 'stridor'],
                'hemoptysis': ['hemoptysis', 'coughing blood', 'blood in sputum'],
                
                # Neurological
                'headache': ['headache', 'head pain', 'cephalgia', 'migraine', 'tension headache'],
                'dizziness': ['dizziness', 'vertigo', 'lightheadedness', 'unsteady'],
                'confusion': ['confusion', 'disorientation', 'altered mental status', 'delirium'],
                'seizure': ['seizure', 'convulsion', 'fit', 'epileptic episode'],
                'weakness': ['weakness', 'paralysis', 'paresis', 'muscle weakness'],
                'numbness': ['numbness', 'tingling', 'paresthesia', 'pins and needles'],
                
                # Gastrointestinal
                'nausea': ['nausea', 'feeling sick', 'queasy', 'sick to stomach'],
                'vomiting': ['vomiting', 'throwing up', 'emesis', 'retching'],
                'abdominal_pain': ['abdominal pain', 'stomach pain', 'belly pain', 'gut pain'],
                'diarrhea': ['diarrhea', 'loose stools', 'watery stools'],
                'constipation': ['constipation', 'difficulty passing stool', 'hard stools'],
                
                # Constitutional
                'fever': ['fever', 'high temperature', 'pyrexia', 'febrile', 'hot'],
                'chills': ['chills', 'rigors', 'shivering', 'cold'],
                'fatigue': ['fatigue', 'tiredness', 'exhaustion', 'weakness', 'lethargy'],
                'weight_loss': ['weight loss', 'losing weight', 'unintentional weight loss'],
                'night_sweats': ['night sweats', 'sweating at night', 'diaphoresis'],
                
                # Musculoskeletal
                'joint_pain': ['joint pain', 'arthralgia', 'aching joints'],
                'muscle_pain': ['muscle pain', 'myalgia', 'muscle aches'],
                'back_pain': ['back pain', 'lower back pain', 'spine pain'],
                
                # Dermatological
                'rash': ['rash', 'skin eruption', 'skin lesions', 'dermatitis'],
                'itching': ['itching', 'pruritus', 'scratching'],
                
                # Genitourinary
                'dysuria': ['dysuria', 'painful urination', 'burning urination'],
                'frequency': ['urinary frequency', 'frequent urination'],
                'urgency': ['urinary urgency', 'urgent need to urinate']
            }
        }
        
        # Severity indicators
        self.severity_indicators = {
            'severe': ['severe', 'intense', 'excruciating', 'unbearable', 'crushing', 'sharp'],
            'moderate': ['moderate', 'significant', 'noticeable', 'considerable'],
            'mild': ['mild', 'slight', 'minor', 'minimal', 'light'],
            'acute': ['acute', 'sudden', 'rapid onset', 'immediate'],
            'chronic': ['chronic', 'persistent', 'long-standing', 'ongoing'],
            'progressive': ['progressive', 'worsening', 'getting worse', 'deteriorating']
        }
        
        # Temporal patterns
        self.temporal_patterns = {
            'duration': [
                r'for (\d+) (days?|weeks?|months?|years?)',
                r'(\d+) (days?|weeks?|months?|years?) ago',
                r'since (\d+) (days?|weeks?|months?|years?)',
                r'over the (past|last) (\d+) (days?|weeks?|months?)'
            ],
            'frequency': [
                r'(\d+) times? (per|a) (day|week|month)',
                r'every (\d+) (hours?|days?|weeks?)',
                r'(daily|weekly|monthly|hourly)'
            ]
        }
        
        # Medical abbreviations
        self.medical_abbreviations = {
            'sob': 'shortness of breath',
            'cp': 'chest pain',
            'ha': 'headache',
            'n/v': 'nausea and vomiting',
            'uri': 'upper respiratory infection',
            'uti': 'urinary tract infection',
            'mi': 'myocardial infarction',
            'pe': 'pulmonary embolism',
            'dvt': 'deep vein thrombosis'
        }

        # Medical validation rules and semantic relationships
        self.symptom_semantic_groups = {
            'cardiovascular': ['chest_pain', 'shortness_of_breath', 'palpitations', 'syncope', 'edema'],
            'respiratory': ['cough', 'sputum', 'wheezing', 'hemoptysis', 'shortness_of_breath'],
            'neurological': ['headache', 'dizziness', 'confusion', 'seizure', 'weakness', 'numbness'],
            'gastrointestinal': ['nausea', 'vomiting', 'abdominal_pain', 'diarrhea', 'constipation'],
            'constitutional': ['fever', 'chills', 'fatigue', 'weight_loss', 'night_sweats'],
            'musculoskeletal': ['joint_pain', 'muscle_pain', 'back_pain'],
            'dermatological': ['rash', 'itching'],
            'genitourinary': ['dysuria', 'frequency', 'urgency']
        }

        # Symptom exclusion rules (symptoms that shouldn't co-occur without strong evidence)
        self.symptom_exclusions = {
            'chest_pain': ['joint_pain', 'rash', 'dysuria'],  # Chest pain rarely co-occurs with these
            'headache': ['abdominal_pain', 'joint_pain'],     # Headache rarely with these unless systemic
            'fever': [],  # Fever can occur with many symptoms
            'cough': ['joint_pain', 'rash']  # Cough rarely with these unless systemic
        }

        # Symptom co-occurrence weights (higher = more likely to occur together)
        self.symptom_cooccurrence = {
            ('chest_pain', 'shortness_of_breath'): 0.9,
            ('chest_pain', 'nausea'): 0.7,
            ('fever', 'cough'): 0.8,
            ('fever', 'headache'): 0.6,
            ('nausea', 'vomiting'): 0.9,
            ('headache', 'dizziness'): 0.7,
            ('cough', 'sputum'): 0.8,
            ('joint_pain', 'muscle_pain'): 0.8
        }
    
    def setup_database(self):
        """Setup enhanced conversation database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS enhanced_conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    timestamp TEXT,
                    user_input TEXT,
                    extracted_symptoms TEXT,
                    confidence_scores TEXT,
                    extraction_method TEXT,
                    severity_assessment TEXT,
                    temporal_context TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✓ Enhanced conversation database initialized")
            
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
    
    def extract_medical_abbreviations(self, text: str) -> str:
        """Expand medical abbreviations"""
        expanded_text = text.lower()
        for abbrev, full_form in self.medical_abbreviations.items():
            expanded_text = re.sub(r'\b' + abbrev + r'\b', full_form, expanded_text)
        return expanded_text
    
    def extract_severity_context(self, text: str) -> Dict[str, float]:
        """Extract severity indicators from text"""
        severity_scores = {}
        text_lower = text.lower()
        
        for severity_level, indicators in self.severity_indicators.items():
            score = 0
            for indicator in indicators:
                if indicator in text_lower:
                    score += 1
            
            if score > 0:
                severity_scores[severity_level] = min(score / len(indicators), 1.0)
        
        return severity_scores
    
    def extract_temporal_context(self, text: str) -> Dict[str, str]:
        """Extract temporal information from text"""
        temporal_info = {}
        
        for pattern_type, patterns in self.temporal_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text.lower())
                for match in matches:
                    temporal_info[pattern_type] = match.group()
                    break
        
        return temporal_info
    
    def fuzzy_match_symptoms(self, text: str, threshold: int = 85) -> Dict[str, float]:
        """Enhanced fuzzy matching with semantic validation"""
        extracted_symptoms = {}
        text_lower = text.lower()

        # Create a comprehensive symptom list
        all_symptoms = []
        symptom_mapping = {}

        for symptom_key, variations in self.medical_entities['symptoms'].items():
            for variation in variations:
                all_symptoms.append(variation)
                symptom_mapping[variation] = symptom_key

        # Use fuzzy matching to find symptoms
        words = text_lower.split()

        # Check individual words and phrases
        for i in range(len(words)):
            for j in range(i + 1, min(i + 5, len(words) + 1)):  # Check up to 4-word phrases
                phrase = ' '.join(words[i:j])

                # Find best matches
                matches = process.extract(phrase, all_symptoms, limit=3, scorer=fuzz.token_sort_ratio)

                for match, score in matches:
                    if score >= threshold:
                        symptom_key = symptom_mapping[match]

                        # Enhanced confidence calculation with semantic validation
                        base_confidence = score / 100.0
                        semantic_confidence = self._validate_symptom_semantics(symptom_key, text_lower, phrase)
                        final_confidence = base_confidence * semantic_confidence

                        # Only include if semantic validation passes
                        if semantic_confidence > 0.5 and final_confidence > 0.6:
                            if symptom_key not in extracted_symptoms or final_confidence > extracted_symptoms[symptom_key]:
                                extracted_symptoms[symptom_key] = final_confidence

        # Apply post-processing validation
        validated_symptoms = self._post_process_symptom_validation(extracted_symptoms, text_lower)

        return validated_symptoms

    def _validate_symptom_semantics(self, symptom: str, full_text: str, matched_phrase: str) -> float:
        """Validate symptom extraction using semantic analysis"""

        # Check if the symptom makes semantic sense in context
        context_words = full_text.split()
        matched_words = matched_phrase.split()

        # Find context around the matched phrase
        context_window = 5
        context_start = max(0, full_text.find(matched_phrase) - context_window * 10)
        context_end = min(len(full_text), full_text.find(matched_phrase) + len(matched_phrase) + context_window * 10)
        context = full_text[context_start:context_end]

        # Semantic validation rules
        semantic_score = 1.0

        # Rule 1: Check for negation
        negation_words = ['no', 'not', 'never', 'without', 'absent', 'denies', 'negative']
        for neg_word in negation_words:
            if neg_word in context and abs(context.find(neg_word) - context.find(matched_phrase)) < 30:
                semantic_score *= 0.1  # Strong penalty for negation

        # Rule 2: Check for uncertainty markers
        uncertainty_words = ['maybe', 'possibly', 'might', 'could', 'uncertain']
        for unc_word in uncertainty_words:
            if unc_word in context:
                semantic_score *= 0.7  # Moderate penalty for uncertainty

        # Rule 3: Check for temporal relevance
        past_indicators = ['had', 'was', 'were', 'used to', 'previously', 'before', 'ago']
        for past_word in past_indicators:
            if past_word in context and abs(context.find(past_word) - context.find(matched_phrase)) < 20:
                semantic_score *= 0.8  # Slight penalty for past symptoms

        # Rule 4: Boost for current/active indicators
        current_indicators = ['having', 'experiencing', 'feeling', 'currently', 'now', 'today']
        for curr_word in current_indicators:
            if curr_word in context:
                semantic_score *= 1.2  # Boost for current symptoms

        return min(semantic_score, 1.0)

    def _post_process_symptom_validation(self, symptoms: Dict[str, float], text: str) -> Dict[str, float]:
        """Post-process extracted symptoms for clinical validity"""
        validated_symptoms = {}

        for symptom, confidence in symptoms.items():
            # Check exclusion rules
            should_exclude = False
            for other_symptom in symptoms:
                if other_symptom != symptom:
                    if other_symptom in self.symptom_exclusions.get(symptom, []):
                        # Check if both symptoms have high confidence
                        if confidence > 0.8 and symptoms[other_symptom] > 0.8:
                            # Keep the one with higher confidence, reduce the other
                            if confidence < symptoms[other_symptom]:
                                confidence *= 0.5

            # Apply co-occurrence boosting
            for other_symptom in symptoms:
                if other_symptom != symptom:
                    cooccur_key = tuple(sorted([symptom, other_symptom]))
                    if cooccur_key in self.symptom_cooccurrence:
                        boost_factor = self.symptom_cooccurrence[cooccur_key]
                        confidence = min(confidence * (1 + boost_factor * 0.2), 1.0)

            # Final validation: ensure symptom is actually mentioned in text
            symptom_variations = self.medical_entities['symptoms'].get(symptom, [])
            text_contains_symptom = any(var.lower() in text.lower() for var in symptom_variations)

            if text_contains_symptom and confidence > 0.6:
                validated_symptoms[symptom] = confidence

        return validated_symptoms
    
    def extract_with_spacy_ner(self, text: str) -> Dict[str, float]:
        """Extract symptoms using spaCy NER"""
        extracted_symptoms = {}
        
        if not self.nlp:
            return extracted_symptoms
        
        doc = self.nlp(text)
        
        # Look for medical entities
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG']:  # Skip non-medical entities
                continue
            
            entity_text = ent.text.lower()
            
            # Check if entity matches known symptoms
            for symptom_key, variations in self.medical_entities['symptoms'].items():
                for variation in variations:
                    if fuzz.ratio(entity_text, variation) > 70:
                        confidence = fuzz.ratio(entity_text, variation) / 100.0
                        if symptom_key not in extracted_symptoms or confidence > extracted_symptoms[symptom_key]:
                            extracted_symptoms[symptom_key] = confidence
        
        return extracted_symptoms
    
    def process_natural_language(self, text: str, session_id: str = None) -> Dict:
        """Enhanced natural language processing with professional medical validation"""

        # Expand abbreviations
        expanded_text = self.extract_medical_abbreviations(text)

        # Extract symptoms using enhanced methods
        fuzzy_symptoms = self.fuzzy_match_symptoms(expanded_text, threshold=85)
        spacy_symptoms = self.extract_with_spacy_ner(expanded_text)

        # Intelligent symptom combination with conflict resolution
        all_symptoms = self._combine_symptom_extractions(fuzzy_symptoms, spacy_symptoms, expanded_text)

        # Extract additional context
        severity_context = self.extract_severity_context(text)
        temporal_context = self.extract_temporal_context(text)

        # Enhanced confidence calculation
        overall_confidence = self._calculate_overall_confidence(all_symptoms, text)

        # Determine follow-up needs using intelligent analysis
        follow_up_analysis = self._analyze_follow_up_needs(all_symptoms, severity_context, overall_confidence)

        # Prepare enhanced result
        result = {
            'normalized_symptoms': all_symptoms,
            'confidence_scores': all_symptoms,
            'severity_context': severity_context,
            'temporal_context': temporal_context,
            'overall_confidence': overall_confidence,
            'extraction_method': 'enhanced_medical_nlp_v2',
            'follow_up_needed': follow_up_analysis['needed'],
            'follow_up_questions': follow_up_analysis['questions'],
            'symptom_completeness': follow_up_analysis['completeness'],
            'clinical_coherence': self._assess_clinical_coherence(all_symptoms)
        }

        # Store in database
        if session_id:
            self.store_conversation(session_id, text, result)

        return result

    def _combine_symptom_extractions(self, fuzzy_symptoms: Dict[str, float],
                                   spacy_symptoms: Dict[str, float], text: str) -> Dict[str, float]:
        """Intelligently combine symptom extractions with conflict resolution"""
        combined_symptoms = {}

        # Start with fuzzy symptoms (more reliable for medical terms)
        for symptom, confidence in fuzzy_symptoms.items():
            combined_symptoms[symptom] = confidence

        # Add spacy symptoms with validation
        for symptom, confidence in spacy_symptoms.items():
            if symptom not in combined_symptoms:
                # Validate spacy extraction against text
                if self._validate_spacy_extraction(symptom, text):
                    combined_symptoms[symptom] = confidence * 0.9  # Slight penalty for spacy-only
            else:
                # Combine confidences using weighted average
                existing_conf = combined_symptoms[symptom]
                combined_conf = (existing_conf * 0.7) + (confidence * 0.3)
                combined_symptoms[symptom] = min(combined_conf, 1.0)

        return combined_symptoms

    def _validate_spacy_extraction(self, symptom: str, text: str) -> bool:
        """Validate spacy-extracted symptoms against original text"""
        symptom_variations = self.medical_entities['symptoms'].get(symptom, [])
        return any(var.lower() in text.lower() for var in symptom_variations)

    def _calculate_overall_confidence(self, symptoms: Dict[str, float], text: str) -> float:
        """Calculate overall confidence with clinical weighting"""
        if not symptoms:
            return 0.0

        # Weight symptoms by clinical importance
        clinical_weights = {
            'chest_pain': 1.2, 'shortness_of_breath': 1.2, 'fever': 1.1,
            'headache': 1.0, 'nausea': 0.9, 'fatigue': 0.8
        }

        weighted_sum = 0.0
        total_weight = 0.0

        for symptom, confidence in symptoms.items():
            weight = clinical_weights.get(symptom, 1.0)
            weighted_sum += confidence * weight
            total_weight += weight

        base_confidence = weighted_sum / total_weight if total_weight > 0 else 0.0

        # Adjust based on text length and complexity
        text_length_factor = min(len(text.split()) / 20.0, 1.0)  # Longer text = more confidence

        return min(base_confidence * (0.7 + 0.3 * text_length_factor), 1.0)

    def _analyze_follow_up_needs(self, symptoms: Dict[str, float],
                               severity_context: Dict[str, float],
                               overall_confidence: float) -> Dict:
        """Analyze if follow-up questions are needed"""

        follow_up_needed = False
        questions = []
        completeness_score = 1.0

        # Check if we have too few symptoms
        if len(symptoms) < 2:
            follow_up_needed = True
            completeness_score *= 0.5
            questions.append("Can you describe any additional symptoms you're experiencing?")

        # Check if confidence is low
        if overall_confidence < 0.7:
            follow_up_needed = True
            completeness_score *= 0.7
            questions.append("Could you provide more details about your main symptoms?")

        # Check for missing severity information
        if not severity_context and symptoms:
            follow_up_needed = True
            completeness_score *= 0.8
            questions.append("How would you rate the severity of your symptoms?")

        # Generate specific follow-up questions
        specific_questions = self.generate_follow_up_questions(symptoms, severity_context)
        questions.extend(specific_questions[:2])  # Limit to 2 additional questions

        return {
            'needed': follow_up_needed,
            'questions': questions[:3],  # Maximum 3 questions
            'completeness': completeness_score
        }

    def _assess_clinical_coherence(self, symptoms: Dict[str, float]) -> float:
        """Assess how clinically coherent the symptom combination is"""
        if len(symptoms) < 2:
            return 1.0

        coherence_score = 1.0
        symptom_list = list(symptoms.keys())

        # Check for symptoms in same system
        system_groups = defaultdict(list)
        for symptom in symptom_list:
            for system, system_symptoms in self.symptom_semantic_groups.items():
                if symptom in system_symptoms:
                    system_groups[system].append(symptom)

        # Boost coherence if symptoms are in related systems
        if len(system_groups) <= 2:  # Symptoms in 1-2 systems = more coherent
            coherence_score *= 1.2
        elif len(system_groups) > 3:  # Symptoms scattered across many systems
            coherence_score *= 0.8

        # Check co-occurrence patterns
        for i, symptom1 in enumerate(symptom_list):
            for symptom2 in symptom_list[i+1:]:
                cooccur_key = tuple(sorted([symptom1, symptom2]))
                if cooccur_key in self.symptom_cooccurrence:
                    coherence_score *= (1 + self.symptom_cooccurrence[cooccur_key] * 0.1)

        return min(coherence_score, 1.0)
    
    def generate_follow_up_questions(self, symptoms: Dict[str, float], severity: Dict[str, float]) -> List[str]:
        """Generate intelligent follow-up questions"""
        questions = []
        
        if not symptoms:
            questions.append("Can you describe your main symptoms in more detail?")
            questions.append("When did these symptoms start?")
            return questions
        
        if not severity:
            questions.append("How would you rate the severity of your symptoms?")
        
        if 'chest_pain' in symptoms:
            questions.append("Does the chest pain radiate to your arm, jaw, or back?")
            questions.append("Is the pain worse with exertion?")
        
        if 'headache' in symptoms:
            questions.append("Is this headache different from your usual headaches?")
            questions.append("Do you have any visual changes or neck stiffness?")
        
        if 'fever' in symptoms:
            questions.append("Have you measured your temperature? What was it?")
        
        return questions[:3]  # Limit to 3 questions
    
    def store_conversation(self, session_id: str, user_input: str, result: Dict):
        """Store conversation in enhanced database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO enhanced_conversations 
                (session_id, timestamp, user_input, extracted_symptoms, confidence_scores, 
                 extraction_method, severity_assessment, temporal_context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                datetime.now().isoformat(),
                user_input,
                json.dumps(result['normalized_symptoms']),
                json.dumps(result['confidence_scores']),
                result['extraction_method'],
                json.dumps(result['severity_context']),
                json.dumps(result['temporal_context'])
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store conversation: {e}")

# Backward compatibility alias
MedicalNLPProcessor = EnhancedMedicalNLP
