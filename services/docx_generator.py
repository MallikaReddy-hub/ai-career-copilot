import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io

def create_resume_docx(resume_text, target_title="Software Engineer"):
    """
    Creates a clean, ATS-compliant Microsoft Word (.docx) document from resume text.
    """
    doc = docx.Document()

    # Set standard 0.75-inch margins for ATS readability
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # Style definitions
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(10.5)
    normal_style.font.color.rgb = RGBColor(33, 37, 41)

    lines = resume_text.strip().split('\n')
    is_header = True

    for i, line in enumerate(lines):
        trimmed = line.strip()
        if not trimmed:
            continue

        # Header name / title detection
        if i == 0 or (is_header and i < 3 and ('@' not in trimmed and 'linkedin' not in trimmed.lower())):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(trimmed)
            run.font.size = Pt(16 if i == 0 else 12)
            run.bold = True
            run.font.color.rgb = RGBColor(15, 23, 42)
            p.paragraph_format.space_after = Pt(2)
            continue
        elif is_header and ('@' in trimmed or 'linkedin' in trimmed.lower() or 'github' in trimmed.lower() or '|' in trimmed):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(trimmed)
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor(100, 116, 139)
            p.paragraph_format.space_after = Pt(10)
            is_header = False
            continue

        is_header = False

        # Section Header Detection (e.g. SUMMARY, SKILLS, EXPERIENCE, PROJECTS, EDUCATION)
        clean_upper = trimmed.upper().replace(':', '')
        if clean_upper in ['PROFESSIONAL SUMMARY', 'SUMMARY', 'TECHNICAL SKILLS', 'SKILLS', 'EXPERIENCE', 'PROFESSIONAL EXPERIENCE', 'WORK EXPERIENCE', 'EDUCATION', 'PROJECTS', 'KEY PROJECTS', 'CERTIFICATIONS']:
            h = doc.add_paragraph()
            h.paragraph_format.space_before = Pt(10)
            h.paragraph_format.space_after = Pt(3)
            run = h.add_run(clean_upper)
            run.bold = True
            run.font.size = Pt(11.5)
            run.font.color.rgb = RGBColor(14, 116, 144)  # ATS Accent color
            continue

        # Bullet point detection
        if trimmed.startswith('•') or trimmed.startswith('-') or trimmed.startswith('*'):
            bullet_content = trimmed.lstrip('•-* ').strip()
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(bullet_content)
            continue

        # Standard text paragraph
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(3)
        run = p.add_run(trimmed)

    # Save to in-memory bytes buffer
    doc_io = io.BytesIO()
    doc.save(doc_io)
    doc_io.seek(0)
    return doc_io
