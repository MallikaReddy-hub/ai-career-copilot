import re
from pypdf import PdfReader

def extract_text_from_pdf(pdf_file_stream):
    """
    Extracts raw text from a PDF file stream or file object.
    Returns:
        dict: containing 'raw_text', 'page_count', 'word_count', 'sections'
    """
    try:
        reader = PdfReader(pdf_file_stream)
        text_content = []
        page_count = len(reader.pages)
        
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)
                
        full_text = "\n".join(text_content)
        words = re.findall(r'\b\w+\b', full_text)
        word_count = len(words)
        
        # Simple section segmenter
        sections = parse_resume_sections(full_text)
        
        return {
            'success': True,
            'raw_text': full_text,
            'page_count': page_count,
            'word_count': word_count,
            'sections': sections
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'raw_text': '',
            'page_count': 0,
            'word_count': 0,
            'sections': {}
        }

def parse_resume_sections(text):
    """
    Identifies common resume section headers and extracts text under each section.
    """
    section_headers = {
        'summary': r'(?:summary|objective|profile|about me)',
        'experience': r'(?:work experience|professional experience|employment history|experience)',
        'education': r'(?:education|academic background|qualifications)',
        'skills': r'(?:skills|technical skills|technologies|core competencies)',
        'projects': r'(?:projects|personal projects|key projects)',
        'certifications': r'(?:certifications|licenses|courses)'
    }
    
    sections = {}
    lines = text.split('\n')
    current_section = 'general'
    sections[current_section] = []
    
    for line in lines:
        clean_line = line.strip().lower()
        matched_header = False
        for sec_name, pattern in section_headers.items():
            if re.match(r'^' + pattern + r'[:\s]*$', clean_line, re.IGNORECASE):
                current_section = sec_name
                if current_section not in sections:
                    sections[current_section] = []
                matched_header = True
                break
        if not matched_header:
            sections[current_section].append(line)
            
    # Rejoin lines into string sections
    return {k: "\n".join(v).strip() for k, v in sections.items() if v}
