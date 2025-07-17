import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/PatientForm.css';

const PatientFormPage = ({ onSubmit, onReset }) => {
  const navigate = useNavigate();
  const [patientInfo, setPatientInfo] = useState({
    name: '',
    age: '',
    condition: ''
  });
  
  const [selectedAgents, setSelectedAgents] = useState([]);
  const [agentData, setAgentData] = useState({
    vital: {
      systolicBP: '',
      diastolicBP: '',
      heartRate: '',
      temperature: '',
      respiratoryRate: '',
      oxygenSaturation: ''
    },
    symptom: {
      symptoms: ''
    },
    xray: {
      imageFile: null
    }
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handlePatientInfoChange = (e) => {
    setPatientInfo({
      ...patientInfo,
      [e.target.name]: e.target.value
    });
  };

  const toggleAgent = (agent) => {
    if (selectedAgents.includes(agent)) {
      setSelectedAgents(selectedAgents.filter(a => a !== agent));
    } else {
      setSelectedAgents([...selectedAgents, agent]);
    }
  };

  const handleAgentDataChange = (agent, field, value) => {
    setAgentData({
      ...agentData,
      [agent]: {
        ...agentData[agent],
        [field]: value
      }
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    const formData = {
      patientInfo,
      selectedAgents,
      agentData: selectedAgents.reduce((acc, agent) => {
        acc[agent] = agentData[agent];
        return acc;
      }, {})
    };
    
    onSubmit(formData);
    
    // Navigate to results page after submission
    setTimeout(() => {
      navigate('/results');
    }, 2000);
  };

  const handleBackToHome = () => {
    onReset();
    navigate('/');
  };

  if (isSubmitting) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <h2>Processing Diagnosis...</h2>
        <p>Our AI agents are analyzing your information</p>
      </div>
    );
  }

  return (
    <div className="patient-form-page">
      <div className="medical-grid"></div>

      {/* Floating Particles */}
      <div className="floating-particles">
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
      </div>

      <div className="form-container">
        <div className="form-header">
          <button className="back-btn" onClick={handleBackToHome}>
            ← Back to Home
          </button>
          <h1 className="form-title">DiagnoNet - Patient Information & Agent Selection</h1>
          <p className="form-subtitle">Please provide your information and select the appropriate diagnostic agents</p>
        </div>

        <form onSubmit={handleSubmit} className="patient-form">
          {/* General Patient Information */}
          <div className="card patient-info-section">
            <h2 className="section-title">General Information</h2>
            
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Full Name *</label>
                <input
                  type="text"
                  name="name"
                  value={patientInfo.name}
                  onChange={handlePatientInfoChange}
                  className="form-input"
                  required
                  placeholder="Enter your full name"
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">Age *</label>
                <input
                  type="number"
                  name="age"
                  value={patientInfo.age}
                  onChange={handlePatientInfoChange}
                  className="form-input"
                  required
                  min="1"
                  max="120"
                  placeholder="Enter your age"
                />
              </div>
            </div>
            
            <div className="form-group">
              <label className="form-label">Current Condition/Concern *</label>
              <textarea
                name="condition"
                value={patientInfo.condition}
                onChange={handlePatientInfoChange}
                className="form-input form-textarea"
                required
                rows="3"
                placeholder="Describe your current health concern or condition"
              />
            </div>
          </div>

          {/* Agent Selection */}
          <div className="card agent-selection-section">
            <h2 className="section-title">Select Diagnostic Agents</h2>
            <p className="section-description">Choose the agents that best match your diagnostic needs</p>
            
            <div className="agents-grid">
              <div 
                className={`agent-card ${selectedAgents.includes('vital') ? 'selected' : ''}`}
                onClick={() => toggleAgent('vital')}
              >
                <div className="agent-icon vital-icon">
                  <svg width="60" height="60" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" fill="currentColor"/>
                  </svg>
                </div>
                <h3>Vital Agent</h3>
                <p>Analyze vital signs including blood pressure, heart rate, temperature, and respiratory rate</p>
              </div>
              
              <div 
                className={`agent-card ${selectedAgents.includes('symptom') ? 'selected' : ''}`}
                onClick={() => toggleAgent('symptom')}
              >
                <div className="agent-icon symptom-icon">
                  <svg width="60" height="60" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="currentColor"/>
                  </svg>
                </div>
                <h3>Symptom Agent</h3>
                <p>Comprehensive symptom analysis and pattern recognition for accurate diagnosis</p>
              </div>
              
              <div 
                className={`agent-card ${selectedAgents.includes('xray') ? 'selected' : ''}`}
                onClick={() => toggleAgent('xray')}
              >
                <div className="agent-icon xray-icon">
                  <svg width="60" height="60" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" stroke="currentColor" strokeWidth="2" fill="none"/>
                    <circle cx="9" cy="9" r="2" fill="currentColor"/>
                    <path d="M21 15l-3.086-3.086a2 2 0 0 0-2.828 0L6 21" stroke="currentColor" strokeWidth="2"/>
                  </svg>
                </div>
                <h3>X-ray Agent</h3>
                <p>Advanced medical imaging analysis for detailed internal examination</p>
              </div>
            </div>
          </div>

          {/* Dynamic Agent Input Fields */}
          {selectedAgents.length > 0 && (
            <div className="agent-inputs-section">
              {selectedAgents.map(agent => (
                <div key={agent} className="card agent-input-card">
                  <h3 className="agent-input-title">
                    {agent.charAt(0).toUpperCase() + agent.slice(1)} Agent Information
                  </h3>
                  
                  {agent === 'vital' && (
                    <div className="vital-inputs">
                      <div className="vital-grid">
                        <div className="vital-input-group">
                          <label className="vital-label">
                            <span className="label-text">Systolic BP</span>
                            <span className="label-unit">(mmHg)</span>
                          </label>
                          <input
                            type="number"
                            className="vital-input"
                            placeholder="120"
                            value={agentData.vital.systolicBP}
                            onChange={(e) => handleAgentDataChange('vital', 'systolicBP', e.target.value)}
                          />
                        </div>

                        <div className="vital-input-group">
                          <label className="vital-label">
                            <span className="label-text">Diastolic BP</span>
                            <span className="label-unit">(mmHg)</span>
                          </label>
                          <input
                            type="number"
                            className="vital-input"
                            placeholder="80"
                            value={agentData.vital.diastolicBP}
                            onChange={(e) => handleAgentDataChange('vital', 'diastolicBP', e.target.value)}
                          />
                        </div>

                        <div className="vital-input-group">
                          <label className="vital-label">
                            <span className="label-text">Heart Rate</span>
                            <span className="label-unit">(BPM)</span>
                          </label>
                          <input
                            type="number"
                            className="vital-input"
                            placeholder="72"
                            value={agentData.vital.heartRate}
                            onChange={(e) => handleAgentDataChange('vital', 'heartRate', e.target.value)}
                          />
                        </div>

                        <div className="vital-input-group">
                          <label className="vital-label">
                            <span className="label-text">Temperature</span>
                            <span className="label-unit">(°F)</span>
                          </label>
                          <input
                            type="number"
                            step="0.1"
                            className="vital-input"
                            placeholder="98.6"
                            value={agentData.vital.temperature}
                            onChange={(e) => handleAgentDataChange('vital', 'temperature', e.target.value)}
                          />
                        </div>

                        <div className="vital-input-group">
                          <label className="vital-label">
                            <span className="label-text">Respiratory Rate</span>
                            <span className="label-unit">(breaths/min)</span>
                          </label>
                          <input
                            type="number"
                            className="vital-input"
                            placeholder="16"
                            value={agentData.vital.respiratoryRate}
                            onChange={(e) => handleAgentDataChange('vital', 'respiratoryRate', e.target.value)}
                          />
                        </div>

                        <div className="vital-input-group">
                          <label className="vital-label">
                            <span className="label-text">Oxygen Saturation</span>
                            <span className="label-unit">(%)</span>
                          </label>
                          <input
                            type="number"
                            className="vital-input"
                            placeholder="98"
                            value={agentData.vital.oxygenSaturation}
                            onChange={(e) => handleAgentDataChange('vital', 'oxygenSaturation', e.target.value)}
                          />
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {agent === 'symptom' && (
                    <div className="symptom-inputs">
                      <div className="symptom-input-group">
                        <label className="symptom-label">
                          <span className="label-text">Describe Your Symptoms</span>
                          <span className="label-description">Please provide detailed information about all symptoms you're experiencing</span>
                        </label>
                        <textarea
                          className="symptom-textarea"
                          rows="6"
                          placeholder="Describe your symptoms in detail including:&#10;• What you're feeling&#10;• When it started&#10;• How severe it is (1-10 scale)&#10;• What makes it better or worse&#10;• Any other relevant details"
                          value={agentData.symptom.symptoms}
                          onChange={(e) => handleAgentDataChange('symptom', 'symptoms', e.target.value)}
                        />
                        <div className="character-count">
                          {agentData.symptom.symptoms.length} characters
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {agent === 'xray' && (
                    <div className="xray-inputs">
                      <div className="xray-upload-group">
                        <label className="xray-label">
                          <span className="label-text">Upload X-ray Image</span>
                          <span className="label-description">Upload a clear X-ray image for AI analysis</span>
                        </label>

                        <div className="file-upload-container">
                          <input
                            type="file"
                            id="xray-upload"
                            className="file-input-hidden"
                            accept="image/*,.dcm"
                            onChange={(e) => handleAgentDataChange('xray', 'imageFile', e.target.files[0])}
                          />
                          <label htmlFor="xray-upload" className="file-upload-area">
                            <div className="upload-icon">
                              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                <polyline points="14,2 14,8 20,8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                <line x1="16" y1="13" x2="8" y2="13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                <line x1="16" y1="17" x2="8" y2="17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                <polyline points="10,9 9,9 8,9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                              </svg>
                            </div>
                            <div className="upload-text">
                              <span className="upload-primary">
                                {agentData.xray.imageFile ? agentData.xray.imageFile.name : 'Click to upload X-ray image'}
                              </span>
                              <span className="upload-secondary">
                                Supports: JPG, PNG, DICOM files (Max 10MB)
                              </span>
                            </div>
                          </label>

                          {agentData.xray.imageFile && (
                            <div className="file-preview">
                              <div className="file-info">
                                <span className="file-name">{agentData.xray.imageFile.name}</span>
                                <span className="file-size">
                                  {(agentData.xray.imageFile.size / 1024 / 1024).toFixed(2)} MB
                                </span>
                              </div>
                              <button
                                type="button"
                                className="remove-file-btn"
                                onClick={() => handleAgentDataChange('xray', 'imageFile', null)}
                              >
                                ✕
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Submit Button */}
          <div className="submit-section">
            <button 
              type="submit" 
              className="btn btn-primary submit-btn"
              disabled={selectedAgents.length === 0}
            >
              Submit for Diagnosis
            </button>
            {selectedAgents.length === 0 && (
              <p className="error-message">Please select at least one diagnostic agent</p>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};

export default PatientFormPage;
