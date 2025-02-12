import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

def get_subject_columns(df):
    """Identify subject columns by excluding non-subject columns"""
    non_subject_columns = ['ID No.', 'Name of Student', 'Overall_percentage', 'Term']
    return [col for col in df.columns if col not in non_subject_columns and not col.endswith('_percentage')]

def clean_data(df):
    """Clean the DataFrame by replacing non-numeric values in subject columns with 0."""
    subject_columns = get_subject_columns(df)
    
    for subject in subject_columns:
        df[subject] = pd.to_numeric(df[subject], errors='coerce').fillna(0)
    
    return df

def analyze_student_performance(df, max_marks):
    """
    Analyze student performance from a DataFrame.
    Args:
        df: DataFrame containing student performance data
        max_marks: Maximum marks per subject
    Returns:
        insights: A dictionary containing analysis results
    """
    # Clean the data to handle errors
    df = clean_data(df)

    # Get subject columns dynamically
    subject_columns = get_subject_columns(df)
    
    print(f"\nAnalyzing performance for subjects: {', '.join(subject_columns)}")
    
    # Calculate subject percentages
    for subject in subject_columns:
        df[f'{subject}_percentage'] = (df[subject] / max_marks) * 100
    
    # Calculate overall percentage
    df['Overall_percentage'] = (df[subject_columns].mean(axis=1) / max_marks) * 100
    
    # Generate insights
    insights = {
        'subject_averages': {},
        'top_performers': {},
        'failed_students': {},
        'above_70_percent': {},
        'failure_counts': {}
    }
    
    # Subject-wise Analysis
    for subject in subject_columns:
        insights['subject_averages'][subject] = {
            'average': df[subject].mean(),
            'highest_score': df[subject].max(),
            'lowest_score': df[subject].min(),
            'topper': df.loc[df[subject].idxmax(), 'Name of Student'],
        }
    
    # Failed Students (less than 40%) with marks
    failed_students = {}
    failure_counts = {}
    
    for subject in subject_columns:
        failed_df = df[df[f'{subject}_percentage'] < 40][['Name of Student', subject]]
        failed_students[subject] = failed_df.to_dict('records')
        failure_counts[subject] = len(failed_df)
    
    insights['failed_students'] = failed_students
    insights['failure_counts'] = failure_counts
    
    # Students scoring above 70%
    high_performers = {}
    
    for subject in subject_columns:
        high_performers_subject = df[df[f'{subject}_percentage'] >= 70]['Name of Student'].tolist()
        if high_performers_subject:
            high_performers[subject] = high_performers_subject
            
    insights['above_70_percent'] = high_performers
    
    # Overall top performers (top 5)
    top_5_overall = df.nlargest(5, 'Overall_percentage')[['Name of Student', 'Overall_percentage']]
    insights['top_performers']['overall'] = top_5_overall.to_dict('records')
    
    return insights, df


def normalize_scores(df, max_marks):
    """Normalize scores to percentage scale"""
    subject_columns = get_subject_columns(df)
    return df[subject_columns].apply(lambda x: (x / max_marks) * 100)

def compare_insights(current_insights, historical_insights):
   """
   Compare current and historical insights.
   Args:
       current_insights: Insights from current data.
       historical_insights: Insights from historical data.
   Returns:
       comparison: A dictionary containing comparison results.
   """
   comparison = {}
   
   for subject in current_insights['subject_averages']:
       current_avg = current_insights['subject_averages'][subject]['average']
       historical_avg = historical_insights['subject_averages'][subject]['average']
       difference = current_avg - historical_avg
       
       # Calculate percentage change
       if historical_avg != 0:  # Avoid division by zero
           percentage_change = (difference / historical_avg) * 100
       else:
           percentage_change = 0  # Handle case where historical average is 0
       
       comparison[subject] = {
           'current_average': current_avg,
           'historical_average': historical_avg,
           'difference': difference,
           'percentage_change': percentage_change
       }
   
   return comparison


def visualize_student_performance(df, term_label, max_marks):
    """Create visualizations for student performance with normalized scores."""
    # Normalize scores to percentages
    normalized_df = normalize_scores(df, max_marks)
    subjects = get_subject_columns(df)

    # 1. Subject-wise Average Performance (Bar Chart with percentage scores)
    ''' fig1 = go.Figure()
    averages = [normalized_df[subject].mean() for subject in subjects]
    
    fig1.add_trace(go.Bar(
        x=subjects,
        y=averages,
        text=[f'{avg:.1f}%' for avg in averages],
        textposition='auto',
    ))

    fig1.update_layout(
        title=f'Average Percentage Scores by Subject ({term_label})',
        yaxis=dict(
            title='Average Percentage Score',
            range=[0, 100],  # Fixed range for percentages
            dtick=10  # Grid lines every 10%
        ),
        xaxis_title='Subjects',
        showlegend=False
    )
    fig1.write_html(f'reports/subject_averages_{term_label}.html') '''
    # fig1.write_html(f'reports/subject_averages_{term_label}.html')
    
     # Subject-wise Average Performance
    fig1 = px.bar(
        x=subjects,
        y=[df[subject].mean() for subject in subjects],
        title=f'Average Scores by Subject ({term_label})',
        labels={'x': 'Subjects', 'y': 'Average Score'},
        color=subjects
    )
    fig1.write_html(f'reports/subject_averages_{term_label}.html')
    # fig1.write_html(f'reports/subject_averages_{term_label}.html')

    # 2. Performance Distribution (Histogram Matrix with percentage scores)
    fig2 = make_subplots(
        rows=1, 
        cols=len(subjects), 
        subplot_titles=subjects
    )
    
    for i, subject in enumerate(subjects, 1):
        fig2.add_trace(
            go.Histogram(
                x=normalized_df[subject],
                nbinsx=20,  # More bins for percentage distribution
                hovertemplate="Percentage Range: %{x}%<br>Count: %{y}<extra></extra>"
            ),
            row=1, col=i
        )
        
        fig2.update_xaxes(
            title_text="Percentage Score",
            range=[0, 100],
            dtick=20,
            row=1, col=i
        )
        fig2.update_yaxes(
            title_text="Frequency" if i == 1 else None,
            row=1, col=i
        )
    
    fig2.update_layout(
        title=f'Score Distribution by Subject ({term_label})',
        showlegend=False,
        height=500
    )
    fig2.write_html(f'reports/score_distribution_{term_label}.html')
    # fig1.write_html(f'reports/subject_averages_{term_label}.html')

    # 3. Performance Bands Distribution
    performance_bands = {
        'Outstanding (â‰¥85%)': lambda x: x >= 85,
        'Excellent (70-84%)': lambda x: (x >= 70) & (x < 85),
        'Good (55-69%)': lambda x: (x >= 55) & (x < 70),
        'Satisfactory (40-54%)': lambda x: (x >= 40) & (x < 55),
        'Needs Improvement (<40%)': lambda x: x < 40
    }

    band_data = {subject: [] for subject in subjects}
    band_labels = list(performance_bands.keys())
    
    for band_name, condition in performance_bands.items():
        for subject in subjects:
            percentage = (condition(normalized_df[subject]).sum() / len(df) * 100)
            band_data[subject].append(percentage)

    fig3 = go.Figure()
    for subject in subjects:
        fig3.add_trace(go.Bar(
            name=subject,
            x=band_labels,
            y=band_data[subject],
            text=[f'{y:.1f}%' for y in band_data[subject]],
            textposition='auto',
        ))

    fig3.update_layout(
        title=f'Performance Bands Distribution ({term_label})',
        xaxis_title='Performance Bands',
        yaxis=dict(
            title='Percentage of Students',
            range=[0, 100],
            dtick=10
        ),
        barmode='group',
        showlegend=True
    )
    fig3.write_html(f'reports/performance_bands_{term_label}.html')

    # 4. Subject Performance Radar Chart with percentage scores
    avg_percentages = [normalized_df[subject].mean() for subject in subjects]
    
    fig4 = go.Figure()
    fig4.add_trace(go.Scatterpolar(
        r=avg_percentages + [avg_percentages[0]],  # Close the polygon
        theta=subjects + [subjects[0]],
        fill='toself',
        name=term_label
    ))

    fig4.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                dtick=20
            )
        ),
        showlegend=True,
        title=f'Subject Performance Radar ({term_label})'
    )
    fig4.write_html(f'reports/radar_chart_{term_label}.html')
    
    # Box Plot
    fig5 = go.Figure()
    for subject in subjects:
       fig5.add_trace(go.Box(y=df[subject], name=subject))
    fig5.update_layout(title=f'Score Ranges by Subject ({term_label})',
                      yaxis_title='Scores')
    fig5.write_html(f'reports/score_ranges_{term_label}.html')

def visualize_comparison(current_df, historical_df, max_marks):
    """Create interactive visualizations to compare current and historical data with normalized scores."""
    # Normalize both datasets
    current_normalized = normalize_scores(current_df, max_marks)
    historical_normalized = normalize_scores(historical_df, max_marks)
    subjects = get_subject_columns(current_df)

    '''# 1. Radar Chart comparing average percentage scores
    avg_current = [current_normalized[subject].mean() for subject in subjects]
    avg_historical = [historical_normalized[subject].mean() for subject in subjects]

    fig1 = go.Figure()
    fig1.add_trace(go.Scatterpolar(
        r=avg_current + [avg_current[0]],
        theta=subjects + [subjects[0]],
        fill='toself',
        name='Current Term'
    ))
    
    fig1.add_trace(go.Scatterpolar(
        r=avg_historical + [avg_historical[0]],
        theta=subjects + [subjects[0]],
        fill='toself',
        name='Historical Term'
    ))

    fig1.update_layout(
        title='Average Percentage Scores Comparison',
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                dtick=20
            )
        ),
        showlegend=True
    )
    fig1.write_html('reports/radar_comparison.html')'''
    
     # Line Chart comparing average scores between current and historical data
    avg_current = [current_df[subject].mean() for subject in subjects]
    avg_historical = [historical_df[subject].mean() for subject in subjects]

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=subjects, y=avg_current, mode='lines+markers', name='Current Term'))
    fig1.add_trace(go.Scatter(x=subjects, y=avg_historical, mode='lines+markers', name='Historical Term'))
   
    fig1.update_layout(title='Average Scores Comparison',
                      xaxis_title='Subjects', yaxis_title='Average Score')
   
   # Save line chart as HTML
    fig1.write_html('reports/average_scores_comparison.html')

    # 2. Performance Change Heatmap
    performance_metrics = {
        'Mean %': lambda x: x.mean(),
        'Median %': lambda x: x.median(),
        'Pass Rate %': lambda x: (x >= 40).mean() * 100,
        'Distinction %': lambda x: (x >= 75).mean() * 100,
        'Std Dev': lambda x: x.std()
    }

    change_matrix = []
    for subject in subjects:
        changes = []
        for metric_name, metric_func in performance_metrics.items():
            current_val = metric_func(current_normalized[subject])
            historical_val = metric_func(historical_normalized[subject])
            changes.append(current_val - historical_val)
        change_matrix.append(changes)

    fig2 = go.Figure(data=go.Heatmap(
        z=change_matrix,
        x=list(performance_metrics.keys()),
        y=subjects,
        colorscale='RdBu',
        zmid=0,
        text=[[f'{val:.1f}' for val in row] for row in change_matrix],
        texttemplate='%{text}',
        textfont={"size": 10},
        hovertemplate="Subject: %{y}<br>Metric: %{x}<br>Change: %{z:.1f}%<extra></extra>"
    ))

    fig2.update_layout(
        title='Performance Changes (Current - Historical)',
        xaxis_title='Metrics',
        yaxis_title='Subjects'
    )
    fig2.write_html('reports/performance_changes.html')

    # 3. Grade Distribution Comparison
    grade_bands = {
        'A (â‰¥85%)': lambda x: x >= 85,
        'B (70-84%)': lambda x: (x >= 70) & (x < 85),
        'C (55-69%)': lambda x: (x >= 55) & (x < 70),
        'D (40-54%)': lambda x: (x >= 40) & (x < 55),
        'F (<40%)': lambda x: x < 40
    }

    '''fig3 = go.Figure()
    for subject in subjects:
        current_grades = []
        historical_grades = []
        
        for grade_func in grade_bands.values():
            current_pct = (grade_func(current_normalized[subject]).sum() / len(current_df) * 100)
            historical_pct = (grade_func(historical_normalized[subject]).sum() / len(historical_df) * 100)
            current_grades.append(current_pct)
            historical_grades.append(historical_pct)
        
        fig3.add_trace(go.Bar(
            name=f'Current - {subject}',
            x=list(grade_bands.keys()),
            y=current_grades,
            text=[f'{val:.1f}%' for val in current_grades],
            textposition='auto'
        ))
        
        fig3.add_trace(go.Bar(
            name=f'Historical - {subject}',
            x=list(grade_bands.keys()),
            y=historical_grades,
            text=[f'{val:.1f}%' for val in historical_grades],
            textposition='auto'
        ))

    fig3.update_layout(
        title='Grade Distribution Comparison',
        xaxis_title='Grades',
        yaxis_title='Percentage of Students',
        barmode='group',
        showlegend=True
    )
    fig3.write_html('reports/grade_distribution_comparison.html')'''
    
def generate_comparison_html(comparison_results):
    """Generate HTML report for comparison between terms"""
    html = """
    <html>
    <head>
        <title>Performance Comparison Report</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                color: #333;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            h1, h2 {
                color: #2c3e50;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }
            th {
                background-color: #f5f6fa;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .positive-change {
                color: #27ae60;
            }
            .negative-change {
                color: #c0392b;
            }
            .section {
                margin: 30px 0;
                padding: 20px;
                background-color: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Performance Comparison Report</h1>
            
            <div class="section">
                <h2>Subject-wise Comparison</h2>
                <table>
                    <tr>
                        <th>Subject</th>
                        <th>Current Average</th>
                        <th>Historical Average</th>
                        <th>Difference</th>
                        <th>Percentage Change</th>
                    </tr>
    """
    
    for subject, data in comparison_results.items():
        difference_class = "positive-change" if data['difference'] >= 0 else "negative-change"
        percentage_class = "positive-change" if data['percentage_change'] >= 0 else "negative-change"
        
        html += f"""
                    <tr>
                        <td>{subject}</td>
                        <td>{data['current_average']:.2f}</td>
                        <td>{data['historical_average']:.2f}</td>
                        <td class="{difference_class}">{data['difference']:.2f}</td>
                        <td class="{percentage_class}">{data['percentage_change']:.2f}%</td>
                    </tr>
        """
    
    html += """
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def generate_report_html(insights, term_label):
    """Generate HTML report in original format"""
    html = f"""
    <html>
    <head>
        <title>Student Performance Analysis - {term_label}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                color: #333;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            h1, h2, h3 {{
                color: #2c3e50;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #f5f6fa;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            .section {{
                margin: 30px 0;
                padding: 20px;
                background-color: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Student Performance Analysis Report - {term_label}</h1>
            
            <div class="section">
                <h2>Subject-wise Analysis</h2>
                <table>
                    <tr>
                        <th>Subject</th>
                        <th>Average Score</th>
                        <th>Highest Score</th>
                        <th>Lowest Score</th>
                        <th>Top Performer</th>
                    </tr>
    """
    
    # Add subject-wise analysis
    for subject, data in insights['subject_averages'].items():
        html += f"""
                    <tr>
                        <td>{subject}</td>
                        <td>{data['average']:.2f}</td>
                        <td>{data['highest_score']}</td>
                        <td>{data['lowest_score']}</td>
                        <td>{data['topper']}</td>
                    </tr>
        """
    
    html += """
                </table>
            </div>
            
            <div class="section">
                <h2>Failed Students Analysis</h2>
    """
    
    # Add failed students analysis
    for subject, students in insights['failed_students'].items():
        if students:
            html += f"""
                <h3>{subject} (Failures: {insights['failure_counts'][subject]})</h3>
                <table>
                    <tr>
                        <th>Student Name</th>
                        <th>Marks</th>
                    </tr>
            """
            for student in students:
                html += f"""
                    <tr>
                        <td>{student['Name of Student']}</td>
                        <td>{student[subject]}</td>
                    </tr>
                """
            html += "</table>"
    
    html += """
            </div>
            
            <div class="section">
                <h2>High Performers (Above 70%)</h2>
    """
    
    # Add high performers
    for subject, students in insights['above_70_percent'].items():
        if students:
            html += f"""
                <h3>{subject}</h3>
                <ul>
            """
            for student in students:
                html += f"<li>{student}</li>"
            html += "</ul>"
    
    html += """
            </div>
            
            <div class="section">
                <h2>Top 5 Overall Performers</h2>
                <table>
                    <tr>
                        <th>Rank</th>
                        <th>Student Name</th>
                        <th>Overall Percentage</th>
                    </tr>
    """
    
    # Add top performers
    for i, student in enumerate(insights['top_performers']['overall'], 1):
        html += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{student['Name of Student']}</td>
                        <td>{student['Overall_percentage']:.2f}%</td>
                    </tr>
        """
    
    html += """
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def save_reports(current_insights, historical_insights=None, comparison_results=None):
    """Save analysis results to HTML reports"""
    # Current Term Report
    with open(os.path.join(REPORTS_DIR, 'current_term_report.html'), 'w') as f:
        f.write(generate_report_html(current_insights, "Current Term"))
    
    # Historical Term Report
    if historical_insights:
        with open(os.path.join(REPORTS_DIR, 'historical_term_report.html'), 'w') as f:
            f.write(generate_report_html(historical_insights, "Historical Term"))
    
    # Comparison Report
    if comparison_results:
        with open(os.path.join(REPORTS_DIR, 'comparison_report.html'), 'w') as f:
            f.write(generate_comparison_html(comparison_results))

def clear_reports():
    """Clear previous reports before generating new ones"""
    for file in os.listdir(REPORTS_DIR):
        if file.endswith(".html"):
            os.remove(os.path.join(REPORTS_DIR, file))

# Update the main function to include report generation
def main():
    csv_file_current = input("Enter the path to your current CSV file: ")
    
    try:
        max_marks = float(input("Enter maximum marks per subject: "))
        
        current_df = pd.read_csv(csv_file_current)
        current_insights, _ = analyze_student_performance(current_df, max_marks)  
        
        visualize_student_performance(current_df, "Current Term", max_marks)
        
        include_historical_data = input("Do you want to include historical data? (yes/no): ").strip().lower()
        
        if include_historical_data == 'yes':
            historical_csv_file = input("Enter the path to your historical CSV file: ")
            historical_df = pd.read_csv(historical_csv_file)
            
            historical_insights, _ = analyze_student_performance(historical_df, max_marks)
            
            visualize_student_performance(historical_df, "Historical Term", max_marks)
            visualize_comparison(current_df, historical_df, max_marks)
            
            comparison_results = compare_insights(current_insights, historical_insights)
            
            # Generate all reports
            save_reports(current_insights, historical_insights, comparison_results)
            print("\nReports generated successfully:")
            print("1. current_term_report.html")
            print("2. historical_term_report.html")
            print("3. comparison_report.html")
        
        else:
            # Generate only current term report
            save_reports(current_insights)
            print("\nReport generated successfully:")
            print("1. current_term_report.html")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
    
