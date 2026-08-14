# 🚀 AI Career Copilot & ATS Resume Analyzer

An intelligent, full-stack ATS resume optimization and skill-gap intelligence platform built with **Python (Flask)**, **MySQL / SQLite**, **HTML5**, **CSS3**, and **JavaScript**.

---

## ✨ Key Features

- 📄 **PDF Resume Ingestion & Parsing**: Parses multi-page PDF documents, extracting contact details, work history, and technical skills.
- 🎯 **ATS Match & Skill Gap Algorithm**: Compares candidate resumes against target job descriptions, identifying missing skills and computing ATS compatibility.
- ⚡ **Actionable Bullet Point Optimizer**: Detects weak/passive resume phrases and rewrites them into quantified STAR-format achievement bullets.
- 📊 **Interactive Dashboard & Score Gauges**: Visualizes overall match score, ATS formatting readability, and metric density with modern UI components.
- 💾 **Dual Database Architecture**: Works out-of-the-box with **SQLite** for instant setup and auto-migrates to **MySQL** in production environments.
- 📜 **Historical Scan Tracking**: Persists analysis history for side-by-side role comparison and score tracking.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, Flask REST API, `pypdf`, `google-genai`
- **Database**: MySQL 8.0 / SQLite (Dual auto-fallback)
- **Frontend**: HTML5, CSS3 (Custom Design System), Vanilla JavaScript (ES6+ fetch API)
- **Tools**: Git, GitHub

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/ai_career_copilot.git
cd ai_career_copilot
```

### 2. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 3. Start the Flask Server
```bash
python app.py
```

Open your browser and navigate to `http://localhost:5000`.

---

## 📁 Repository Structure

```text
ai_career_copilot/
├── app.py                  # Main Flask REST API & Web Server
├── database.py             # Database connectivity layer (MySQL / SQLite)
├── schema.sql              # MySQL Database Schema definition
├── requirements.txt        # Python package dependencies
├── services/
│   ├── pdf_parser.py       # PDF extraction & section segmenter
│   └── analyzer.py         # ATS scoring algorithm & bullet optimizer
├── static/
│   ├── css/style.css       # Custom design system & score gauges
│   └── js/app.js           # Client-side async dashboard controller
└── templates/
    └── index.html          # Dynamic HTML view
```

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.
