from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.badge_generator import generate_badge_code
from app.models.badge import Badge
from app.models.certificate import Certificate
from app.models.lesson import Lesson
from app.models.lesson_completion import LessonCompletion

BADGE_DEFINITIONS: list[dict[str, str]] = [
    {
        "badge_code": "FIRST_LESSON_COMPLETED",
        "badge_name": "First Lesson Completed",
        "badge_description": "Awarded when a learner completes their first lesson.",
        "icon": "bi-bookmark-check",
    },
    {
        "badge_code": "COURSE_COMPLETED",
        "badge_name": "Course Completed",
        "badge_description": "Awarded when a learner completes all lessons in a course.",
        "icon": "bi-patch-check",
    },
    {
        "badge_code": "THREE_COURSES_COMPLETED",
        "badge_name": "Three Courses Completed",
        "badge_description": "Awarded when a learner completes three courses.",
        "icon": "bi-award",
    },
]


def list_badge_definitions() -> list[dict[str, str]]:
    return [definition.copy() for definition in BADGE_DEFINITIONS]


def get_badge(db: Session, badge_id: int) -> Badge | None:
    return db.query(Badge).filter(Badge.id == badge_id).first()


def get_badge_by_code(db: Session, badge_code: str) -> Badge | None:
    return db.query(Badge).filter(Badge.badge_code == badge_code).first()


def get_badges(db: Session, skip: int = 0, limit: int = 100) -> list[Badge]:
    return db.query(Badge).order_by(Badge.awarded_at.desc()).offset(skip).limit(limit).all()


def get_user_badges(db: Session, user_id: int) -> list[Badge]:
    return db.query(Badge).filter(Badge.user_id == user_id).order_by(Badge.awarded_at.desc()).all()


def get_course_badges(db: Session, course_id: int) -> list[Badge]:
    return db.query(Badge).filter(Badge.course_id == course_id).order_by(Badge.awarded_at.desc()).all()


def _get_definition(badge_code: str) -> dict[str, str] | None:
    for definition in BADGE_DEFINITIONS:
        if definition["badge_code"] == badge_code:
            return definition
    return None


def _has_badge(db: Session, user_id: int, badge_code: str, course_id: int | None = None) -> bool:
    query = db.query(Badge).filter(Badge.user_id == user_id, Badge.badge_code == badge_code)
    if course_id is None:
        query = query.filter(Badge.course_id.is_(None))
    else:
        query = query.filter(Badge.course_id == course_id)
    return query.first() is not None


def award_badge(
    db: Session,
    user_id: int,
    badge_code: str,
    badge_name: str | None = None,
    badge_description: str | None = None,
    course_id: int | None = None,
) -> Badge | None:
    definition = _get_definition(badge_code)
    resolved_name = badge_name or (definition["badge_name"] if definition else badge_code.replace("_", " ").title())
    resolved_description = badge_description or (definition["badge_description"] if definition else None)

    if _has_badge(db, user_id=user_id, badge_code=badge_code, course_id=course_id):
        return None

    badge = Badge(
        user_id=user_id,
        course_id=course_id,
        badge_code=badge_code if badge_code else generate_badge_code(),
        badge_name=resolved_name,
        badge_description=resolved_description,
    )
    db.add(badge)
    db.commit()
    db.refresh(badge)
    return badge


def ensure_default_badges(db: Session) -> list[dict[str, str]]:
    # Badge definitions are static in code for now; this helper keeps the contract
    # for callers that expect a seeding hook.
    return list_badge_definitions()


def award_milestone_badges(db: Session, user_id: int, course_id: int) -> list[Badge]:
    awarded: list[Badge] = []

    total_completed = db.query(LessonCompletion).filter(LessonCompletion.user_id == user_id).count()
    if total_completed >= 1:
        first_badge = award_badge(db, user_id, "FIRST_LESSON_COMPLETED")
        if first_badge is not None:
            awarded.append(first_badge)

    total_lessons = db.query(Lesson).filter(Lesson.course_id == course_id).count()
    course_completed = (
        db.query(LessonCompletion)
        .join(Lesson, Lesson.id == LessonCompletion.lesson_id)
        .filter(LessonCompletion.user_id == user_id, Lesson.course_id == course_id)
        .count()
    )
    if total_lessons and course_completed >= total_lessons:
        course_badge = award_badge(db, user_id, "COURSE_COMPLETED", course_id=course_id)
        if course_badge is not None:
            awarded.append(course_badge)

    completed_courses = (
        db.query(Certificate.course_id)
        .filter(Certificate.user_id == user_id)
        .distinct()
        .count()
    )
    if completed_courses >= 3:
        trio_badge = award_badge(db, user_id, "THREE_COURSES_COMPLETED")
        if trio_badge is not None:
            awarded.append(trio_badge)

    return awarded
