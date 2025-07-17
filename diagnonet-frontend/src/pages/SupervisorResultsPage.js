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

  const {
    patientInfo,
    vitalsResult,
    symptomsResult,
    xrayResult,
    multiAgentSummary,
    errors = [],
    error
  } = results;

  // Debug logging (can be removed in production)
  if (process.env.NODE_ENV === 'development') {
    console.log('🔍 SupervisorResultsPage - Results received:', {
      vitals: !!vitalsResult,
      symptoms: !!symptomsResult,
      xray: !!xrayResult,
      summary: !!multiAgentSummary,
      errors: errors.length
    });
  }

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
                <span className="confidence-label">Analysis Status</span>
                <span className="confidence-value">
                  {errors.length > 0 ? 'Partial' : 'Complete'}
                </span>
              </div>
            </div>

            <div className="patient-details">
              <div className="detail-item">
                <span className="detail-label">Name:</span>
                <span className="detail-value">
                  {patientInfo?.name ||
                   multiAgentSummary?.patient_info?.name ||
                   xrayResult?.patient_demographics?.patient_name ||
                   'Not provided'}
                </span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Age:</span>
                <span className="detail-value">
                  {(() => {
                    const age = patientInfo?.age ||
                               multiAgentSummary?.patient_info?.age ||
                               xrayResult?.patient_demographics?.age;
                    return age ? `${age} years` : 'Not provided';
                  })()}
                </span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Height:</span>
                <span className="detail-value">
                  {(() => {
                    const height = patientInfo?.height ||
                                  multiAgentSummary?.patient_info?.height ||
                                  xrayResult?.patient_demographics?.height;
                    const unit = patientInfo?.heightUnit || multiAgentSummary?.patient_info?.heightUnit;

                    if (height) {
                      // If height comes from X-ray demographics, it's already formatted (e.g., "170 cm")
                      if (xrayResult?.patient_demographics?.height && !patientInfo?.height && !multiAgentSummary?.patient_info?.height) {
                        return height;
                      }
                      // Otherwise, format with unit
                      return `${height} ${unit === 'ft' ? 'feet' : 'cm'}`;
                    }
                    return 'Not provided';
                  })()}
                </span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Agents Used:</span>
                <span className="detail-value">
                  {(() => {
                    const agents = [];
                    if (vitalsResult) agents.push('Vital');
                    if (symptomsResult) agents.push('Symptom');
                    if (xrayResult) agents.push('X-ray');
                    return agents.length > 0 ? agents.join(', ') : 'None';
                  })()}
                </span>
              </div>
            </div>
          </div>

          {/* Error Display */}
          {(error || errors.length > 0) && (
            <div className="card error-card fade-in">
              <div className="card-header">
                <h2 className="card-title" style={{ color: '#E61A4F' }}>Processing Errors</h2>
              </div>
              <div className="error-content">
                {error && <p className="error-message">{error}</p>}
                {errors.map((err, index) => (
                  <p key={index} className="error-message">{err}</p>
                ))}
              </div>
            </div>
          )}

          {/* Multi-Agent Summary */}
          {multiAgentSummary && (
            <div className="card supervisor-analysis-card fade-in">
              <div className="card-header">
                <h2 className="card-title">Multi-Agent AI Summary</h2>
                <div className="analysis-status">
                  <div className="status-indicator active"></div>
                  <span>Comprehensive Analysis Complete</span>
                </div>
              </div>

              <div className="supervisor-analysis-content">
                <div className="analysis-text-container">
                  <div className="analysis-text">
                    <h4>Clinical Summary:</h4>
                    <p>{multiAgentSummary.clinical_summary}</p>

                    <h4>Overall Assessment:</h4>
                    <p>{multiAgentSummary.overall_assessment}</p>

                    <div className="summary-metrics">
                      <div className="metric">
                        <span className="metric-label">Urgency Level:</span>
                        <span className={`metric-value urgency-${multiAgentSummary.urgency_level.toLowerCase()}`}>
                          {multiAgentSummary.urgency_level}
                        </span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">Confidence:</span>
                        <span className="metric-value">
                          {(multiAgentSummary.confidence_score * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>

                    <h4>Key Findings:</h4>
                    <ul className="findings-list">
                      {multiAgentSummary.key_findings.map((finding, index) => (
                        <li key={index}>{finding}</li>
                      ))}
                    </ul>

                    <h4>Recommendations:</h4>
                    <ul className="recommendations-list">
                      {multiAgentSummary.recommendations.map((rec, index) => (
                        <li key={index}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Individual Agent Results */}
          {vitalsResult && (
            <div className="card agent-result-card fade-in">
              <div className="card-header">
                <h2 className="card-title">🩺 Vitals Analysis Results</h2>
                <div className="agent-badge vitals-badge">BioGPT Agent</div>
              </div>
              <div className="agent-result-content">
                <div className="primary-diagnosis">
                  <h4>Primary Diagnosis:</h4>
                  <p>{vitalsResult.final_diagnosis}</p>
                  <span className="confidence">Confidence: {(vitalsResult.confidence * 100).toFixed(1)}%</span>
                  <span className={`severity-badge severity-${vitalsResult.severity?.toLowerCase()}`}>
                    {vitalsResult.severity}
                  </span>
                </div>

                {vitalsResult.vitals_details && (
                  <div className="vitals-details">
                    <h4>Vital Signs Assessment:</h4>
                    <div className="vitals-grid">
                      {vitalsResult.vitals_details.vital_analysis && Object.entries(vitalsResult.vitals_details.vital_analysis).map(([key, value]) => (
                        <div key={key} className="vital-item">
                          <span className="vital-label">{key.replace('_', ' ').toUpperCase()}:</span>
                          <span className={`vital-status status-${value.status?.toLowerCase()}`}>
                            {value.status} {value.value && `(${value.value})`}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {vitalsResult.recommendations && (
                  <div className="recommendations">
                    <h4>Clinical Recommendations:</h4>
                    <ul>
                      {vitalsResult.recommendations.map((rec, index) => (
                        <li key={index}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {vitalsResult.reasoning && (
                  <div className="clinical-reasoning">
                    <h4>Clinical Reasoning:</h4>
                    <p>{vitalsResult.reasoning}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {symptomsResult && (
            <div className="card agent-result-card fade-in">
              <div className="card-header">
                <h2 className="card-title">🔍 Symptoms Analysis Results</h2>
                <div className="agent-badge symptoms-badge">AI Symptoms Agent</div>
              </div>
              <div className="agent-result-content">
                <div className="symptoms-detected">
                  <h4>Detected Symptoms:</h4>
                  <div className="symptoms-list">
                    {symptomsResult.symptoms_detected.map((symptom, index) => (
                      <span key={index} className="symptom-tag">
                        {symptom.replace('_', ' ').toUpperCase()}
                        {(symptomsResult.symptom_analysis?.extracted_symptoms?.[symptom] ||
                          symptomsResult.confidence_scores?.[symptom]) && (
                          <span className="symptom-confidence">
                            {((symptomsResult.symptom_analysis?.extracted_symptoms?.[symptom] ||
                               symptomsResult.confidence_scores?.[symptom]) * 100).toFixed(0)}%
                          </span>
                        )}
                      </span>
                    ))}
                  </div>
                  {symptomsResult.symptom_analysis && (
                    <div className="symptom-analysis-details">
                      <p className="extraction-confidence">
                        Extraction Confidence: {(symptomsResult.symptom_analysis.extraction_confidence * 100).toFixed(1)}%
                      </p>
                    </div>
                  )}
                </div>

                {/* Primary Diagnosis */}
                {symptomsResult.primary_diagnosis && (
                  <div className="primary-diagnosis">
                    <h4>Primary Diagnosis:</h4>
                    <div className="diagnosis-item">
                      <div className="diagnosis-name">{symptomsResult.primary_diagnosis}</div>
                      <div className="diagnosis-confidence">
                        <div className="confidence-bar">
                          <div
                            className="confidence-fill"
                            style={{ width: `${(symptomsResult.confidence * 100)}%` }}
                          ></div>
                        </div>
                        <span className="confidence-text">{(symptomsResult.confidence * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                )}

                <div className="urgency-assessment">
                  <h4>Urgency Assessment:</h4>
                  <div className="urgency-container">
                    <span className={`urgency-badge urgency-${symptomsResult.urgency_level.toLowerCase()}`}>
                      {symptomsResult.urgency_level}
                    </span>
                    {symptomsResult.clinical_assessment?.severity_assessment && (
                      <span className={`severity-badge severity-${symptomsResult.clinical_assessment.severity_assessment.toLowerCase()}`}>
                        {symptomsResult.clinical_assessment.severity_assessment}
                      </span>
                    )}
                    {symptomsResult.urgency_recommendation && (
                      <p className="urgency-recommendation">{symptomsResult.urgency_recommendation}</p>
                    )}
                  </div>
                </div>

                {/* Differential Diagnoses */}
                {symptomsResult.differential_diagnoses && symptomsResult.differential_diagnoses.length > 0 && (
                  <div className="differential-diagnoses">
                    <h4>Differential Diagnoses:</h4>
                    <div className="diagnoses-list">
                      {symptomsResult.differential_diagnoses.slice(0, 3).map((diagnosis, index) => (
                        <div key={index} className="diagnosis-item">
                          <div className="diagnosis-name">{diagnosis.condition}</div>
                          <div className="diagnosis-confidence">
                            <div className="confidence-bar">
                              <div
                                className="confidence-fill"
                                style={{ width: `${(diagnosis.confidence * 100)}%` }}
                              ></div>
                            </div>
                            <span className="confidence-text">{(diagnosis.confidence * 100).toFixed(1)}%</span>
                          </div>
                          {diagnosis.description && (
                            <span className="diagnosis-description">{diagnosis.description}</span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Enhanced Recommendations */}
                {symptomsResult.recommendations && symptomsResult.recommendations.length > 0 && (
                  <div className="enhanced-recommendations">
                    <h4>Clinical Recommendations:</h4>
                    <ul className="recommendations-list">
                      {symptomsResult.recommendations.slice(0, 4).map((recommendation, index) => (
                        <li key={index} className="recommendation-item">{recommendation}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {symptomsResult.ai_analysis && (
                  <div className="ai-analysis">
                    <h4>AI Analysis:</h4>
                    <p>{symptomsResult.ai_analysis}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {xrayResult && (
            <div className="card agent-result-card fade-in">
              <div className="card-header">
                <h2 className="card-title">X-Ray Analysis Results</h2>
                <div className="agent-badge xray-badge">Ollama + GradCAM</div>
              </div>
              <div className="agent-result-content">
                <div className="primary-finding">
                  <h4>Primary Finding:</h4>
                  <p>{xrayResult.primary_finding}</p>
                  <span className="confidence">Confidence: {(xrayResult.confidence * 100).toFixed(1)}%</span>
                </div>
                {xrayResult.clinical_explanation && (
                  <div className="clinical-explanation">
                    <h4>Clinical Interpretation:</h4>
                    <p>{xrayResult.clinical_explanation}</p>
                  </div>
                )}
                {(xrayResult.gradcam_b64 || (xrayResult.gradcam_visualization && xrayResult.gradcam_visualization.base64_image)) && (
                  <div className="gradcam-visualization">
                    <h4>GradCAM Heatmap:</h4>
                    <img
                      src={`data:image/png;base64,${xrayResult.gradcam_b64 || xrayResult.gradcam_visualization.base64_image}`}
                      alt="GradCAM Heatmap"
                      className="gradcam-image"
                    />
                    <p className="gradcam-description">
                      Red/yellow areas indicate regions of interest identified by the AI model for: {xrayResult.gradcam_visualization?.target_pathology || xrayResult.primary_finding}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}



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
            <button className="btn btn-primary" onClick={handleNewAnalysis}>
              New Analysis
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SupervisorResultsPage;
