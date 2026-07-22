import os
from sqlalchemy import create_engine, text
from config import Config
from models import db, User, Subject, Exam, Question, StudentAnswer, Evaluation
from ai_module import ai_evaluator

def init_db(app):
    """
    Initializes database with MySQL primary attempt and automatic SQLite fallback.
    """
    try:
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        connection = engine.connect()
        connection.close()
        app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
        print("[+] Connected successfully to MySQL Database!")
    except Exception as e:
        print(f"[!] MySQL Connection failed: {e}. Falling back to SQLite database...")
        os.makedirs(os.path.dirname(Config.SQLITE_DB_PATH), exist_ok=True)
        app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLITE_DATABASE_URI
        print(f"[+] SQLite Database connected at {Config.SQLITE_DB_PATH}")

    db.init_app(app)

    with app.app_context():
        db.create_all()
        seed_sample_data_if_empty()


def seed_sample_data_if_empty():
    """
    Seeds database with initial hackathon demonstration data if empty.
    """
    if User.query.first() is not None:
        return

    print("[+] Database empty. Seeding sample hackathon data...")

    # 1. Users
    admin = User(name="System Admin", email="admin@eval.ai", role="admin")
    admin.set_password("admin123")

    teacher1 = User(name="Dr. Alan Turing", email="turing@university.edu", role="teacher")
    teacher1.set_password("teacher123")

    teacher2 = User(name="Prof. Ada Lovelace", email="ada@university.edu", role="teacher")
    teacher2.set_password("teacher123")

    student1 = User(name="John Doe", email="john@student.edu", role="student")
    student1.set_password("student123")

    student2 = User(name="Jane Smith", email="jane@student.edu", role="student")
    student2.set_password("student123")

    student3 = User(name="Robert Paulson", email="robert@student.edu", role="student")
    student3.set_password("student123")

    db.session.add_all([admin, teacher1, teacher2, student1, student2, student3])
    db.session.commit()

    # 2. Subjects
    subj1 = Subject(subject_name="Data Structures & Algorithms", subject_code="CS201", teacher_id=teacher1.id)
    subj2 = Subject(subject_name="Database Management Systems", subject_code="CS301", teacher_id=teacher2.id)
    
    db.session.add_all([subj1, subj2])
    db.session.commit()

    # 3. Exams
    exam1 = Exam(subject_id=subj1.subject_id, exam_name="Mid-Term Assessment 2026", total_marks=20.0)
    exam2 = Exam(subject_id=subj2.subject_id, exam_name="DBMS Final Theory Exam", total_marks=10.0)

    db.session.add_all([exam1, exam2])
    db.session.commit()

    # 4. Questions
    q1 = Question(
        exam_id=exam1.exam_id,
        question_text="Explain the concept of Binary Search Trees (BST) and state its average-case search time complexity.",
        model_answer="A Binary Search Tree (BST) is a node-based binary tree data structure where the key in each node is greater than all keys in its left subtree and less than all keys in its right subtree. The average-case search time complexity is O(log n), whereas the worst-case search complexity is O(n) for a skewed tree.",
        keywords="node, binary tree, left subtree, right subtree, search complexity, O(log n), skewed tree",
        max_marks=10.0
    )

    q2 = Question(
        exam_id=exam1.exam_id,
        question_text="Describe QuickSort algorithm, pivot selection, and partition process.",
        model_answer="QuickSort is an efficient divide-and-conquer sorting algorithm. It selects a pivot element and partitions the array into two sub-arrays such that elements smaller than the pivot are placed before it and larger elements after it. Recursively sorting the sub-arrays yields O(n log n) average time complexity.",
        keywords="divide and conquer, pivot element, partition, recursion, sub-array, O(n log n)",
        max_marks=10.0
    )

    q3 = Question(
        exam_id=exam2.exam_id,
        question_text="What is ACID property in Database Management Systems? Explain each component.",
        model_answer="ACID stands for Atomicity, Consistency, Isolation, and Durability. Atomicity ensures all operations in a transaction succeed or none occur. Consistency ensures data matches database constraints before and after transactions. Isolation guarantees concurrent transactions do not interfere. Durability guarantees committed data persists even during crashes.",
        keywords="Atomicity, Consistency, Isolation, Durability, transaction, constraints, concurrency, persistence",
        max_marks=10.0
    )

    db.session.add_all([q1, q2, q3])
    db.session.commit()

    # 5. Student Answers
    ans1 = StudentAnswer(
        student_id=student1.id,
        question_id=q1.question_id,
        answer_text="A Binary Search Tree is a data structure where each node has at most two children. The left subtree contains values smaller than the root, and the right subtree contains larger values. Searching in a BST takes O(log n) average time complexity."
    )

    ans2 = StudentAnswer(
        student_id=student2.id,
        question_id=q1.question_id,
        answer_text="BST stands for Binary Search Tree. It stores numbers in a tree. You look at left and right node to find things. It is very fast."
    )

    ans3 = StudentAnswer(
        student_id=student1.id,
        question_id=q3.question_id,
        answer_text="ACID properties stand for Atomicity, Consistency, Isolation, and Durability. Atomicity means all or nothing. Consistency keeps data valid. Isolation makes transactions independent. Durability ensures data is saved permanently even if server crashes."
    )

    db.session.add_all([ans1, ans2, ans3])
    db.session.commit()

    # 6. Pre-evaluate
    for ans in [ans1, ans2, ans3]:
        q = Question.query.get(ans.question_id)
        res = ai_evaluator.evaluate_answer(
            model_answer=q.model_answer,
            student_answer=ans.answer_text,
            keywords=q.keywords or "",
            max_marks=q.max_marks
        )
        
        evaluation = Evaluation(
            answer_id=ans.answer_id,
            student_id=ans.student_id,
            question_id=ans.question_id,
            similarity_score=res['similarity_score'],
            grammar_score=res['grammar_score'],
            keyword_score=res['keyword_score'],
            confidence_score=res.get('confidence_score', 92.5),
            obtained_marks=res['obtained_marks'],
            feedback=res['feedback'],
            matched_keywords=res['matched_keywords'],
            missing_keywords=res['missing_keywords']
        )
        db.session.add(evaluation)

    db.session.commit()
    print("[+] Sample hackathon data seeded successfully!")
