import React from 'react';
import './Sidebar.css';

const Sidebar = () => {
  return (
    <div className="sidebar">
      <h2>Mentoria</h2>
      <ul>
        <li>Time Table Generator</li>
        <li>Question Paper Generator</li>
        <li>Analysis</li>
        <li>Data</li>
        <li>Coming Soon...</li>
      </ul>
      <div className="tutorials">
        <h3>Tutorials</h3>
        <ul>
          <li>1. Time Table</li>
          <li>2. Question Paper</li>
          <li>3. Data</li>
          <li>4. Analysis</li>
        </ul>
      </div>
      <button>Send Feedback</button>
    </div>
  );
};

export default Sidebar;
