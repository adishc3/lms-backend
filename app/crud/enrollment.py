from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.enrollment import Enrollment
from app.models.user import User


def get_enrollment(db: Session, user_id: int, course_id: int):
    return db.query(Enrollment).filter(Enrollment.user_id == user_id, Enrollment.course_id == course_id).first()


def create_enrollment(db: Session, user_id: int, course_id: int):
    enrollment = Enrollment(user_id=user_id, course_id=course_id)
    db.add(enrollment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return enrollment
    db.refresh(enrollment)
    return enrollment


def list_enrollments_for_user(db: Session, user_id: int):
    return db.query(Enrollment).filter(Enrollment.user_id == user_id).all()


def get_enrolled_students_by_course(db: Session, course_id: int) -> list[User]:
    return db.query(User).join(Enrollment).filter(Enrollment.course_id == course_id).all()
