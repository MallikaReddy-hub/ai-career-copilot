import os
import json
import sqlite3
import tempfile
import mysql.connector
from mysql.connector import Error as MySQLError

MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
MYSQL_DB = os.environ.get('MYSQL_DATABASE', 'career_copilot_db')

USE_MYSQL = False

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
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NULL,
            name VARCHAR(255) NULL,
            google_id VARCHAR(255) NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NULL,
            filename VARCHAR(255) NOT NULL,
            file_path VARCHAR(500),
            raw_text LONGTEXT,
            word_count INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NULL,
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
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
    else:
        # SQLite schema initialization
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            name TEXT,
            google_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            filename TEXT NOT NULL,
            file_path TEXT,
            raw_text TEXT,
            word_count INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
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
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
        );
        """)

        # Migration: Add user_id column if table existed previously without it
        try:
            cursor.execute("ALTER TABLE resumes ADD COLUMN user_id INTEGER;")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE analyses ADD COLUMN user_id INTEGER;")
        except Exception:
            pass

    conn.commit()
    conn.close()

# USER AUTHENTICATION HELPERS
def create_user(email, password_hash=None, name=None, google_id=None):
    try:
        init_db()
    except Exception:
        pass
    conn = get_db_connection()
    cursor = conn.cursor()
    clean_email = email.strip().lower()
    
    if USE_MYSQL:
        query = "INSERT INTO users (email, password_hash, name, google_id) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (clean_email, password_hash, name, google_id))
        user_id = cursor.lastrowid
    else:
        query = "INSERT INTO users (email, password_hash, name, google_id) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (clean_email, password_hash, name, google_id))
        user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def get_user_by_email(email):
    try:
        init_db()
    except Exception:
        pass
    conn = get_db_connection()
    cursor = conn.cursor()
    clean_email = email.strip().lower()

    if USE_MYSQL:
        query = "SELECT id, email, password_hash, name, google_id, created_at FROM users WHERE email = %s"
        cursor.execute(query, (clean_email,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        conn.close()
        return {
            'id': row[0],
            'email': row[1],
            'password_hash': row[2],
            'name': row[3],
            'google_id': row[4],
            'created_at': str(row[5])
        }
    else:
        query = "SELECT id, email, password_hash, name, google_id, created_at FROM users WHERE email = ?"
        cursor.execute(query, (clean_email,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        r = dict(row)
        conn.close()
        return {
            'id': r['id'],
            'email': r['email'],
            'password_hash': r['password_hash'],
            'name': r['name'],
            'google_id': r['google_id'],
            'created_at': str(r['created_at'])
        }

def get_user_by_id(user_id):
    try:
        init_db()
    except Exception:
        pass
    conn = get_db_connection()
    cursor = conn.cursor()

    if USE_MYSQL:
        query = "SELECT id, email, name, google_id, created_at FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        conn.close()
        return {
            'id': row[0],
            'email': row[1],
            'name': row[2],
            'google_id': row[3],
            'created_at': str(row[4])
        }
    else:
        query = "SELECT id, email, name, google_id, created_at FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        r = dict(row)
        conn.close()
        return {
            'id': r['id'],
            'email': r['email'],
            'name': r['name'],
            'google_id': r['google_id'],
            'created_at': str(r['created_at'])
        }

def get_user_by_google_id(google_id):
    try:
        init_db()
    except Exception:
        pass
    conn = get_db_connection()
    cursor = conn.cursor()

    if USE_MYSQL:
        query = "SELECT id, email, name, google_id, created_at FROM users WHERE google_id = %s"
        cursor.execute(query, (google_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        conn.close()
        return {
            'id': row[0],
            'email': row[1],
            'name': row[2],
            'google_id': row[3],
            'created_at': str(row[4])
        }
    else:
        query = "SELECT id, email, name, google_id, created_at FROM users WHERE google_id = ?"
        cursor.execute(query, (google_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        r = dict(row)
        conn.close()
        return {
            'id': r['id'],
            'email': r['email'],
            'name': r['name'],
            'google_id': r['google_id'],
            'created_at': str(r['created_at'])
        }

def update_user_google_id(user_id, google_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    if USE_MYSQL:
        cursor.execute("UPDATE users SET google_id = %s WHERE id = %s", (google_id, user_id))
    else:
        cursor.execute("UPDATE users SET google_id = ? WHERE id = ?", (google_id, user_id))
    conn.commit()
    conn.close()

# RESUME & ANALYSIS HELPERS
def save_resume(filename, file_path, raw_text, word_count, user_id=None):
    try:
        init_db()
    except Exception:
        pass
    conn = get_db_connection()
    cursor = conn.cursor()
    if USE_MYSQL:
        query = "INSERT INTO resumes (user_id, filename, file_path, raw_text, word_count) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (user_id, filename, file_path, raw_text, word_count))
        resume_id = cursor.lastrowid
    else:
        query = "INSERT INTO resumes (user_id, filename, file_path, raw_text, word_count) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(query, (user_id, filename, file_path, raw_text, word_count))
        resume_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return resume_id

def save_analysis(resume_id, target_job_title, job_description, overall_score, ats_score, quantified_score, summary, missing_skills, present_skills, bullet_improvements, user_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    missing_json = json.dumps(missing_skills)
    present_json = json.dumps(present_skills)
    bullets_json = json.dumps(bullet_improvements)

    if USE_MYSQL:
        query = """
        INSERT INTO analyses 
        (user_id, resume_id, target_job_title, job_description, overall_match_score, ats_formatting_score, quantified_impact_score, summary_feedback, missing_critical_skills, present_matching_skills, bullet_improvements)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, resume_id, target_job_title, job_description, overall_score, ats_score, quantified_score, summary, missing_json, present_json, bullets_json))
        analysis_id = cursor.lastrowid
    else:
        query = """
        INSERT INTO analyses 
        (user_id, resume_id, target_job_title, job_description, overall_match_score, ats_formatting_score, quantified_impact_score, summary_feedback, missing_critical_skills, present_matching_skills, bullet_improvements)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (user_id, resume_id, target_job_title, job_description, overall_score, ats_score, quantified_score, summary, missing_json, present_json, bullets_json))
        analysis_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return analysis_id

def get_analysis_history(user_id=None, limit=20):
    """
    Returns private scan history. If user_id is None (guest), returns only guest scans for current session.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    result = []

    if USE_MYSQL:
        if user_id is not None:
            query = """
            SELECT a.id, a.target_job_title, a.overall_match_score, a.ats_formatting_score, a.analyzed_at, r.filename
            FROM analyses a
            LEFT JOIN resumes r ON a.resume_id = r.id
            WHERE a.user_id = %s
            ORDER BY a.analyzed_at DESC LIMIT %s
            """
            cursor.execute(query, (user_id, limit))
        else:
            conn.close()
            return []
            
        rows = cursor.fetchall()
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
        if user_id is not None:
            query = """
            SELECT a.id, a.target_job_title, a.overall_match_score, a.ats_formatting_score, a.analyzed_at, r.filename
            FROM analyses a
            LEFT JOIN resumes r ON a.resume_id = r.id
            WHERE a.user_id = ?
            ORDER BY a.analyzed_at DESC LIMIT ?
            """
            cursor.execute(query, (user_id, limit))
        else:
            conn.close()
            return []

        rows = cursor.fetchall()
        for r in rows:
            r_dict = dict(r)
            result.append({
                'id': r_dict['id'],
                'target_job_title': r_dict['target_job_title'],
                'overall_match_score': r_dict['overall_match_score'],
                'ats_formatting_score': r_dict['ats_formatting_score'],
                'analyzed_at': str(r_dict['analyzed_at']),
                'filename': r_dict['filename'] or 'Uploaded Resume'
            })
    conn.close()
    return result

def get_analysis_by_id(analysis_id, user_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if USE_MYSQL:
        if user_id is not None:
            query = "SELECT a.*, r.filename, r.raw_text FROM analyses a LEFT JOIN resumes r ON a.resume_id = r.id WHERE a.id = %s AND (a.user_id = %s OR a.user_id IS NULL)"
            cursor.execute(query, (analysis_id, user_id))
        else:
            query = "SELECT a.*, r.filename, r.raw_text FROM analyses a LEFT JOIN resumes r ON a.resume_id = r.id WHERE a.id = %s"
            cursor.execute(query, (analysis_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        conn.close()
        return {
            'id': row[0],
            'target_job_title': row[3],
            'job_description': row[4],
            'overall_match_score': row[5],
            'ats_formatting_score': row[6],
            'quantified_impact_score': row[7],
            'summary_feedback': row[8],
            'missing_critical_skills': json.loads(row[9]) if isinstance(row[9], str) else row[9],
            'present_matching_skills': json.loads(row[10]) if isinstance(row[10], str) else row[10],
            'bullet_improvements': json.loads(row[11]) if isinstance(row[11], str) else row[11],
            'analyzed_at': str(row[12]),
            'filename': row[13]
        }
    else:
        if user_id is not None:
            query = "SELECT a.*, r.filename, r.raw_text FROM analyses a LEFT JOIN resumes r ON a.resume_id = r.id WHERE a.id = ? AND (a.user_id = ? OR a.user_id IS NULL)"
            cursor.execute(query, (analysis_id, user_id))
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
