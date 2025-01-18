import React from 'react';
import { useNavigate } from 'react-router-dom';

const TutorialsAnalysis = () => {
  const navigate = useNavigate();

  const handleBack = () => {
    navigate(-1); // Navigates back to the previous page
  };

  return (
    <div style={{ padding: '20px' , marginLeft: '280px'}}>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
        <button
          onClick={handleBack}
          style={{
            padding: '10px 20px',
            backgroundColor: '#7766d7',
            color: '#fff',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
            marginRight: '15px',
          }}
        >
          Back
        </button>
        <h1 style={{ margin: 0 }}>Analysis (Tutorials)</h1>
      </div>
      <p>Find step-by-step guides and tutorials on how to use the Analysis tool on this page.</p>
    </div>
  );
};

export default TutorialsAnalysis;
