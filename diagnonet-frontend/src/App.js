import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import DiagnosisMethodPage from './pages/DiagnosisMethodPage';
import PatientFormPage from './pages/PatientFormPage';
import SupervisorResultsPage from './pages/SupervisorResultsPage';
import './styles/App.css';

// DiagnoNet Backend API Configuration
const API_BASE_URL = 'http://localhost:8001';

function App() {
  const [patientData, setPatientData] = useState(null);
  const [diagnosisResults, setDiagnosisResults] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStatus, setProcessingStatus] = useState('');

  // API call functions for DiagnoNet backend
  const callVitalsAnalysis = async (vitalsData) => {
    const formData = new FormData();
    formData.append('vitals_data', JSON.stringify({
      systolic_bp: parseInt(vitalsData.systolicBP),
      diastolic_bp: parseInt(vitalsData.diastolicBP),
      heart_rate: parseInt(vitalsData.heartRate),
      temperature: parseFloat(vitalsData.temperature),
      respiratory_rate: parseInt(vitalsData.respiratoryRate),
      oxygen_saturation: parseInt(vitalsData.oxygenSaturation)
    }));

    const response = await fetch(`${API_BASE_URL}/biogpt-analysis`, {
      method: 'POST',
      body: formData
    });
    if (!response.ok) throw new Error('Vitals analysis failed');
    return await response.json();
  };

  const callSymptomsAnalysis = async (symptomsData) => {
    const formData = new FormData();
    formData.append('symptoms_text', symptomsData.symptoms);

    const response = await fetch(`${API_BASE_URL}/symptoms-analysis`, {
      method: 'POST',
      body: formData
    });
    if (!response.ok) throw new Error('Symptoms analysis failed');
    return await response.json();
  };

  const callXrayAnalysis = async (xrayFile, patientInfo = null) => {
    const formData = new FormData();
    formData.append('xray_image', xrayFile);
    formData.append('generate_gradcam', 'true');
    formData.append('generate_explanation', 'true');

    // Add patient demographics if available
    if (patientInfo) {
      if (patientInfo.name) {
        formData.append('patient_name', patientInfo.name);
      }
      if (patientInfo.age) {
        formData.append('patient_age', patientInfo.age.toString());
      }
      if (patientInfo.height) {
        formData.append('patient_height', patientInfo.height);
      }
    }

    const response = await fetch(`${API_BASE_URL}/xray-chest-analysis`, {
      method: 'POST',
      body: formData
    });
    if (!response.ok) throw new Error('X-ray analysis failed');
    return await response.json();
  };

  const callMultiAgentSummary = async (vitalsResult, symptomsResult, xrayResult, patientInfo = null) => {
    const requestPayload = {
      patient_info: patientInfo || patientData?.patientInfo || null // Include patient info
    };

    if (vitalsResult) {
      requestPayload.vitals_result = {
        primary_diagnosis: vitalsResult.final_diagnosis,
        confidence: vitalsResult.confidence,
        recommendations: vitalsResult.recommendations,
        severity: vitalsResult.severity,
        vitals_details: vitalsResult.vitals_details
      };
    }

    if (symptomsResult) {
      requestPayload.symptoms_result = {
        symptoms_detected: symptomsResult.symptoms_detected,
        primary_diagnosis: symptomsResult.primary_diagnosis,
        confidence: symptomsResult.confidence,
        differential_diagnoses: symptomsResult.differential_diagnoses,
        urgency_level: symptomsResult.urgency_level,
        urgency_recommendation: symptomsResult.urgency_recommendation,
        recommendations: symptomsResult.recommendations,
        clinical_assessment: symptomsResult.clinical_assessment,
        ai_analysis: symptomsResult.ai_analysis
      };
    }

    if (xrayResult) {
      requestPayload.xray_result = {
        primary_finding: xrayResult.primary_finding,
        confidence: xrayResult.confidence,
        clinical_explanation: xrayResult.clinical_explanation,
        severity: xrayResult.severity,
        recommendations: xrayResult.recommendations,
        gradcam_visualization: xrayResult.gradcam_visualization
      };
    }

    const response = await fetch(`${API_BASE_URL}/multi-agent-summary`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestPayload)
    });
    if (!response.ok) throw new Error('Multi-agent summary failed');
    return await response.json();
  };

  const handleFormSubmit = async (data) => {
    setPatientData(data);
    setIsProcessing(true);

    try {
      const results = {
        patientInfo: data.patientInfo, // Fix: use data.patientInfo instead of entire data object
        vitalsResult: null,
        symptomsResult: null,
        xrayResult: null,
        multiAgentSummary: null,
        errors: []
      };

      // Process each selected agent
      const selectedAgents = data.selectedAgents;

      // Vitals Analysis
      if (selectedAgents.includes('vital')) {
        try {
          setProcessingStatus('Analyzing vital signs...');
          console.log('🔬 Calling Vitals Analysis with data:', data.agentData.vital);
          results.vitalsResult = await callVitalsAnalysis(data.agentData.vital);
          console.log('✅ Vitals Analysis Result:', results.vitalsResult);
        } catch (error) {
          console.error('❌ Vitals Analysis Error:', error);
          results.errors.push(`Vitals analysis error: ${error.message}`);
        }
      }

      // Symptoms Analysis
      if (selectedAgents.includes('symptom')) {
        try {
          setProcessingStatus('Analyzing symptoms...');
          console.log('🔬 Calling Symptoms Analysis with data:', data.agentData.symptom);
          results.symptomsResult = await callSymptomsAnalysis(data.agentData.symptom);
          console.log('✅ Symptoms Analysis Result:', results.symptomsResult);
        } catch (error) {
          console.error('❌ Symptoms Analysis Error:', error);
          results.errors.push(`Symptoms analysis error: ${error.message}`);
        }
      }

      // X-ray Analysis
      if (selectedAgents.includes('xray') && data.agentData.xray.imageFile) {
        try {
          setProcessingStatus('Analyzing X-ray image...');
          results.xrayResult = await callXrayAnalysis(data.agentData.xray.imageFile, data.patientInfo);
        } catch (error) {
          results.errors.push(`X-ray analysis error: ${error.message}`);
        }
      }

      // Multi-Agent Summary (if at least 2 agents completed successfully)
      const completedAnalyses = [results.vitalsResult, results.symptomsResult, results.xrayResult].filter(Boolean);
      console.log('🔬 Completed Analyses Count:', completedAnalyses.length);
      console.log('🔬 Completed Analyses:', completedAnalyses);

      if (completedAnalyses.length >= 2) {
        try {
          setProcessingStatus('Generating comprehensive summary...');
          console.log('🔬 Calling Multi-Agent Summary...');
          results.multiAgentSummary = await callMultiAgentSummary(
            results.vitalsResult,
            results.symptomsResult,
            results.xrayResult,
            data.patientInfo
          );
          console.log('✅ Multi-Agent Summary Result:', results.multiAgentSummary);
        } catch (error) {
          console.error('❌ Multi-Agent Summary Error:', error);
          results.errors.push(`Multi-agent summary error: ${error.message}`);
        }
      } else {
        console.log('⚠️ Skipping Multi-Agent Summary: Need at least 2 successful agents');
      }

      console.log('🎯 Final Results Object:', results);
      setDiagnosisResults(results);
      return { success: true, results };
    } catch (error) {
      const errorResults = {
        patientInfo: data.patientInfo, // Fix: use data.patientInfo instead of entire data object
        error: `Processing failed: ${error.message}`,
        errors: [`General error: ${error.message}`]
      };
      setDiagnosisResults(errorResults);
      return { success: false, results: errorResults };
    } finally {
      setIsProcessing(false);
      setProcessingStatus('');
    }
  };

  const resetApp = () => {
    setPatientData(null);
    setDiagnosisResults(null);
    setIsProcessing(false);
    setProcessingStatus('');
  };

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/diagnosis-method" element={<DiagnosisMethodPage />} />
          <Route
            path="/patient-form"
            element={
              <PatientFormPage
                onSubmit={handleFormSubmit}
                onReset={resetApp}
                isProcessing={isProcessing}
                processingStatus={processingStatus}
              />
            }
          />
          <Route
            path="/results"
            element={
              diagnosisResults ? (
                <SupervisorResultsPage
                  results={diagnosisResults}
                  onReset={resetApp}
                />
              ) : (
                <Navigate to="/patient-form" replace />
              )
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
