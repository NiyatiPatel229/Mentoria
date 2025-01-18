import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Analysis = () => {
  const navigate = useNavigate();
  const [usePreviousTermData, setUsePreviousTermData] = useState(false);

  return (
    <div className="main-content">
      <div className="header">
        <button onClick={() => navigate("/")} className="back-button">← Back</button>
        <h1>Analysis</h1>
      </div>
      <div className="content">
        <div className="input-section">
          <label className="label">
            Enter the data file in csv format:
          </label>
          <button className="action-button">
            <span role="img" aria-label="upload" className="upload-icon">
              📤
            </span>{" "}
            Select
          </button>
        </div>
        <div className="checkbox-section">
          <label className="label">
            <input
              type="checkbox"
              checked={usePreviousTermData}
              onChange={(e) => setUsePreviousTermData(e.target.checked)}
            />
            Use data of previous term&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
          </label>
          <button
            className={`action-button ${!usePreviousTermData ? "disabled" : ""}`}
            disabled={!usePreviousTermData}
          >
            <span
              role="img"
              aria-label={usePreviousTermData ? "upload" : "disabled"}
              className="upload-icon"
            >
              {usePreviousTermData ? "📤" : "📤"}
            </span>{" "}
            Select
          </button>
        </div>
        <div className="generate-button-section">
          <button className="generate-button">GENERATE</button>
        </div>
      </div>
    </div>
  );
};

export default Analysis;
