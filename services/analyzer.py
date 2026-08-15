import os
import re
import json

# Comprehensive Multi-Industry Skills Taxonomy
UNIVERSAL_SKILLS_TAXONOMY = [
    # 1. Tech, Software & Cloud Engineering
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust", "ruby", "php", "sql", "html", "css",
    "react", "next.js", "angular", "vue.js", "node.js", "express", "django", "flask", "fastapi", "spring boot",
    "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "sqlite", "oracle", "snowflake", "dynamodb",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd", "git", "github", "gitlab", "jenkins",
    "rest api", "graphql", "microservices", "kafka", "rabbitmq", "grpc", "linux", "bash", "cybersecurity",
    
    # 2. Data Science, AI & Analytics
    "machine learning", "deep learning", "nlp", "llm", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn",
    "data analysis", "data visualization", "tableau", "power bi", "excel", "bigquery", "data modeling",
    "statistical analysis", "a/b testing", "predictive modeling", "etl", "data warehousing", "r", "spark",
    
    # 3. Product & Project Management
    "product management", "project management", "agile", "scrum", "kanban", "jira", "confluence", "prd",
    "roadmapping", "product strategy", "user stories", "sprint planning", "feature prioritization",
    "stakeholder management", "go-to-market", "gtm", "market research", "kpi tracking", "okrs",
    
    # 4. UI/UX Design & Creative
    "figma", "sketch", "adobe xd", "ui/ux design", "wireframing", "prototyping", "user research", "usability testing",
    "design systems", "interaction design", "photoshop", "illustrator", "creative direction", "graphic design",
    
    # 5. Marketing, Growth & Content
    "seo", "sem", "google analytics", "content marketing", "content strategy", "social media marketing",
    "email marketing", "copywriting", "conversion rate optimization", "cro", "hubspot", "mailchimp", "ppc",
    "paid advertising", "brand strategy", "growth hacking", "lead generation", "public relations",
    
    # 6. Sales, Business Development & Partnerships
    "b2b sales", "b2c sales", "salesforce", "crm", "cold calling", "cold outreach", "pipeline management",
    "account management", "contract negotiation", "client relationship management", "revenue growth", "closing",
    
    # 7. Finance, Accounting & Banking
    "financial modeling", "financial analysis", "forecasting", "budgeting", "valuation", "quickbooks", "gaap",
    "auditing", "cash flow management", "risk management", "p&l management", "payroll", "tax compliance", "sap",
    
    # 8. Human Resources & Talent Acquisition
    "talent acquisition", "recruiting", "sourcing", "technical recruiting", "workday", "bamboohr",
    "employee relations", "onboarding", "performance management", "compensation & benefits", "hr policies",
    
    # 9. Operations, Supply Chain & Quality
    "supply chain management", "logistics", "procurement", "inventory management", "lean six sigma", "erp",
    "vendor management", "process optimization", "quality assurance", "operations management",
    
    # 10. Healthcare, Clinical & Nursing
    "patient care", "clinical documentation", "electronic health records", "ehr", "cpr", "bls", "hipaa",
    "medical terminology", "triage", "care coordination", "vital signs",
    
    # 11. Customer Support & Success
    "customer success", "customer support", "zendesk", "intercom", "churn reduction", "troubleshooting",
    "client retention", "sla compliance", "help desk"
]

UNIVERSAL_SOFT_SKILLS = [
    "leadership", "communication", "problem solving", "collaboration", "cross-functional collaboration",
    "critical thinking", "adaptability", "time management", "strategic planning", "mentorship",
    "analytical skills", "conflict resolution", "negotiation", "decision making", "presentation skills"
]

WEAK_VERBS = [
    "responsible for", "worked on", "helped with", "assisted in", "handled", "participated in", "did", "tasked with", "involved in"
]

def analyze_resume_vs_jd(resume_text, job_description, target_job_title="Software Engineer"):
    """
    Analyzes resume text against ANY target job description across all industries and roles.
    Uses dynamic JD keyword harvesting + universal taxonomy + optional Gemini AI zero-shot evaluation.
    """
    resume_clean = resume_text.lower()
    jd_clean = job_description.lower()
    
    # 1. Extract Domain Skills dynamically from JD & Resume
    jd_skills = extract_skills_universal(jd_clean)
    resume_skills = extract_skills_universal(resume_clean)
    
    # If standard taxonomy didn't capture enough from JD, harvest custom dynamic keywords from JD
    dynamic_jd_terms = harvest_keywords_from_jd(job_description)
    for term in dynamic_jd_terms:
        if term.lower() not in [s.lower() for s in jd_skills]:
            jd_skills.append(term)
            if term.lower() in resume_clean:
                resume_skills.append(term)
    
    matching_skills = sorted(list(set([s for s in jd_skills if s.lower() in [r.lower() for r in resume_skills]])))
    missing_skills = sorted(list(set([s for s in jd_skills if s.lower() not in [r.lower() for r in resume_skills]])))
    
    # Match score based on skill overlap
    if jd_skills:
        skill_score = min(100, int((len(matching_skills) / max(1, len(jd_skills))) * 100))
    else:
        skill_score = 75
        
    # 2. ATS Formatting & Content Quality Check
    ats_score, ats_feedback = evaluate_ats_formatting(resume_text)
    
    # 3. Overall Weighted Score (Skill coverage 65% + ATS readability 35%)
    overall_score = int((skill_score * 0.65) + (ats_score * 0.35))
    
    # 4. Role-Aware Bullet Point Rewriter Recommendations
    bullet_improvements = generate_bullet_improvements(resume_text, target_job_title)
    
    # 5. Overall Summary
    summary_feedback = generate_summary_text(overall_score, len(missing_skills), target_job_title)
    
    # Try optional Gemini LLM Enhancement if API key is present (Works for ANY job role globally)
    gemini_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    if gemini_key:
        ai_enhancement = get_gemini_insights(resume_text, job_description, target_job_title, gemini_key)
        if ai_enhancement:
            if 'summary' in ai_enhancement and ai_enhancement['summary']:
                summary_feedback = ai_enhancement['summary']
            if 'bullet_improvements' in ai_enhancement and ai_enhancement['bullet_improvements']:
                bullet_improvements = ai_enhancement['bullet_improvements']
            if 'missing_skills' in ai_enhancement and ai_enhancement['missing_skills']:
                missing_skills = ai_enhancement['missing_skills']
            if 'matching_skills' in ai_enhancement and ai_enhancement['matching_skills']:
                matching_skills = ai_enhancement['matching_skills']
            if 'overall_score' in ai_enhancement and isinstance(ai_enhancement['overall_score'], int):
                overall_score = ai_enhancement['overall_score']

    return {
        'overall_match_score': overall_score,
        'ats_formatting_score': ats_score,
        'quantified_impact_score': 0, # Kept for DB compatibility
        'summary_feedback': summary_feedback,
        'missing_critical_skills': missing_skills[:15],
        'present_matching_skills': matching_skills[:15],
        'bullet_improvements': bullet_improvements,
        'ats_feedback': ats_feedback
    }

def extract_skills_universal(text):
    """
    Extracts skills matching our comprehensive multi-industry taxonomy.
    """
    found = []
    combined_taxonomy = UNIVERSAL_SKILLS_TAXONOMY + UNIVERSAL_SOFT_SKILLS
    for skill in combined_taxonomy:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            found.append(format_skill_name(skill))
    return sorted(list(set(found)))

def harvest_keywords_from_jd(jd_text):
    """
    Extracts domain-specific keywords and uppercase acronyms directly from any job description.
    Enables support for 100% of niche jobs in legal, healthcare, real estate, aviation, etc.
    """
    harvested = []
    
    # 1. Catch uppercase domain acronyms (e.g. HIPAA, GAAP, SEO, CAD, PRD, EHR, CRM, SLA, B2B, GTM, KPI)
    acronyms = re.findall(r'\b[A-Z0-9]{2,8}\b', jd_text)
    common_stops = {"THE", "AND", "FOR", "WITH", "ARE", "YOU", "WILL", "OUR", "WHO", "CAN", "JOB", "ROLE", "NOT", "YES", "MUST", "HAVE", "TEAM"}
    for acr in acronyms:
        if acr not in common_stops and len(acr) >= 2:
            harvested.append(acr)
            
    # 2. Extract Title Case multi-word industry phrases (e.g. "Risk Management", "Supply Chain", "Clinical Trials")
    phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', jd_text)
    stop_phrases = {"Job Description", "Equal Opportunity", "United States", "Years Experience", "Bachelor Degree", "Master Degree"}
    stop_leading_words = {"Seeking", "Hiring", "Looking", "Need", "Require", "Must", "Will", "Should", "Can"}
    
    for phrase in phrases:
        cleaned_phrase = phrase
        words = phrase.split()
        if words[0] in stop_leading_words and len(words) > 1:
            cleaned_phrase = " ".join(words[1:])
            
        if cleaned_phrase not in stop_phrases and len(cleaned_phrase.split()) <= 3 and len(cleaned_phrase) > 3:
            harvested.append(cleaned_phrase)
            
    return list(set(harvested))[:10]

def format_skill_name(skill):
    special_cases = {
        "sql": "SQL", "html": "HTML", "css": "CSS", "aws": "AWS", "gcp": "GCP", "ci/cd": "CI/CD",
        "rest api": "REST API", "graphql": "GraphQL", "nlp": "NLP", "llm": "LLM", "ui/ux design": "UI/UX Design",
        "seo": "SEO", "sem": "SEM", "cro": "CRO", "crm": "CRM", "b2b sales": "B2B Sales", "b2c sales": "B2C Sales",
        "gaap": "GAAP", "kpi tracking": "KPI Tracking", "okrs": "OKRs", "prd": "PRD", "gtm": "GTM",
        "ehr": "EHR", "cpr": "CPR", "bls": "BLS", "hipaa": "HIPAA", "sla compliance": "SLA Compliance",
        "power bi": "Power BI", "p&l management": "P&L Management", "adobe xd": "Adobe XD"
    }
    return special_cases.get(skill.lower(), skill.title())

def evaluate_ats_formatting(resume_text):
    score = 100
    feedback = []
    
    words = re.findall(r'\b\w+\b', resume_text)
    word_count = len(words)
    
    if word_count < 200:
        score -= 20
        feedback.append("Resume length is short (< 200 words). Add more details regarding your responsibilities and achievements.")
    elif word_count > 1200:
        score -= 15
        feedback.append("Resume length is long (> 1200 words). Aim for a clean 1 or 2 page concise format.")
    else:
        feedback.append("Optimal word count (~300-800 words). Great for ATS parsing.")
        
    # Check key contact fields
    if not re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text):
        score -= 15
        feedback.append("Missing email address or formatted contact info.")
    if not re.search(r'(?:linkedin\.com|github\.com|portfolio|\.com|\.io|\.me)', resume_text, re.IGNORECASE):
        score -= 10
        feedback.append("Include your LinkedIn profile or professional portfolio link.")
        
    # Check section presence
    text_lower = resume_text.lower()
    if 'skills' not in text_lower and 'competencies' not in text_lower and 'expertise' not in text_lower:
        score -= 15
        feedback.append("Dedicated 'Skills' or 'Core Competencies' section heading missing.")
        
    return max(30, score), feedback

def generate_bullet_improvements(resume_text, target_job_title="Software Engineer"):
    """
    Analyzes bullets in resume text or rewrites a single submitted bullet string,
    adapting power action verbs according to the target job role.
    """
    lines = resume_text.strip().split('\n')
    bullet_improvements = []
    
    # Select dynamic power verbs based on role category
    title_lower = target_job_title.lower()
    if any(k in title_lower for k in ["product", "project", "program", "manager", "lead", "director"]):
        lead_verbs = ["Spearheaded", "Directed", "Orchestrated", "Formulated", "Championed"]
        outcome_tail = ", driving a 30% increase in product adoption and aligning key cross-functional stakeholders."
    elif any(k in title_lower for k in ["market", "growth", "sales", "business development", "account"]):
        lead_verbs = ["Accelerated", "Generated", "Boosted", "Captured", "Negotiated"]
        outcome_tail = ", achieving a 28% increase in pipeline conversion and exceeding revenue targets."
    elif any(k in title_lower for k in ["finance", "account", "analyst", "data", "operations", "supply"]):
        lead_verbs = ["Streamlined", "Optimized", "Consolidated", "Audited", "Forecasted"]
        outcome_tail = ", cutting operational turnaround time by 35% and improving reporting accuracy."
    elif any(k in title_lower for k in ["design", "ui", "ux", "creative", "art"]):
        lead_verbs = ["Conceptualized", "Crafted", "Redesigned", "Pioneered", "Standardized"]
        outcome_tail = ", improving user engagement by 40% across key digital touchpoints."
    else:
        lead_verbs = ["Architected and engineered", "Spearheaded", "Developed", "Optimized"]
        outcome_tail = ", delivering a 30% reduction in response latency and improving system reliability."

    # Single bullet optimization
    if len(lines) == 1 and len(lines[0]) > 10:
        clean_text = re.sub(r'^[•\-\*\d\.]+\s*', '', lines[0].strip())
        lower_bullet = clean_text.lower()
        replaced = False
        for weak in WEAK_VERBS:
            if weak in lower_bullet:
                revised = re.sub(r'\b' + re.escape(weak) + r'\b', lead_verbs[0], clean_text, flags=re.IGNORECASE)
                if not re.search(r'\d+', revised):
                    revised += outcome_tail
                bullet_improvements.append({
                    'original': clean_text,
                    'revised': revised,
                    'reason': f"Replaced passive verb '{weak}' with high-impact leadership action verb and quantified business outcome."
                })
                replaced = True
                break
        if not replaced:
            bullet_improvements.append({
                'original': clean_text,
                'revised': f"{lead_verbs[0]} {clean_text[0].lower() + clean_text[1:] if len(clean_text) > 1 else clean_text}{outcome_tail}",
                'reason': "Elevated sentence structure with active power verbs and measurable results."
            })
        return bullet_improvements

    for line in lines:
        clean = line.strip()
        if len(clean) > 20 and (clean.startswith('•') or clean.startswith('-') or clean.startswith('*') or re.match(r'^\d+\.', clean)):
            clean_text = re.sub(r'^[•\-\*\d\.]+\s*', '', clean)
            lower_bullet = clean_text.lower()
            
            for weak in WEAK_VERBS:
                if weak in lower_bullet:
                    revised = re.sub(r'\b' + re.escape(weak) + r'\b', lead_verbs[0], clean_text, flags=re.IGNORECASE)
                    if not re.search(r'\d+', revised):
                        revised += outcome_tail
                    
                    bullet_improvements.append({
                        'original': clean_text,
                        'revised': revised,
                        'reason': f"Replaced weak phrase '{weak}' with strong action verb and added measurable impact."
                    })
                    break
                    
    if not bullet_improvements:
        bullet_improvements.append({
            'original': "Worked on project deliverables and coordinated team tasks.",
            'revised': f"{lead_verbs[0]} core deliverables and streamlined cross-functional workflows{outcome_tail}",
            'reason': "Replaced weak passive opener 'Worked on' with strong action verb + added metric."
        })
        bullet_improvements.append({
            'original': "Helped with daily client communications and performance metrics.",
            'revised': f"Standardized client communication strategy across major accounts, increasing client retention by 22%.",
            'reason': "Converted vague support statement into clear strategic leadership with quantified result."
        })
        
    return bullet_improvements[:4]

def generate_summary_text(overall_score, missing_count, target_job_title="Software Engineer"):
    if overall_score >= 80:
        return f"Outstanding alignment for '{target_job_title}'! Match score is {overall_score}%. Strong domain keyword density and clean ATS readability."
    elif overall_score >= 60:
        return f"Good match for '{target_job_title}' ({overall_score}%). Recommended action: Add the {missing_count} missing domain keyword(s) to your skills section and use the optimized bullet points below."
    else:
        return f"Needs revision for '{target_job_title}' ({overall_score}%). Update your resume with the missing role keywords and rewritten bullet points to pass ATS screening."

def get_gemini_insights(resume_text, job_description, target_job_title, api_key):
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        prompt = f"""
        You are an expert ATS recruiter and career strategist.
        Analyze this resume against the target job role and description:
        
        Target Role: {target_job_title}
        Job Description:
        {job_description[:2500]}
        
        Resume:
        {resume_text[:2500]}
        
        Respond ONLY with a valid JSON object matching this exact schema:
        {{
            "overall_score": <integer 0-100 representing fit for this specific job>,
            "summary": "<2-sentence actionable recruiter assessment for this candidate>",
            "missing_skills": ["Skill1", "Skill2", "Skill3"],
            "matching_skills": ["SkillA", "SkillB", "SkillC"],
            "bullet_improvements": [
                {{
                    "original": "<exact weak bullet from resume>",
                    "revised": "<high-impact rewrite with strong action verb and quantified outcome>",
                    "reason": "<brief explanation of why this rewrite is stronger>"
                }}
            ]
        }}
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        if response.text:
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            return json.loads(text.strip())
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None

def generate_cover_letter(resume_text, job_description, target_job_title="Software Engineer", tone="Professional"):
    gemini_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    if gemini_key:
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            prompt = f"""
            You are an expert career coach and hiring manager. Write a compelling, ATS-optimized cover letter for the role of '{target_job_title}'.
            
            Tone: {tone}
            
            Candidate Highlights & Experience:
            {resume_text[:2000]}
            
            Job Requirements & Description:
            {job_description[:2000]}
            
            Format:
            - Professional greeting
            - 3-4 structured paragraphs: Strong introduction, specific proof of relevant qualifications matching JD, enthusiasm for company mission, and confident call to action.
            - Professional sign-off
            - Return ONLY the clean cover letter text.
            """
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            if response.text and len(response.text.strip()) > 100:
                return response.text.strip()
        except Exception:
            pass

    # Universal Rule-Based Cover Letter Template for ANY role
    return f"""Dear Hiring Team,

I am writing to express my strong interest in the {target_job_title} position. With a solid track record of driving results and executing high-priority initiatives, I am excited about the opportunity to contribute to your team's ongoing success.

Throughout my career, I have consistently aligned core competencies with organizational objectives to deliver measurable impact. My experience in executing projects, collaborating across multifunctional teams, and solving complex challenges positions me to add immediate value in the {target_job_title} role.

I am particularly drawn to your organization's forward-thinking vision and commitment to excellence. I look forward to the opportunity to discuss how my qualifications, work ethic, and dedication can support your upcoming goals.

Thank you for your time and consideration.

Sincerely,
Candidate
"""
