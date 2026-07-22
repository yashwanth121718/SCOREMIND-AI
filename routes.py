import os
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, Subject, Exam, Question, StudentAnswer, Evaluation
from ai_module import ai_evaluator
from evaluation import evaluate_single_answer, evaluate_exam_answers
from reports import generate_student_pdf_report, generate_exam_excel_report
from config import Config

auth_bp = Blueprint('auth', __name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')
student_bp = Blueprint('student', __name__, url_prefix='/student')
common_bp = Blueprint('common', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['teacher', 'admin']:
            flash('Teacher privileges required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['student', 'admin']:
            flash('Student account required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# ================= AUTH ROUTES =================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_role_dashboard(current_user.role)

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect_role_dashboard(user.role)
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect_role_dashboard(current_user.role)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'student').lower()

        if role not in ['teacher', 'student']:
            role = 'student'

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address is already registered.', 'warning')
        else:
            new_user = User(name=name, email=email, role=role)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login with your credentials.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('common.home'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        new_password = request.form.get('new_password', '')
        
        if name:
            current_user.name = name

        if new_password:
            current_user.set_password(new_password)
            flash('Password updated successfully.', 'success')

        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"user_{current_user.id}_{file.filename}")
                os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
                file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
                current_user.profile_pic = filename

        db.session.commit()
        flash('Profile details updated.', 'success')

    return render_template('profile.html', user=current_user)

def redirect_role_dashboard(role):
    if role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif role == 'teacher':
        return redirect(url_for('teacher.dashboard'))
    else:
        return redirect(url_for('student.dashboard'))


# ================= COMMON & LANDING ROUTES =================
@common_bp.route('/')
def home():
    return render_template('index.html')


# ================= ADMIN ROUTES =================
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_teachers = User.query.filter_by(role='teacher').count()
    total_students = User.query.filter_by(role='student').count()
    total_subjects = Subject.query.count()
    total_exams = Exam.query.count()
    total_evaluations = Evaluation.query.count()

    # Calculate Average Marks and Pass Percentage
    evaluations = Evaluation.query.all()
    if evaluations:
        avg_marks = sum(e.obtained_marks for e in evaluations) / len(evaluations)
        pass_count = sum(1 for e in evaluations if (e.obtained_marks / (e.question.max_marks if e.question else 10.0)) >= 0.50)
        pass_pct = (pass_count / len(evaluations)) * 100.0
        avg_sim = sum(e.similarity_score for e in evaluations) / len(evaluations)
    else:
        avg_marks = 0.0
        pass_pct = 0.0
        avg_sim = 0.0

    recent_users = User.query.order_by(User.id.desc()).limit(10).all()
    recent_evaluations = Evaluation.query.order_by(Evaluation.evaluation_id.desc()).limit(10).all()

    return render_template('admin_dashboard.html',
                           total_users=total_users,
                           total_teachers=total_teachers,
                           total_students=total_students,
                           total_subjects=total_subjects,
                           total_exams=total_exams,
                           total_evaluations=total_evaluations,
                           avg_marks=round(avg_marks, 2),
                           pass_pct=round(pass_pct, 1),
                           avg_sim=round(avg_sim, 1),
                           recent_users=recent_users,
                           recent_evaluations=recent_evaluations)

@admin_bp.route('/user/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        flash('You cannot delete your own admin account.', 'danger')
        return redirect(url_for('admin.dashboard'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.name} removed successfully.', 'success')
    return redirect(url_for('admin.dashboard'))


# ================= TEACHER ROUTES =================
@teacher_bp.route('/dashboard')
@login_required
@teacher_required
def dashboard():
    subjects = Subject.query.filter_by(teacher_id=current_user.id).all() if current_user.role == 'teacher' else Subject.query.all()
    subj_ids = [s.subject_id for s in subjects]
    exams = Exam.query.filter(Exam.subject_id.in_(subj_ids)).all() if subj_ids else []
    
    exam_ids = [e.exam_id for e in exams]
    questions = Question.query.filter(Question.exam_id.in_(exam_ids)).all() if exam_ids else []
    q_ids = [q.question_id for q in questions]

    answers = StudentAnswer.query.filter(StudentAnswer.question_id.in_(q_ids)).all() if q_ids else []
    evaluations = Evaluation.query.filter(Evaluation.question_id.in_(q_ids)).all() if q_ids else []

    # Analytics for Teacher: Top Performing Students & Weak Topics
    student_scores = {}
    for ev in evaluations:
        s_name = ev.student.name if ev.student else 'Unknown'
        student_scores[s_name] = student_scores.get(s_name, 0.0) + ev.obtained_marks

    top_students = sorted(student_scores.items(), key=lambda x: x[1], reverse=True)[:5]

    # Weak topics (Questions with low average score)
    weak_topics = []
    for q in questions:
        q_evals = [e for e in evaluations if e.question_id == q.question_id]
        if q_evals:
            avg_score = sum(e.obtained_marks for e in q_evals) / len(q_evals)
            if (avg_score / q.max_marks) < 0.65:
                weak_topics.append({
                    'question_text': q.question_text[:60] + '...',
                    'avg_score': round(avg_score, 1),
                    'max_marks': q.max_marks
                })

    all_teachers = User.query.filter_by(role='teacher').all()

    return render_template('teacher_dashboard.html',
                           subjects=subjects,
                           exams=exams,
                           questions=questions,
                           answers=answers,
                           evaluations=evaluations,
                           top_students=top_students,
                           weak_topics=weak_topics,
                           all_teachers=all_teachers)

@teacher_bp.route('/subject/add', methods=['POST'])
@login_required
@teacher_required
def add_subject():
    name = request.form.get('subject_name', '').strip()
    code = request.form.get('subject_code', '').strip().upper()
    teacher_id = request.form.get('teacher_id') or current_user.id

    if name and code:
        existing = Subject.query.filter_by(subject_code=code).first()
        if existing:
            flash(f'Subject code {code} already exists.', 'warning')
        else:
            subj = Subject(subject_name=name, subject_code=code, teacher_id=teacher_id)
            db.session.add(subj)
            db.session.commit()
            flash(f'Subject "{name}" created.', 'success')
    return redirect(url_for('teacher.dashboard'))

@teacher_bp.route('/exam/add', methods=['POST'])
@login_required
@teacher_required
def add_exam():
    subject_id = request.form.get('subject_id')
    exam_name = request.form.get('exam_name', '').strip()
    total_marks = float(request.form.get('total_marks') or 100.0)

    if subject_id and exam_name:
        exam = Exam(subject_id=subject_id, exam_name=exam_name, total_marks=total_marks)
        db.session.add(exam)
        db.session.commit()
        flash(f'Exam "{exam_name}" created.', 'success')
    return redirect(url_for('teacher.dashboard'))

@teacher_bp.route('/question/add', methods=['POST'])
@login_required
@teacher_required
def add_question():
    exam_id = request.form.get('exam_id')
    question_text = request.form.get('question_text', '').strip()
    model_answer = request.form.get('model_answer', '').strip()
    keywords = request.form.get('keywords', '').strip()
    max_marks = float(request.form.get('max_marks') or 10.0)

    if exam_id and question_text and model_answer:
        q = Question(exam_id=exam_id, question_text=question_text, model_answer=model_answer, keywords=keywords, max_marks=max_marks)
        db.session.add(q)
        db.session.commit()
        flash('Question and model answer added successfully.', 'success')
    return redirect(url_for('teacher.dashboard'))

@teacher_bp.route('/evaluate/<int:answer_id>', methods=['POST', 'GET'])
@login_required
@teacher_required
def trigger_evaluation(answer_id):
    try:
        eval_rec = evaluate_single_answer(answer_id)
        flash(f'Answer evaluated successfully! Score: {eval_rec.obtained_marks}/{eval_rec.question.max_marks}', 'success')
    except Exception as e:
        flash(f'Evaluation failed: {str(e)}', 'danger')
    return redirect(url_for('teacher.dashboard'))

@teacher_bp.route('/evaluate-exam/<int:exam_id>', methods=['POST', 'GET'])
@login_required
@teacher_required
def trigger_exam_evaluation(exam_id):
    try:
        count = evaluate_exam_answers(exam_id)
        flash(f'Successfully batch-evaluated {count} student answer scripts for Exam #{exam_id}.', 'success')
    except Exception as e:
        flash(f'Batch evaluation error: {str(e)}', 'danger')
    return redirect(url_for('teacher.dashboard'))

@teacher_bp.route('/export-excel/<int:exam_id>')
@login_required
@teacher_required
def export_excel(exam_id):
    try:
        filepath = generate_exam_excel_report(exam_id)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        flash(f'Failed to export report: {str(e)}', 'danger')
        return redirect(url_for('teacher.dashboard'))


# ================= STUDENT ROUTES =================
@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    exams = Exam.query.all()
    questions = Question.query.all()
    my_answers = StudentAnswer.query.filter_by(student_id=current_user.id).all()
    my_evaluations = Evaluation.query.filter_by(student_id=current_user.id).all()

    ans_map = {ans.question_id: ans for ans in my_answers}
    eval_map = {ev.question_id: ev for ev in my_evaluations}

    # Student progress metrics
    total_assigned = len(questions)
    total_submitted = len(my_answers)
    progress_pct = (total_submitted / total_assigned * 100.0) if total_assigned > 0 else 0.0

    return render_template('student_dashboard.html',
                           exams=exams,
                           questions=questions,
                           ans_map=ans_map,
                           eval_map=eval_map,
                           my_evaluations=my_evaluations,
                           progress_pct=round(progress_pct, 1))

@student_bp.route('/submit/<int:question_id>', methods=['GET', 'POST'])
@login_required
@student_required
def submit_answer(question_id):
    question = Question.query.get_or_404(question_id)

    if request.method == 'POST':
        answer_text = request.form.get('answer_text', '').strip()
        file = request.files.get('uploaded_file')

        saved_filename = None
        if file and allowed_file(file.filename):
            saved_filename = secure_filename(f"script_q{question_id}_u{current_user.id}_{file.filename}")
            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
            filepath = os.path.join(Config.UPLOAD_FOLDER, saved_filename)
            file.save(filepath)

            if saved_filename.endswith('.txt'):
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    answer_text = f.read()

        if not answer_text and not saved_filename:
            flash('Please enter text answer or upload a valid answer script file.', 'warning')
            return redirect(url_for('student.submit_answer', question_id=question_id))

        existing_ans = StudentAnswer.query.filter_by(student_id=current_user.id, question_id=question_id).first()
        if not existing_ans:
            existing_ans = StudentAnswer(student_id=current_user.id, question_id=question_id)
            db.session.add(existing_ans)

        existing_ans.answer_text = answer_text
        if saved_filename:
            existing_ans.uploaded_file = saved_filename

        db.session.commit()

        try:
            evaluate_single_answer(existing_ans.answer_id)
            flash('Answer submitted and evaluated by AI successfully!', 'success')
        except Exception as e:
            flash('Answer submitted. Evaluation queued.', 'info')

        return redirect(url_for('student.dashboard'))

    return render_template('upload_answers.html', question=question)

@student_bp.route('/result/<int:eval_id>')
@login_required
def view_result(eval_id):
    eval_rec = Evaluation.query.get_or_404(eval_id)
    
    if current_user.role == 'student' and eval_rec.student_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('student.dashboard'))

    return render_template('evaluation.html', eval=eval_rec)

@student_bp.route('/download-pdf/<int:eval_id>')
@login_required
def download_pdf(eval_id):
    eval_rec = Evaluation.query.get_or_404(eval_id)
    if current_user.role == 'student' and eval_rec.student_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('student.dashboard'))

    try:
        filepath = generate_student_pdf_report(eval_id)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        flash(f'PDF generation failed: {str(e)}', 'danger')
        return redirect(url_for('student.view_result', eval_id=eval_id))
