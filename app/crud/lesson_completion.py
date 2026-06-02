from sqlalchemy.orm import Session
from datetime import datetime
from app.models.lesson_completion import LessonCompletion
from app.models.enrollment import Enrollment


def get_completion(db: Session, user_id: int, lesson_id: int):
    return (
        db.query(LessonCompletion)
        .filter(LessonCompletion.user_id == user_id, LessonCompletion.lesson_id == lesson_id)
        .first()
    )


def mark_completion(db: Session, user_id: int, lesson_id: int, time_spent_minutes: int | None = None):
    existing = get_completion(db, user_id, lesson_id)
    if existing:
        existing.completed_at = datetime.utcnow()
        if time_spent_minutes is not None:
            existing.time_spent_minutes = time_spent_minutes
        db.commit()
        db.refresh(existing)
        return existing

    completion = LessonCompletion(
        user_id=user_id,
        lesson_id=lesson_id,
        time_spent_minutes=time_spent_minutes,
    )
    db.add(completion)
    db.commit()
    db.refresh(completion)
    # After marking completion, check if user has completed all lessons for the course
    try:
        from app.models.lesson import Lesson
        from app.crud.certificate import create_certificate, get_certificate_by_user_course
        from app.crud.badge import award_milestone_badges

        lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
        if lesson:
            course_id = lesson.course_id
            total = db.query(Lesson).filter(Lesson.course_id == course_id).count()
            completed = (
                db.query(LessonCompletion)
                .join(Lesson, Lesson.id == LessonCompletion.lesson_id)
                .filter(LessonCompletion.user_id == user_id, Lesson.course_id == course_id)
                .count()
            )
            if total and completed >= total:
                # only create certificate if one doesn't already exist
                existing_cert = get_certificate_by_user_course(db, user_id, course_id)
                if not existing_cert:
                    create_certificate(db, user_id, course_id)

            award_milestone_badges(db, user_id, course_id)
    except Exception:
        # don't fail completion if certificate generation fails
        pass

    return completion


def get_completed_lessons_for_user_in_course(db: Session, user_id: int, course_id: int):
    # join LessonCompletion -> Lesson to filter by course
    from app.models.lesson import Lesson

    return (
        db.query(LessonCompletion)
        .join(Lesson, Lesson.id == LessonCompletion.lesson_id)
        .filter(LessonCompletion.user_id == user_id, Lesson.course_id == course_id)
        .all()
    )


def count_completed_lessons_for_user_in_course(db: Session, user_id: int, course_id: int) -> int:
    from app.models.lesson import Lesson

    return (
        db.query(LessonCompletion)
        .join(Lesson, Lesson.id == LessonCompletion.lesson_id)
        .filter(LessonCompletion.user_id == user_id, Lesson.course_id == course_id)
        .count()
    )


def get_completion_stats(db: Session, user_id: int) -> dict:
    from app.models.lesson import Lesson
    from app.models.course import Course
    
    total_lessons = db.query(Lesson).count()
    completed_lessons = (
        db.query(LessonCompletion)
        .filter(LessonCompletion.user_id == user_id)
        .count()
    )
    
    courses_total = db.query(Course).count()
    courses_enrolled = (
        db.query(Enrollment)
        .filter(Enrollment.user_id == user_id)
        .count()
    )
    
    return {
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "completion_rate": int((completed_lessons / total_lessons * 100)) if total_lessons > 0 else 0,
        "courses_total": courses_total,
        "courses_enrolled": courses_enrolled,
    }
