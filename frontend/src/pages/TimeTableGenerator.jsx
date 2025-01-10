import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const TimeTableGenerator = () => {
  const navigate = useNavigate();

  // State for modals
  const [isTimeTableModalOpen, setIsTimeTableModalOpen] = useState(false);
  const [isAddTeachersModalOpen, setIsAddTeachersModalOpen] = useState(false);
  const [isCreateClassModalOpen, setIsCreateClassModalOpen] = useState(false);

  // State for Create Time Table Structure
  const [numDays, setNumDays] = useState(5);
  const [numPeriods, setNumPeriods] = useState(1);
  const [lunchBreakAfter, setLunchBreakAfter] = useState(1);

  // State for Add Teachers
  const [numTeachers, setNumTeachers] = useState(0);
  const [teachersData, setTeachersData] = useState([]);

  // State for Create Classes
  const [classes, setClasses] = useState([]);
  const [selectedClass, setSelectedClass] = useState(null);
  const [className, setClassName] = useState("");
  const [lectures, setLectures] = useState([]);
  const [remainingLectures, setRemainingLectures] = useState(0);

  // Calculate total lectures when numDays or numPeriods changes
  useEffect(() => {
    setRemainingLectures(numDays * numPeriods);
  }, [numDays, numPeriods]);

  // Functions for Create Time Table Structure
  const saveTimeTableStructure = () => {
    console.log({ numDays, numPeriods, lunchBreakAfter });
    setIsTimeTableModalOpen(false);
    document.querySelector(".create-timetable-button").style.backgroundColor = "#73FD78";
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
    document.querySelector(".add-teachers-button").style.backgroundColor = "#73FD78";
  };

  // Functions for Create Classes
  const handleCreateClass = () => {
    const newClass = `Class ${classes.length + 1}`;
    setClasses([...classes, newClass]);
  };

  const handleClassClick = (classIndex) => {
    setSelectedClass(classIndex);
    setClassName(`Class ${classIndex + 1}`);
    setLectures([]);
    setIsCreateClassModalOpen(true);
    setRemainingLectures(numDays * numPeriods);
  };

  const handleAddLecture = () => {
    setLectures([...lectures, { subject: "", teacher: "", numLectures: 1 }]);
  };

  const handleLectureChange = (index, field, value) => {
    const updatedLectures = [...lectures];
    updatedLectures[index] = { ...updatedLectures[index], [field]: value };
    setLectures(updatedLectures);

    // Update remaining lectures
    const totalAssignedLectures = updatedLectures.reduce((sum, lecture) => 
      sum + (parseInt(lecture.numLectures) || 0), 0);
    setRemainingLectures((numDays * numPeriods) - totalAssignedLectures);
  };

  const handleDeleteClass = () => {
    const updatedClasses = classes.filter((_, index) => index !== selectedClass);
    setClasses(updatedClasses);
    setIsCreateClassModalOpen(false);
  };

  const saveClass = () => {
    if (remainingLectures !== 0) {
      alert("Cannot save! Remaining lectures should be zero.");
      return;
    }
    
    // Update the class name in the classes array
    const updatedClasses = [...classes];
    updatedClasses[selectedClass] = className;
    setClasses(updatedClasses);
    
    // Make the specific class button green
    const classButtons = document.querySelectorAll('.class-button');
    classButtons[selectedClass].style.backgroundColor = "#73FD78";
    
    setIsCreateClassModalOpen(false);
  };

  // Get all unique subjects from teachers
  const getAllSubjects = () => {
    const subjects = new Set();
    teachersData.forEach(teacher => {
      teacher.subjects.forEach(subject => {
        subjects.add(subject.name);
      });
    });
    return Array.from(subjects);
  };

  // Get teachers for a specific subject
  const getTeachersForSubject = (subjectName) => {
    return teachersData.filter(teacher =>
      teacher.subjects.some(subject => subject.name === subjectName)
    ).map(teacher => teacher.name);
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
  <div className="class-buttons">
    {classes.map((className, index) => (
      <button
        key={index}
        className="class-button"
        onClick={() => handleClassClick(index)}
        style={{ backgroundColor: "#4a90e2" }} // Set default blue color explicitly
      >
        {className}
      </button>
    ))}
    <button 
      className="action-button create-classes-button" 
      onClick={handleCreateClass}
      style={{ backgroundColor: "#ffa500" }} // Keep create button orange
    >
      + Create
    </button>
  </div>
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

      {/* Create Class Modal */}
      {isCreateClassModalOpen && (
        <div className="modal">
          <div className="modal-content">
            <div className="modal-header">
              <h2>Create Class</h2>
              <button
                className="close-button"
                onClick={() => setIsCreateClassModalOpen(false)}
              >
                &times;
              </button>
            </div>
            <div className="modal-body">
              <div className="modal-input">
                <label>Class Name:</label>
                <input
                  type="text"
                  value={className}
                  onChange={(e) => setClassName(e.target.value)}
                />
              </div>
              
              <div className="remaining-lectures">
                <h3>Remaining Lectures: {remainingLectures}</h3>
                <button className="action-button" onClick={handleAddLecture}>
                  + Add Lecture
                </button>
              </div>

              {lectures.map((lecture, index) => (
                <div key={index} className="lecture-section">
                  <h4 style={{ color: "#B0B0B0" }}>Lecture {index + 1}</h4>
                  <div className="modal-input">
                    <label>Subject Name:</label>
                    <select
                      value={lecture.subject}
                      onChange={(e) => handleLectureChange(index, "subject", e.target.value)}
                    >
                      <option value="">Select Subject</option>
                      {getAllSubjects().map((subject, idx) => (
                        <option key={idx} value={subject}>
                          {subject}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="modal-input">
                    <label>Teacher Name:</label>
                    <select
                      value={lecture.teacher}
                      onChange={(e) => handleLectureChange(index, "teacher", e.target.value)}
                      disabled={!lecture.subject}
                    >
                      <option value="">Select Teacher</option>
                      {lecture.subject &&
                        getTeachersForSubject(lecture.subject).map((teacher, idx) => (
                          <option key={idx} value={teacher}>
                            {teacher}
                          </option>
                        ))}
                    </select>
                  </div>
                  <div className="modal-input">
                    <label>Number of Lectures:</label>
                    <input
                      type="number"
                      min="1"
                      max={remainingLectures + (parseInt(lecture.numLectures) || 0)}
                      value={lecture.numLectures}
                      onChange={(e) => handleLectureChange(index, "numLectures", e.target.value)
                      }
                    />
                  </div>
                </div>
              ))}
            </div>
            {/* // Modify the save button in the Create Class Modal footer */}
<div className="modal-footer">
  <button className="delete-button" onClick={handleDeleteClass}>
    Delete Class
  </button>
  <button 
    className={`save-button ${remainingLectures !== 0 ? 'disabled-button' : ''}`} 
    onClick={saveClass}
  >
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