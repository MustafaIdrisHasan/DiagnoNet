import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/SupervisorResults.css';

const SupervisorResultsPage = ({ results, onReset }) => {
  const navigate = useNavigate();

  const handleNewAnalysis = () => {
    onReset();
    navigate('/');
  };

  const handlePrintReport = () => {
    window.print();
  };

  if (!results) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <h2>Processing Results...</h2>
      </div>
    );
  }

  const { patientInfo, supervisorAnalysis, confidence } = results;

  return (
    <div className="supervisor-results-page">
      <div className="medical-grid"></div>

      {/* Floating Particles */}
      <div className="floating-particles">
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
      </div>

      {/* Medical Visualization Elements */}
      <div className="results-decorations">
        <div className="dna-helix" style={{ top: '10%', left: '5%' }}></div>
        <div className="medical-chart" style={{ top: '20%', right: '10%' }}>
          <svg width="100" height="80" viewBox="0 0 100 80" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10 70 L25 50 L40 60 L55 30 L70 45 L85 20" stroke="#E61A4F" strokeWidth="3" fill="none" opacity="0.6"/>
            <circle cx="25" cy="50" r="3" fill="#E61A4F"/>
            <circle cx="40" cy="60" r="3" fill="#FB6E92"/>
            <circle cx="55" cy="30" r="3" fill="#800080"/>
            <circle cx="70" cy="45" r="3" fill="#E61A4F"/>
          </svg>
        </div>
        
        <div className="brain-scan" style={{ bottom: '15%', left: '8%' }}>
          <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C8.5 2 6 4.5 6 8c0 1.5.5 3 1.5 4C6.5 13 6 14.5 6 16c0 3.5 2.5 6 6 6s6-2.5 6-6c0-1.5-.5-3-1.5-4 1-1 1.5-2.5 1.5-4 0-3.5-2.5-6-6-6z" fill="#800080" opacity="0.2"/>
            <circle cx="9" cy="10" r="1" fill="#E61A4F"/>
            <circle cx="15" cy="10" r="1" fill="#E61A4F"/>
            <path d="M9 14 Q12 16 15 14" stroke="#FB6E92" strokeWidth="1.5" fill="none"/>
          </svg>
        </div>
      </div>

      <div className="results-container">
        <div className="results-header">
          <h1 className="results-title fade-in">
            DiagnoNet ANALYSIS COMPLETE
          </h1>
          <p className="results-subtitle">
            Comprehensive AI-Assisted Diagnosis Report
          </p>
        </div>

        <div className="results-content">
          {/* Patient Summary Card */}
          <div className="card patient-summary-card fade-in">
            <div className="card-header">
              <h2 className="card-title">Patient Summary</h2>
              <div className="confidence-badge">
                <span className="confidence-label">Confidence</span>
                <span className="confidence-value">{confidence}</span>
              </div>
            </div>
            
            <div className="patient-details">
              <div className="detail-item">
                <span className="detail-label">Name:</span>
                <span className="detail-value">{patientInfo.name}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Age:</span>
                <span className="detail-value">{patientInfo.age} years</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Condition:</span>
                <span className="detail-value">{patientInfo.condition}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Agents Used:</span>
                <span className="detail-value">
                  {patientInfo.selectedAgents.map(agent => 
                    agent.charAt(0).toUpperCase() + agent.slice(1)
                  ).join(', ')}
                </span>
              </div>
            </div>
          </div>

          {/* AI Supervisor Analysis Card */}
          <div className="card supervisor-analysis-card fade-in">
            <div className="card-header">
              <h2 className="card-title">AI Supervisor Analysis</h2>
              <div className="analysis-status">
                <div className="status-indicator active"></div>
                <span>Analysis Complete</span>
              </div>
            </div>

            <div className="supervisor-analysis-content">
              <div className="analysis-text-container">
                <div className="analysis-text">
                  {supervisorAnalysis || "Based on the analysis from our AI agents, preliminary findings suggest further examination is recommended."}
                </div>
              </div>
            </div>
          </div>



          {/* Important Notice */}
          <div className="card notice-card fade-in">
            <div className="notice-header">
              <svg width="30" height="30" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L2 7v10c0 5.55 3.84 9.74 9 11 5.16-1.26 9-5.45 9-11V7l-10-5z" fill="#800080"/>
                <path d="M12 8v4M12 16h.01" stroke="white" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              <h3>Important Medical Notice</h3>
            </div>
            <div className="notice-content">
              <p>
                <strong>This AI analysis is for informational purposes only and should not replace professional medical advice.</strong>
                Please consult with a qualified healthcare provider for proper diagnosis and treatment. 
                AI assists, but does not replace, professional medical judgment.
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="action-buttons">
            <button className="btn btn-primary" onClick={handlePrintReport}>
              Print Report
            </button>
            <button className="btn btn-secondary" onClick={handleNewAnalysis}>
              New Analysis
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SupervisorResultsPage;
