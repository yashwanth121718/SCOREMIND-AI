from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'admin', 'teacher', 'student'
    profile_pic = db.Column(db.String(255), default='default_avatar.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    subjects = db.relationship('Subject', backref='teacher', lazy=True, cascade='all, delete-orphan')
    answers = db.relationship('StudentAnswer', backref='student', lazy=True, cascade='all, delete-orphan')
    evaluations = db.relationship('Evaluation', backref='student', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'profile_pic': self.profile_pic,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else ''
        }


class QuestionPaper(db.Model):
    __tablename__ = 'question_papers'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id', ondelete='CASCADE'), nullable=True)
    exam_name = db.Column(db.String(150), nullable=False)
    semester = db.Column(db.String(50), nullable=True, default='Semester 1')
    pdf_path = db.Column(db.String(255), nullable=True)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='draft')  # 'draft', 'reviewed', 'published'

    # Relationships
    teacher = db.relationship('User', backref='question_papers', lazy=True)
    subject = db.relationship('Subject', backref='question_papers', lazy=True)
    questions = db.relationship('Question', backref='question_paper', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.name if self.teacher else 'Unknown',
            'subject_id': self.subject_id,
            'subject_name': self.subject.subject_name if self.subject else 'Unassigned',
            'exam_name': self.exam_name,
            'semester': self.semester,
            'pdf_path': self.pdf_path,
            'upload_date': self.upload_date.strftime('%Y-%m-%d %H:%M') if self.upload_date else '',
            'status': self.status,
            'question_count': len(self.questions)
        }


class Subject(db.Model):
    __tablename__ = 'subjects'

    subject_id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(150), nullable=False)
    subject_code = db.Column(db.String(50), nullable=False, unique=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Relationships
    exams = db.relationship('Exam', backref='subject', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'subject_id': self.subject_id,
            'subject_name': self.subject_name,
            'subject_code': self.subject_code,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.name if self.teacher else 'Unassigned'
        }


class Exam(db.Model):
    __tablename__ = 'exams'

    exam_id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id', ondelete='CASCADE'), nullable=False)
    exam_name = db.Column(db.String(150), nullable=False)
    exam_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    total_marks = db.Column(db.Float, nullable=False, default=100.0)

    # Relationships
    questions = db.relationship('Question', backref='exam', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'exam_id': self.exam_id,
            'subject_id': self.subject_id,
            'subject_name': self.subject.subject_name if self.subject else '',
            'subject_code': self.subject.subject_code if self.subject else '',
            'exam_name': self.exam_name,
            'exam_date': str(self.exam_date),
            'total_marks': self.total_marks,
            'question_count': len(self.questions)
        }


class Question(db.Model):
    __tablename__ = 'questions'

    question_id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.exam_id', ondelete='CASCADE'), nullable=True)
    paper_id = db.Column(db.Integer, db.ForeignKey('question_papers.id', ondelete='CASCADE'), nullable=True)
    
    question_no = db.Column(db.String(20), nullable=True, default='Q1')
    question_text = db.Column(db.Text, nullable=False)
    model_answer = db.Column(db.Text, nullable=True)
    keywords = db.Column(db.Text, nullable=True)  # Comma-separated or JSON list
    max_marks = db.Column(db.Float, nullable=False, default=10.0)
    
    question_type = db.Column(db.String(50), nullable=True, default='Short Answer')  # Short, Long, MCQ
    difficulty = db.Column(db.String(50), nullable=True, default='Medium')           # Easy, Medium, Hard
    blooms_level = db.Column(db.String(100), nullable=True, default='Understand')
    expected_length = db.Column(db.String(50), nullable=True, default='40-70 words')

    # Relationships
    answers = db.relationship('StudentAnswer', backref='question', lazy=True, cascade='all, delete-orphan')
    evaluations = db.relationship('Evaluation', backref='question', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'question_id': self.question_id,
            'exam_id': self.exam_id,
            'paper_id': self.paper_id,
            'question_no': self.question_no,
            'question_text': self.question_text,
            'model_answer': self.model_answer or '',
            'keywords': self.keywords or '',
            'max_marks': self.max_marks,
            'question_type': self.question_type,
            'difficulty': self.difficulty,
            'blooms_level': self.blooms_level,
            'expected_length': self.expected_length
        }


class StudentAnswer(db.Model):
    __tablename__ = 'student_answers'

    answer_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id', ondelete='CASCADE'), nullable=False)
    answer_text = db.Column(db.Text, nullable=True)
    uploaded_file = db.Column(db.String(255), nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    evaluation = db.relationship('Evaluation', backref='student_answer', uselist=False, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'answer_id': self.answer_id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else 'Unknown',
            'question_id': self.question_id,
            'answer_text': self.answer_text,
            'uploaded_file': self.uploaded_file,
            'submitted_at': self.submitted_at.strftime('%Y-%m-%d %H:%M') if self.submitted_at else ''
        }


class Evaluation(db.Model):
    __tablename__ = 'evaluations'

    evaluation_id = db.Column(db.Integer, primary_key=True)
    answer_id = db.Column(db.Integer, db.ForeignKey('student_answers.answer_id', ondelete='CASCADE'), nullable=False, unique=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id', ondelete='CASCADE'), nullable=False)
    
    similarity_score = db.Column(db.Float, nullable=False, default=0.0)  # Percentage 0-100
    grammar_score = db.Column(db.Float, nullable=False, default=0.0)     # Percentage 0-100
    keyword_score = db.Column(db.Float, nullable=False, default=0.0)     # Percentage 0-100
    confidence_score = db.Column(db.Float, nullable=False, default=90.0)  # AI Confidence percentage
    obtained_marks = db.Column(db.Float, nullable=False, default=0.0)
    
    teacher_marks = db.Column(db.Float, nullable=True)                   # Override marks if teacher edits
    is_verified = db.Column(db.Boolean, default=False)                   # Teacher verification flag
    teacher_feedback = db.Column(db.Text, nullable=True)                 # Teacher notes/feedback
    status = db.Column(db.String(50), default='pending')                 # 'pending', 'verified', 'published'
    
    feedback = db.Column(db.Text, nullable=True)
    matched_keywords = db.Column(db.Text, nullable=True)
    missing_keywords = db.Column(db.Text, nullable=True)
    evaluated_date = db.Column(db.DateTime, default=datetime.utcnow)

    def final_marks(self):
        return self.teacher_marks if self.teacher_marks is not None else self.obtained_marks

    def to_dict(self):
        return {
            'evaluation_id': self.evaluation_id,
            'answer_id': self.answer_id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else 'Unknown',
            'question_id': self.question_id,
            'question_text': self.question.question_text if self.question else '',
            'max_marks': self.question.max_marks if self.question else 10.0,
            'similarity_score': round(self.similarity_score, 2),
            'grammar_score': round(self.grammar_score, 2),
            'keyword_score': round(self.keyword_score, 2),
            'confidence_score': round(self.confidence_score, 2),
            'obtained_marks': round(self.obtained_marks, 2),
            'teacher_marks': round(self.teacher_marks, 2) if self.teacher_marks is not None else None,
            'final_marks': round(self.final_marks(), 2),
            'is_verified': self.is_verified,
            'status': self.status,
            'feedback': self.feedback,
            'teacher_feedback': self.teacher_feedback,
            'matched_keywords': self.matched_keywords,
            'missing_keywords': self.missing_keywords,
            'evaluated_date': self.evaluated_date.strftime('%Y-%m-%d %H:%M') if self.evaluated_date else ''
        }

