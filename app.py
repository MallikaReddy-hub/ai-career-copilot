import os
import sys
import json
from flask import Flask, render_template, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

# Ensure local directories are in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import (
    init_db, save_resume, save_analysis, get_analysis_history, get_analysis_by_id,
    create_user, get_user_by_email, get_user_by_id, get_user_by_google_id, update_user_google_id
)
from services.pdf_parser import extract_text_from_file
from services.analyzer import analyze_resume_vs_jd, generate_bullet_improvements, generate_cover_letter

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'career_copilot_jwt_secure_session_key_2026')
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

# ----------------- AUTHENTICATION API ROUTES ----------------- #

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'logged_in': False, 'user': None})
    
    user = get_user_by_id(user_id)
    if not user:
        session.pop('user_id', None)
        return jsonify({'logged_in': False, 'user': None})
        
    return jsonify({
        'logged_in': True,
        'user': {
            'id': user['id'],
            'email': user['email'],
            'name': user['name'] or user['email'].split('@')[0]
        }
    })

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json() or {}
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        name = data.get('name', '').strip() or email.split('@')[0]

        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password are required.'}), 400

        if len(password) < 6:
            return jsonify({'success': False, 'error': 'Password must be at least 6 characters long.'}), 400

        existing_user = get_user_by_email(email)
        if existing_user:
            return jsonify({'success': False, 'error': 'An account with this email already exists. Please sign in.'}), 400

        pwd_hash = generate_password_hash(password)
        user_id = create_user(email=email, password_hash=pwd_hash, name=name)

        session['user_id'] = user_id
        session.permanent = True

        return jsonify({
            'success': True,
            'user': {
                'id': user_id,
                'email': email,
                'name': name
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f"Registration error: {str(e)}"}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or {}
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password are required.'}), 400

        user = get_user_by_email(email)
        if not user or not user.get('password_hash'):
            return jsonify({'success': False, 'error': 'Invalid email or password.'}), 401

        if not check_password_hash(user['password_hash'], password):
            return jsonify({'success': False, 'error': 'Invalid email or password.'}), 401

        session['user_id'] = user['id']
        session.permanent = True

        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'] or user['email'].split('@')[0]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f"Login error: {str(e)}"}), 500

@app.route('/api/auth/google', methods=['POST'])
def google_auth():
    """
    Handles Google Sign-In authentication.
    Accepts credential payload from Google Identity Services or profile info.
    """
    try:
        data = request.get_json() or {}
        email = data.get('email', '').strip().lower()
        name = data.get('name', '').strip()
        google_id = data.get('google_id', '').strip()

        if not email:
            return jsonify({'success': False, 'error': 'Google profile email is missing.'}), 400

        # Check if user exists by email or google_id
        user = get_user_by_email(email)
        if user:
            if google_id and not user.get('google_id'):
                update_user_google_id(user['id'], google_id)
            user_id = user['id']
            user_name = user['name'] or name or email.split('@')[0]
        else:
            user_name = name or email.split('@')[0]
            user_id = create_user(email=email, password_hash=None, name=user_name, google_id=google_id)

        session['user_id'] = user_id
        session.permanent = True

        return jsonify({
            'success': True,
            'user': {
                'id': user_id,
                'email': email,
                'name': user_name
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f"Google Sign-In failed: {str(e)}"}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'success': True, 'message': 'Logged out successfully'})

# ----------------- SCAN & RESUME ANALYSIS ROUTES ----------------- #

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

        current_user_id = session.get('user_id')

        # Save Resume Record
        resume_id = save_resume(
            filename=filename,
            file_path=file_path,
            raw_text=extracted_text,
            word_count=word_count,
            user_id=current_user_id
        )

        # Run Analysis Algorithm
        analysis_data = analyze_resume_vs_jd(
            resume_text=extracted_text,
            job_description=job_description,
            target_job_title=target_job_title
        )

        # Save Analysis to DB linked to current user
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
            bullet_improvements=analysis_data['bullet_improvements'],
            user_id=current_user_id
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
        user_id = session.get('user_id')
        if not user_id:
            # If user is not logged in, return empty list so no public scans are shown
            return jsonify({'success': True, 'scans': [], 'authenticated': False})

        scans = get_analysis_history(user_id=user_id, limit=20)
        return jsonify({'success': True, 'scans': scans, 'authenticated': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analysis/<int:analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    try:
        user_id = session.get('user_id')
        data = get_analysis_by_id(analysis_id, user_id=user_id)
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

@app.route('/api/cover-letter', methods=['POST'])
def cover_letter():
    try:
        data = request.get_json() or {}
        resume_text = data.get('resume_text', '').strip()
        job_description = data.get('job_description', '').strip()
        target_job_title = data.get('target_job_title', 'Software Engineer').strip()
        tone = data.get('tone', 'Professional').strip()

        if not resume_text and not job_description:
            return jsonify({'success': False, 'error': 'Please provide resume details and job description.'}), 400

        letter = generate_cover_letter(
            resume_text=resume_text,
            job_description=job_description,
            target_job_title=target_job_title,
            tone=tone
        )
        return jsonify({'success': True, 'cover_letter': letter})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
