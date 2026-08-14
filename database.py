import os
import json
import sqlite3
import mysql.connector
from mysql.connector import Error as MySQLError

MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
MYSQL_DB = os.environ.get('MYSQL_DATABASE', 'career_copilot_db')

import tempfile

def get_db_connection():
    global USE_MYSQL
    if os.environ.get('MYSQL_HOST') and os.environ.get('MYSQL_USER') and os.environ.get('MYSQL_HOST') != 'localhost':
        try:
            conn = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DB,
                connect_timeout=3
            )
            USE_MYSQL = True
            return conn
        except Exception:
            pass

    USE_MYSQL = False
    # On Vercel / serverless platforms, use tempfile.gettempdir() (/tmp) which is 100% writable
    if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
        db_path = os.path.join(tempfile.gettempdir(), 'career_copilot.db')
    else:
        db_path = os.path.join(os.path.dirname(__file__), 'career_copilot.db')
        
    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.OperationalError:
        # Fallback to /tmp if current directory is read-only
        db_path = os.path.join(tempfile.gettempdir(), 'career_copilot.db')
        conn = sqlite3.connect(db_path)

    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    if USE_MYSQL:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB};")
        cursor.execute(f"USE {MYSQL_DB};")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            file_path VARCHAR(500),
            raw_text LONGTEXT,
            word_count INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            resume_id INT,
            target_job_title VARCHAR(255) NOT NULL,
            job_description TEXT NOT NULL,
            overall_match_score INT DEFAULT 0,
            ats_formatting_score INT DEFAULT 0,
            quantified_impact_score INT DEFAULT 0,
            summary_feedback TEXT,
            missing_critical_skills JSON,
            present_matching_skills JSON,
            bullet_improvements JSON,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
    else:
        # SQLite schema initialization
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_path TEXT,
            raw_text TEXT,
            word_count INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id INTEGER,
            target_job_title TEXT NOT NULL,
            job_description TEXT NOT NULL,
            overall_match_score INTEGER DEFAULT 0,
            ats_formatting_score INTEGER DEFAULT 0,
            quantified_impact_score INTEGER DEFAULT 0,
            summary_feedback TEXT,
            missing_critical_skills TEXT,
            present_matching_skills TEXT,
            bullet_improvements TEXT,
            analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
        );
        """)
    conn.commit()
    conn.close()

def save_resume(filename, file_path, raw_text, word_count):
    try:
        init_db()
    except Exception:
        pass
    conn = get_db_connection()
    cursor = conn.cursor()
    if USE_MYSQL:
        query = "INSERT INTO resumes (filename, file_path, raw_text, word_count) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (filename, file_path, raw_text, word_count))
        resume_id = cursor.lastrowid
    else:
        query = "INSERT INTO resumes (filename, file_path, raw_text, word_count) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (filename, file_path, raw_text, word_count))
        resume_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return resume_id

def save_analysis(resume_id, target_job_title, job_description, overall_score, ats_score, quantified_score, summary, missing_skills, present_skills, bullet_improvements):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    missing_json = json.dumps(missing_skills)
    present_json = json.dumps(present_skills)
    bullets_json = json.dumps(bullet_improvements)

    if USE_MYSQL:
        query = """
        INSERT INTO analyses 
        (resume_id, target_job_title, job_description, overall_match_score, ats_formatting_score, quantified_impact_score, summary_feedback, missing_critical_skills, present_matching_skills, bullet_improvements)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (resume_id, target_job_title, job_description, overall_score, ats_score, quantified_score, summary, missing_json, present_json, bullets_json))
        analysis_id = cursor.lastrowid
    else:
        query = """
        INSERT INTO analyses 
        (resume_id, target_job_title, job_description, overall_match_score, ats_formatting_score, quantified_impact_score, summary_feedback, missing_critical_skills, present_matching_skills, bullet_improvements)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (resume_id, target_job_title, job_description, overall_score, ats_score, quantified_score, summary, missing_json, present_json, bullets_json))
        analysis_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return analysis_id

def get_analysis_history(limit=10):
    conn = get_db_connection()
    cursor = conn.cursor()
    if USE_MYSQL:
        query = """
        SELECT a.id, a.target_job_title, a.overall_match_score, a.ats_formatting_score, a.analyzed_at, r.filename
        FROM analyses a
        LEFT JOIN resumes r ON a.resume_id = r.id
        ORDER BY a.analyzed_at DESC LIMIT %s
        """
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            result.append({
                'id': r[0],
                'target_job_title': r[1],
                'overall_match_score': r[2],
                'ats_formatting_score': r[3],
                'analyzed_at': str(r[4]),
                'filename': r[5] or 'Uploaded Resume'
            })
    else:
        query = """
        SELECT a.id, a.target_job_title, a.overall_match_score, a.ats_formatting_score, a.analyzed_at, r.filename
        FROM analyses a
        LEFT JOIN resumes r ON a.resume_id = r.id
        ORDER BY a.analyzed_at DESC LIMIT ?
        """
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            result.append({
                'id': dict(r)['id'],
                'target_job_title': dict(r)['target_job_title'],
                'overall_match_score': dict(r)['overall_match_score'],
                'ats_formatting_score': dict(r)['ats_formatting_score'],
                'analyzed_at': str(dict(r)['analyzed_at']),
                'filename': dict(r)['filename'] or 'Uploaded Resume'
            })
    conn.close()
    return result

def get_analysis_by_id(analysis_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    if USE_MYSQL:
        query = "SELECT a.*, r.filename, r.raw_text FROM analyses a LEFT JOIN resumes r ON a.resume_id = r.id WHERE a.id = %s"
        cursor.execute(query, (analysis_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        conn.close()
        return {
            'id': row[0],
            'target_job_title': row[2],
            'job_description': row[3],
            'overall_match_score': row[4],
            'ats_formatting_score': row[5],
            'quantified_impact_score': row[6],
            'summary_feedback': row[7],
            'missing_critical_skills': json.loads(row[8]) if isinstance(row[8], str) else row[8],
            'present_matching_skills': json.loads(row[9]) if isinstance(row[9], str) else row[9],
            'bullet_improvements': json.loads(row[10]) if isinstance(row[10], str) else row[10],
            'analyzed_at': str(row[11]),
            'filename': row[12]
        }
    else:
        query = "SELECT a.*, r.filename, r.raw_text FROM analyses a LEFT JOIN resumes r ON a.resume_id = r.id WHERE a.id = ?"
        cursor.execute(query, (analysis_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        r_dict = dict(row)
        conn.close()
        return {
            'id': r_dict['id'],
            'target_job_title': r_dict['target_job_title'],
            'job_description': r_dict['job_description'],
            'overall_match_score': r_dict['overall_match_score'],
            'ats_formatting_score': r_dict['ats_formatting_score'],
            'quantified_impact_score': r_dict['quantified_impact_score'],
            'summary_feedback': r_dict['summary_feedback'],
            'missing_critical_skills': json.loads(r_dict['missing_critical_skills']) if r_dict['missing_critical_skills'] else [],
            'present_matching_skills': json.loads(r_dict['present_matching_skills']) if r_dict['present_matching_skills'] else [],
            'bullet_improvements': json.loads(r_dict['bullet_improvements']) if r_dict['bullet_improvements'] else [],
            'analyzed_at': str(r_dict['analyzed_at']),
            'filename': r_dict['filename']
        }
