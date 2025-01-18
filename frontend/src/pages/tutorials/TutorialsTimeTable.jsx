import React from 'react';
import { useNavigate } from 'react-router-dom';

const TutorialsTimeTable = () => {
  const navigate = useNavigate();

  const handleBack = () => {
    navigate(-1); // Navigates back to the previous page
  };

  return (
    <div style={{ padding: '20px' , marginLeft: '280px'}}>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
        <button
          onClick={handleBack}
          className='back-button'
        >
        ← Back
        </button>
        <h1 style={{ margin: 0 }}>Time Table (Tutorials)</h1>
      </div>
      <p>Welcome to the Time Table tutorials page. Here you'll find helpful instructions and guides on how to use the Time Table generator effectively.</p>
    </div>
  );
};

export default TutorialsTimeTable;
