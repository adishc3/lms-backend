from sqlalchemy.orm import Session
from app.models.course import Course


def get_course(db: Session, course_id: int):
    return db.query(Course).filter(Course.id == course_id).first()


def get_courses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Course).offset(skip).limit(limit).all()


def create_course(db: Session, course_in, owner_id: int):
    course = Course(
        title=course_in.title,
        description=course_in.description,
        cover_image_url=course_in.cover_image_url,
        owner_id=owner_id,
        price=course_in.price or 0,
        is_paid=course_in.is_paid,
        prerequisite_course_id=course_in.prerequisite_course_id,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def update_course(db: Session, course: Course, course_in):
    course.title = course_in.title
    course.description = course_in.description
    course.cover_image_url = course_in.cover_image_url
    course.price = course_in.price or 0
    course.is_paid = course_in.is_paid
    course.prerequisite_course_id = course_in.prerequisite_course_id
    db.commit()
    db.refresh(course)
    return course


def delete_course(db: Session, course: Course):
    db.delete(course)
    db.commit()
