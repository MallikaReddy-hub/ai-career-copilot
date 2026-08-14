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
    Returns structured analysis dict with optimized resume generation.
    """
    resume_clean = resume_text.lower()
    jd_clean = job_description.lower()
    
    # 1. Extract Skills from JD & Resume
    jd_skills = extract_skills(jd_clean)
    resume_skills = extract_skills(resume_clean)
    
    matching_skills = list(set(jd_skills).intersection(set(resume_skills)))
    missing_skills = list(set(jd_skills) - set(resume_skills))
    
    # Match score based on skill overlap
    if jd_skills:
        skill_score = min(100, int((len(matching_skills) / max(1, len(jd_skills))) * 100))
    else:
        skill_score = 75
        
    # 2. ATS Formatting & Content Quality Check
    ats_score, ats_feedback = evaluate_ats_formatting(resume_text)
    
    # 3. Overall Weighted Score (Skill coverage 65% + ATS readability 35%)
    overall_score = int((skill_score * 0.65) + (ats_score * 0.35))
    
    # 4. Bullet Point Rewriter Recommendations
    bullet_improvements = generate_bullet_improvements(resume_text)
    
    # 5. Overall Summary
    summary_feedback = generate_summary_text(overall_score, len(missing_skills), ats_score)
    
    # Try optional Gemini LLM Enhancement if API key is present
    gemini_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    if gemini_key:
        ai_enhancement = get_gemini_insights(resume_text, job_description, gemini_key)
        if ai_enhancement:
            if 'summary' in ai_enhancement and ai_enhancement['summary']:
                summary_feedback = ai_enhancement['summary']
            if 'bullet_improvements' in ai_enhancement and ai_enhancement['bullet_improvements']:
                bullet_improvements = ai_enhancement['bullet_improvements']

    return {
        'overall_match_score': overall_score,
        'ats_formatting_score': ats_score,
        'quantified_impact_score': 0, # Kept for DB compatibility
        'summary_feedback': summary_feedback,
        'missing_critical_skills': missing_skills,
        'present_matching_skills': matching_skills,
        'bullet_improvements': bullet_improvements,
        'ats_feedback': ats_feedback
    }

def extract_skills(text):
    found = []
    for skill in TECH_SKILLS_TAXONOMY + SOFT_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text):
            found.append(skill.title())
    return sorted(list(set(found)))

def evaluate_ats_formatting(resume_text):
    score = 100
    feedback = []
    
    words = re.findall(r'\b\w+\b', resume_text)
    word_count = len(words)
    
    if word_count < 200:
        score -= 20
        feedback.append("Resume length is short (< 200 words). Add more details regarding achievements and technical scope.")
    elif word_count > 1200:
        score -= 15
        feedback.append("Resume length is long (> 1200 words). Aim for a clean 1 or 2 page concise format.")
    else:
        feedback.append("Optimal word count (~300-800 words). Great for ATS parsing.")
        
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

def generate_bullet_improvements(resume_text):
    """
    Analyzes bullets in resume text or rewrites a single submitted bullet string.
    """
    lines = resume_text.strip().split('\n')
    bullet_improvements = []
    
    # Check if single line passed
    if len(lines) == 1 and len(lines[0]) > 10:
        clean_text = re.sub(r'^[•\-\*\d\.]+\s*', '', lines[0].strip())
        lower_bullet = clean_text.lower()
        replaced = False
        for weak in WEAK_VERBS:
            if weak in lower_bullet:
                revised = re.sub(r'\b' + re.escape(weak) + r'\b', 'Architected and engineered', clean_text, flags=re.IGNORECASE)
                if not re.search(r'\d+', revised):
                    revised += ", delivering a 30% reduction in response latency and improving system reliability."
                bullet_improvements.append({
                    'original': clean_text,
                    'revised': revised,
                    'reason': f"Replaced passive verb '{weak}' with strong engineering verbs and added measurable performance impact."
                })
                replaced = True
                break
        if not replaced:
            bullet_improvements.append({
                'original': clean_text,
                'revised': f"Spearheaded {clean_text[0].lower() + clean_text[1:] if len(clean_text) > 1 else clean_text}, enhancing throughput by 25% and ensuring 99.9% uptime.",
                'reason': "Elevated sentence structure with leadership action verbs and quantified business outcome."
            })
        return bullet_improvements

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
        bullet_improvements.append({
            'original': "Worked on backend APIs and database tables for user authentication.",
            'revised': "Architected high-throughput REST APIs and optimized database indexing, cutting latency by 35%.",
            'reason': "Replaced weak passive opener 'Worked on' with strong action verb 'Architected' + added metric."
        })
        bullet_improvements.append({
            'original': "Helped team with building frontend UI components in HTML/CSS.",
            'revised': "Spearheaded design system UI migration across 15+ modern components, increasing page load speed by 20%.",
            'reason': "Converted vague teamwork statement into clear leadership action with metric outcome."
        })
        
    return bullet_improvements[:4]

def generate_summary_text(overall_score, missing_count, ats_score):
    if overall_score >= 80:
        return f"Outstanding resume alignment! Match score is {overall_score}%. High keyword density and strong ATS formatting."
    elif overall_score >= 60:
        return f"Good match ({overall_score}%). Recommended action: Add the {missing_count} missing skill keyword(s) to your skills section and use the optimized bullet points below."
    else:
        return f"Needs revision ({overall_score}%). Update your resume with the missing job keywords and rewritten bullet points to pass ATS screening."

def generate_cover_letter(resume_text, job_description, target_job_title="Software Engineer", tone="Professional"):
    gemini_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    if gemini_key:
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            prompt = f"""
            You are an expert career coach and hiring manager. Write a compelling, ATS-optimized cover letter for the role of '{target_job_title}'.
            
            Tone: {tone}
            
            Candidate Resume Info:
            {resume_text[:2500]}
            
            Target Job Description:
            {job_description[:2500]}
            
            Instructions:
            1. Create a professional, persuasive 3-4 paragraph cover letter.
            2. Match candidate's skills directly to key job requirements.
            3. Highlight measurable impact and technical achievements.
            4. Keep placeholders clean like [Hiring Team / Company Name] or [Your Name].
            5. Return ONLY the cover letter text, no markdown code fence blocks.
            """
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            if response.text:
                return response.text.strip()
        except Exception:
            pass

    extracted_skills = extract_skills(resume_text.lower())
    top_skills = ", ".join(extracted_skills[:4]) if extracted_skills else "Full-Stack Development, Scalable System Design, and Modern Cloud Architecture"
    
    tone_greeting = "Dear Hiring Manager," if tone == "Professional" else "Hello Hiring Team,"
    
    letter = f"""{tone_greeting}

I am writing to express my strong interest in the {target_job_title} position. With a strong track record of engineering scalable applications and delivering measurable product impact, I am confident in my ability to make an immediate, positive contribution to your team.

Throughout my experience, I have specialized in {top_skills}. In my previous roles, I focused on architecting resilient solutions, optimizing performance bottlenecks, and collaborating across engineering and product teams to deliver high-quality features on schedule.

Your job opening stood out to me because of the opportunity to solve complex technical challenges and contribute to high-impact systems. My background in building clean, maintainable codebases aligns directly with the core requirements outlined in your description.

Thank you for your time and consideration. I welcome the opportunity to discuss how my technical expertise and problem-solving mindset can support your engineering objectives.

Sincerely,
[Your Name]
[Your Phone Number] | [Your Email]
[LinkedIn Profile URL] | [GitHub Profile URL]"""

    return letter

def get_gemini_insights(resume_text, job_description, api_key):
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
    except Exception:
        pass
    return None
