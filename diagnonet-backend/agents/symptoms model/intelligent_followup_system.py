#!/usr/bin/env python3
"""
Intelligent Groq-Powered Follow-up System
Generates contextual follow-up questions for incomplete symptom information
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from groq import Groq
from datetime import datetime
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntelligentFollowUpSystem:
    """Groq-powered intelligent follow-up question generation system"""
    
    def __init__(self):
        self.groq_client = None
        self.conversation_state = {}
        self.question_history = {}
        self.disease_symptom_matrix = self._load_disease_symptom_correlations()
        self.initialize_groq()
        self.setup_conversation_database()
    
    def initialize_groq(self):
        """Initialize Groq AI client"""
        try:
            api_key = os.getenv('GROQ_API_KEY')
            if api_key:
                self.groq_client = Groq(api_key=api_key)
                logger.info("✅ Groq AI initialized for intelligent follow-up")
            else:
                logger.warning("⚠️ GROQ_API_KEY not found - follow-up questions will be rule-based")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Groq: {e}")
    
    def setup_conversation_database(self):
        """Setup database for conversation state management"""
        try:
            self.conn = sqlite3.connect('conversation_state.db', check_same_thread=False)
            cursor = self.conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversation_sessions (
                    session_id TEXT PRIMARY KEY,
                    symptoms_extracted TEXT,
                    questions_asked TEXT,
                    confidence_scores TEXT,
                    last_updated TIMESTAMP,
                    completion_status TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS question_effectiveness (
                    question_type TEXT,
                    success_rate REAL,
                    avg_information_gain REAL,
                    usage_count INTEGER
                )
            ''')
            
            self.conn.commit()
            logger.info("✅ Conversation state database initialized")
        except Exception as e:
            logger.error(f"❌ Failed to setup conversation database: {e}")
    
    def _load_disease_symptom_correlations(self) -> Dict:
        """Load disease-symptom correlation matrix for intelligent questioning"""
        return {
            'cardiovascular': {
                'primary_symptoms': ['chest_pain', 'shortness_of_breath', 'palpitations'],
                'secondary_symptoms': ['nausea', 'sweating', 'dizziness', 'fatigue'],
                'critical_questions': [
                    "Is the chest pain crushing or squeezing in nature?",
                    "Does the pain radiate to your arm, jaw, or back?",
                    "Are you experiencing any sweating or nausea?",
                    "How long have you been having these symptoms?"
                ]
            },
            'respiratory': {
                'primary_symptoms': ['cough', 'shortness_of_breath', 'sputum'],
                'secondary_symptoms': ['fever', 'chest_pain', 'wheezing'],
                'critical_questions': [
                    "Are you producing any sputum when you cough?",
                    "What color is the sputum?",
                    "Do you have any fever or chills?",
                    "Is the shortness of breath worse with activity?"
                ]
            },
            'neurological': {
                'primary_symptoms': ['headache', 'dizziness', 'confusion'],
                'secondary_symptoms': ['nausea', 'vision_changes', 'weakness'],
                'critical_questions': [
                    "Is this the worst headache you've ever had?",
                    "Do you have any sensitivity to light?",
                    "Are you experiencing any weakness or numbness?",
                    "When did the headache start?"
                ]
            },
            'gastrointestinal': {
                'primary_symptoms': ['nausea', 'vomiting', 'abdominal_pain'],
                'secondary_symptoms': ['diarrhea', 'fever', 'constipation'],
                'critical_questions': [
                    "Where exactly is the abdominal pain located?",
                    "Is the pain constant or does it come and go?",
                    "Have you had any changes in bowel movements?",
                    "Any recent changes in diet or medications?"
                ]
            }
        }
    
    def analyze_symptom_completeness(self, symptoms: Dict[str, float], 
                                   session_id: str = None) -> Dict:
        """Analyze symptom completeness and determine follow-up needs"""
        
        # Identify primary symptom systems
        symptom_systems = self._identify_symptom_systems(symptoms)
        
        # Calculate completeness score
        completeness_analysis = {
            'overall_completeness': 0.0,
            'missing_critical_symptoms': [],
            'system_completeness': {},
            'follow_up_priority': 'low'
        }
        
        for system, system_data in self.disease_symptom_matrix.items():
            if system in symptom_systems:
                primary_present = sum(1 for s in system_data['primary_symptoms'] if s in symptoms)
                primary_total = len(system_data['primary_symptoms'])
                
                secondary_present = sum(1 for s in system_data['secondary_symptoms'] if s in symptoms)
                secondary_total = len(system_data['secondary_symptoms'])
                
                system_completeness = (primary_present / primary_total * 0.7 + 
                                     secondary_present / secondary_total * 0.3)
                
                completeness_analysis['system_completeness'][system] = system_completeness
                
                # Identify missing critical symptoms
                missing_primary = [s for s in system_data['primary_symptoms'] if s not in symptoms]
                completeness_analysis['missing_critical_symptoms'].extend(missing_primary)
        
        # Calculate overall completeness
        if completeness_analysis['system_completeness']:
            completeness_analysis['overall_completeness'] = sum(
                completeness_analysis['system_completeness'].values()
            ) / len(completeness_analysis['system_completeness'])
        
        # Determine follow-up priority
        if completeness_analysis['overall_completeness'] < 0.4:
            completeness_analysis['follow_up_priority'] = 'high'
        elif completeness_analysis['overall_completeness'] < 0.7:
            completeness_analysis['follow_up_priority'] = 'medium'
        
        return completeness_analysis
    
    def generate_intelligent_questions(self, symptoms: Dict[str, float], 
                                     completeness_analysis: Dict,
                                     session_id: str = None) -> List[str]:
        """Generate intelligent follow-up questions using Groq AI"""
        
        if not self.groq_client:
            return self._generate_rule_based_questions(symptoms, completeness_analysis)
        
        try:
            # Prepare context for Groq
            symptom_list = list(symptoms.keys())
            missing_symptoms = completeness_analysis.get('missing_critical_symptoms', [])
            
            # Get conversation history
            previous_questions = self._get_previous_questions(session_id) if session_id else []
            
            prompt = self._create_groq_prompt(symptom_list, missing_symptoms, previous_questions)
            
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a medical AI assistant specialized in generating precise, clinically relevant follow-up questions to gather missing symptom information. Focus on the most diagnostically important questions."},
                    {"role": "user", "content": prompt}
                ],
                model="llama3-70b-8192",
                temperature=0.3,
                max_tokens=300
            )
            
            questions_text = response.choices[0].message.content
            questions = self._parse_groq_questions(questions_text)
            
            # Store questions for tracking
            if session_id:
                self._store_questions(session_id, questions)
            
            return questions[:3]  # Limit to 3 questions
            
        except Exception as e:
            logger.warning(f"Groq question generation failed: {e}, using rule-based fallback")
            return self._generate_rule_based_questions(symptoms, completeness_analysis)
    
    def _create_groq_prompt(self, symptoms: List[str], missing_symptoms: List[str], 
                           previous_questions: List[str]) -> str:
        """Create optimized prompt for Groq question generation"""
        
        prompt = f"""
        MEDICAL FOLLOW-UP QUESTION GENERATION

        Current symptoms identified: {', '.join(symptoms)}
        Missing critical symptoms: {', '.join(missing_symptoms)}
        Previously asked questions: {', '.join(previous_questions)}

        Generate 2-3 precise, clinically relevant follow-up questions to:
        1. Clarify missing critical symptoms for differential diagnosis
        2. Gather severity and temporal information
        3. Identify red flags or urgent symptoms

        Requirements:
        - Questions must be specific and actionable
        - Avoid repeating previous questions
        - Focus on most diagnostically important information
        - Use clear, patient-friendly language
        - Prioritize questions that could change urgency level

        Format: Return only the questions, one per line, numbered.
        """
        
        return prompt
    
    def _parse_groq_questions(self, questions_text: str) -> List[str]:
        """Parse questions from Groq response"""
        questions = []
        lines = questions_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and ('?' in line or line.endswith('.')):
                # Remove numbering and clean up
                cleaned = line.split('.', 1)[-1].strip() if '.' in line else line
                if cleaned and len(cleaned) > 10:  # Minimum question length
                    questions.append(cleaned)
        
        return questions
    
    def _generate_rule_based_questions(self, symptoms: Dict[str, float], 
                                     completeness_analysis: Dict) -> List[str]:
        """Generate rule-based follow-up questions as fallback"""
        questions = []
        
        # System-specific questions
        for system, completeness in completeness_analysis.get('system_completeness', {}).items():
            if completeness < 0.7:
                system_questions = self.disease_symptom_matrix[system]['critical_questions']
                questions.extend(system_questions[:2])
        
        # General questions if no specific system identified
        if not questions:
            if len(symptoms) < 2:
                questions.append("Can you describe any other symptoms you're experiencing?")
            
            questions.append("How long have you been experiencing these symptoms?")
            questions.append("How would you rate the severity of your symptoms on a scale of 1-10?")
        
        return questions[:3]
    
    def _identify_symptom_systems(self, symptoms: Dict[str, float]) -> List[str]:
        """Identify which medical systems are involved based on symptoms"""
        systems = []
        
        for system, system_data in self.disease_symptom_matrix.items():
            all_system_symptoms = system_data['primary_symptoms'] + system_data['secondary_symptoms']
            if any(symptom in all_system_symptoms for symptom in symptoms):
                systems.append(system)
        
        return systems
    
    def _get_previous_questions(self, session_id: str) -> List[str]:
        """Get previously asked questions for this session"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT questions_asked FROM conversation_sessions WHERE session_id = ?",
                (session_id,)
            )
            result = cursor.fetchone()
            if result and result[0]:
                return json.loads(result[0])
        except Exception as e:
            logger.error(f"Failed to get previous questions: {e}")
        
        return []
    
    def _store_questions(self, session_id: str, questions: List[str]):
        """Store questions for session tracking"""
        try:
            cursor = self.conn.cursor()
            questions_json = json.dumps(questions)
            
            cursor.execute('''
                INSERT OR REPLACE INTO conversation_sessions 
                (session_id, questions_asked, last_updated)
                VALUES (?, ?, ?)
            ''', (session_id, questions_json, datetime.now().isoformat()))
            
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to store questions: {e}")
    
    def update_conversation_state(self, session_id: str, new_symptoms: Dict[str, float], 
                                confidence_scores: Dict[str, float]):
        """Update conversation state with new information"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO conversation_sessions 
                (session_id, symptoms_extracted, confidence_scores, last_updated)
                VALUES (?, ?, ?, ?)
            ''', (
                session_id,
                json.dumps(new_symptoms),
                json.dumps(confidence_scores),
                datetime.now().isoformat()
            ))
            
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to update conversation state: {e}")
