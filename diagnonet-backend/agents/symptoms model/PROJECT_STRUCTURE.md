# 📁 Medical AI Project Structure

## Overview

This document outlines the complete project structure for the Medical AI Diagnosis System, organized for production deployment and seamless integration with other diagnosis models.

## 🏗️ Directory Structure

```
medical-ai-diagnosis/
├── 📄 README.md                          # Main project documentation
├── 📄 PROJECT_STRUCTURE.md               # This file - project organization
├── 📄 requirements.txt                   # Python dependencies
├── 📄 setup.py                          # Environment setup script
├── 📄 check_model_auc.py                # Model performance checker
├── 📄 test_medical_ai.py                # Comprehensive test suite
│
├── 🔧 Core System Files
│   ├── 📄 medical_ai_api.py             # Main API interface (PRIMARY INTEGRATION POINT)
│   ├── 📄 streamlined_medical_ai.py     # Core ML engine
│   ├── 📄 advanced_model_trainer.py     # ML model training & management
│   ├── 📄 enhanced_medical_nlp.py       # ScispaCy-based NLP processor
│   ├── 📄 simplified_medical_nlp.py     # Fallback NLP processor
│   └── 📄 intelligent_followup_system.py # Conversation management
│
├── 📊 Model Files
│   ├── 📄 advanced_disease_predictor.pkl # Trained ensemble model (98%+ accuracy)
│   ├── 📄 disease_predictor_model.pkl   # Backup model file
│   └── 📄 advanced_data_loader.py       # Data loading utilities
│
├── 🗂️ Backend Components
│   ├── 📄 backend/data_loader.py        # Basic data loading
│   ├── 📄 backend/model_trainer.py      # Basic model training
│   ├── 📄 backend/symptom_analyzer.py   # Symptom analysis utilities
│   ├── 📄 backend/medical_insights.py   # Medical insights generator
│   ├── 📄 backend/mock_dataset.csv      # Sample training data
│   └── 📄 backend/requirements.txt      # Backend-specific dependencies
│
├── 📚 Documentation
│   ├── 📄 docs/api_reference.md         # Complete API documentation
│   ├── 📄 docs/integration_guide.md     # Integration patterns & examples
│   └── 📄 docs/model_architecture.md    # ML model documentation
│
├── 🧪 Examples & Testing
│   ├── 📄 examples/integration_example.py # Integration demonstration
│   ├── 📄 examples/basic_usage.py       # Basic usage examples
│   └── 📄 examples/batch_processing.py  # Batch processing examples
│
└── 📋 Configuration
    ├── 📄 .env.example                  # Environment variables template
    └── 📄 advanced_model_requirements.txt # Advanced model dependencies
```

## 🎯 Core Components Description

### Primary Integration Points

#### 1. **medical_ai_api.py** - Main API Interface
- **Purpose**: Primary integration point for external systems
- **Key Classes**: `MedicalAIAPI`
- **Key Functions**: `analyze_symptoms()`, `check_urgency()`
- **Integration**: Use this for all external integrations

```python
from medical_ai_api import MedicalAIAPI
api = MedicalAIAPI()
result = api.analyze("patient symptoms")
```

#### 2. **streamlined_medical_ai.py** - Core Engine
- **Purpose**: Orchestrates all system components
- **Features**: ML ensemble coordination, clinical validation
- **Dependencies**: All other core components

### ML Model System

#### 3. **advanced_model_trainer.py** - ML Model Management
- **Purpose**: Ensemble model training, evaluation, and management
- **Models**: Random Forest, Gradient Boosting, SVM, Neural Networks
- **Metrics**: Accuracy, Precision, Recall, F1-Score, AUC
- **Performance**: 98%+ accuracy maintained

#### 4. **advanced_disease_predictor.pkl** - Trained Model
- **Type**: Ensemble model with multiple algorithms
- **Accuracy**: 98%+ cross-validated
- **Features**: 20+ symptom features
- **Diseases**: 40+ medical conditions

### NLP Processing

#### 5. **enhanced_medical_nlp.py** - Advanced NLP
- **Technology**: ScispaCy with medical models
- **Models**: en_core_sci_md, en_ner_bc5cdr_md
- **Features**: Medical entity recognition, clinical validation
- **Fallback**: Graceful degradation to simplified NLP

#### 6. **simplified_medical_nlp.py** - Fallback NLP
- **Purpose**: Lightweight NLP without ScispaCy dependency
- **Method**: Pattern-based symptom extraction
- **Use Case**: Deployment environments without ScispaCy

## 🔧 File Responsibilities

### API Layer
| File | Responsibility | Integration Priority |
|------|---------------|---------------------|
| `medical_ai_api.py` | Main API interface | **HIGH** - Primary integration point |
| `streamlined_medical_ai.py` | System orchestration | **MEDIUM** - Internal coordination |

### ML Layer
| File | Responsibility | Integration Priority |
|------|---------------|---------------------|
| `advanced_model_trainer.py` | Model training/management | **LOW** - Background operations |
| `*.pkl` files | Trained models | **HIGH** - Required for predictions |

### NLP Layer
| File | Responsibility | Integration Priority |
|------|---------------|---------------------|
| `enhanced_medical_nlp.py` | Advanced symptom extraction | **MEDIUM** - Optimal performance |
| `simplified_medical_nlp.py` | Fallback extraction | **MEDIUM** - Deployment flexibility |

### Support Layer
| File | Responsibility | Integration Priority |
|------|---------------|---------------------|
| `backend/` | Legacy/utility components | **LOW** - Optional utilities |
| `docs/` | Documentation | **HIGH** - Integration guidance |
| `examples/` | Integration examples | **HIGH** - Implementation guidance |

## 🚀 Deployment Configurations

### Minimal Deployment
**For basic integration with fallback capabilities:**
```
Required Files:
├── medical_ai_api.py
├── streamlined_medical_ai.py
├── simplified_medical_nlp.py
├── advanced_model_trainer.py
├── advanced_disease_predictor.pkl
└── requirements.txt (core dependencies only)
```

### Full Deployment
**For optimal performance with all features:**
```
All files included
+ ScispaCy models installed
+ Groq API key configured
+ Full test suite validated
```

### Production Deployment
**For enterprise integration:**
```
Full Deployment +
├── Monitoring and logging configured
├── Performance optimization enabled
├── Security validation completed
└── Integration tests passed
```

## 📊 Data Flow

### Input Processing Flow
```
Natural Language Input
        ↓
Input Validation (medical_ai_api.py)
        ↓
NLP Processing (enhanced_medical_nlp.py OR simplified_medical_nlp.py)
        ↓
Symptom Extraction & Validation
        ↓
ML Ensemble Prediction (advanced_model_trainer.py)
        ↓
Clinical Validation & Confidence Scoring
        ↓
Structured Output (medical_ai_api.py)
```

### Model Training Flow
```
Training Data (advanced_data_loader.py)
        ↓
Data Preprocessing & Feature Engineering
        ↓
Multiple Algorithm Training (advanced_model_trainer.py)
        ↓
Cross-Validation & Performance Evaluation
        ↓
Ensemble Creation & Calibration
        ↓
Model Persistence (*.pkl files)
```

## 🔧 Configuration Management

### Environment Variables
```bash
# Optional AI Enhancement
GROQ_API_KEY=your_groq_api_key

# Performance Tuning
MEDICAL_AI_BATCH_SIZE=10
MEDICAL_AI_TIMEOUT=30
MEDICAL_AI_LOG_LEVEL=ERROR

# Model Configuration
MEDICAL_AI_CONFIDENCE_THRESHOLD=0.7
MEDICAL_AI_MAX_DIFFERENTIAL=5
```

### Configuration Files
- `requirements.txt` - Core Python dependencies
- `advanced_model_requirements.txt` - Advanced model dependencies
- `backend/requirements.txt` - Backend-specific dependencies
- `.env.example` - Environment variables template

## 🧪 Testing Structure

### Test Categories
1. **Unit Tests** - Individual component testing
2. **Integration Tests** - API integration validation
3. **Performance Tests** - Speed and accuracy validation
4. **System Tests** - End-to-end functionality

### Test Files
- `test_medical_ai.py` - Comprehensive test suite
- `examples/integration_example.py` - Integration demonstration
- `check_model_auc.py` - Model performance validation

## 📋 Maintenance Procedures

### Regular Maintenance
1. **Model Performance Monitoring**
   ```bash
   python check_model_auc.py
   ```

2. **System Health Check**
   ```bash
   python test_medical_ai.py --category integration
   ```

3. **Dependency Updates**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

### Model Updates
1. **Retrain Models**
   ```bash
   python advanced_model_trainer.py
   ```

2. **Validate Performance**
   ```bash
   python check_model_auc.py
   ```

3. **Update Documentation**
   - Update performance metrics in README.md
   - Validate API documentation
   - Test integration examples

## 🔒 Security Considerations

### File Permissions
- Model files (*.pkl): Read-only in production
- Configuration files: Restricted access
- Log files: Appropriate rotation and access controls

### Data Handling
- No persistent storage of patient data
- Input validation and sanitization
- Secure API key management

## 📞 Support Structure

### Documentation Hierarchy
1. **README.md** - Quick start and overview
2. **docs/api_reference.md** - Complete API documentation
3. **docs/integration_guide.md** - Integration patterns
4. **examples/** - Practical implementation examples

### Troubleshooting
1. **System Issues**: Check `test_medical_ai.py` results
2. **Performance Issues**: Run `check_model_auc.py`
3. **Integration Issues**: Review `examples/integration_example.py`
4. **Dependency Issues**: Validate `requirements.txt` installation

---

## 🎯 Integration Quick Start

For immediate integration:

1. **Install**: `python setup.py`
2. **Test**: `python test_medical_ai.py`
3. **Integrate**: Use `medical_ai_api.py` as primary interface
4. **Validate**: Run `examples/integration_example.py`

**Production Ready** ✅
