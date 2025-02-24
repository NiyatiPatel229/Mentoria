import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const TimeTableOutput = () => {
  const navigate = useNavigate();
  const { state } = useLocation();
  
  // Add safe default values
  const { timetable = {}, teachers = {}, originalData = {} } = state || {};
  const numDays = originalData?.num_days || 2;
  const periodsPerDay = (originalData?.periods_per_day || 4)+1;
  const lunchAfter = originalData?.lunch_after_period || 2;

  const parseTransposedTimetable = () => {
    try {
      if (!timetable || Object.keys(timetable).length === 0) return [];
      
      return Object.entries(timetable).map(([className, days]) => {
        const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'].slice(0, numDays);
        const periods = Array.from({ length: periodsPerDay }, (_, i) => i + 1);

        return {
          className,
          dayNames,
          periods: periods.map(periodNumber => ({
            period: periodNumber,
            days: days.slice(0, numDays).map((day, dayIndex) => {
              // FIX 3: Handle lunch period data
              let periodData = day[periodNumber - 1];
              const isLunchPeriod = periodNumber === lunchAfter + 1;
              
              if (isLunchPeriod) {
                periodData = 'LUNCH'; // Force lunch marker
              }

              return {
                day: dayNames[dayIndex],
                subject: periodData || 'FREE',
                teacherCode: periodData && periodData !== 'LUNCH' ? 
                  originalData.class_requirements[className]?.[periodData]?.teacher : '',
                isLunch: isLunchPeriod
              };
            })
          }))
        };
      });
    } catch (error) {
      console.error('Error parsing timetable:', error);
      return [];
    }
  };

  if (!state) {
    return (
      <div className="main-content">
        <div className="header">
          <button onClick={() => navigate("/")} className="back-button">← Back</button>
          <h1>Generated Timetable</h1>
        </div>
        <div className="error-message">No timetable data found. Please generate a timetable first.</div>
      </div>
    );
  }

  const classTimetables = parseTransposedTimetable();

  return (
    <div className="main-content">
      <div className="header">
        <button onClick={() => navigate("/")} className="back-button">← Back</button>
        <h1>Generated Timetable</h1>
      </div>

      {classTimetables.length > 0 ? (
        <div className="timetable-container">
          {classTimetables.map((classTimetable) => (
            <div key={classTimetable.className} className="class-timetable">
              <h2>{classTimetable.className}</h2>
              <table className="transposed-timetable">
                <thead>
                  <tr className='header-row'>
                    <th>Period</th>
                    {classTimetable.dayNames.map(day => (
                      <th key={day}>{day}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {classTimetable.periods.map((period, idx) => (
                    <tr key={idx} className={period.isLunch ? 'lunch-row' : ''}>
                      <td className="period-label">
                        {period.isLunch ? 'Lunch' : `Period ${period.period}`}
                      </td>
                      {period.days.map((day, dayIdx) => (
                        <td key={dayIdx} className={`timetable-cell ${period.isLunch ? 'lunch-cell' : ''}`}>
                          {day.subject === 'LUNCH' ? (
                            <div className="lunch-break">LUNCH</div>
                          ) : (
                            <>
                              <div className="subject">{day.subject}</div>
                              {day.teacherCode && (
                                <div className="teacher">{day.teacherCode}</div>
                              )}
                            </>
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </div>
      ) : (
        <div className="loading-message">
          {Object.keys(timetable).length === 0 
            ? "No timetable generated yet" 
            : "Loading timetable..."}
        </div>
      )}
    </div>
  );
};

export default TimeTableOutput;
