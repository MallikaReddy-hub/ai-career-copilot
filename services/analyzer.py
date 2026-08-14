import os
import re
import json

# Comprehensive Tech Skills taxonomy for engineering resumes
TECH_SKILLS_TAXONOMY = [
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust", "ruby", "php", "sql", "html", "css",
    "react", "next.js", "angular", "vue.js", "node.js", "express", "django", "flask", "fastapi", "spring boot",
    "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "sqlite", "oracle", "snowflake",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd", "git", "github", "gitlab", "jenkins",
    "rest api", "graphql", "microservices", "kafka", "rabbitmq", "grpc", "linux", "bash",
    "machine learning", "deep learning", "nlp", "llm", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn"
]

SOFT_SKILLS = ["leadership", "communication", "problem solving", "collaboration", "agile", "scrum", "project management"]

WEAK_VERBS = [
    "responsible for", "worked on", "helped with", "assisted in", "handled", "participated in", "did", "tasked with"
]

POWER_VERBS = [
    "engineered", "architected", "spearheaded", "optimized", "developed", "built", "implemented", "reduced", "increased", "boosted"
]

def analyze_resume_vs_jd(resume_text, job_description, target_job_title="Software Engineer"):
    """
    Analyzes resume text against a target job description.
    Returns structured analysis dict.
    """
    resume_clean = resume_text.lower()
    jd_clean = job_description.lower()
    
    # 1. Extract Skills from JD & Resume
    jd_skills = extract_skills(jd_clean)
    resume_skills = extract_skills(resume_clean)
    
    matching_skills = list(set(jd_skills).intersection(set(resume_skills)))
    missing_skills = list(set(jd_skills) - set(resume_skills))
    
    # Match score based on skill overlap + word overlap
    if jd_skills:
        skill_score = min(100, int((len(matching_skills) / max(1, len(jd_skills))) * 100))
    else:
        skill_score = 70
        
    # 2. ATS Formatting & Content Quality Check
    ats_score, ats_feedback = evaluate_ats_formatting(resume_text)
    
    # 3. Quantified Impact Audit
    quantified_score, metrics_found = evaluate_quantified_impact(resume_text)
    
    # 4. Overall Weighted Score
    overall_score = int((skill_score * 0.50) + (ats_score * 0.25) + (quantified_score * 0.25))
    
    # 5. Bullet Point Rewriter Recommendations
    bullet_improvements = generate_bullet_improvements(resume_text)
    
    # 6. Overall Summary
    summary_feedback = generate_summary_text(overall_score, len(missing_skills), quantified_score, ats_score)
    
    # Try optional Gemini LLM Enhancement if API key is present
    gemini_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    if gemini_key:
        ai_enhancement = get_gemini_insights(resume_text, job_description, gemini_key)
        if ai_enhancement:
            summary_feedback = ai_enhancement.get('summary', summary_feedback)
            if 'bullet_improvements' in ai_enhancement:
                bullet_improvements = ai_enhancement['bullet_improvements']
    
    return {
        'overall_match_score': overall_score,
        'ats_formatting_score': ats_score,
        'quantified_impact_score': quantified_score,
        'summary_feedback': summary_feedback,
        'missing_critical_skills': missing_skills,
        'present_matching_skills': matching_skills,
        'bullet_improvements': bullet_improvements,
        'ats_feedback': ats_feedback
    }

def extract_skills(text):
    found = []
    for skill in TECH_SKILLS_TAXONOMY + SOFT_SKILLS:
        # Match whole word or token boundary
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text):
            found.append(skill.title())
    return sorted(list(set(found)))

def evaluate_ats_formatting(resume_text):
    score = 100
    feedback = []
    
    words = re.findall(r'\b\w+\b', resume_text)
    word_count = len(words)
    
    if word_count < 250:
        score -= 20
        feedback.append("Resume length is short (< 250 words). Add more details regarding achievements and technical scope.")
    elif word_count > 1200:
        score -= 15
        feedback.append("Resume length is long (> 1200 words). Aim for a clean 1 or 2 page concise format.")
    else:
        feedback.append("Optimal word count (~400-800 words). Perfect for ATS parsing.")
        
    # Check key contact fields
    if not re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text):
        score -= 15
        feedback.append("Missing email address or formatted contact info.")
    if not re.search(r'(?:linkedin\.com|github\.com)', resume_text, re.IGNORECASE):
        score -= 10
        feedback.append("Include your LinkedIn or GitHub profile link for technical verification.")
        
    # Check section presence
    text_lower = resume_text.lower()
    if 'skills' not in text_lower and 'technologies' not in text_lower:
        score -= 15
        feedback.append("Dedicated 'Skills' section heading missing. Ensure ATS can easily aggregate your tech stack.")
        
    return max(30, score), feedback

def evaluate_quantified_impact(resume_text):
    # Regex to find numbers, percentages, dollar amounts, multipliers (2x, 50%, $10k, 100ms)
    metrics_patterns = [
        r'\b\d+%\b',
        r'\$\d+(?:,\d+)*(?:\.\d+)?(?:k|m|b)?\b',
        r'\b\d+x\b',
        r'\b\d+\s*(?:ms|seconds|min|hours|days|percent|users|customers|requests|transactions)\b',
        r'\b(?:increased|decreased|reduced|improved|grew|saved|scaled)\s+by\s+\d+',
    ]
    
    found_metrics = []
    for pattern in metrics_patterns:
        matches = re.findall(pattern, resume_text, re.IGNORECASE)
        found_metrics.extend(matches)
        
    unique_metrics = list(set(found_metrics))
    count = len(unique_metrics)
    
    if count >= 5:
        score = 95
    elif count >= 3:
        score = 80
    elif count >= 1:
        score = 60
    else:
        score = 35
        
    return score, unique_metrics

def generate_bullet_improvements(resume_text):
    lines = resume_text.split('\n')
    bullet_improvements = []
    
    for line in lines:
        clean = line.strip()
        if len(clean) > 20 and (clean.startswith('•') or clean.startswith('-') or clean.startswith('*') or re.match(r'^\d+\.', clean)):
            clean_text = re.sub(r'^[•\-\*\d\.]+\s*', '', clean)
            lower_bullet = clean_text.lower()
            
            for weak in WEAK_VERBS:
                if weak in lower_bullet:
                    revised = re.sub(r'\b' + re.escape(weak) + r'\b', 'engineered and optimized', clean_text, flags=re.IGNORECASE)
                    if not re.search(r'\d+', revised):
                        revised += " resulting in a 25% improvement in processing latency."
                    
                    bullet_improvements.append({
                        'original': clean_text,
                        'revised': revised,
                        'reason': f"Replaced weak phrase '{weak}' with strong action verb and added quantified outcome."
                    })
                    break
                    
    if not bullet_improvements:
        # Fallback sample optimizations if no explicit bullets detected
        bullet_improvements.append({
            'original': "Worked on backend APIs and database tables for user authentication.",
            'revised': "Architected high-throughput REST APIs and optimized MySQL indexing, cutting auth latency by 35%.",
            'reason': "Replaced weak passive opener 'Worked on' with strong action verb 'Architected' + added metric."
        })
        bullet_improvements.append({
            'original': "Helped team with building frontend UI components in HTML/CSS.",
            'revised': "Spearheaded design system UI migration across 15+ modern components, increasing page load speed by 20%.",
            'reason': "Converted vague teamwork statement into clear leadership action with metric outcome."
        })
        
    return bullet_improvements[:4]

def generate_summary_text(overall_score, missing_count, quantified_score, ats_score):
    if overall_score >= 85:
        return f"Outstanding resume alignment! Match score is {overall_score}%. High keyword density and strong ATS formatting."
    elif overall_score >= 70:
        return f"Strong match ({overall_score}%). Recommended action: Address the {missing_count} missing skill keyword(s) and incorporate more quantified impact metrics."
    else:
        return f"Moderate match ({overall_score}%). Resume requires targeted optimization to pass ATS filters for this role."

def get_gemini_insights(resume_text, job_description, api_key):
    """Optional Gemini API integration if GOOGLE_API_KEY is available."""
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        prompt = f"""
        You are an expert technical recruiter and ATS specialist.
        Compare this Candidate Resume to the Job Description.

        Resume:
        {resume_text[:2000]}

        Job Description:
        {job_description[:2000]}

        Return JSON with key 'summary' (str) and 'bullet_improvements' (list of dicts with original, revised, reason).
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        if response.text:
            cleaned = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(cleaned)
    except Exception as e:
        pass
    return None
