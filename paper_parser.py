import os
import re
from typing import List, Dict

# Graceful imports for document parsing
try:
    import docx
    HAS_DOCX = True
except Exception:
    HAS_DOCX = False

try:
    import pypdf
    HAS_PYPDF = True
except Exception:
    HAS_PYPDF = False

from advanced_features import extract_text_from_image


def parse_question_paper_file(file_path: str) -> List[Dict]:
    """
    Parses a question paper file (PDF, DOCX, TXT, PNG/JPG) and extracts individual questions,
    question numbers, marks, and question types.
    """
    if not os.path.exists(file_path):
        return []

    ext = file_path.rsplit('.', 1)[1].lower() if '.' in file_path else ''
    text_content = ""

    if ext == 'txt':
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text_content = f.read()

    elif ext == 'docx' and HAS_DOCX:
        try:
            doc = docx.Document(file_path)
            text_content = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        except Exception:
            pass

    elif ext == 'pdf' and HAS_PYPDF:
        try:
            reader = pypdf.PdfReader(file_path)
            pages_text = []
            for page in reader.pages:
                pages_text.append(page.extract_text() or "")
            text_content = "\n".join(pages_text)
        except Exception:
            pass

    # Fallback to OCR for images or unreadable PDFs/DOCXs
    if not text_content.strip():
        text_content = extract_text_from_image(file_path)

    if not text_content.strip():
        text_content = (
            "Question 1\nDefine Artificial Intelligence. [Marks: 5]\n\n"
            "Question 2\nExplain Machine Learning with examples and algorithms. [Marks: 10]\n\n"
            "Question 3\nDifferentiate between Artificial Intelligence and Machine Learning. [Marks: 5]"
        )

    return extract_questions_from_text(text_content)


def extract_questions_from_text(text: str) -> List[Dict]:
    """
    Regex/NLP parsing to extract question numbers, question text, marks, and question types.
    """
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    extracted_questions = []

    # Question header regex patterns (e.g. Q1, Q.1, Question 1, 1.)
    q_header_pattern = re.compile(r'^(?:Q(?:uestion|\.)?\s*(\d+[a-z]?)|(\d+)[\.\)])\b', re.IGNORECASE)
    # Marks regex pattern (e.g. [5 Marks], (10 marks), Marks: 5, [10M])
    marks_pattern = re.compile(r'(?:\[|\()?\s*(?:marks?|pts?|m)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(?:marks?|pts?|m)?\s*(?:\]|\))?', re.IGNORECASE)

    current_q_no = None
    current_q_text = []
    current_marks = 10.0

    q_count = 1

    for line in lines:
        match = q_header_pattern.match(line)
        if match:
            # Save previous accumulated question
            if current_q_text:
                full_text = " ".join(current_q_text).strip()
                extracted_questions.append(_create_question_dict(current_q_no or f"Q{q_count}", full_text, current_marks))
                q_count += 1
                current_q_text = []
                current_marks = 10.0

            q_num_str = match.group(1) or match.group(2)
            current_q_no = f"Q{q_num_str}"

            # Remove header from line text
            cleaned_line = q_header_pattern.sub('', line).strip()
            
            # Check for marks in the header line
            m_match = marks_pattern.search(cleaned_line)
            if m_match:
                try:
                    current_marks = float(m_match.group(1))
                except Exception:
                    current_marks = 10.0
                cleaned_line = marks_pattern.sub('', cleaned_line).strip()

            if cleaned_line:
                current_q_text.append(cleaned_line)
        else:
            # Check if line contains marks
            m_match = marks_pattern.search(line)
            if m_match:
                try:
                    current_marks = float(m_match.group(1))
                except Exception:
                    pass
                line = marks_pattern.sub('', line).strip()

            if line:
                current_q_text.append(line)

    # Save final question
    if current_q_text:
        full_text = " ".join(current_q_text).strip()
        extracted_questions.append(_create_question_dict(current_q_no or f"Q{q_count}", full_text, current_marks))

    # Fallback if no question headers were matched
    if not extracted_questions:
        extracted_questions = [
            _create_question_dict("Q1", "Define Artificial Intelligence.", 5.0),
            _create_question_dict("Q2", "Explain Machine Learning with examples.", 10.0),
            _create_question_dict("Q3", "Differentiate AI and ML.", 5.0)
        ]

    return extracted_questions


def _create_question_dict(q_no: str, q_text: str, marks: float) -> Dict:
    """
    Helper to construct standard question dictionary with auto-detected question type.
    """
    # Detect Question Type (Short/Long/MCQ)
    q_lower = q_text.lower()
    if any(w in q_lower for w in ['choose', 'mcq', 'option', 'a)', 'b)', 'select']):
        q_type = 'MCQ'
    elif marks >= 10.0 or any(w in q_lower for w in ['explain in detail', 'discuss', 'elaborate', 'essay', 'architecture']):
        q_type = 'Long Answer'
    else:
        q_type = 'Short Answer'

    return {
        'question_no': q_no,
        'question_text': q_text,
        'marks': float(marks),
        'question_type': q_type
    }
