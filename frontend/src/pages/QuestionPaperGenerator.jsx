import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const QuestionPaperGenerator = () => {
  const navigate = useNavigate();
  const [mcqFields, setMcqFields] = useState([{ number: 0, marks: 0 }]);
  const [descFields, setDescFields] = useState([{ number: 0, marks: 0 }]);
  const [scenarioFields, setScenarioFields] = useState([{ number: 0, marks: 0 }]);

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

    fields[index][type] = Math.max(0, parseInt(value) || 0); // Prevent values less than 0

    if (section === "mcq") setMcqFields(fields);
    else if (section === "desc") setDescFields(fields);
    else setScenarioFields(fields);
  };

  return (
    <div className="question-paper-generator">
      {/* Title Section */}
      <div className="title-bar">
        <button className="back-button" onClick={() => navigate(-1)}>
          &#8592; Back
        </button>
        <h1 className="title">Question Paper Generator</h1>
      </div>

      {/* File Input and Text Paste Section */}
      <div className="file-input-section">
        <label className="label">Choose file :</label>
        <button className="button">
          <span role="img" aria-label="upload" className="upload-icon">
            📤
          </span>{" "}
          Select
        </button>
        <span className="separator">or</span>
        <label className="label">Paste text :</label>
        <textarea placeholder="Enter text" className="text-area" />
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
            <label className="label">Marks of MCQ:</label>
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
            <label className="label">Marks of Descriptive:</label>
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
            <label className="label">Marks of Scenario-based:</label>
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
      <button className="generate-button">GENERATE</button>
    </div>
  );
};

export default QuestionPaperGenerator;
