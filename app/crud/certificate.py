from sqlalchemy.orm import Session
from app.models.certificate import Certificate


def create_certificate(db: Session, user_id: int, course_id: int) -> Certificate:
    existing = (
        db.query(Certificate)
        .filter(Certificate.user_id == user_id, Certificate.course_id == course_id)
        .first()
    )
    if existing:
        return existing

    cert = Certificate(user_id=user_id, course_id=course_id)
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert


def get_certificate_by_user_course(db: Session, user_id: int, course_id: int):
    return (
        db.query(Certificate)
        .filter(Certificate.user_id == user_id, Certificate.course_id == course_id)
        .first()
    )
