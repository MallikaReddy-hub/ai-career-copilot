import re

def clean_and_normalize_resume_text(text):
    """
    Cleans raw extracted PDF/DOCX text by fixing choppy line wraps while
    strictly preserving candidate name, contact lines, section headers, and bullet points.
    """
    raw_lines = text.replace('\r\n', '\n').split('\n')
    cleaned_lines = []
    
    known_headers = [
        'PROFILE', 'SUMMARY', 'PROFESSIONAL SUMMARY', 'OBJECTIVE',
        'TECHNICAL SKILLS', 'SKILLS', 'CORE COMPETENCIES', 'TECHNOLOGIES',
        'EXPERIENCE', 'PROFESSIONAL EXPERIENCE', 'WORK EXPERIENCE', 'EMPLOYMENT HISTORY',
        'PROJECTS', 'KEY PROJECTS', 'ACADEMIC PROJECTS',
        'EDUCATION', 'ACADEMIC BACKGROUND', 'CERTIFICATIONS', 'ACHIEVEMENTS'
    ]

    non_empty_count = 0
    i = 0
    while i < len(raw_lines):
        line = raw_lines[i].strip()
        if not line:
            cleaned_lines.append("")
            i += 1
            continue

        clean_upper = line.upper().rstrip(':')

        # 1. Candidate Name (First non-empty line)
        if non_empty_count == 0:
            cleaned_lines.append(line)
            non_empty_count += 1
            i += 1
            continue

        # 2. Contact Information Row (Second non-empty line)
        if non_empty_count == 1 and ('@' in line or 'linkedin' in line.lower() or 'github' in line.lower() or '|' in line or '+' in line or re.search(r'\d{8,}', line)):
            cleaned_lines.append(line)
            non_empty_count += 1
            i += 1
            continue

        non_empty_count += 1

        # 3. Section Header
        if clean_upper in known_headers:
            cleaned_lines.append(f"\n{clean_upper}")
            i += 1
            continue

        # 4. Bullet Point
        if line.startswith('•') or line.startswith('-') or line.startswith('*') or re.match(r'^\d+\.', line):
            bullet_text = re.sub(r'^[•\-\*\d\.]+\s*', '', line).strip()
            i += 1
            while i < len(raw_lines):
                next_line = raw_lines[i].strip()
                if not next_line:
                    break
                next_upper = next_line.upper().rstrip(':')
                if next_upper in known_headers or next_line.startswith('•') or next_line.startswith('-') or next_line.startswith('*') or re.match(r'^\d+\.', next_line):
                    break
                bullet_text += " " + next_line
                i += 1
            cleaned_lines.append(f"• {bullet_text}")
            continue

        # 5. Field Key-Value lines (e.g. "Languages: Python, Java...")
        if ':' in line and len(line.split(':')[0].split()) <= 4:
            field_text = line
            i += 1
            while i < len(raw_lines):
                next_line = raw_lines[i].strip()
                if not next_line:
                    break
                next_upper = next_line.upper().rstrip(':')
                if next_upper in known_headers or next_line.startswith('•') or next_line.startswith('-') or next_line.startswith('*') or re.match(r'^\d+\.', next_line) or (':' in next_line and len(next_line.split(':')[0].split()) <= 4):
                    break
                field_text += " " + next_line
                i += 1
            cleaned_lines.append(field_text)
            continue

        # 6. Regular paragraph text - merge wrapped sentences
        para_text = line
        i += 1
        while i < len(raw_lines):
            next_line = raw_lines[i].strip()
            if not next_line:
                break
            next_upper = next_line.upper().rstrip(':')
            if next_upper in known_headers or next_line.startswith('•') or next_line.startswith('-') or next_line.startswith('*') or re.match(r'^\d+\.', next_line):
                break
            para_text += " " + next_line
            i += 1
        cleaned_lines.append(para_text)

    result = "\n".join(cleaned_lines)
    result = re.sub(r'\n{3,}', '\n\n', result).strip()
    return result

def format_resume_as_html(resume_text):
    """
    Converts cleaned resume text into a beautiful, executive-styled HTML document
    suitable for screen preview and crisp PDF printing.
    """
    lines = resume_text.strip().split('\n')
    html_parts = []
    
    known_headers = [
        'PROFILE', 'SUMMARY', 'PROFESSIONAL SUMMARY', 'OBJECTIVE',
        'TECHNICAL SKILLS', 'SKILLS', 'CORE COMPETENCIES', 'TECHNOLOGIES',
        'EXPERIENCE', 'PROFESSIONAL EXPERIENCE', 'WORK EXPERIENCE', 'EMPLOYMENT HISTORY',
        'PROJECTS', 'KEY PROJECTS', 'ACADEMIC PROJECTS',
        'EDUCATION', 'ACADEMIC BACKGROUND', 'CERTIFICATIONS', 'ACHIEVEMENTS'
    ]

    is_header_phase = True
    in_bullet_list = False

    for i, raw_line in enumerate(lines):
        line = raw_line.strip()
        if not line:
            if in_bullet_list:
                html_parts.append("</ul>")
                in_bullet_list = False
            continue

        clean_upper = line.upper().rstrip(':')

        # Header candidate name (first line)
        if is_header_phase and (i == 0 or (len(line.split()) <= 5 and '@' not in line and 'http' not in line and clean_upper not in known_headers)):
            html_parts.append(f'<h1 class="resume-name">{escape_html(line)}</h1>')
            continue
        elif is_header_phase and ('@' in line or 'linkedin' in line.lower() or 'github' in line.lower() or '|' in line or '+' in line):
            contacts = [c.strip() for c in line.split('|')]
            formatted_contacts = " &bull; ".join([f'<span>{escape_html(c)}</span>' for c in contacts if c])
            html_parts.append(f'<div class="resume-contact">{formatted_contacts}</div>')
            is_header_phase = False
            continue

        is_header_phase = False

        # Section Header
        if clean_upper in known_headers:
            if in_bullet_list:
                html_parts.append("</ul>")
                in_bullet_list = False
            html_parts.append(f'<div class="resume-section-header"><h2>{escape_html(clean_upper)}</h2></div>')
            continue

        # Bullet point
        if line.startswith('•') or line.startswith('-') or line.startswith('*'):
            bullet_content = re.sub(r'^[•\-\*\d\.]+\s*', '', line).strip()
            if not in_bullet_list:
                html_parts.append('<ul class="resume-bullet-list">')
                in_bullet_list = True
            html_parts.append(f'<li>{escape_html(bullet_content)}</li>')
            continue

        if in_bullet_list:
            html_parts.append("</ul>")
            in_bullet_list = False

        # Subfield (e.g. "Languages: Python, Java...")
        if ':' in line and len(line.split(':')[0].split()) <= 4:
            parts = line.split(':', 1)
            html_parts.append(f'<p class="resume-subfield"><strong>{escape_html(parts[0].strip())}:</strong> {escape_html(parts[1].strip())}</p>')
        else:
            html_parts.append(f'<p class="resume-text">{escape_html(line)}</p>')

    if in_bullet_list:
        html_parts.append("</ul>")

    return "\n".join(html_parts)

def escape_html(str_val):
    if not str_val:
        return ""
    return str_val.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#039;')
