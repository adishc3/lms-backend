from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.deps import get_db, get_current_active_user, require_instructor
from app.crud.lesson_completion import get_completion_stats
from app.crud.enrollment import list_enrollments_for_user
from app.crud.course import get_courses
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.lesson import Lesson
from app.models.lesson_completion import LessonCompletion
from app.models.user import User

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/progress-summary")
def progress_summary(db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    stats = get_completion_stats(db, current_user.id)
    return {"user_id": current_user.id, "completion_stats": stats}


@router.get("/recommended-courses")
def recommended_courses(limit: int = 5, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    if current_user.role.value not in ["student", "admin"]:
        raise HTTPException(status_code=403, detail="Only students can get recommendations")
    
    enrolled_course_ids = [e.course_id for e in list_enrollments_for_user(db, current_user.id)]
    all_courses = get_courses(db, limit=limit * 3)
    
    recommendations = []
    for course in all_courses:
        if course.id not in enrolled_course_ids:
            recommendations.append({
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "reason": "Popular course you haven't enrolled in"
            })
        if len(recommendations) >= limit:
            break
    
    return {"recommendations": recommendations}


@router.get("/instructor-overview")
def instructor_overview(current_user=Depends(require_instructor), db: Session = Depends(get_db)):
    total_courses = db.query(Course).filter(Course.owner_id == current_user.id).count()
    unique_students = (
        db.query(func.count(func.distinct(Enrollment.user_id)))
        .join(Course, Enrollment.course_id == Course.id)
        .filter(Course.owner_id == current_user.id)
        .scalar()
        or 0
    )
    total_lessons = (
        db.query(Lesson)
        .join(Course, Lesson.course_id == Course.id)
        .filter(Course.owner_id == current_user.id)
        .count()
    )
    total_completions = (
        db.query(LessonCompletion)
        .join(Lesson, LessonCompletion.lesson_id == Lesson.id)
        .join(Course, Lesson.course_id == Course.id)
        .filter(Course.owner_id == current_user.id)
        .count()
    )

    return {
        "total_courses": total_courses,
        "unique_students": unique_students,
        "total_lessons": total_lessons,
        "total_completions": total_completions,
    }


@router.get("/leaderboard")
def leaderboard(limit: int = 10, db: Session = Depends(get_db)):
    top_users = (
        db.query(User)
        .order_by(User.points.desc(), User.level.desc())
        .limit(limit)
        .all()
    )
    return {
        "leaderboard": [
            {
                "user_id": user.id,
                "full_name": user.full_name,
                "points": user.points,
                "level": user.level,
            }
            for user in top_users
        ]
    }