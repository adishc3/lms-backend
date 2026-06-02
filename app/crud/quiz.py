from sqlalchemy.orm import Session
from app.models.quiz import Quiz, Question, Option, QuizAttempt, AttemptAnswer
from app.schemas.quiz import QuizCreate, QuizAttemptCreate


def get_quiz(db: Session, quiz_id: int):
    return db.query(Quiz).filter(Quiz.id == quiz_id).first()


def get_quizzes_by_course(db: Session, course_id: int):
    return db.query(Quiz).filter(Quiz.course_id == course_id).all()


def create_quiz(db: Session, quiz_in: QuizCreate, owner_id: int):
    quiz = Quiz(
        title=quiz_in.title,
        description=quiz_in.description,
        course_id=quiz_in.course_id,
        owner_id=owner_id,
    )
    db.add(quiz)
    db.flush()

    for question_in in quiz_in.questions:
        question = Question(text=question_in.text, quiz_id=quiz.id)
        db.add(question)
        db.flush()
        for option_in in question_in.options:
            db.add(
                Option(
                    text=option_in.text,
                    is_correct=option_in.is_correct,
                    question_id=question.id,
                )
            )

    db.commit()
    db.refresh(quiz)
    return quiz


def get_quiz_attempt(db: Session, attempt_id: int):
    return db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()


def get_attempts_for_quiz(db: Session, quiz_id: int):
    return db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).all()


def get_attempts_for_user(db: Session, user_id: int, quiz_id: int | None = None):
    query = db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id)
    if quiz_id is not None:
        query = query.filter(QuizAttempt.quiz_id == quiz_id)
    return query.all()


def get_option(db: Session, option_id: int):
    return db.query(Option).filter(Option.id == option_id).first()


def get_question(db: Session, question_id: int):
    return db.query(Question).filter(Question.id == question_id).first()


def submit_quiz_attempt(db: Session, user_id: int, quiz_id: int, attempt_in: QuizAttemptCreate):
    quiz = get_quiz(db, quiz_id)
    if not quiz:
        return None

    attempt = QuizAttempt(
        user_id=user_id,
        quiz_id=quiz_id,
        score=0,
        total=len(quiz.questions),
    )
    db.add(attempt)
    db.flush()

    score = 0
    for answer_data in attempt_in.answers:
        question = get_question(db, answer_data.question_id)
        if not question or question.quiz_id != quiz_id:
            continue
        option = get_option(db, answer_data.selected_option_id)
        if not option or option.question_id != question.id:
            continue

        is_correct = bool(option.is_correct)
        if is_correct:
            score += 1

        db.add(
            AttemptAnswer(
                attempt_id=attempt.id,
                question_id=question.id,
                selected_option_id=option.id,
                is_correct=is_correct,
            )
        )

    attempt.score = score
    db.commit()
    db.refresh(attempt)
    return attempt
