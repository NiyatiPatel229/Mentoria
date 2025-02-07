from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import pandas as pd
from analysis import analyze_student_performance, visualize_student_performance, compare_insights, visualize_comparison, save_reports
import traceback

app = Flask(__name__)
CORS(app)

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Create reports directory if it doesn't exist
REPORTS_FOLDER = 'reports'
if not os.path.exists(REPORTS_FOLDER):
    os.makedirs(REPORTS_FOLDER)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        # Get files and data
        if 'currentFile' not in request.files:
            return jsonify({'error': 'No current file provided'}), 400
            
        current_file = request.files['currentFile']
        if not current_file.filename:
            return jsonify({'error': 'No current file selected'}), 400

        if 'maxMarks' not in request.form:
            return jsonify({'error': 'Maximum marks not provided'}), 400
            
        try:
            max_marks = float(request.form['maxMarks'])
        except ValueError:
            return jsonify({'error': 'Invalid maximum marks value'}), 400

        # Save current file
        current_filename = secure_filename(current_file.filename)
        current_path = os.path.join(UPLOAD_FOLDER, current_filename)
        current_file.save(current_path)
        
        # Process current term data
        try:
            current_df = pd.read_csv(current_path)
        except Exception as e:
            return jsonify({'error': f'Error reading CSV file: {str(e)}'}), 400

        try:
            current_insights, _ = analyze_student_performance(current_df, max_marks)
            visualize_student_performance(current_df, "Current Term", max_marks)
        except Exception as e:
            print("Analysis error:", traceback.format_exc())  # Print full error trace
            return jsonify({'error': f'Error during analysis: {str(e)}'}), 500

        use_historical = request.form.get('useHistorical') == 'true'
        
        if use_historical:
            if 'historicalFile' not in request.files:
                return jsonify({'error': 'No historical file provided'}), 400
                
            historical_file = request.files['historicalFile']
            if not historical_file.filename:
                return jsonify({'error': 'No historical file selected'}), 400

            historical_filename = secure_filename(historical_file.filename)
            historical_path = os.path.join(UPLOAD_FOLDER, historical_filename)
            historical_file.save(historical_path)
            
            try:
                historical_df = pd.read_csv(historical_path)
                historical_insights, _ = analyze_student_performance(historical_df, max_marks)
                visualize_student_performance(historical_df, "Historical Term", max_marks)
                visualize_comparison(current_df, historical_df, max_marks)
                comparison_results = compare_insights(current_insights, historical_insights)
                save_reports(current_insights, historical_insights, comparison_results)
            except Exception as e:
                print("Historical analysis error:", traceback.format_exc())
                return jsonify({'error': f'Error processing historical data: {str(e)}'}), 500

            return jsonify({
                'current_insights': current_insights,
                'historical_insights': historical_insights,
                'comparison_results': comparison_results,
                'message': 'Analysis completed successfully'
            })
        
        else:
            save_reports(current_insights)
            return jsonify({
                'current_insights': current_insights,
                'message': 'Analysis completed successfully'
            })
            
    except Exception as e:
        print("Unexpected error:", traceback.format_exc())
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/reports/<filename>')
def get_report(filename):
    try:
        return send_file(filename)
    except Exception as e:
        return jsonify({'error': f'Error retrieving report: {str(e)}'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)