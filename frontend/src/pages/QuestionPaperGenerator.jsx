import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";

const QuestionPaperGenerator = () => {
  const navigate = useNavigate();
  const [mcqFields, setMcqFields] = useState([{ number: 0, marks: 0 }]);
  const [descFields, setDescFields] = useState([{ number: 0, marks: 0 }]);
  const [scenarioFields, setScenarioFields] = useState([{ number: 0, marks: 0 }]);
  const [fileSelected, setFileSelected] = useState(false);
  const [pastedText, setPastedText] = useState("");
  const fileInputRef = useRef(null);

// QuestionPaperGenerator.jsx modifications
const handleGenerate = async () => {
  const formData = new FormData();
  const config = {
      mcq: mcqFields.filter(f => f.number > 0).map(f => ({ marks: f.marks, count: f.number })),
      descriptive: descFields.filter(f => f.number > 0).map(f => ({ marks: f.marks, count: f.number })),
      scenario: scenarioFields.filter(f => f.number > 0).map(f => ({ marks: f.marks, count: f.number }))
  };

  // Add inputs to form data
  formData.append('config', JSON.stringify(config));
  
  if (fileSelected && fileInputRef.current.files[0]) {
      formData.append('pdfFile', fileInputRef.current.files[0]);
  } else if (pastedText) {
      formData.append('textInput', pastedText);
  }

  try {
      const response = await fetch('http://localhost:5000/api/generate-question-paper', {
          method: 'POST',
          body: formData
      });
      
      const result = await response.json();
      if (result.error) throw new Error(result.error);
      
      navigate('/question-paper-generator/qoutput', {
          state: {
              questionPaper: result.questionPaper,
              answerKey: result.answerKey
          }
      });
  } catch (error) {
      console.error('Generation failed:', error);
      alert(`Generation failed: ${error.message}`);
  }
};


  // Field management functions remain unchanged
  const addMcqField = () => {
    setMcqFields([...mcqFields, { number: 0, marks: 0 }]);
  };

  const addDescField = () => {
    setDescFields([...descFields, { number: 0, marks: 0 }]);
  };

  const addScenarioField = () => {
    setScenarioFields([...scenarioFields, { number: 0, marks: 0 }]);
  };

  const handleInputChange = (index, value, type, section) => {
    const fields =
      section === "mcq"
        ? [...mcqFields]
        : section === "desc"
        ? [...descFields]
        : [...scenarioFields];

    fields[index][type] = Math.max(0, parseInt(value) || 0);

    if (section === "mcq") setMcqFields(fields);
    else if (section === "desc") setDescFields(fields);
    else setScenarioFields(fields);
  };

  // New file/text input handlers
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFileSelected(true);
      setPastedText(""); // Clear text area
      console.log("Selected PDF file:", file.name);
    }
  };

  const handleTextChange = (e) => {
    const text = e.target.value;
    setPastedText(text);
    
    if (text.length > 0) {
      setFileSelected(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = ""; // Clear file input
      }
    }
  };

  return (
    <div className="main-content">
      {/* Title Section */}
      <div className="title-bar">
        <button className="back-button" onClick={() => navigate(-1)}>
          &#8592; Back
        </button>
        <h1 className="title">Question Paper Generator</h1>
      </div>

      {/* File Input and Text Paste Section */}
      <div className="file-input-section">
        <label className="label">Choose PDF file:</label>
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          style={{ display: "none" }}
          id="file-upload"
          ref={fileInputRef}
        />
        <label 
          htmlFor="file-upload" 
          className={`action-button ${pastedText ? "disabled" : ""}`}
        >
          <span role="img" aria-label="upload" className="upload-icon">
            📤
          </span>{" "}
          Select
        </label>
        <span className="separator">or</span>
        <label className="label">Paste text:</label>
        <textarea 
          placeholder="Enter text here..." 
          className="text-area"
          value={pastedText}
          onChange={handleTextChange}
          disabled={fileSelected}
        />
      </div>

      {/* MCQ Section */}
      <div className="section">
        <button onClick={addMcqField} className="add-button">
          + Add
        </button>
        {mcqFields.map((field, index) => (
          <div key={index} className="field-row">
            <label className="label">Number of MCQ:</label>
            <input
              type="number"
              value={field.number}
              onChange={(e) =>
                handleInputChange(index, e.target.value, "number", "mcq")
              }
              className="input"
            />
            <label className="label">Marks per MCQ:</label>
            <input
              type="number"
              value={field.marks}
              onChange={(e) =>
                handleInputChange(index, e.target.value, "marks", "mcq")
              }
              className="input"
            />
          </div>
        ))}
      </div>

      {/* Descriptive Section */}
      <div className="section">
        <button onClick={addDescField} className="add-button">
          + Add
        </button>
        {descFields.map((field, index) => (
          <div key={index} className="field-row">
            <label className="label">Number of Descriptive:</label>
            <input
              type="number"
              value={field.number}
              onChange={(e) =>
                handleInputChange(index, e.target.value, "number", "desc")
              }
              className="input"
            />
            <label className="label">Marks per Descriptive:</label>
            <input
              type="number"
              value={field.marks}
              onChange={(e) =>
                handleInputChange(index, e.target.value, "marks", "desc")
              }
              className="input"
            />
          </div>
        ))}
      </div>

      {/* Scenario-based Section */}
      <div className="section">
        <button onClick={addScenarioField} className="add-button">
          + Add
        </button>
        {scenarioFields.map((field, index) => (
          <div key={index} className="field-row">
            <label className="label">Number of Scenario-based:</label>
            <input
              type="number"
              value={field.number}
              onChange={(e) =>
                handleInputChange(index, e.target.value, "number", "scenario")
              }
              className="input"
            />
            <label className="label">Marks per Scenario:</label>
            <input
              type="number"
              value={field.marks}
              onChange={(e) =>
                handleInputChange(index, e.target.value, "marks", "scenario")
              }
              className="input"
            />
          </div>
        ))}
      </div>

      {/* Generate Button */}
      <button onClick={handleGenerate} className="generate-button">
        GENERATE
      </button>
    </div>
  );
};

export default QuestionPaperGenerator;
