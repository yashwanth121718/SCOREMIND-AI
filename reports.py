import os
import csv
from datetime import datetime
from config import Config
from models import User, Exam, Subject, Question, StudentAnswer, Evaluation

# Graceful imports for PDF (ReportLab) and Excel (Pandas/openpyxl)
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except Exception:
    HAS_REPORTLAB = False

try:
    import pandas as pd
    HAS_PANDAS = True
except Exception:
    HAS_PANDAS = False


def generate_student_pdf_report(evaluation_id: int) -> str:
    """
    Generates a PDF report for a single evaluation.
    Returns absolute filepath of the generated PDF.
    """
    eval_rec = Evaluation.query.get(evaluation_id)
    if not eval_rec:
        raise ValueError(f"Evaluation with ID {evaluation_id} not found.")

    os.makedirs(Config.REPORT_FOLDER, exist_ok=True)
    filename = f"Evaluation_Report_Eval_{evaluation_id}_{eval_rec.student_id}.pdf"
    filepath = os.path.join(Config.REPORT_FOLDER, filename)

    student = eval_rec.student
    question = eval_rec.question
    exam = question.exam if question else None
    subject = exam.subject if exam else None

    if HAS_REPORTLAB:
        doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        
        # Custom Styles
        title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#00e5ff'), spaceAfter=12)
        h2_style = ParagraphStyle('SectionHeader', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#1b5e20'), spaceBefore=10, spaceAfter=8)
        body_style = ParagraphStyle('DocBody', parent=styles['BodyText'], fontSize=10, leading=14)

        story = []

        # Header Title
        story.append(Paragraph("Automated Answer Evaluation Report", title_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#00e5ff'), spaceAfter=15))

        # Metadata Table
        meta_data = [
            [Paragraph("<b>Student Name:</b>", body_style), Paragraph(student.name if student else 'N/A', body_style),
             Paragraph("<b>Date:</b>", body_style), Paragraph(eval_rec.evaluated_date.strftime('%Y-%m-%d'), body_style)],
            [Paragraph("<b>Subject:</b>", body_style), Paragraph(f"{subject.subject_name} ({subject.subject_code})" if subject else 'N/A', body_style),
             Paragraph("<b>Exam:</b>", body_style), Paragraph(exam.exam_name if exam else 'N/A', body_style)],
        ]
        t_meta = Table(meta_data, colWidths=[100, 180, 80, 180])
        t_meta.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f4f6f9')),
            ('PADDING', (0,0), (-1,-1), 6),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ]))
        story.append(t_meta)
        story.append(Spacer(1, 15))

        # Marks Summary Card Table
        scores_data = [
            ["Obtained Marks", "Max Marks", "Similarity Score", "Keyword Score", "Grammar Score"],
            [f"{eval_rec.obtained_marks:.2f}", f"{question.max_marks:.2f}", f"{eval_rec.similarity_score:.1f}%", f"{eval_rec.keyword_score:.1f}%", f"{eval_rec.grammar_score:.1f}%"]
        ]
        t_scores = Table(scores_data, colWidths=[108, 108, 108, 108, 108])
        t_scores.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1f2937')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#e5e7eb')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#9ca3af')),
        ]))
        story.append(t_scores)
        story.append(Spacer(1, 15))

        # Question & Answers
        story.append(Paragraph("Question", h2_style))
        story.append(Paragraph(question.question_text if question else 'N/A', body_style))
        story.append(Spacer(1, 10))

        story.append(Paragraph("Model Answer", h2_style))
        story.append(Paragraph(question.model_answer if question else 'N/A', body_style))
        story.append(Spacer(1, 10))

        student_ans = eval_rec.student_answer.answer_text if eval_rec.student_answer else 'N/A'
        story.append(Paragraph("Student's Submitted Answer", h2_style))
        story.append(Paragraph(student_ans, body_style))
        story.append(Spacer(1, 15))

        # AI Feedback & Keywords
        story.append(Paragraph("AI Diagnostic Feedback", h2_style))
        feedback_lines = eval_rec.feedback.replace('\n', '<br/>') if eval_rec.feedback else 'No detailed feedback.'
        story.append(Paragraph(feedback_lines, body_style))
        story.append(Spacer(1, 15))

        # Footer
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.gray, spaceBefore=20, spaceAfter=10))
        story.append(Paragraph("Generated by Automated Answer Script Evaluation System Using AI", ParagraphStyle('Footer', parent=body_style, fontSize=8, textColor=colors.gray, alignment=1)))

        doc.build(story)

    else:
        # Fallback Text File / Simple HTML representation if reportlab is unavailable
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"=== EVALUATION REPORT ===\n")
            f.write(f"Evaluation ID: {eval_rec.evaluation_id}\n")
            f.write(f"Student: {student.name if student else 'N/A'}\n")
            f.write(f"Exam: {exam.exam_name if exam else 'N/A'}\n")
            f.write(f"Obtained Marks: {eval_rec.obtained_marks} / {question.max_marks}\n")
            f.write(f"Similarity Score: {eval_rec.similarity_score}%\n")
            f.write(f"Keyword Score: {eval_rec.keyword_score}%\n")
            f.write(f"Grammar Score: {eval_rec.grammar_score}%\n")
            f.write(f"Feedback:\n{eval_rec.feedback}\n")

    return filepath


def generate_exam_excel_report(exam_id: int) -> str:
    """
    Generates an Excel/CSV report for an entire exam with all student evaluation statistics.
    Returns absolute filepath of the generated file.
    """
    exam = Exam.query.get(exam_id)
    if not exam:
        raise ValueError(f"Exam with ID {exam_id} not found.")

    os.makedirs(Config.REPORT_FOLDER, exist_ok=True)
    filename = f"Exam_Results_Exam_{exam_id}.xlsx" if HAS_PANDAS else f"Exam_Results_Exam_{exam_id}.csv"
    filepath = os.path.join(Config.REPORT_FOLDER, filename)

    questions = Question.query.filter_by(exam_id=exam_id).all()
    q_ids = [q.question_id for q in questions]

    evaluations = Evaluation.query.filter(Evaluation.question_id.in_(q_ids)).all() if q_ids else []

    rows = []
    for ev in evaluations:
        student = ev.student
        q = ev.question
        rows.append({
            'Evaluation ID': ev.evaluation_id,
            'Student ID': ev.student_id,
            'Student Name': student.name if student else 'N/A',
            'Student Email': student.email if student else 'N/A',
            'Question ID': ev.question_id,
            'Question Text': q.question_text[:50] + '...' if q else '',
            'Max Marks': q.max_marks if q else 10.0,
            'Obtained Marks': ev.obtained_marks,
            'Similarity Score (%)': ev.similarity_score,
            'Keyword Score (%)': ev.keyword_score,
            'Grammar Score (%)': ev.grammar_score,
            'Matched Keywords': ev.matched_keywords,
            'Missing Keywords': ev.missing_keywords,
            'Evaluated Date': ev.evaluated_date.strftime('%Y-%m-%d %H:%M') if ev.evaluated_date else ''
        })

    if HAS_PANDAS and filename.endswith('.xlsx'):
        df = pd.DataFrame(rows)
        df.to_excel(filepath, index=False, engine='openpyxl' if 'openpyxl' in str(pd.show_versions) else None)
    else:
        # CSV Fallback
        filepath = filepath.replace('.xlsx', '.csv')
        if rows:
            keys = rows[0].keys()
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                dict_writer = csv.DictWriter(f, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(rows)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("No evaluations recorded for this exam.\n")

    return filepath
