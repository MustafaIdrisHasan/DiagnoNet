# 🏥 DiagnoNET 2.0 - AI-Powered Medical Diagnosis Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

DiagnoNET 2.0 is an advanced multi-modal medical diagnosis platform that combines multiple AI agents to provide comprehensive medical analysis. The system integrates vital signs analysis, symptom assessment, and X-ray image analysis with clinical explanations powered by Ollama's Llama 3.2 models.

## 🌟 Features

### 🔬 **Multi-Agent Analysis**
- **Vitals Agent**: Analyzes vital signs with machine learning models and SHAP explanations
- **Symptoms Agent**: Natural language processing of medical symptoms
- **X-ray Agent**: Advanced chest X-ray analysis with TorchXRayVision and GradCAM++ visualizations

### 🧠 **AI-Powered Insights**
- **Clinical Explanations**: Powered by Ollama Llama 3.2 models
- **Confidence Scoring**: Uncertainty quantification for all predictions
- **Cross-Modal Analysis**: Integrated insights from multiple data sources
- **Patient Demographics**: Complete patient information tracking

### 🎯 **Advanced Capabilities**
- **GradCAM++ Visualizations**: Heatmaps showing AI decision areas
- **Real-time Processing**: Background task processing with polling
- **Comprehensive Reports**: Detailed medical reports with recommendations
- **JSON Export**: Structured data output for integration
- **Graceful Degradation**: System remains functional even if some components fail

### 🛡️ **Resilient Design**
DiagnoNET 2.0 is designed to work even with missing dependencies:
- **No Groq API Key**: Symptoms analysis uses ML-only predictions (still functional)
- **Missing Ollama**: Clinical summaries use fallback text generation
- **Network Issues**: Local ML models continue to work offline
- **Component Failures**: Other agents remain operational

## 🚀 Quick Start

### Prerequisites

Before running DiagnoNET 2.0, ensure you have the following installed:

1. **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
2. **Node.js 16+** - [Download Node.js](https://nodejs.org/)
3. **Ollama** - [Download Ollama](https://ollama.ai/)

### 📦 Installation

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd DiagnoNET2.0
```

#### 2. Backend Setup
```bash
cd diagnonet-backend

# Install Python dependencies
pip install -r requirements.txt

# Install additional AI/ML packages if needed
pip install torch torchvision
pip install torchxrayvision
pip install pytorch-grad-cam
pip install scikit-image
pip install matplotlib
```

#### 3. Frontend Setup
```bash
cd ../diagnonet-frontend

# Install Node.js dependencies
npm install
```

#### 4. Ollama Setup
```bash
# Install Ollama models for clinical explanations
ollama pull llama3.2:latest
ollama pull llama3.2:1b
```

### 🏃‍♂️ Running the Application

#### Method 1: Manual Start (Recommended for Development)

**Terminal 1 - Backend Server:**
```bash
cd diagnonet-backend
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 2 - Frontend Server:**
```bash
cd diagnonet-frontend
npm start
```

**Terminal 3 - Ollama Service (if not running as service):**
```bash
ollama serve
```

#### Method 2: Quick Start Script

Create a `start.bat` file (Windows) or `start.sh` file (Linux/Mac):

**Windows (start.bat):**
```batch
@echo off
echo Starting DiagnoNET 2.0...

start "Backend" cmd /k "cd diagnonet-backend && python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload"
start "Frontend" cmd /k "cd diagnonet-frontend && npm start"

echo DiagnoNET 2.0 is starting...
echo Backend: http://localhost:8001
echo Frontend: http://localhost:3000
pause
```

**Linux/Mac (start.sh):**
```bash
#!/bin/bash
echo "Starting DiagnoNET 2.0..."

# Start backend in background
cd diagnonet-backend
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload &

# Start frontend in background
cd ../diagnonet-frontend
npm start &

echo "DiagnoNET 2.0 is starting..."
echo "Backend: http://localhost:8001"
echo "Frontend: http://localhost:3000"
echo "Press Ctrl+C to stop all services"
wait
```

### 🌐 Accessing the Application

Once both servers are running:

1. **Frontend (Main Application)**: http://localhost:3000
2. **Backend API**: http://localhost:8001
3. **API Documentation**: http://localhost:8001/docs

## 📋 Usage Guide

### 🏠 **Getting Started**
1. Open http://localhost:3000 in your browser
2. Click "Start Diagnosis" on the landing page
3. Choose your preferred analysis method
4. Select diagnostic agents (Vitals, Symptoms, X-ray)

### 👤 **Patient Information**
Fill in patient demographics:
- **Name**: Patient's full name
- **Age**: Patient's age in years
- **Height**: Patient's height (cm or ft/in)
- **Weight**: Patient's weight (kg or lbs)

### 🔬 **Diagnostic Agents**

#### **Vitals Agent**
Input vital signs:
- Systolic/Diastolic Blood Pressure (mmHg)
- Heart Rate (bpm)
- Temperature (°C)
- Respiratory Rate (breaths/min)
- Oxygen Saturation (%)

#### **Symptoms Agent**
Describe symptoms in natural language:
- Current symptoms
- Duration and severity
- Associated factors

#### **X-ray Agent**
Upload chest X-ray images:
- Supported formats: PNG, JPG, JPEG, DICOM
- Maximum file size: 10MB
- Automatic analysis with GradCAM visualizations

### 📊 **Results**
The system provides:
- **Individual Agent Results**: Detailed analysis from each agent
- **Multi-Agent Summary**: Comprehensive clinical assessment
- **Confidence Scores**: Reliability indicators for all predictions
- **Recommendations**: Clinical guidance and next steps
- **Visualizations**: GradCAM heatmaps for X-ray analysis

## 🛠️ Command Line Interface

### X-ray Analysis CLI

For advanced users, DiagnoNET includes a powerful CLI for X-ray analysis:

```bash
cd diagnonet-backend
python "agents/x-ray chest/run_cxr.py" --help
```

#### **Basic Usage:**
```bash
# Basic X-ray analysis
python "agents/x-ray chest/run_cxr.py" --image chest.png

# With patient demographics
python "agents/x-ray chest/run_cxr.py" \
  --image chest.png \
  --patient-name "John Doe" \
  --age 42 \
  --height-cm 178

# Height conversion (feet/inches to cm)
python "agents/x-ray chest/run_cxr.py" \
  --image chest.png \
  --patient-name "Jane Smith" \
  --height-ft 5 \
  --height-in 7

# With clinical explanations
python "agents/x-ray chest/run_cxr.py" \
  --image chest.png \
  --patient-name "Test Patient" \
  --age 30 \
  --height-cm 170 \
  --no-cam

# Skip GradCAM and explanations for faster processing
python "agents/x-ray chest/run_cxr.py" \
  --image chest.png \
  --no-cam \
  --no-explain
```

#### **CLI Options:**
- `--patient-name`: Patient name
- `--age`: Patient age in years
- `--height-cm`: Height in centimeters
- `--height-ft`: Height in feet (converts to cm)
- `--height-in`: Height in inches (converts to cm)
- `--topk`: Number of predictions to include (default: 18)
- `--no-cam`: Skip GradCAM generation
- `--no-explain`: Skip clinical explanations
- `--json-out`: Output JSON file path

## 🚨 Troubleshooting

### Common Issues

#### **Backend Won't Start**
- Check Python version: `python --version` (requires 3.11+)
- Install missing dependencies: `pip install -r requirements.txt`
- Check port availability: `netstat -an | findstr 8001`

#### **Frontend Won't Start**
- Check Node.js version: `node --version` (requires 16+)
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`

#### **Ollama Issues**
- Check Ollama installation: `ollama --version`
- Verify models are downloaded: `ollama list`
- Restart Ollama service: `ollama serve`

#### **X-ray Analysis Fails**
- Verify image format (PNG, JPG, JPEG)
- Check file size (max 10MB)
- Ensure TorchXRayVision is installed: `pip install torchxrayvision`

#### **"Failed to Fetch" Errors**
- Verify backend is running on port 8001
- Check CORS configuration in backend
- Ensure frontend API_BASE_URL points to correct backend URL

#### **🔑 API Key Configuration Issues**

**Symptoms Analysis Not Working:**
```
Error: "Symptoms analysis not available" or "Groq AI not configured"
```

**Solution:**
1. **Get a Groq API Key** (Free):
   - Visit: https://console.groq.com/
   - Sign up for a free account
   - Generate an API key

2. **Set Environment Variable**:
   ```bash
   # Windows (Command Prompt)
   set GROQ_API_KEY=your_api_key_here

   # Windows (PowerShell)
   $env:GROQ_API_KEY="your_api_key_here"

   # Linux/Mac
   export GROQ_API_KEY="your_api_key_here"
   ```

3. **Or Create .env File**:
   ```bash
   # Copy template
   cp diagnonet-backend/.env.example diagnonet-backend/.env

   # Edit .env file and add:
   GROQ_API_KEY=your_api_key_here
   ```

4. **Restart Backend Server** after setting the API key

**Note**: DiagnoNET will still work without Groq API key, but with limited symptoms analysis capabilities. Vitals and X-ray analysis remain fully functional.

#### **🧪 Missing Python Packages**
```
Error: "ModuleNotFoundError" or "ImportError"
```

**Solution:**
```bash
cd diagnonet-backend
pip install -r requirements.txt

# If specific packages are missing:
pip install torch torchvision
pip install torchxrayvision
pip install groq
pip install transformers
pip install scikit-learn
```

#### **🔧 System Initialization Failed**
```
Error: "System initialization failed" in backend logs
```

**Solution:**
1. Check all dependencies are installed
2. Verify Python version compatibility (3.11+)
3. Ensure sufficient disk space for model downloads
4. Check internet connection for initial model downloads
5. Restart backend server: `Ctrl+C` then restart

**The system is designed to be resilient - even if some components fail, core functionality remains available.**

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Medical Disclaimer

**IMPORTANT**: DiagnoNET 2.0 is for educational and research purposes only. This system is NOT intended for actual medical diagnosis or treatment decisions. Always consult qualified healthcare professionals for medical advice, diagnosis, and treatment.

## 🆘 Support

For support and questions:
- Check the troubleshooting section above
- Review API documentation at http://localhost:8001/docs
- Submit issues on the project repository

---

**DiagnoNET 2.0** - Advancing AI-powered medical diagnosis through multi-modal analysis 🏥✨
