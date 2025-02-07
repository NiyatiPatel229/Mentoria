import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Sidebar from './components/Sidebar';
import TimeTableGenerator from './pages/TimeTableGenerator';
import QuestionPaperGenerator from './pages/QuestionPaperGenerator';
import Analysis from './pages/Analysis';
import TutorialsTimeTable from './pages/tutorials/TutorialsTimeTable';
import TutorialsQuestionPaper from './pages/tutorials/TutorialsQuestionPaper';
import TutorialsAnalysis from './pages/tutorials/TutorialsAnalysis';
import TimeTableOutput from './pages/outputs/TimeTableOutput';
import QuestionPaperOutput from './pages/outputs/QuestionPaperOutput';
import AnalysisOutput from './pages/outputs/AnalysisOutput';

const App = () => {
  return (
    <Router>
      <Sidebar />
      <div>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/time-table-generator" element={<TimeTableGenerator />} />
          <Route path="/question-paper-generator" element={<QuestionPaperGenerator />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/tutorials/time-table" element={<TutorialsTimeTable />} />
          <Route path="/tutorials/question-paper" element={<TutorialsQuestionPaper />} />
          <Route path="/tutorials/analysis" element={<TutorialsAnalysis />} />
          <Route path="/analysis/aoutput" element={<AnalysisOutput />} />
          <Route path="/time-table-generator/toutput" element={<TimeTableOutput />} />
          <Route path="/question-paper-generator/qoutput" element={<QuestionPaperOutput />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
