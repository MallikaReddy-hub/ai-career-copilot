import os
import sys
from flask import Flask, render_template, request, jsonify

# Ensure local directories are in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_db, save_resume, save_analysis, get_analysis_history, get_analysis_by_id
from services.pdf_parser import extract_text_from_file
from services.analyzer import analyze_resume_vs_jd, generate_bullet_improvements

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload limit

# Initialize database tables on startup
with app.app_context():
    try:
        init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Warning: Database initialization error: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        target_job_title = request.form.get('target_job_title', 'Software Engineer').strip()
        job_description = request.form.get('job_description', '').strip()
        raw_text_input = request.form.get('resume_text', '').strip()
        
        filename = "pasted_resume.txt"
        file_path = None
        extracted_text = raw_text_input
        word_count = 0

        # Handle PDF / DOCX File Upload if present
        if 'resume_pdf' in request.files and request.files['resume_pdf'].filename != '':
            uploaded_file = request.files['resume_pdf']
            filename = uploaded_file.filename
            
            # Extract PDF or DOCX text
            parse_result = extract_text_from_file(uploaded_file, filename)
            if not parse_result['success']:
                return jsonify({'success': False, 'error': f"Failed to parse document: {parse_result.get('error')}"}), 400
                
            extracted_text = parse_result['raw_text']
            word_count = parse_result['word_count']

        if not extracted_text:
            return jsonify({'success': False, 'error': 'Please upload a valid PDF or DOCX resume or paste resume text.'}), 400

        if not job_description:
            return jsonify({'success': False, 'error': 'Please provide a target job description to run match analysis.'}), 400

        if word_count == 0:
            words = extracted_text.split()
            word_count = len(words)

        # Save Resume Record
        resume_id = save_resume(
            filename=filename,
            file_path=file_path,
            raw_text=extracted_text,
            word_count=word_count
        )

        # Run Analysis Algorithm
        analysis_data = analyze_resume_vs_jd(
            resume_text=extracted_text,
            job_description=job_description,
            target_job_title=target_job_title
        )

        # Save Analysis to DB
        analysis_id = save_analysis(
            resume_id=resume_id,
            target_job_title=target_job_title,
            job_description=job_description,
            overall_score=analysis_data['overall_match_score'],
            ats_score=analysis_data['ats_formatting_score'],
            quantified_score=analysis_data['quantified_impact_score'],
            summary=analysis_data['summary_feedback'],
            missing_skills=analysis_data['missing_critical_skills'],
            present_skills=analysis_data['present_matching_skills'],
            bullet_improvements=analysis_data['bullet_improvements']
        )

        analysis_data['id'] = analysis_id
        analysis_data['filename'] = filename
        analysis_data['word_count'] = word_count
        analysis_data['success'] = True

        return jsonify(analysis_data)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f"Internal Server Error: {str(e)}"}), 500

@app.route('/api/history', methods=['GET'])
def history():
    try:
        scans = get_analysis_history(limit=20)
        return jsonify({'success': True, 'scans': scans})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analysis/<int:analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    try:
        data = get_analysis_by_id(analysis_id)
        if not data:
            return jsonify({'success': False, 'error': 'Analysis record not found'}), 404
        data['success'] = True
        return jsonify(data)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/optimize-bullet', methods=['POST'])
def optimize_bullet():
    try:
        data = request.get_json() or {}
        bullet = data.get('bullet', '').strip()
        if not bullet:
            return jsonify({'success': False, 'error': 'Please provide a bullet point to optimize'}), 400
            
        improvements = generate_bullet_improvements(bullet)
        return jsonify({'success': True, 'result': improvements[0] if improvements else None})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
