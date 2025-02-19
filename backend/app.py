# backend/app.py
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import pprint
import json
from werkzeug.utils import secure_filename
from student_analysis import (
    analyze_student_performance, 
    compare_insights, 
    save_reports, 
    visualize_student_performance,
    visualize_comparison,
    clear_reports  # Defined in student_analysis.py to clear the reports folder
)
from question_paper import generate_question_paper_with_answers
app = Flask(__name__)
APP_DIR = os.path.dirname(__file__)
app.config['REPORTS_FOLDER'] = os.path.join(APP_DIR, 'reports')
app.config['UPLOAD_FOLDER'] = os.path.join(APP_DIR, 'uploads')

CORS(app)
app.config['QUPLOAD_FOLDER'] = os.path.join(APP_DIR, 'quploads')
app.config['QREPORTS_FOLDER'] = os.path.join(APP_DIR, 'qreports')

# Create directories on startup (add these lines)
os.makedirs(app.config['QUPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['QREPORTS_FOLDER'], exist_ok=True)

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)

def clear_directory(directory, extension_filter=None):
    """Delete files in a directory; if extension_filter is provided, only remove matching files."""
    for filename in os.listdir(directory):
        if extension_filter:
            if filename.endswith(extension_filter):
                os.remove(os.path.join(directory, filename))
        else:
            os.remove(os.path.join(directory, filename))

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        # Clear previous uploads and reports
        clear_directory(app.config['UPLOAD_FOLDER'])
        clear_reports()  # Clears previous HTML reports from the reports folder

        # Process the current file upload
        current_file = request.files['currentFile']
        max_marks = float(request.form['maxMarks'])
        use_historical = request.form.get('useHistorical', 'false') == 'true'
        
        # Save current file using a secure filename
        current_filename = secure_filename(current_file.filename)
        current_path = os.path.join(app.config['UPLOAD_FOLDER'], current_filename)
        current_file.save(current_path)
        
        # Analyze and generate visualizations for current dataset
        current_df = pd.read_csv(current_path)
        current_insights, _ = analyze_student_performance(current_df, max_marks)
        visualize_student_performance(current_df, "Current Term", max_marks)
        
        historical_insights = None
        comparison_results = None
        
        if use_historical:
            historical_file = request.files['historicalFile']
            historical_filename = secure_filename(historical_file.filename)
            historical_path = os.path.join(app.config['UPLOAD_FOLDER'], historical_filename)
            historical_file.save(historical_path)
            
            historical_df = pd.read_csv(historical_path)
            historical_insights, _ = analyze_student_performance(historical_df, max_marks)
            
            # Generate visualizations for historical data and the comparison
            visualize_student_performance(historical_df, "Historical Term", max_marks)
            visualize_comparison(current_df, historical_df, max_marks)
            comparison_results = compare_insights(current_insights, historical_insights)
        
        # Generate reports (HTML files) for current (and optionally historical/comparison)
        save_reports(current_insights, historical_insights, comparison_results)
        
        # Gather any extra visualization files (those not defined as reports)
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

# backend/app.py modifications (add these routes)
@app.route('/api/generate-question-paper', methods=['POST'])
def generate_question_paper():
    try:
        # Clear previous files
        clear_directory(os.path.join(APP_DIR, 'quploads'), '.pdf')
        clear_directory(os.path.join(APP_DIR, 'qreports'), '.pdf')

        # Get inputs
        question_config = json.loads(request.form['config'])
        print("\nReceived Question Config:")
        pprint.pprint(question_config)

        # Handle file/text input
        if 'pdfFile' in request.files and request.files['pdfFile'].filename:
            pdf_file = request.files['pdfFile']
            pdf_path = os.path.join(app.config['QUPLOAD_FOLDER'], secure_filename(pdf_file.filename))
            pdf_file.save(pdf_path)
            print(f"\nSaved PDF input: {pdf_path}")
        else:
            text = request.form['textInput']
            pdf_path = os.path.join(APP_DIR, 'quploads', 'text_input.pdf')
            create_pdf_from_text(text, pdf_path)
            print(f"\nCreated PDF from text: {pdf_path}")

        # Generate reports
        output_path = os.path.join(APP_DIR, 'qreports', 'question_paper.pdf')
        answer_path = os.path.join(APP_DIR, 'qreports', 'answer_key.pdf')
        
        print("\nStarting question paper generation...")
        success = generate_question_paper_with_answers(
            pdf_path,
            question_config,
            output_path,
            answer_path
        )
        
        if success:
            print("\nGeneration successful!")
            print(f"Question Paper: {output_path}")
            print(f"Answer Key: {answer_path}")
            return jsonify({
                'questionPaper': 'qreports/question_paper.pdf',
                'answerKey': 'qreports/answer_key.pdf'
            })
        return jsonify({'error': 'Failed to generate papers'})

    except Exception as e:
        print(f"\nError during processing: {str(e)}")
        return jsonify({'error': str(e)})

def create_pdf_from_text(text, output_path):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    pdf.output(output_path)


@app.route('/qreports/<filename>')
def serve_qreport(filename):
    return send_from_directory(
        app.config['QREPORTS_FOLDER'], 
        filename, 
        mimetype='application/pdf',  # Add MIME type
        as_attachment=False  # Ensure PDFs are displayed, not downloaded
    )

@app.route('/reports/<filename>')
def serve_report(filename):
    return send_from_directory(app.config['REPORTS_FOLDER'], filename)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)
    os.makedirs(app.config['QUPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['QREPORTS_FOLDER'], exist_ok=True)
    app.run(port=5000, debug=True)
