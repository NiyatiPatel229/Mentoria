// App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Home from './pages/Home';
import TimeTableGenerator from './pages/TimeTableGenerator';
import QuestionPaperGenerator from './pages/QuestionPaperGenerator';
import Analysis from './pages/Analysis';

const App = () => {
  return (
    <Router>
      <div className="dashboard">
        <Sidebar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/time-table-generator" element={<TimeTableGenerator />} />
          <Route path="/question-paper-generator" element={<QuestionPaperGenerator />} />
          <Route path="/analysis" element={<Analysis />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
