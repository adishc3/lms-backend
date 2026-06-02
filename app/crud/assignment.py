from sqlalchemy.orm import Session
from app.models.assignment import Assignment


def create_assignment(db: Session, course_id: int, title: str, description: str | None = None, due_date=None, max_score: int | None = None):
    assignment = Assignment(
        course_id=course_id,
        title=title,
        description=description,
        due_date=due_date,
        max_score=max_score,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


def get_assignment(db: Session, assignment_id: int):
    return db.query(Assignment).filter(Assignment.id == assignment_id).first()


def list_assignments_for_course(db: Session, course_id: int):
    return db.query(Assignment).filter(Assignment.course_id == course_id).all()
