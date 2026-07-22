from datetime import datetime
from models import db, StudentAnswer, Question, Evaluation
from ai_module import ai_evaluator
from config import Config

def evaluate_single_answer(answer_id: int) -> Evaluation:
    """
    Evaluates a single student answer by ID and saves/updates the Evaluation record in DB.
    """
    answer = db.session.get(StudentAnswer, answer_id)
    if not answer:
        raise ValueError(f"StudentAnswer with ID {answer_id} not found.")

    question = db.session.get(Question, answer.question_id)
    if not question:
        raise ValueError(f"Question with ID {answer.question_id} not found.")

    text_content = answer.answer_text or ""
    
    res = ai_evaluator.evaluate_answer(
        model_answer=question.model_answer,
        student_answer=text_content,
        keywords=question.keywords or "",
        max_marks=question.max_marks,
        sim_weight=Config.SIMILARITY_WEIGHT,
        kw_weight=Config.KEYWORD_WEIGHT,
        gram_weight=Config.GRAMMAR_WEIGHT
    )

    eval_record = Evaluation.query.filter_by(answer_id=answer_id).first()
    if not eval_record:
        eval_record = Evaluation(
            answer_id=answer_id,
            student_id=answer.student_id,
            question_id=answer.question_id
        )
        db.session.add(eval_record)

    eval_record.similarity_score = res['similarity_score']
    eval_record.grammar_score = res['grammar_score']
    eval_record.keyword_score = res['keyword_score']
    eval_record.confidence_score = res.get('confidence_score', 90.0)
    eval_record.obtained_marks = res['obtained_marks']
    eval_record.feedback = res['feedback']
    eval_record.matched_keywords = res['matched_keywords']
    eval_record.missing_keywords = res['missing_keywords']
    eval_record.evaluated_date = datetime.utcnow()

    db.session.commit()
    return eval_record


def evaluate_exam_answers(exam_id: int) -> int:
    """
    Evaluates all pending or existing student answers for a specific exam.
    Returns the count of evaluated answers.
    """
    questions = Question.query.filter_by(exam_id=exam_id).all()
    question_ids = [q.question_id for q in questions]

    if not question_ids:
        return 0

    answers = StudentAnswer.query.filter(StudentAnswer.question_id.in_(question_ids)).all()
    count = 0

    for ans in answers:
        evaluate_single_answer(ans.answer_id)
        count += 1

    return count
