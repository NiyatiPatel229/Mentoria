import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const TimeTableGenerator = () => {
  const navigate = useNavigate();

  // State for modals
  const [isTimeTableModalOpen, setIsTimeTableModalOpen] = useState(false);
  const [isAddTeachersModalOpen, setIsAddTeachersModalOpen] = useState(false);

  // State for Create Time Table Structure
  const [numDays, setNumDays] = useState(5);
  const [numPeriods, setNumPeriods] = useState(1);
  const [lunchBreakAfter, setLunchBreakAfter] = useState(1);

  // State for Add Teachers
  const [numTeachers, setNumTeachers] = useState(0);
  const [teachersData, setTeachersData] = useState([]);

  // Functions for Create Time Table Structure
  const saveTimeTableStructure = () => {
    console.log({ numDays, numPeriods, lunchBreakAfter });
    setIsTimeTableModalOpen(false);
    document.querySelector(".create-timetable-button").style.backgroundColor =
      "#73FD78";
  };

  // Functions for Add Teachers
  const handleNumTeachersChange = (e) => {
    const count = parseInt(e.target.value, 10);
    setNumTeachers(count);
    setTeachersData(Array(count).fill({ name: "", code: "", subjects: [] }));
  };

  const handleTeacherInputChange = (index, field, value) => {
    const updatedTeachers = [...teachersData];
    updatedTeachers[index] = {
      ...updatedTeachers[index],
      [field]: value,
    };
    setTeachersData(updatedTeachers);
  };

  const handleSubjectInputChange = (teacherIndex, subjectIndex, field, value) => {
    const updatedTeachers = [...teachersData];
    const updatedSubjects = [...(updatedTeachers[teacherIndex].subjects || [])];
    updatedSubjects[subjectIndex] = {
      ...updatedSubjects[subjectIndex],
      [field]: value,
    };
    updatedTeachers[teacherIndex].subjects = updatedSubjects;
    setTeachersData(updatedTeachers);
  };

  const handleAddSubject = (teacherIndex) => {
    const updatedTeachers = [...teachersData];
    const updatedSubjects = [...(updatedTeachers[teacherIndex].subjects || [])];
    updatedSubjects.push({ name: "", code: "" });
    updatedTeachers[teacherIndex].subjects = updatedSubjects;
    setTeachersData(updatedTeachers);
  };

  const saveTeachers = () => {
    console.log("Teachers Data Saved:", teachersData);
    setIsAddTeachersModalOpen(false);
    document.querySelector(".add-teachers-button").style.backgroundColor =
      "#73FD78";
  };

  return (
    <div className="main-content">
      {/* Header */}
      <div className="header">
        <button onClick={() => navigate("/")} className="back-button">
          ← Back
        </button>
        <h1>Time Table Generator</h1>
      </div>

      {/* Buttons Section */}
      <div className="time-table-container">
        {/* Create Time Table Structure */}
        <div className="time-table-item">
          <span>Create Time Table Structure:</span>
          <button
            className="action-button create-timetable-button"
            onClick={() => setIsTimeTableModalOpen(true)}
          >
            + Create
          </button>
        </div>

        {/* Add Teachers */}
        <div className="time-table-item">
          <span>Add Teachers:</span>
          <button
            className="action-button add-teachers-button"
            onClick={() => setIsAddTeachersModalOpen(true)}
          >
            + Add
          </button>
        </div>

        {/* Create Classes */}
        <div className="time-table-item">
          <span>Create Classes:</span>
          <button className="action-button create-classes-button">+ Create</button>
        </div>

        <div className="generate-button-container">
          <button className="generate-button">GENERATE</button>
        </div>
      </div>

      {/* Create Time Table Modal */}
      {isTimeTableModalOpen && (
        <div className="modal">
          <div className="modal-content">
            <div className="modal-header">
              <h2>Create Time Table Structure</h2>
              <button
                className="close-button"
                onClick={() => setIsTimeTableModalOpen(false)}
              >
                &times;
              </button>
            </div>
            <div className="modal-body">
              <div className="modal-input">
                <label>Number of Days:</label>
                <select
                  value={numDays}
                  onChange={(e) => setNumDays(parseInt(e.target.value, 10))}
                >
                  <option value={5}>5</option>
                  <option value={6}>6</option>
                </select>
              </div>
              <div className="modal-input">
                <label>Number of Periods:</label>
                <select
                  value={numPeriods}
                  onChange={(e) => setNumPeriods(parseInt(e.target.value, 10))}
                >
                  {Array.from({ length: 10 }, (_, i) => (
                    <option key={i + 1} value={i + 1}>
                      {i + 1}
                    </option>
                  ))}
                </select>
              </div>
              <div className="modal-input">
                <label>Lunch Break After Which Period:</label>
                <select
                  value={lunchBreakAfter}
                  onChange={(e) =>
                    setLunchBreakAfter(parseInt(e.target.value, 10))
                  }
                >
                  {Array.from({ length: numPeriods }, (_, i) => (
                    <option key={i + 1} value={i + 1}>
                      {i + 1}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="modal-footer">
              <button className="save-button" onClick={saveTimeTableStructure}>
                Save
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Teachers Modal */}
      {isAddTeachersModalOpen && (
        <div className="modal">
          <div className="modal-content" style={{ maxHeight: "500px" }}>
            <div className="modal-header">
              <h2>Add Teachers</h2>
              <button
                className="close-button"
                onClick={() => setIsAddTeachersModalOpen(false)}
              >
                &times;
              </button>
            </div>
            <div className="modal-body">
              <div className="modal-input">
                <label>Enter Number of Teachers:</label>
                <input
                  type="number"
                  min="1"
                  onChange={handleNumTeachersChange}
                />
              </div>

              {/* Dynamic Teacher Inputs */}
              {teachersData.map((teacher, teacherIndex) => (
                <div key={teacherIndex} className="teacher-section">
                  <h3 style={{ color: "#B0B0B0" }}>Teacher {teacherIndex + 1}</h3>
                  <div className="modal-input">
                    <label>Name:</label>
                    <input
                      type="text"
                      value={teacher.name}
                      onChange={(e) =>
                        handleTeacherInputChange(teacherIndex, "name", e.target.value)
                      }
                    />
                  </div>
                  <div className="modal-input">
                    <label>Code:</label>
                    <input
                      type="text"
                      value={teacher.code}
                      onChange={(e) =>
                        handleTeacherInputChange(teacherIndex, "code", e.target.value)
                      }
                    />
                  </div>
                  {/* Add Subjects */}
                  {teacher.subjects.map((subject, subjectIndex) => (
                    <div key={subjectIndex} className="subject-section">
                      <div className="modal-input">
                        <label>Subject Name:</label>
                        <input
                          type="text"
                          value={subject.name}
                          onChange={(e) =>
                            handleSubjectInputChange(
                              teacherIndex,
                              subjectIndex,
                              "name",
                              e.target.value
                            )
                          }
                        />
                      </div>
                      <div className="modal-input">
                        <label>Subject Code:</label>
                        <input
                          type="text"
                          value={subject.code}
                          onChange={(e) =>
                            handleSubjectInputChange(
                              teacherIndex,
                              subjectIndex,
                              "code",
                              e.target.value
                            )
                          }
                        />
                      </div>
                    </div>
                  ))}
                  <button
                    className="action-button add-subject-button"
                    onClick={() => handleAddSubject(teacherIndex)}
                  >
                    + Add Subject
                  </button>
                </div>
              ))}
            </div>
            <div className="modal-footer">
              <button className="save-button" onClick={saveTeachers}>
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TimeTableGenerator;
