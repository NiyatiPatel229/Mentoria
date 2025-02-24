import React, { useState, useEffect,useRef, useLayoutEffect } from "react";
import { useNavigate } from "react-router-dom";


const TimeTableGenerator = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [formData, setFormData] = useState({
    num_days: 5,
    periods_per_day: 6,
    lunch_after_period: 3,
    classes: [],
    subjects: {},
    teachers: {},
    class_requirements: {}
  });

  // Step handlers
  const nextStep = () => setStep(prev => Math.min(prev + 1, 6));
  const prevStep = () => setStep(prev => Math.max(prev - 1, 1));

// Update the handleGenerate function
const handleGenerate = async () => {
  setLoading(true);
  setError("");
  try {
    // Convert class_requirements to backend format
    const backendData = {
      ...formData,
      class_requirements: Object.fromEntries(
        Object.entries(formData.class_requirements).map(([cls, subjects]) => [
          cls,
          Object.fromEntries(
            Object.entries(subjects).map(([subj, req]) => [
              subj,
              {
                teacher: req.teacher,
                lectures: req.lectures
              }
            ])
          )
        ])
      )
    };

    const response = await fetch('http://localhost:5000/api/generate-timetable', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(backendData)
    });

    const data = await response.json();
    if (data.status === 'success') {
      navigate('/time-table-generator/toutput', { 
        state: { 
          timetable: data.timetable,
          teachers: data.teachers,
          originalData: formData
        } 
      });
    } else {
      setError(data.message || 'Failed to generate timetable');
    }
  } catch (err) {
    setError('Network error occurred');
    console.error(err);
  } finally {
    setLoading(false);
  }
};

  // Step 1: Basic Structure
  const Step1 = () => (
    <div className="step-content">
      <h2>Step 1: Basic Structure</h2>
      <div className="form-group">
        <label>Number of Days (1-7):</label>
        <input
          type="number"
          min="1"
          max="7"
          value={formData.num_days}
          onChange={e => setFormData({
            ...formData,
            num_days: Math.min(7, Math.max(1, parseInt(e.target.value)))
          })}
        />
      </div>
      <div className="form-group">
        <label>Periods per Day:</label>
        <input
          type="number"
          min="1"
          value={formData.periods_per_day}
          onChange={e => setFormData({
            ...formData,
            periods_per_day: Math.max(1, parseInt(e.target.value))
          })}
        />
      </div>
      <div className="form-group">
        <label>Lunch After Period:</label>
        <input
          type="number"
          min="1"
          max={formData.periods_per_day}
          value={formData.lunch_after_period}
          onChange={e => setFormData({
            ...formData,
            lunch_after_period: Math.min(
              formData.periods_per_day,
              Math.max(1, parseInt(e.target.value))
            )
          })}
        />
      </div>
    </div>
  );

  // Step 2: Class Information
  const Step2 = () => {
    const [localClasses, setLocalClasses] = useState([...formData.classes]);
    const [activeIndex, setActiveIndex] = useState(null);
  
    // Sync local state with formData
    useEffect(() => {
      setLocalClasses([...formData.classes]);
    }, [formData.classes.length]);
  
    const handleClassUpdate = (index) => {
      const newName = localClasses[index].trim();
      if (!newName) return;
  
      setFormData(prev => {
        const updatedClasses = [...prev.classes];
        const oldName = updatedClasses[index];
        updatedClasses[index] = newName;
  
        const newRequirements = { ...prev.class_requirements };
        newRequirements[newName] = newRequirements[oldName] || {};
        if (oldName !== newName) delete newRequirements[oldName];
  
        return {
          ...prev,
          classes: updatedClasses,
          class_requirements: newRequirements
        };
      });
      setActiveIndex(null);
    };
  
    return (
      <div className="step-content">
        <h2>Step 2: Class Information</h2>
        <div className="form-group">
          <label>Number of Classes:</label>
          <input
            type="number"
            min="1"
            value={formData.classes.length}
            onChange={e => {
              const newCount = Math.max(1, parseInt(e.target.value) || 1);
              setFormData(prev => {
                const currentClasses = prev.classes;
                let newClasses;
  
                if (newCount > currentClasses.length) {
                  newClasses = [
                    ...currentClasses,
                    ...Array(newCount - currentClasses.length).fill("")
                  ];
                } else {
                  newClasses = currentClasses.slice(0, newCount);
                }
  
                const newRequirements = { ...prev.class_requirements };
                currentClasses
                  .filter((_, i) => i >= newCount)
                  .forEach(cls => delete newRequirements[cls]);
  
                return { ...prev, classes: newClasses, class_requirements: newRequirements };
              });
            }}
          />
        </div>
  
        {formData.classes.map((cls, i) => (
          <div className="form-group" key={`class-${i}`}>
            <label>Class {i+1} Name:</label>
            <input
              value={localClasses[i] || ""}
              onChange={e => {
                const newLocalClasses = [...localClasses];
                newLocalClasses[i] = e.target.value;
                setLocalClasses(newLocalClasses);
              }}
              onFocus={() => setActiveIndex(i)}
              onBlur={() => handleClassUpdate(i)}
              onKeyPress={e => e.key === 'Enter' && handleClassUpdate(i)}
              placeholder="Enter class name (e.g., 10-A)"
            />
            {activeIndex === i && (
              <small className="hint"></small>
            )}
          </div>
        ))}
      </div>
    );
  };
  
  

  // Step 3: Subject Management
  const Step3 = () => {
    const [subject, setSubject] = useState({ name: "", is_lab: false });

    return (
      <div className="step-content">
        <h2>Step 3: Subject Management</h2>
        <div className="form-group">
          <label>Subject Name:</label>
          <input
            value={subject.name}
            onChange={e => setSubject({ ...subject, name: e.target.value })}
          />
        </div>
        <div className="form-group">
          <label>
            <input
              type="checkbox"
              checked={subject.is_lab}
              onChange={e => setSubject({ ...subject, is_lab: e.target.checked })}
            />
            Lab Subject
          </label>
        </div>
        <button
          className="add-button"
          onClick={() => {
            if (!subject.name) return;
            setFormData({
              ...formData,
              subjects: {
                ...formData.subjects,
                [subject.name]: { is_lab: subject.is_lab }
              }
            });
            setSubject({ name: "", is_lab: false });
          }}
        >
          Add Subject
        </button>

        <div className="subject-list">
          <h4>Added Subjects:</h4>
          {Object.keys(formData.subjects).map(subj => (
            <div key={subj} className="subject-item">
              {subj} {formData.subjects[subj].is_lab && "(Lab)"}
            </div>
          ))}
        </div>
      </div>
    );
  };

  // Step 4: Teacher Management
  const Step4 = () => {
    const [teacher, setTeacher] = useState({ code: "", name: "", subjects: [] });

    return (
      <div className="step-content">
        <h2>Step 4: Teacher Management</h2>
        <div className="form-group">
          <label>Teacher Code:</label>
          <input
            value={teacher.code}
            onChange={e => setTeacher({...teacher, code: e.target.value})}
          />
        </div>
        <div className="form-group">
          <label>Teacher Name:</label>
          <input
            value={teacher.name}
            onChange={e => setTeacher({...teacher, name: e.target.value})}
          />
        </div>
        <div className="form-group">
          <label>Subjects Can Teach:</label>
          <select
            multiple
            value={teacher.subjects}
            onChange={e => setTeacher({
              ...teacher,
              subjects: Array.from(e.target.selectedOptions, option => option.value)
            })}
          >
            {Object.keys(formData.subjects).map(subject => (
              <option key={subject} value={subject}>{subject}</option>
            ))}
          </select>
        </div>
        <button
          className="add-button"
          onClick={() => {
            if (!teacher.code || !teacher.name || !teacher.subjects.length) return;
            setFormData({
              ...formData,
              teachers: {
                ...formData.teachers,
                [teacher.code]: {
                  name: teacher.name,
                  subjects: teacher.subjects
                }
              }
            });
            setTeacher({ code: "", name: "", subjects: [] });
          }}
        >
          Add Teacher
        </button>

        <div className="teacher-list">
          <h4>Added Teachers:</h4>
          {Object.entries(formData.teachers).map(([code, t]) => (
            <div key={code} className="teacher-item">
              {code} - {t.name} ({t.subjects.join(", ")})
            </div>
          ))}
        </div>
      </div>
    );
  };

  const Step5 = () => {
    // Initialize requirements structure only once
    const [requirements, setRequirements] = useState(() => {
      const initial = {};
      formData.classes.forEach(className => {
        initial[className] = {};
        Object.keys(formData.subjects).forEach(subject => {
          initial[className][subject] = formData.class_requirements?.[className]?.[subject] || {
            teacher: "",
            lectures: 0
          };
        });
      });
      return initial;
    });
  
    // Save to formData only when moving to next step
    const handleNext = () => {
      setFormData(prev => ({
        ...prev,
        class_requirements: requirements
      }));
      // Move to next step
      setCurrentStep(prev => prev + 1);
    };
  
    return (
      <div className="step-content">
        <h2>Step 5: Class Requirements</h2>
        {formData.classes.map(className => (
          <div key={className} className="class-requirements">
            <h3>{className}</h3>
            {Object.keys(formData.subjects).map(subject => (
              <div key={subject} className="form-group">
                <label>{subject} ({formData.subjects[subject].is_lab ? 'Lab' : 'Theory'}):</label>
                <select
                  value={requirements[className][subject].teacher}
                  onChange={e => setRequirements(prev => ({
                    ...prev,
                    [className]: {
                      ...prev[className],
                      [subject]: {
                        ...prev[className][subject],
                        teacher: e.target.value
                      }
                    }
                  }))}
                >
                  <option value="">Select Teacher</option>
                  {Object.entries(formData.teachers)
                    .filter(([_, t]) => t.subjects.includes(subject))
                    .map(([code, t]) => (
                      <option key={code} value={code}>{t.name} ({code})</option>
                    ))}
                </select>
                <input
                  type="number"
                  min="0"
                  value={requirements[className][subject].lectures}
                  onChange={e => {
                    const lectures = Math.max(0, parseInt(e.target.value) || 0);
                    setRequirements(prev => ({
                      ...prev,
                      [className]: {
                        ...prev[className],
                        [subject]: {
                          ...prev[className][subject],
                          lectures: lectures
                        }
                      }
                    }));
                  }}
                />
              </div>
            ))}
          </div>
        ))}
        
        {/* Next Button */}
        <button onClick={handleNext} className="next-button">
          SAVE
        </button>
      </div>
    );
  };  
  
  
  
  // Step 6: Review and Generate
  const Step6 = () => (
    <div className="step-content">
      <h2>Step 6: Review and Generate</h2>
      {error && <div className="error-message">{error}</div>}
      <button
        className="generate-button"
        onClick={handleGenerate}
        disabled={loading}
      >
        {loading ? "Generating..." : "Generate Timetable"}
      </button>
      <pre className="review-data">{JSON.stringify(formData, null, 2)}</pre>
    </div>
  );

  return (
    <div className="main-content">
      <div className="header">
        <button onClick={() => navigate("/")} className="back-button">
          ← Back
        </button>
        <h1>Time Table Generator</h1>
      </div>

      <div className="stepper-container">
        <div className="stepper-header">
          {[1, 2, 3, 4, 5, 6].map(s => (
            <div key={s} className={`stepper-circle ${s <= step ? "active" : ""}`}>
              {s}
            </div>
          ))}
        </div>

        <div className="step-content-wrapper">
          {step === 1 && <Step1 />}
          {step === 2 && <Step2 />}
          {step === 3 && <Step3 />}
          {step === 4 && <Step4 />}
          {step === 5 && <Step5 />}
          {step === 6 && <Step6 />}
        </div>

        <div className="stepper-controls">
          {step > 1 && (
            <button className="nav-button prev-button" onClick={prevStep}>
              Previous
            </button>
          )}
          {step < 6 && (
            <button className="nav-button next-button" onClick={nextStep}>
              Next
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default TimeTableGenerator;