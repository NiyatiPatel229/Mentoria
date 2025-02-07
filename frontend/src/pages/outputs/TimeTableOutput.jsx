import React from 'react';
import { useNavigate } from 'react-router-dom';

const TimeTableOutput = () => {
  const navigate = useNavigate();
  return (
    <div className="main-content">
      <div className="header">
        <button onClick={() => navigate("/")} className="back-button">← Back</button>
        <h1>Time Table output</h1>
      </div>
      <p>The output of the Time Table Generator will be displayed here.</p>
    </div>
  );
};

export default TimeTableOutput;
