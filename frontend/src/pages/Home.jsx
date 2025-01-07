// Home.jsx
import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
  return (
    <div className="main-content">
      <div className="card-container">
        <Link to="/time-table-generator" className="card">
          <img src="/assets/timetable.png" alt="Time Table" />
          <h3>Time Table Generator</h3>
        </Link>
        <Link to="/question-paper-generator" className="card">
          <img src="/assets/question-paper.png" alt="Question Paper" />
          <h3>Question Paper Generator</h3>
        </Link>
        <Link to="/analysis" className="card">
          <img src="/assets/analysis.png" alt="Analysis" />
          <h3>Analysis</h3>
        </Link>
      </div>
    </div>
  );
};

export default Home;
