import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import PatientFormPage from './pages/PatientFormPage';
import SupervisorResultsPage from './pages/SupervisorResultsPage';
import './styles/App.css';

function App() {
  const [patientData, setPatientData] = useState(null);
  const [diagnosisResults, setDiagnosisResults] = useState(null);

  const handleFormSubmit = (data) => {
    setPatientData(data);
    // Simulate backend processing
    setTimeout(() => {
      setDiagnosisResults({
        patientInfo: data,
        supervisorAnalysis: "Based on the comprehensive analysis from our specialized AI agents, the following assessment has been made:\n\nThe vital signs analysis indicates parameters within expected ranges for the patient's age group. The symptom evaluation reveals patterns consistent with common presentations, though further clinical correlation is recommended.\n\nThe integrated assessment suggests a systematic approach to diagnosis, with consideration of both objective measurements and subjective symptom reporting. The AI supervisor recommends clinical follow-up for comprehensive evaluation and appropriate treatment planning.\n\nThis analysis should be interpreted in conjunction with clinical judgment and additional diagnostic testing as deemed appropriate by the healthcare provider.",
        confidence: "85%"
      });
    }, 2000);
  };

  const resetApp = () => {
    setPatientData(null);
    setDiagnosisResults(null);
  };

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route
            path="/patient-form"
            element={
              <PatientFormPage
                onSubmit={handleFormSubmit}
                onReset={resetApp}
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
                <Navigate to="/" replace />
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
