import React from 'react';
import { Link } from 'react-router-dom';
import './Sidebar.css';

const Sidebar = () => {
  return (
    <div className="sidebar">
      <Link to="/">
  <img src="/assets/mentoria.jpg" alt="Mentoria Logo" className="logo" />
</Link>

      <ul>
        <li>
          <Link to="/time-table-generator">Time Table Generator</Link>
        </li>
        <li>
          <Link to="/question-paper-generator">Question Paper Generator</Link>
        </li>
        <li>
          <Link to="/analysis">Analysis</Link>
        </li>
      </ul>
      <div className="tutorials">
        <h3 id='tut'>Tutorials</h3>
        <ul>
          <li>
            <Link to="/tutorials/time-table">1. Time Table</Link>
          </li>
          <li>
            <Link to="/tutorials/question-paper">2. Question Paper</Link>
          </li>
          <li>
            <Link to="/tutorials/analysis">4. Analysis</Link>
          </li>
        </ul>
      </div>
      <button>Send Feedback</button>
    </div>
  );
};

export default Sidebar;
