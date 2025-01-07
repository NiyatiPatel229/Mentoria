import React from 'react';
import Sidebar from './Sidebar';
import Card from './Card';
import timetable from '../assets/timetable.png';
import questionPaper from '../assets/question-paper.png';
import analysis from '../assets/analysis.png';

const Dashboard = () => {
  return (
    <div className="dashboard">
      <Sidebar />
      <div className="main-content">
        <div className="card-container">
          <Card title="Time Table Generator" image={timetable} />
          <Card title="Question Paper Generator" image={questionPaper} />
          <Card title="Analysis" image={analysis} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
