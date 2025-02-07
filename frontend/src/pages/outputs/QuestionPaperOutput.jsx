import React from 'react';
import { useNavigate } from 'react-router-dom';

const QuestionPaperOutput = () => {
  const navigate = useNavigate();
  return (
    <div className="main-content">
      <div className="header">
        <button onClick={() => navigate("/")} className="back-button">← Back</button>
        <h1>Question paper output</h1>
      </div>
      <p>The output of the Question Paper Generator will be displayed here.</p>
    </div>
  );
};

export default QuestionPaperOutput;
