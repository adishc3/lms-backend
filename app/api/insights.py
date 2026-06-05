from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.crud.lesson_completion import get_completion_stats
from app.crud.enrollment import list_enrollments_for_user
from app.crud.course import get_courses

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