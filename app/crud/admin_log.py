from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.admin_log import AdminLog
from app.models.user import User, Role
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.lesson_completion import LessonCompletion
from app.models.lesson import Lesson


def create_admin_log(db: Session, user_id: int, action: str, details: str | None = None, ip_address: str | None = None) -> AdminLog:
    log = AdminLog(user_id=user_id, action=action, details=details, ip_address=ip_address)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_admin_logs(db: Session, skip: int = 0, limit: int = 50) -> list[AdminLog]:
    return db.query(AdminLog).order_by(AdminLog.created_at.desc()).offset(skip).limit(limit).all()


def get_system_context_for_ai(db: Session) -> dict:
    """Gather comprehensive system context for AI analysis"""
    
    try:
        # Get user statistics by role - simple counts
        student_count = db.query(User).filter(User.role == Role.student).count()
        instructor_count = db.query(User).filter(User.role == Role.instructor).count()
        
        # Get course statistics
        total_courses = db.query(Course).count()
        
        # Get enrollment statistics
        total_enrollments = db.query(Enrollment).count()
        
        # Get lesson completion statistics
        total_completions = db.query(LessonCompletion).count()
        
        # Get simple list of courses
        courses_list = db.query(Course.id, Course.title, Course.owner_id).all()
        courses_data = [
            {"id": c[0], "title": c[1] or "Untitled", "owner_id": c[2]}
            for c in courses_list
        ]
        
        # Get simple list of enrollments
        enrollments_list = db.query(Enrollment.id, Enrollment.user_id, Enrollment.course_id).all()
        enrollments_data = [
            {"user_id": e[1], "course_id": e[2]}
            for e in enrollments_list
        ]
        
        # Get activity logs
        recent_logs = get_admin_logs(db, skip=0, limit=50)
        recent_activity = []
        try:
            for log in recent_logs:
                if log.user and log.user.role != Role.admin:
                    recent_activity.append({
                        "action": log.action,
                        "user_name": log.user.full_name or "Unknown",
                        "user_email": log.user.email or "Unknown",
                        "details": log.details or "",
                        "timestamp": str(log.created_at) if log.created_at else ""
                    })
        except Exception as e:
            recent_activity = [{"error": str(e)}]
        
        context = {
            "user_statistics": {
                "total_students": student_count,
                "total_instructors": instructor_count,
            },
            "course_statistics": {
                "total_courses": total_courses,
                "courses": courses_data[:50]
            },
            "enrollment_statistics": {
                "total_enrollments": total_enrollments,
                "sample_enrollments": enrollments_data[:50]
            },
            "lesson_completion_statistics": {
                "total_completions": total_completions
            },
            "recent_activity": recent_activity
        }
        
        return context
    except Exception as e:
        # Return minimal safe context
        return {
            "user_statistics": {"total_students": 0, "total_instructors": 0},
            "course_statistics": {"total_courses": 0, "courses": []},
            "enrollment_statistics": {"total_enrollments": 0, "sample_enrollments": []},
            "lesson_completion_statistics": {"total_completions": 0},
            "recent_activity": [],
            "error": str(e)
        }