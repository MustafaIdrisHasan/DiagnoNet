# 📚 Medical AI API Reference

## Overview

The Medical AI Diagnosis System provides a clean, standardized API for integrating medical symptom analysis and disease prediction into other diagnosis models. This document provides comprehensive API documentation for seamless integration.

## 🚀 Quick Start

```python
from medical_ai_api import MedicalAIAPI, analyze_symptoms, check_urgency

# Initialize API
api = MedicalAIAPI()

# Simple analysis
result = analyze_symptoms("I have fever and cough")
print(result['predictions']['primary']['disease'])
```

## 📋 Core API Classes

### MedicalAIAPI

Main API class for medical analysis functionality.

#### Constructor

```python
MedicalAIAPI(groq_api_key: Optional[str] = None)
```

**Parameters:**
- `groq_api_key` (optional): API key for enhanced AI analysis

**Example:**
```python
# Basic initialization
api = MedicalAIAPI()

# With AI enhancement
api = MedicalAIAPI("your_groq_api_key")
```

#### Methods

##### analyze(input_text: str) → Dict

Analyzes natural language symptom descriptions and returns comprehensive medical analysis.

**Parameters:**
- `input_text` (str): Natural language description of symptoms

**Returns:**
- `Dict`: Comprehensive analysis result (see Output Format section)

**Example:**
```python
result = api.analyze("I have severe chest pain and shortness of breath")
```

##### batch_analyze(inputs: List[str]) → List[Dict]

Analyzes multiple symptom descriptions in batch.

**Parameters:**
- `inputs` (List[str]): List of symptom descriptions

**Returns:**
- `List[Dict]`: List of analysis results

**Example:**
```python
results = api.batch_analyze([
    "fever and cough",
    "headache and nausea",
    "chest pain"
])
```

##### get_system_info() → Dict

Returns system information and capabilities.

**Returns:**
- `Dict`: System status and component information

**Example:**
```python
info = api.get_system_info()
print(f"Status: {info['status']}")
print(f"Components: {info['components']}")
```

## 🔧 Standalone Functions

### analyze_symptoms(input_text: str) → Dict

Convenience function for quick symptom analysis.

**Parameters:**
- `input_text` (str): Symptom description

**Returns:**
- `Dict`: Analysis result

**Example:**
```python
result = analyze_symptoms("fever, cough, and fatigue")
primary_diagnosis = result['predictions']['primary']['disease']
```

### check_urgency(input_text: str) → str

Quick urgency assessment for symptom descriptions.

**Parameters:**
- `input_text` (str): Symptom description

**Returns:**
- `str`: Urgency level ("Low", "Moderate", "High", "Emergency")

**Example:**
```python
urgency = check_urgency("severe chest pain")
print(urgency)  # "High" or "Emergency"
```

## 🚀 Quick Start

```python
from medical_ai_api import MedicalAIAPI, analyze_symptoms, check_urgency

# Initialize API
api = MedicalAIAPI()

# Simple analysis
result = analyze_symptoms("I have fever and cough")
print(result['predictions']['primary']['disease'])
```

## 📋 Core API Classes

### MedicalAIAPI

Main API class for medical analysis functionality.

#### Constructor

```python
MedicalAIAPI(groq_api_key: Optional[str] = None)
```

**Parameters:**
- `groq_api_key` (optional): API key for enhanced AI analysis

**Example:**
```python
# Basic initialization
api = MedicalAIAPI()

# With AI enhancement
api = MedicalAIAPI("your_groq_api_key")
```

#### Methods

##### analyze(input_text: str) → Dict

Analyzes natural language symptom descriptions and returns comprehensive medical analysis.

**Parameters:**
- `input_text` (str): Natural language description of symptoms

**Returns:**
- `Dict`: Comprehensive analysis result (see Output Format section)

**Example:**
```python
result = api.analyze("I have severe chest pain and shortness of breath")
```

##### batch_analyze(inputs: List[str]) → List[Dict]

Analyzes multiple symptom descriptions in batch.

**Parameters:**
- `inputs` (List[str]): List of symptom descriptions

**Returns:**
- `List[Dict]`: List of analysis results

**Example:**
```python
results = api.batch_analyze([
    "fever and cough",
    "headache and nausea",
    "chest pain"
])
```

##### get_system_info() → Dict

Returns system information and capabilities.

**Returns:**
- `Dict`: System status and component information

**Example:**
```python
info = api.get_system_info()
print(f"Status: {info['status']}")
print(f"Components: {info['components']}")
```

## 🔧 Standalone Functions

### analyze_symptoms(input_text: str) → Dict

Convenience function for quick symptom analysis.

**Parameters:**
- `input_text` (str): Symptom description

**Returns:**
- `Dict`: Analysis result

**Example:**
```python
result = analyze_symptoms("fever, cough, and fatigue")
primary_diagnosis = result['predictions']['primary']['disease']
```

### check_urgency(input_text: str) → str

Quick urgency assessment for symptom descriptions.

**Parameters:**
- `input_text` (str): Symptom description

**Returns:**
- `str`: Urgency level ("Low", "Moderate", "High", "Emergency")

**Example:**
```python
urgency = check_urgency("severe chest pain")
print(urgency)  # "High" or "Emergency"
```

## 📊 Input Format

The API accepts natural language symptom descriptions in various formats:

### Supported Input Types

1. **Natural Language**: "I have been experiencing chest pain and shortness of breath"
2. **Medical Terminology**: "Patient presents with dyspnea and chest discomfort"
3. **Symptom Lists**: "fever, cough, headache, fatigue"
4. **Informal Descriptions**: "my head hurts and I feel sick"
5. **Temporal Context**: "chest pain for 2 days, getting worse"

### Input Examples

```python
# Various input formats
inputs = [
    "I have severe chest pain radiating to my left arm",
    "Patient presents with acute abdominal pain and nausea",
    "fever 102°F, chills, body aches for 3 days",
    "can't breathe properly, chest feels tight",
    "headache, dizziness, blurred vision"
]

for input_text in inputs:
    result = api.analyze(input_text)
    # Process result...
```

## 📤 Output Format

### Complete Response Structure

```python
{
    "symptoms": {
        "detected": ["fever", "cough", "headache"],
        "confidence_scores": {
            "fever": 0.95,
            "cough": 0.88,
            "headache": 0.92
        },
        "extraction_method": "enhanced_medical_nlp",
        "total_symptoms": 3
    },
    "predictions": {
        "primary": {
            "disease": "Upper Respiratory Infection",
            "confidence": 0.89,
            "confidence_percentage": 89.2,
            "confidence_level": "High - Significant diagnostic consideration"
        },
        "differential": [
            {
                "disease": "Influenza",
                "confidence": 0.76,
                "confidence_percentage": 76.3,
                "confidence_level": "High - Significant diagnostic consideration"
            },
            {
                "disease": "Common Cold",
                "confidence": 0.68,
                "confidence_percentage": 68.1,
                "confidence_level": "Moderate - Possible diagnostic consideration"
            }
        ],
        "ml_confidence": 0.89,
        "model_version": "advanced_ensemble_v1"
    },
    "assessment": {
        "urgency_level": "Moderate",
        "recommendation": "Prompt medical evaluation advised",
        "overall_confidence": 0.87,
        "clinical_notes": "Respiratory symptoms suggest viral infection"
    },
    "ai_analysis": "Based on the symptom pattern...",
    "metadata": {
        "processing_time": 0.234,
        "timestamp": "2024-01-15T10:30:00Z",
        "api_version": "1.0.0"
    }
}
```

### Field Descriptions

#### symptoms
- `detected` (List[str]): List of detected symptom names
- `confidence_scores` (Dict[str, float]): Confidence score (0-1) for each symptom
- `extraction_method` (str): NLP method used ("enhanced_medical_nlp" or "simplified_medical_nlp")
- `total_symptoms` (int): Number of symptoms detected

#### predictions
- `primary` (Dict): Primary diagnosis prediction
  - `disease` (str): Disease name
  - `confidence` (float): Confidence score (0-1)
  - `confidence_percentage` (float): Confidence as percentage
  - `confidence_level` (str): Human-readable confidence interpretation
- `differential` (List[Dict]): Alternative diagnoses (top 5)
- `ml_confidence` (float): Overall ML model confidence
- `model_version` (str): ML model version identifier

#### assessment
- `urgency_level` (str): "Low", "Moderate", "High", or "Emergency"
- `recommendation` (str): Clinical recommendation text
- `overall_confidence` (float): Overall analysis confidence (0-1)
- `clinical_notes` (str): Additional clinical observations

#### ai_analysis (optional)
- Enhanced AI analysis text when Groq API is available

#### metadata
- `processing_time` (float): Analysis time in seconds
- `timestamp` (str): ISO format timestamp
- `api_version` (str): API version

## 🔍 Error Handling

### Error Response Format

```python
{
    "error": "Error description",
    "error_type": "ValidationError",
    "error_code": "INVALID_INPUT",
    "suggestions": ["Check input format", "Ensure medical content"]
}
```

### Common Error Types

1. **ValidationError**: Invalid input format
2. **SystemError**: Internal system error
3. **ModelError**: ML model prediction error
4. **NLPError**: Natural language processing error

### Error Handling Example

```python
result = api.analyze(user_input)

if "error" in result:
    print(f"Analysis failed: {result['error']}")
    if "suggestions" in result:
        print("Suggestions:", result['suggestions'])
else:
    # Process successful result
    symptoms = result['symptoms']['detected']
    primary = result['predictions']['primary']
```

## 🎯 Integration Patterns

### Pattern 1: Simple Integration

```python
from medical_ai_api import analyze_symptoms

def quick_diagnosis(symptoms_text):
    """Simple diagnosis integration"""
    result = analyze_symptoms(symptoms_text)
    
    if "error" in result:
        return None
    
    return {
        "diagnosis": result['predictions']['primary']['disease'],
        "confidence": result['predictions']['primary']['confidence_percentage'],
        "urgency": result['assessment']['urgency_level']
    }
```

### Pattern 2: Comprehensive Integration

```python
from medical_ai_api import MedicalAIAPI

class MedicalDiagnosisSystem:
    def __init__(self):
        self.medical_ai = MedicalAIAPI()
        self.other_models = []  # Your other diagnosis models
    
    def combined_analysis(self, symptoms):
        """Combine Medical AI with other models"""
        # Get Medical AI analysis
        ai_result = self.medical_ai.analyze(symptoms)
        
        if "error" in ai_result:
            return {"error": "Medical AI analysis failed"}
        
        # Extract key information
        ai_diagnosis = ai_result['predictions']['primary']
        ai_confidence = ai_result['assessment']['overall_confidence']
        
        # Combine with other models
        combined_result = {
            "medical_ai": ai_diagnosis,
            "confidence_weighted": ai_confidence,
            "urgency": ai_result['assessment']['urgency_level'],
            "symptoms": ai_result['symptoms']['detected']
        }
        
        return combined_result
```

### Pattern 3: Batch Processing

```python
def process_patient_batch(patient_records):
    """Process multiple patients efficiently"""
    api = MedicalAIAPI()
    
    # Extract symptom descriptions
    symptom_texts = [record['symptoms'] for record in patient_records]
    
    # Batch analyze
    results = api.batch_analyze(symptom_texts)
    
    # Combine with patient data
    for i, result in enumerate(results):
        patient_records[i]['ai_analysis'] = result
        patient_records[i]['priority'] = result['assessment']['urgency_level']
    
    return patient_records
```

## 📈 Performance Considerations

### Response Times
- **Average**: 200-500ms per analysis
- **Batch processing**: ~100ms per item (parallelized)
- **Cold start**: First analysis may take 1-2 seconds

### Memory Usage
- **Base system**: ~200MB
- **With ScispaCy**: ~400MB
- **Per analysis**: ~1-5MB temporary

### Optimization Tips

1. **Reuse API instance**: Initialize once, use multiple times
2. **Batch processing**: Use `batch_analyze()` for multiple inputs
3. **Caching**: Cache results for identical inputs
4. **Async processing**: Wrap in async functions for concurrent requests

```python
# Good: Reuse instance
api = MedicalAIAPI()
for symptom in symptoms_list:
    result = api.analyze(symptom)

# Better: Batch processing
results = api.batch_analyze(symptoms_list)
```

## 🔒 Security & Privacy

### Data Handling
- **No persistence**: Input data is not stored permanently
- **Memory cleanup**: Temporary data cleared after processing
- **No external transmission**: Data stays within your system (except optional Groq AI)

### API Key Management
```python
import os

# Secure API key handling
groq_key = os.getenv('GROQ_API_KEY')
api = MedicalAIAPI(groq_key)
```

### Input Validation
- Automatic input sanitization
- Medical content validation
- Length and format checks

## 🧪 Testing Integration

### Validation Test

```python
def test_integration():
    """Test Medical AI integration"""
    api = MedicalAIAPI()
    
    # Test basic functionality
    result = api.analyze("fever and cough")
    assert "symptoms" in result
    assert "predictions" in result
    assert len(result['symptoms']['detected']) > 0
    
    # Test error handling
    error_result = api.analyze("")
    assert "error" in error_result or len(error_result['symptoms']['detected']) == 0
    
    print("✅ Integration test passed")

test_integration()
```

---

## 📞 Support

For integration support:
1. Run the test suite: `python test_medical_ai.py`
2. Check system info: `api.get_system_info()`
3. Review example integrations in `examples/`
4. Validate with provided test cases
