from sqlalchemy.orm import Session
from app.models.submission import Submission
from datetime import datetime, timezone


def create_submission(db: Session, assignment_id: int, user_id: int, content: str | None = None, file_path: str | None = None):
    existing = (
        db.query(Submission)
        .filter(Submission.assignment_id == assignment_id, Submission.user_id == user_id)
        .first()
    )
    now = datetime.now(timezone.utc)
    if existing:
        existing.content = content
        existing.file_path = file_path
        existing.submitted_at = now
        db.commit()
        db.refresh(existing)
        return existing

    sub = Submission(assignment_id=assignment_id, user_id=user_id, content=content, file_path=file_path)
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


def list_submissions_for_assignment(db: Session, assignment_id: int):
    return db.query(Submission).filter(Submission.assignment_id == assignment_id).all()


def grade_submission(db: Session, submission: Submission, grader_id: int, grade: int, feedback: str | None = None):
    submission.grade = grade
    submission.feedback = feedback
    submission.graded_at = datetime.now(timezone.utc)
    submission.graded_by = grader_id
    db.commit()
    db.refresh(submission)
    return submission


def get_submission(db: Session, submission_id: int):
    return db.query(Submission).filter(Submission.id == submission_id).first()
