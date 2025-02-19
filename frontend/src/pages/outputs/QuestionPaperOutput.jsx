import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const QuestionPaperOutput = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [pdfUrls, setPdfUrls] = useState({
    question: null,
    answer: null
  });

  // Cache-busting timestamp
  const timestamp = Date.now();

  useEffect(() => {
    if (location.state) {
      setPdfUrls({
        question: `http://localhost:5000/qreports/${
          location.state.questionPaper.split('/')[1]
        }?t=${timestamp}`,
        answer: `http://localhost:5000/qreports/${
          location.state.answerKey.split('/')[1]
        }?t=${timestamp}`
      });
    }
  }, [location.state, timestamp]);

  return (
    <div className="main-content">
      <div className="header">
        <button onClick={() => navigate(-1)} className="back-button">
          ← Back
        </button>
        <h1>Question Paper Output</h1>
      </div>

      <div className="pdf-container">
        {pdfUrls.question && (
          <div className="pdf-viewer">
            <h2>Generated Question Paper</h2>
            <iframe
              src={pdfUrls.question}
              title="Question Paper"
              width="100%"
              height="500px"
              onError={(e) => console.error('Failed to load question paper:', e)}
            />
          </div>
        )}

        {pdfUrls.answer && (
          <div className="pdf-viewer">
            <h2>Answer Key</h2>
            <iframe
              src={pdfUrls.answer}
              title="Answer Key"
              width="100%"
              height="500px"
              onError={(e) => console.error('Failed to load answer key:', e)}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default QuestionPaperOutput;
