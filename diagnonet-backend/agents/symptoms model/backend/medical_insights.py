"""
Medical Insights Generator for Professional Analysis
"""

class MedicalInsightsGenerator:
    def __init__(self):
        # Medical terminology and explanations for common symptoms
        self.symptom_explanations = {
            'fever': 'Elevated body temperature, often indicating infection or inflammatory response',
            'cough': 'Respiratory symptom that may indicate respiratory tract involvement',
            'headache': 'Cephalgia, may indicate neurological, vascular, or systemic involvement',
            'fatigue': 'Systemic symptom indicating possible metabolic or infectious etiology',
            'nausea': 'Gastrointestinal symptom suggesting digestive system involvement',
            'vomiting': 'Active gastric emptying, may indicate GI or systemic pathology',
            'diarrhea': 'Increased frequency of loose stools, suggesting GI tract involvement',
            'abdominal_pain': 'Visceral pain indicating possible intra-abdominal pathology',
            'chest_pain': 'Thoracic pain requiring differential diagnosis of cardiac, pulmonary, or musculoskeletal origin',
            'shortness_of_breath': 'Dyspnea indicating possible respiratory or cardiac compromise',
            'dizziness': 'Vertigo or lightheadedness suggesting vestibular, cardiovascular, or neurological etiology',
            'muscle_pain': 'Myalgia indicating possible inflammatory, infectious, or metabolic process',
            'joint_pain': 'Arthralgia suggesting musculoskeletal or systemic inflammatory involvement',
            'skin_rash': 'Dermatological manifestation that may indicate allergic, infectious, or autoimmune process',
            'sore_throat': 'Pharyngeal discomfort suggesting upper respiratory tract involvement'
        }
        
        # Disease categories and their clinical significance
        self.disease_categories = {
            'infectious': 'Infectious diseases require prompt identification and appropriate antimicrobial therapy',
            'autoimmune': 'Autoimmune conditions require immunosuppressive management and monitoring',
            'metabolic': 'Metabolic disorders require lifestyle modifications and targeted therapy',
            'cardiovascular': 'Cardiovascular conditions require immediate assessment and cardiac monitoring',
            'respiratory': 'Respiratory conditions may require pulmonary function assessment and respiratory support',
            'gastrointestinal': 'GI conditions require dietary modifications and possible endoscopic evaluation',
            'neurological': 'Neurological conditions require detailed neurological examination and imaging'
        }
    
    def generate_symptom_analysis(self, symptoms):
        """Generate professional analysis of symptom combination"""
        analysis = {
            'symptom_overview': self._analyze_symptom_pattern(symptoms),
            'clinical_significance': self._assess_clinical_significance(symptoms),
            'system_involvement': self._identify_system_involvement(symptoms),
            'urgency_assessment': self._assess_urgency(symptoms)
        }
        return analysis
    
    def _analyze_symptom_pattern(self, symptoms):
        """Analyze the pattern of symptoms presented"""
        symptom_count = len(symptoms)
        
        if symptom_count == 1:
            return f"Single symptom presentation: {symptoms[0]}. Consider focused differential diagnosis."
        elif symptom_count <= 3:
            return f"Oligosymptomatic presentation with {symptom_count} symptoms. Suggests localized pathology."
        else:
            return f"Polysymptomatic presentation with {symptom_count} symptoms. Consider systemic disease process."
    
    def _assess_clinical_significance(self, symptoms):
        """Assess the clinical significance of symptom combination"""
        constitutional_symptoms = ['fever', 'fatigue', 'weight_loss', 'night_sweats']
        neurological_symptoms = ['headache', 'dizziness', 'confusion', 'seizure']
        cardiac_symptoms = ['chest_pain', 'shortness_of_breath', 'palpitations']
        
        significance = []
        
        if any(symptom in constitutional_symptoms for symptom in symptoms):
            significance.append("Constitutional symptoms present - suggests systemic illness")
        
        if any(symptom in neurological_symptoms for symptom in symptoms):
            significance.append("Neurological symptoms present - requires neurological assessment")
        
        if any(symptom in cardiac_symptoms for symptom in symptoms):
            significance.append("Cardiac symptoms present - requires cardiovascular evaluation")
        
        return significance if significance else ["Localized symptom pattern - focused evaluation indicated"]
    
    def _identify_system_involvement(self, symptoms):
        """Identify which body systems are involved"""
        systems = {
            'respiratory': ['cough', 'shortness_of_breath', 'chest_pain', 'wheezing'],
            'gastrointestinal': ['nausea', 'vomiting', 'diarrhea', 'abdominal_pain', 'constipation'],
            'neurological': ['headache', 'dizziness', 'confusion', 'seizure', 'weakness'],
            'cardiovascular': ['chest_pain', 'palpitations', 'shortness_of_breath', 'edema'],
            'musculoskeletal': ['joint_pain', 'muscle_pain', 'stiffness', 'swelling'],
            'dermatological': ['skin_rash', 'itching', 'lesions', 'discoloration'],
            'constitutional': ['fever', 'fatigue', 'weight_loss', 'night_sweats']
        }
        
        involved_systems = []
        for system, system_symptoms in systems.items():
            if any(symptom in system_symptoms for symptom in symptoms):
                involved_systems.append(system)
        
        return involved_systems
    
    def _assess_urgency(self, symptoms):
        """Assess the urgency level based on symptoms"""
        high_urgency = ['chest_pain', 'shortness_of_breath', 'severe_headache', 'confusion', 'high_fever']
        moderate_urgency = ['fever', 'persistent_cough', 'abdominal_pain', 'dizziness']
        
        if any(symptom in high_urgency for symptom in symptoms):
            return "HIGH - Immediate medical evaluation recommended"
        elif any(symptom in moderate_urgency for symptom in symptoms):
            return "MODERATE - Prompt medical evaluation advised"
        else:
            return "LOW - Routine medical consultation appropriate"
    
    def generate_disease_explanation(self, disease_name, confidence):
        """Generate professional explanation for predicted disease"""
        explanation = {
            'disease_name': disease_name,
            'confidence_level': self._interpret_confidence(confidence),
            'clinical_context': self._get_disease_context(disease_name),
            'recommended_actions': self._get_recommended_actions(disease_name, confidence)
        }
        return explanation
    
    def _interpret_confidence(self, confidence):
        """Interpret confidence score in medical terms"""
        if confidence >= 0.8:
            return "HIGH - Strong diagnostic probability"
        elif confidence >= 0.6:
            return "MODERATE - Significant diagnostic consideration"
        elif confidence >= 0.4:
            return "LOW-MODERATE - Possible diagnostic consideration"
        elif confidence >= 0.2:
            return "LOW - Differential diagnosis consideration"
        else:
            return "VERY LOW - Remote diagnostic possibility"
    
    def _get_disease_context(self, disease_name):
        """Get clinical context for the disease"""
        # This would be expanded with a comprehensive disease database
        return f"Clinical assessment for {disease_name} requires comprehensive evaluation including history, physical examination, and appropriate diagnostic testing."
    
    def _get_recommended_actions(self, disease_name, confidence):
        """Get recommended clinical actions"""
        actions = []
        
        if confidence >= 0.6:
            actions.append("Consider as primary differential diagnosis")
            actions.append("Obtain relevant diagnostic tests")
            actions.append("Initiate appropriate monitoring")
        elif confidence >= 0.3:
            actions.append("Include in differential diagnosis")
            actions.append("Consider targeted diagnostic evaluation")
        else:
            actions.append("Consider as remote possibility")
            actions.append("Monitor for additional symptoms")
        
        actions.append("Correlate with clinical presentation and examination findings")
        actions.append("Consider specialist consultation if indicated")
        
        return actions
    
    def generate_medical_disclaimer(self):
        """Generate comprehensive medical disclaimer"""
        return {
            'primary_disclaimer': "This diagnostic tool is intended for healthcare professional assistance only and should not replace clinical judgment, comprehensive patient evaluation, or established diagnostic protocols.",
            'limitations': [
                "AI predictions are based on statistical patterns and may not account for individual patient factors",
                "Clinical correlation with history, physical examination, and diagnostic testing is essential",
                "Rare diseases and atypical presentations may not be adequately represented",
                "Tool accuracy depends on quality and completeness of symptom input"
            ],
            'recommendations': [
                "Always perform comprehensive clinical assessment",
                "Consider patient's medical history, risk factors, and comorbidities",
                "Utilize appropriate diagnostic testing and specialist consultation",
                "Follow established clinical guidelines and protocols",
                "Document clinical reasoning and decision-making process"
            ],
            'emergency_note': "For emergency situations or acute symptoms, seek immediate medical attention regardless of AI predictions."
        }
