import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Analysis = () => {
  const navigate = useNavigate();
  const [usePreviousTermData, setUsePreviousTermData] = useState(false);
  const [currentFile, setCurrentFile] = useState(null);
  const [historicalFile, setHistoricalFile] = useState(null);
  const [maxMarks, setMaxMarks] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleCurrentFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === "text/csv") {
      setCurrentFile(file);
    } else {
      alert("Please select a valid CSV file.");
      setCurrentFile(null);
    }
  };

  const handleHistoricalFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === "text/csv") {
      setHistoricalFile(file);
    } else {
      alert("Please select a valid CSV file.");
      setHistoricalFile(null);
    }
  };

  const handleMaxMarksChange = (e) => {
    const value = e.target.value;
    if (value === "" || (Number(value) > 0 && /^\d+$/.test(value))) {
      setMaxMarks(value);
    } else {
      alert("Please enter a valid number greater than 0.");
    }
  };

  const handleGenerate = async () => {
    if (!currentFile || !maxMarks) {
      alert("Please provide all required inputs");
      return;
    }

    if (usePreviousTermData && !historicalFile) {
      alert("Please provide historical data file");
      return;
    }

    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append('currentFile', currentFile);
      formData.append('maxMarks', maxMarks);
      formData.append('useHistorical', usePreviousTermData ? "true" : "false");
      
      if (usePreviousTermData && historicalFile) {
        formData.append('historicalFile', historicalFile);
      }

      const response = await fetch('http://localhost:5000/api/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data = await response.json();
      localStorage.setItem('analysisResults', JSON.stringify(data));
      navigate('/analysis/aoutput');
    } catch (error) {
      alert('Error during analysis: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="main-content">
      <div className="header">
        <button onClick={() => navigate("/")} className="back-button">← Back</button>
        <h1>Analysis</h1>
      </div>
      <div className="time-table-container">
        <div className="time-table-item">
          <label className="label">Enter the data file in csv format:</label>
          <div className="file-input-container">
            <label className={`action-button ${currentFile ? 'file-selected' : ''}`}>
              <input
                type="file"
                accept=".csv"
                style={{ display: "none" }}
                onChange={handleCurrentFileChange}
              />
              <span role="img" aria-label="upload" className="upload-icon">
                📤
              </span>{" "}
              Select
            </label>
            <span className="file-status">
              {currentFile ? currentFile.name : "No file selected"}
            </span>
          </div>
        </div>

        <div className="time-table-item1">
          <label className="label">Enter maximum marks per subject:</label>
          <input
            type="number"
            value={maxMarks}
            onChange={handleMaxMarksChange}
            className="max-marks-input"
            placeholder="Enter a number > 0"
          />
        </div>

        <div className="checkbox-section">
          <div className="time-table-item">
            <label className="label">
              <input
                type="checkbox"
                checked={usePreviousTermData}
                onChange={(e) => setUsePreviousTermData(e.target.checked)}
              />
              Use data of previous term&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            </label>
            <label
              className={`action-button ${!usePreviousTermData ? "disabled" : ""} ${historicalFile ? 'file-selected' : ''}`}
            >
              <input
                type="file"
                accept=".csv"
                style={{ display: "none" }}
                disabled={!usePreviousTermData}
                onChange={handleHistoricalFileChange}
              />
              <span
                role="img"
                aria-label={usePreviousTermData ? "upload" : "disabled"}
                className="upload-icon"
              >
                📤
              </span>{" "}
              Select
            </label>
            <span className="file-status">
              {historicalFile ? historicalFile.name : "No file selected"}
            </span>
          </div>
        </div>

        <div className="generate-button-section">
          <button
            onClick={handleGenerate}
            disabled={isLoading}
            className="generate-button"
          >
            {isLoading ? "Generating..." : "GENERATE"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Analysis;