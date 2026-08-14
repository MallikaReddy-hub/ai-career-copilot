-- Database Schema for AI Career Copilot & ATS Resume Analyzer
-- Target DBMS: MySQL 8.0+

CREATE DATABASE IF NOT EXISTS career_copilot_db;
USE career_copilot_db;

-- Table 1: Resumes
CREATE TABLE IF NOT EXISTS resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    raw_text LONGTEXT,
    word_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 2: Analyses
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

-- Table 3: Extracted Skills Master Log
CREATE TABLE IF NOT EXISTS skills_extracted (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT,
    skill_name VARCHAR(100) NOT NULL,
    category ENUM('hard_skill', 'soft_skill', 'tool', 'domain_knowledge') DEFAULT 'hard_skill',
    is_matching BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
