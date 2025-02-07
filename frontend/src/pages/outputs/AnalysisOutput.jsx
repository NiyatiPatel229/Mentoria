import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const AnalysisOutput = () => {
  const navigate = useNavigate();
  const [results, setResults] = useState(null);

  useEffect(() => {
    const storedResults = localStorage.getItem('analysisResults');
    if (storedResults) {
      setResults(JSON.parse(storedResults));
    }
  }, []);

  return (
    <div>
      <div className="navigation">
        <button onClick={() => navigate('/analysis')} className="back-button">← Back</button>
        <h1>Analysis Results</h1>
      </div>
      <div className="content">
        {results ? (
          <div className="results-container">
            {/* Current Term Results */}
            <div className="report-section">
              <h2>Current Term Analysis</h2>
              <iframe
                src="http://localhost:5000/reports/current_term_report.html"
                style={{ width: '100%', height: '600px', border: 'none' }}
                title="Current Term Report"
              />
            </div>

            {/* Show Historical Analysis if available */}
            {results.historical_insights && (
              <div className="report-section">
                <h2>Historical Term Analysis</h2>
                <iframe
                  src="http://localhost:5000/reports/historical_term_report.html"
                  style={{ width: '100%', height: '600px', border: 'none' }}
                  title="Historical Term Report"
                />
              </div>
            )}

            {/* Show Comparison if available */}
            {results.comparison_results && (
              <div className="report-section">
                <h2>Comparison Analysis</h2>
                <iframe
                  src="http://localhost:5000/reports/comparison_report.html"
                  style={{ width: '100%', height: '600px', border: 'none' }}
                  title="Comparison Report"
                />
              </div>
            )}
          </div>
        ) : (
          <p>Loading analysis results...</p>
        )}
      </div>
    </div>
  );
};

export default AnalysisOutput;