import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/DiagnosisMethod.css';
import '../styles/SupervisorResults.css';

const DiagnosisMethodPage = () => {
  const navigate = useNavigate();
  
  // State for file upload and analysis
  const [uploadStatus, setUploadStatus] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleManualEntry = () => {
    navigate('/patient-form');
  };

  // File selection and automatic upload handler
  const handleFileSelection = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setIsProcessing(true);
    setUploadStatus(`Uploading ${file.name}...`);
    setAnalysisResult(null);

    try {
      const response = await fetch("http://localhost:8001/analyze", {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const { job_id } = await response.json();
      setUploadStatus("Processing medical data with AI agents...");
      pollAnalysisResults(job_id);
    } catch (error) {
      setUploadStatus("Upload failed: " + error.message);
      setIsProcessing(false);
    }
  };

  // Polling function for analysis results
  const pollAnalysisResults = async (jobId) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`http://localhost:8001/results/${jobId}`);
        const data = await response.json();
        
        if (data.status === "complete") {
          clearInterval(pollInterval);
          setAnalysisResult(data.result);
          setUploadStatus("Analysis complete!");
          setIsProcessing(false);
        } else if (data.status === "failed") {
          clearInterval(pollInterval);
          setUploadStatus("Analysis failed: " + (data.result?.error || "Unknown error"));
          setIsProcessing(false);
        }
        // Continue polling if status is "processing"
      } catch (error) {
        clearInterval(pollInterval);
        setUploadStatus("Error checking results: " + error.message);
        setIsProcessing(false);
      }
    }, 3000);
  };

  const handleBackToHome = () => {
    navigate('/');
  };

  return (
    <div className="diagnosis-method-page">
      {/* Background Elements */}
      <div className="medical-grid"></div>
      
      {/* Floating DNA Helixes */}
      <div className="floating-particles">
        <div className="particle particle-1"></div>
        <div className="particle particle-2"></div>
        <div className="particle particle-3"></div>
        <div className="particle particle-4"></div>
        <div className="particle particle-5"></div>
        <div className="particle particle-6"></div>
      </div>

      <div className="method-container">
        <div className="method-content">
          <div className="method-header">
            <h1>Choose Diagnosis Method</h1>
            <p>Select how you would like to provide medical information for analysis</p>
          </div>

          <div className="method-options">
            {/* Manual Entry Option */}
            <div className="method-card">
              <div className="method-icon">
                <svg width="60" height="60" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.89 22 5.99 22H18C19.1 22 20 21.1 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" fill="none"/>
                  <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" fill="none"/>
                  <path d="M16 13H8" stroke="currentColor" strokeWidth="2"/>
                  <path d="M16 17H8" stroke="currentColor" strokeWidth="2"/>
                  <path d="M10 9H9H8" stroke="currentColor" strokeWidth="2"/>
                </svg>
              </div>
              <h3>Manual Entry</h3>
              <p>Enter patient information, vitals, symptoms, and upload X-rays manually through our guided form</p>
              <button 
                className="btn btn-primary cta-button"
                onClick={handleManualEntry}
              >
                Enter Manually
              </button>
            </div>

            {/* File Upload Option */}
            <div className="method-card">
              <div className="method-icon">
                <svg width="60" height="60" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M21 15V19C21 20.1 20.1 21 19 21H5C3.9 21 3 20.1 3 19V15" stroke="currentColor" strokeWidth="2"/>
                  <path d="M17 8L12 3L7 8" stroke="currentColor" strokeWidth="2"/>
                  <path d="M12 3V15" stroke="currentColor" strokeWidth="2"/>
                </svg>
              </div>
              <h3>Upload Medical File</h3>
              <p>Upload medical files (PDF reports, JSON/CSV data, X-ray images) for automatic AI analysis</p>
              
              <div className="upload-section">
                <input
                  type="file"
                  id="medicalFileInput"
                  accept=".pdf,.json,.csv,.png,.dcm,.jpg,.jpeg"
                  style={{ display: 'none' }}
                  onChange={handleFileSelection}
                  disabled={isProcessing}
                />
                <button
                  type="button"
                  onClick={() => document.getElementById('medicalFileInput').click()}
                  disabled={isProcessing}
                  className="btn btn-primary cta-button"
                >
                  {isProcessing ? 'Processing...' : 'Select Medical File'}
                </button>
              </div>

              {uploadStatus && (
                <div className="status-message">
                  {uploadStatus}
                </div>
              )}
            </div>
          </div>

          {/* Back Button */}
          <div className="back-section">
            <button 
              className="btn btn-outline back-button"
              onClick={handleBackToHome}
            >
              ← Back to Home
            </button>
          </div>
        </div>
      </div>

      {/* Enhanced Analysis Results Section */}
      {analysisResult && (
        <div className="analysis-results-section">
          <div className="results-container">
            <div className="results-header">
              <h1 className="results-title">
                DiagnoNet ANALYSIS COMPLETE
              </h1>
              <p className="results-subtitle">
                Comprehensive AI-Assisted Diagnosis Report
              </p>
            </div>

            <div className="results-content">
              {analysisResult.error ? (
                <div className="card error-card">
                  <div className="card-header">
                    <h2 className="card-title" style={{ color: '#E61A4F' }}>Analysis Error</h2>
                  </div>
                  <div className="error-content">
                    <p className="error-message">{analysisResult.error}</p>
                  </div>
                </div>
              ) : (
                <>
                  {/* File Summary Card */}
                  <div className="card patient-summary-card">
                    <div className="card-header">
                      <h2 className="card-title">File Analysis Summary</h2>
                      <div className="confidence-badge">
                        <span className="confidence-label">Analysis Status</span>
                        <span className="confidence-value">Complete</span>
                      </div>
                    </div>
                    <div className="patient-details">
                      <div className="detail-item">
                        <span className="detail-label">File:</span>
                        <span className="detail-value" title={analysisResult.filename}>
                          {analysisResult.filename}
                        </span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">Analysis Time:</span>
                        <span className="detail-value">
                          {new Date(analysisResult.analysis_timestamp).toLocaleString()}
                        </span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">Agents Used:</span>
                        <span className="detail-value">
                          {[
                            analysisResult.vitals_analysis && 'Vitals',
                            analysisResult.symptoms_analysis && 'Symptoms',
                            analysisResult.xray_analysis && 'X-ray'
                          ].filter(Boolean).join(', ')}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Multi-Agent Summary */}
                  {analysisResult.multi_agent_summary && (
                    <div className="card supervisor-analysis-card">
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
                            <p>{analysisResult.multi_agent_summary.clinical_summary}</p>

                            <h4>Overall Assessment:</h4>
                            <p>{analysisResult.multi_agent_summary.overall_assessment}</p>

                            <div className="summary-metrics">
                              <div className="metric">
                                <span className="metric-label">Urgency Level:</span>
                                <span className={`metric-value urgency-${analysisResult.multi_agent_summary.urgency_level.toLowerCase()}`}>
                                  {analysisResult.multi_agent_summary.urgency_level}
                                </span>
                              </div>
                              <div className="metric">
                                <span className="metric-label">Confidence:</span>
                                <span className="metric-value">
                                  {(analysisResult.multi_agent_summary.confidence_score * 100).toFixed(1)}%
                                </span>
                              </div>
                            </div>

                            {analysisResult.multi_agent_summary.key_findings && (
                              <>
                                <h4>Key Findings:</h4>
                                <ul className="findings-list">
                                  {analysisResult.multi_agent_summary.key_findings.map((finding, index) => (
                                    <li key={index}>{finding}</li>
                                  ))}
                                </ul>
                              </>
                            )}

                            {analysisResult.multi_agent_summary.recommendations && (
                              <>
                                <h4>Recommendations:</h4>
                                <ul className="recommendations-list">
                                  {analysisResult.multi_agent_summary.recommendations.map((rec, index) => (
                                    <li key={index}>{rec}</li>
                                  ))}
                                </ul>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Individual Agent Results */}
                  {analysisResult.vitals_analysis && (
                    <div className="card agent-result-card">
                      <div className="card-header">
                        <h2 className="card-title">🩺 Vitals Analysis Results</h2>
                        <div className="agent-badge vitals-badge">BioGPT Agent</div>
                      </div>
                      <div className="agent-result-content">
                        <div className="primary-diagnosis">
                          <h4>Primary Diagnosis:</h4>
                          <p>{analysisResult.vitals_analysis.primary_diagnosis}</p>
                          <span className="confidence">
                            Confidence: {(analysisResult.vitals_analysis.confidence * 100).toFixed(1)}%
                          </span>
                          {analysisResult.vitals_analysis.severity && (
                            <span className={`severity-badge severity-${analysisResult.vitals_analysis.severity.toLowerCase()}`}>
                              {analysisResult.vitals_analysis.severity}
                            </span>
                          )}
                        </div>

                        {analysisResult.vitals_analysis.vital_analysis && (
                          <div className="vitals-details">
                            <h4>Vital Signs Assessment:</h4>
                            <div className="vitals-grid">
                              {Object.entries(analysisResult.vitals_analysis.vital_analysis).map(([key, value]) => (
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

                        {analysisResult.vitals_analysis.recommendations && (
                          <div className="recommendations">
                            <h4>Clinical Recommendations:</h4>
                            <ul>
                              {analysisResult.vitals_analysis.recommendations.map((rec, index) => (
                                <li key={index}>{rec}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {analysisResult.vitals_analysis.reasoning && (
                          <div className="clinical-reasoning">
                            <h4>Clinical Reasoning:</h4>
                            <p>{analysisResult.vitals_analysis.reasoning}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {analysisResult.symptoms_analysis && (
                    <div className="card agent-result-card">
                      <div className="card-header">
                        <h2 className="card-title">🔍 Symptoms Analysis Results</h2>
                        <div className="agent-badge symptoms-badge">AI Symptoms Agent</div>
                      </div>
                      <div className="agent-result-content">
                        {analysisResult.symptoms_analysis.symptoms_detected && (
                          <div className="symptoms-detected">
                            <h4>Detected Symptoms:</h4>
                            <div className="symptoms-list">
                              {analysisResult.symptoms_analysis.symptoms_detected.map((symptom, index) => (
                                <span key={index} className="symptom-tag">
                                  {symptom.replace('_', ' ').toUpperCase()}
                                  {analysisResult.symptoms_analysis.symptom_analysis?.extracted_symptoms?.[symptom] && (
                                    <span className="symptom-confidence">
                                      {(analysisResult.symptoms_analysis.symptom_analysis.extracted_symptoms[symptom] * 100).toFixed(0)}%
                                    </span>
                                  )}
                                </span>
                              ))}
                            </div>
                            {analysisResult.symptoms_analysis.symptom_analysis && (
                              <div className="symptom-analysis-details">
                                <p className="extraction-confidence">
                                  Extraction Confidence: {(analysisResult.symptoms_analysis.symptom_analysis.extraction_confidence * 100).toFixed(1)}%
                                </p>
                              </div>
                            )}
                          </div>
                        )}

                        {analysisResult.symptoms_analysis.primary_diagnosis && (
                          <div className="primary-diagnosis">
                            <h4>Primary Diagnosis:</h4>
                            <div className="diagnosis-item">
                              <div className="diagnosis-name">{analysisResult.symptoms_analysis.primary_diagnosis}</div>
                              <div className="diagnosis-confidence">
                                <div className="confidence-bar">
                                  <div
                                    className="confidence-fill"
                                    style={{ width: `${(analysisResult.symptoms_analysis.confidence * 100)}%` }}
                                  ></div>
                                </div>
                                <span className="confidence-text">{(analysisResult.symptoms_analysis.confidence * 100).toFixed(1)}%</span>
                              </div>
                            </div>
                          </div>
                        )}

                        {analysisResult.symptoms_analysis.urgency_level && (
                          <div className="urgency-assessment">
                            <h4>Urgency Assessment:</h4>
                            <div className="urgency-container">
                              <span className={`urgency-badge urgency-${analysisResult.symptoms_analysis.urgency_level.toLowerCase()}`}>
                                {analysisResult.symptoms_analysis.urgency_level}
                              </span>
                              {analysisResult.symptoms_analysis.urgency_recommendation && (
                                <p className="urgency-recommendation">{analysisResult.symptoms_analysis.urgency_recommendation}</p>
                              )}
                            </div>
                          </div>
                        )}

                        {analysisResult.symptoms_analysis.differential_diagnoses && analysisResult.symptoms_analysis.differential_diagnoses.length > 0 && (
                          <div className="differential-diagnoses">
                            <h4>Differential Diagnoses:</h4>
                            <div className="diagnoses-list">
                              {analysisResult.symptoms_analysis.differential_diagnoses.slice(0, 3).map((diagnosis, index) => (
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

                        {analysisResult.symptoms_analysis.recommendations && analysisResult.symptoms_analysis.recommendations.length > 0 && (
                          <div className="recommendations">
                            <h4>Clinical Recommendations:</h4>
                            <ul>
                              {analysisResult.symptoms_analysis.recommendations.map((rec, index) => (
                                <li key={index}>{rec}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {analysisResult.symptoms_analysis.clinical_reasoning && (
                          <div className="clinical-reasoning">
                            <h4>Clinical Reasoning:</h4>
                            <p>{analysisResult.symptoms_analysis.clinical_reasoning}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {analysisResult.xray_analysis && (
                    <div className="card agent-result-card">
                      <div className="card-header">
                        <h2 className="card-title">🫁 X-ray Analysis Results</h2>
                        <div className="agent-badge xray-badge">TorchXRayVision Agent</div>
                      </div>
                      <div className="agent-result-content">
                        <div className="primary-diagnosis">
                          <h4>Primary Finding:</h4>
                          <p>{analysisResult.xray_analysis.primary_finding}</p>
                          <span className="confidence">
                            Confidence: {(analysisResult.xray_analysis.confidence * 100).toFixed(1)}%
                          </span>
                          {analysisResult.xray_analysis.severity && (
                            <span className={`severity-badge severity-${analysisResult.xray_analysis.severity.toLowerCase()}`}>
                              {analysisResult.xray_analysis.severity}
                            </span>
                          )}
                        </div>

                        {analysisResult.xray_analysis.findings && analysisResult.xray_analysis.findings.length > 0 && (
                          <div className="xray-findings">
                            <h4>Detailed Findings:</h4>
                            <div className="findings-grid">
                              {analysisResult.xray_analysis.findings.map((finding, index) => (
                                <div key={index} className="finding-item">
                                  <div className="finding-name">{finding.pathology}</div>
                                  <div className="finding-confidence">
                                    <div className="confidence-bar">
                                      <div
                                        className="confidence-fill"
                                        style={{ width: `${(finding.confidence * 100)}%` }}
                                      ></div>
                                    </div>
                                    <span className="confidence-text">{(finding.confidence * 100).toFixed(1)}%</span>
                                  </div>
                                  {finding.severity && (
                                    <span className={`severity-indicator severity-${finding.severity.toLowerCase()}`}>
                                      {finding.severity}
                                    </span>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {analysisResult.xray_analysis.clinical_explanation && (
                          <div className="clinical-reasoning">
                            <h4>Clinical Explanation:</h4>
                            <p>{analysisResult.xray_analysis.clinical_explanation}</p>
                          </div>
                        )}

                        {analysisResult.xray_analysis.recommendations && analysisResult.xray_analysis.recommendations.length > 0 && (
                          <div className="recommendations">
                            <h4>Clinical Recommendations:</h4>
                            <ul>
                              {analysisResult.xray_analysis.recommendations.map((rec, index) => (
                                <li key={index}>{rec}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {analysisResult.xray_analysis.gradcam_visualization && analysisResult.xray_analysis.gradcam_visualization.available && (
                          <div className="gradcam-visualization">
                            <h4>AI Attention Map (GradCAM):</h4>
                            <p className="gradcam-description">
                              Areas highlighted in red show where the AI focused its attention for the diagnosis of: {analysisResult.xray_analysis.gradcam_visualization.target_pathology}
                            </p>
                            <div className="gradcam-image-container">
                              <img
                                src={`data:image/png;base64,${analysisResult.xray_analysis.gradcam_visualization.base64_image}`}
                                alt="GradCAM Visualization"
                                className="gradcam-image"
                              />
                            </div>
                          </div>
                        )}

                        <div className="technical-details">
                          <h4>Technical Details:</h4>
                          <div className="tech-info">
                            <span className="tech-label">Model:</span>
                            <span className="tech-value">TorchXRayVision DenseNet121</span>
                          </div>
                          <div className="tech-info">
                            <span className="tech-label">Image Quality:</span>
                            <span className="tech-value">{analysisResult.xray_analysis.technical_quality || 'Good'}</span>
                          </div>
                          <div className="tech-info">
                            <span className="tech-label">Pathologies Analyzed:</span>
                            <span className="tech-value">{analysisResult.xray_analysis.pathology_count || 'Multiple'}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="results-actions">
                    <button
                      className="btn btn-primary cta-button"
                      onClick={() => window.print()}
                    >
                      Print Report
                    </button>
                    <button
                      className="btn btn-primary cta-button"
                      onClick={() => {
                        setAnalysisResult(null);
                        setUploadStatus(null);
                        setIsProcessing(false);
                      }}
                    >
                      New Analysis
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DiagnosisMethodPage;
