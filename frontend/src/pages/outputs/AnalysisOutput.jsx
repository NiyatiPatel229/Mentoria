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
    <div className='main-content'>
      <div className="header">
        <button onClick={() => navigate('/analysis')} className="back-button">← Back</button>
        <h1>Analysis Results</h1>
      </div>
      <div className="content">
        {results ? (
          <div className="results-container">
            {/* Reports Section */}
            <div className="report-section">
              <h2>Analysis Reports</h2>
              <iframe
                src={`http://localhost:5000/reports/${results.reports.current}?t=${new Date().getTime()}`}
                style={{ width: '100%', height: '600px', border: 'none' }}
                title="Current Term Report"
              />
              
              {results.reports.historical && (
                <iframe
                  src={`http://localhost:5000/reports/${results.reports.historical}`}
                  style={{ width: '100%', height: '600px', border: 'none' }}
                  title="Historical Term Report"
                />
              )}
              
              {results.reports.comparison && (
                <iframe
                  src={`http://localhost:5000/reports/${results.reports.comparison}`}
                  style={{ width: '100%', height: '600px', border: 'none' }}
                  title="Comparison Report"
                />
              )}
            </div>

            {/* Visualizations Section */}
            {results.reports.visualizations && (
              <div className="visualizations-section">
                <h2>Performance Visualizations</h2>
                <div className="visualization-grid">
                  {results.reports.visualizations.map((vizFile, index) => (
                    <div key={index} className="visualization-item">
                      <h3>{vizFile.split('.')[0].replace(/_/g, ' ')}</h3>
                      <iframe
                        src={`http://localhost:5000/reports/${vizFile}`}
                        style={{ width: '100%', height: '550px', border: 'none' }}
                        title={vizFile}
                      />
                    </div>
                  ))}
                </div>
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
