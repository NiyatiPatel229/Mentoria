import React from 'react';
import { useNavigate } from 'react-router-dom';

const Analysis = () => {
  const navigate = useNavigate();

  return (
    <div className="main-content">
      <div className="header">
        <button onClick={() => navigate("/")} className="back-button">← Back</button>
        <h1>Analysis</h1>
      </div>
    </div>
  );
};

export default Analysis;
