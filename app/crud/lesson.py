from sqlalchemy.orm import Session
from app.models.lesson import Lesson
from app.core.sanitization import sanitize_html


def get_lesson(db: Session, lesson_id: int):
    return db.query(Lesson).filter(Lesson.id == lesson_id).first()


def get_lessons_by_course(db: Session, course_id: int):
    return db.query(Lesson).filter(Lesson.course_id == course_id).all()


def create_lesson(db: Session, lesson_in, course_id: int, asset_path: str | None = None):
    lesson = Lesson(
        title=lesson_in.title,
        content=sanitize_html(lesson_in.content),
        course_id=course_id,
        asset_path=asset_path,
    )
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


def set_lesson_asset(db: Session, lesson: Lesson, asset_path: str):
    lesson.asset_path = asset_path
    db.commit()
    db.refresh(lesson)
    return lesson
