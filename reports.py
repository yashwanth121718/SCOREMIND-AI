import os
import csv
from datetime import datetime
from config import Config
from models import db, User, Exam, Subject, Question, StudentAnswer, Evaluation

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
    Includes College Header, Student/Subject/Exam Info, AI Score, Marks, Teacher Signature line, Date.
    """
    eval_rec = db.session.get(Evaluation, evaluation_id)
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
        
        hdr_style = ParagraphStyle('CollegeLogoHdr', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#0f2027'), alignment=1, spaceAfter=2)
        sub_hdr_style = ParagraphStyle('CollegeSubHdr', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#4a5568'), alignment=1, spaceAfter=12)
        title_style = ParagraphStyle('DocTitle', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#00b0ff'), spaceAfter=10, alignment=1)
        h2_style = ParagraphStyle('SectionHeader', parent=styles['Heading3'], fontSize=12, textColor=colors.HexColor('#1b5e20'), spaceBefore=8, spaceAfter=6)
        body_style = ParagraphStyle('DocBody', parent=styles['BodyText'], fontSize=9.5, leading=13.5)

        story = []

        story.append(Paragraph("<b>UNIVERSITY COLLEGE OF ENGINEERING & TECHNOLOGY</b>", hdr_style))
        story.append(Paragraph("Department of Computer Science & Engineering | Automated AI Script Evaluation", sub_hdr_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#00e5ff'), spaceAfter=12))

        story.append(Paragraph("STUDENT EVALUATION & DIAGNOSTIC GRADE SHEET", title_style))

        meta_data = [
            [Paragraph("<b>Student Name:</b>", body_style), Paragraph(student.name if student else 'N/A', body_style),
             Paragraph("<b>Date of Eval:</b>", body_style), Paragraph(eval_rec.evaluated_date.strftime('%Y-%m-%d %H:%M'), body_style)],
            [Paragraph("<b>Roll / Email:</b>", body_style), Paragraph(student.email if student else 'N/A', body_style),
             Paragraph("<b>Subject:</b>", body_style), Paragraph(f"{subject.subject_name} ({subject.subject_code})" if subject else 'N/A', body_style)],
            [Paragraph("<b>Exam Title:</b>", body_style), Paragraph(exam.exam_name if exam else 'N/A', body_style),
             Paragraph("<b>Evaluator:</b>", body_style), Paragraph("EvalAI Engine v2.0", body_style)],
        ]
        t_meta = Table(meta_data, colWidths=[90, 190, 80, 180])
        t_meta.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('PADDING', (0,0), (-1,-1), 5),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ]))
        story.append(t_meta)
        story.append(Spacer(1, 12))

        conf_score = getattr(eval_rec, 'confidence_score', 92.5)
        scores_data = [
            ["Obtained Marks", "Max Marks", "Similarity Match", "Keyword Match", "Grammar Score", "AI Confidence"],
            [f"{eval_rec.obtained_marks:.2f}", f"{question.max_marks:.2f}", f"{eval_rec.similarity_score:.1f}%", f"{eval_rec.keyword_score:.1f}%", f"{eval_rec.grammar_score:.1f}%", f"{conf_score:.1f}%"]
        ]
        t_scores = Table(scores_data, colWidths=[90, 90, 90, 90, 90, 90])
        t_scores.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#f1f5f9')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#94a3b8')),
        ]))
        story.append(t_scores)
        story.append(Spacer(1, 12))

        story.append(Paragraph("Question Prompt", h2_style))
        story.append(Paragraph(question.question_text if question else 'N/A', body_style))
        story.append(Spacer(1, 8))

        story.append(Paragraph("Model Reference Answer", h2_style))
        story.append(Paragraph(question.model_answer if question else 'N/A', body_style))
        story.append(Spacer(1, 8))

        student_ans = eval_rec.student_answer.answer_text if eval_rec.student_answer else 'N/A'
        story.append(Paragraph("Student's Submitted Answer", h2_style))
        story.append(Paragraph(student_ans, body_style))
        story.append(Spacer(1, 12))

        story.append(Paragraph("AI Diagnostic Feedback & Analysis", h2_style))
        feedback_lines = eval_rec.feedback.replace('\n', '<br/>') if eval_rec.feedback else 'No feedback.'
        story.append(Paragraph(feedback_lines, body_style))
        story.append(Spacer(1, 20))

        sig_data = [
            [Paragraph("<b>Evaluator Signature:</b> _______________________", body_style),
             Paragraph("<b>Verified Date:</b> _______________________", body_style)]
        ]
        t_sig = Table(sig_data, colWidths=[270, 270])
        t_sig.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(t_sig)

        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.gray, spaceBefore=15, spaceAfter=8))
        story.append(Paragraph("Automated Answer Script Evaluation System - Official Grade Record", ParagraphStyle('Footer', parent=body_style, fontSize=7.5, textColor=colors.gray, alignment=1)))

        doc.build(story)

    else:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"=== UNIVERSITY COLLEGE OF ENGINEERING & TECHNOLOGY ===\n")
            f.write(f"Evaluation ID: {eval_rec.evaluation_id}\n")
            f.write(f"Student: {student.name if student else 'N/A'}\n")
            f.write(f"Exam: {exam.exam_name if exam else 'N/A'}\n")
            f.write(f"Obtained Marks: {eval_rec.obtained_marks} / {question.max_marks}\n")
            f.write(f"Similarity Score: {eval_rec.similarity_score}%\n")
            f.write(f"Keyword Score: {eval_rec.keyword_score}%\n")
            f.write(f"Feedback:\n{eval_rec.feedback}\n")
            f.write(f"\nTeacher Signature: _______________________\n")

    return filepath


def generate_exam_excel_report(exam_id: int) -> str:
    """
    Generates an Excel report for an entire exam with student-wise marks, subject results, stats, pass percentage.
    """
    exam = db.session.get(Exam, exam_id)
    if not exam:
        raise ValueError(f"Exam with ID {exam_id} not found.")

    os.makedirs(Config.REPORT_FOLDER, exist_ok=True)
    filename = f"Exam_Results_Exam_{exam_id}.xlsx" if HAS_PANDAS else f"Exam_Results_Exam_{exam_id}.csv"
    filepath = os.path.join(Config.REPORT_FOLDER, filename)

    questions = Question.query.filter_by(exam_id=exam_id).all()
    q_ids = [q.question_id for q in questions]

    evaluations = Evaluation.query.filter(Evaluation.question_id.in_(q_ids)).all() if q_ids else []

    rows = []
    total_obtained = 0.0
    total_max = 0.0
    pass_count = 0

    for ev in evaluations:
        student = ev.student
        q = ev.question
        max_m = q.max_marks if q else 10.0
        obt_m = ev.obtained_marks
        pass_status = "PASS" if (obt_m / max_m) >= 0.50 else "FAIL"

        if pass_status == "PASS":
            pass_count += 1
        total_obtained += obt_m
        total_max += max_m

        rows.append({
            'Evaluation ID': ev.evaluation_id,
            'Student ID': ev.student_id,
            'Student Name': student.name if student else 'N/A',
            'Student Email': student.email if student else 'N/A',
            'Subject Code': exam.subject.subject_code if exam.subject else 'N/A',
            'Subject Name': exam.subject.subject_name if exam.subject else 'N/A',
            'Exam Name': exam.exam_name,
            'Question ID': ev.question_id,
            'Max Marks': max_m,
            'Obtained Marks': obt_m,
            'Pass Status': pass_status,
            'Similarity Score (%)': ev.similarity_score,
            'Keyword Score (%)': ev.keyword_score,
            'Grammar Score (%)': ev.grammar_score,
            'AI Confidence (%)': getattr(ev, 'confidence_score', 92.5),
            'Matched Keywords': ev.matched_keywords,
            'Missing Keywords': ev.missing_keywords,
            'Evaluated Date': ev.evaluated_date.strftime('%Y-%m-%d %H:%M') if ev.evaluated_date else ''
        })

    if HAS_PANDAS and filename.endswith('.xlsx'):
        df = pd.DataFrame(rows)
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Student Evaluation Results', index=False)
            
            total_students = len(evaluations)
            avg_score = (total_obtained / total_students) if total_students > 0 else 0.0
            pass_pct = (pass_count / total_students * 100.0) if total_students > 0 else 0.0
            
            summary_df = pd.DataFrame([{
                'Exam Name': exam.exam_name,
                'Total Evaluated Scripts': total_students,
                'Passed Students': pass_count,
                'Pass Percentage (%)': round(pass_pct, 2),
                'Average Marks Obtained': round(avg_score, 2),
                'Generated Date': datetime.now().strftime('%Y-%m-%d %H:%M')
            }])
            summary_df.to_excel(writer, sheet_name='Exam Statistics Summary', index=False)
    else:
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
