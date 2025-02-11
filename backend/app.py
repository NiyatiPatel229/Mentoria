# backend/app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
# from student_analysis import analyze_student_performance, compare_insights, save_reports
import pandas as pd  # Add this at the beginning of app.py
from student_analysis import analyze_student_performance, compare_insights, save_reports
from student_analysis import (
    analyze_student_performance, 
    compare_insights, 
    save_reports, 
    visualize_student_performance,
    visualize_comparison
)

app = Flask(__name__)
app.config['REPORTS_FOLDER'] = os.path.join(os.path.dirname(__file__), 'reports')
CORS(app)

UPLOAD_FOLDER = 'uploads'
REPORTS_FOLDER = 'reports'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

@app.route('/api/analyze', methods=['POST'])
# Add these imports at the top


@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        current_file = request.files['currentFile']
        max_marks = float(request.form['maxMarks'])
        use_historical = request.form.get('useHistorical', 'false') == 'true'
        
        # Save current file
        current_path = os.path.join(UPLOAD_FOLDER, current_file.filename)
        current_file.save(current_path)
        
        # Process current data
        current_df = pd.read_csv(current_path)
        current_insights, _ = analyze_student_performance(current_df, max_marks)
        
        # Generate visualizations for current term
        visualize_student_performance(current_df, "Current Term", max_marks)
        
        historical_insights = None
        comparison_results = None
        
        if use_historical:
            historical_file = request.files['historicalFile']
            historical_path = os.path.join(UPLOAD_FOLDER, historical_file.filename)
            historical_file.save(historical_path)
            
            historical_df = pd.read_csv(historical_path)
            historical_insights, _ = analyze_student_performance(historical_df, max_marks)
            
            # Generate visualizations for historical and comparison
            visualize_student_performance(historical_df, "Historical Term", max_marks)
            visualize_comparison(current_df, historical_df, max_marks)
            comparison_results = compare_insights(current_insights, historical_insights)
        
        # Generate reports
        save_reports(current_insights, historical_insights, comparison_results)
        
        # Get list of generated visualization files
        visualization_files = [f for f in os.listdir(app.config['REPORTS_FOLDER']) 
                             if f.endswith('.html') and 'report' not in f]
        
        return jsonify({
            'status': 'success',
            'reports': {
                'current': 'current_term_report.html',
                'historical': 'historical_term_report.html' if historical_insights else None,
                'comparison': 'comparison_report.html' if comparison_results else None,
                'visualizations': visualization_files
            }
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/reports/<filename>')
def serve_report(filename):
    return send_from_directory(app.config['REPORTS_FOLDER'], filename)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
