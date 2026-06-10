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


def get_admin_logs(db: Session, skip: int = 0, limit: int | None = None) -> list[AdminLog]:
    query = db.query(AdminLog).order_by(AdminLog.created_at.desc()).offset(skip)
    if limit is not None:
        query = query.limit(limit)
    return query.all()


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

        # Aggregate lesson counts per course
        lesson_counts_by_course = dict(
            db.query(Lesson.course_id, func.count(Lesson.id)).group_by(Lesson.course_id).all()
        )

        # Count enrollments per course
        enrollment_counts_by_course = dict(
            db.query(Enrollment.course_id, func.count(Enrollment.id)).group_by(Enrollment.course_id).all()
        )

        # Count completions per lesson
        completion_counts_by_lesson = dict(
            db.query(LessonCompletion.lesson_id, func.count(LessonCompletion.id)).group_by(LessonCompletion.lesson_id).all()
        )

        # Count completions per user and course
        course_user_progress_rows = db.query(
            LessonCompletion.user_id,
            Lesson.course_id,
            func.count(LessonCompletion.id).label("completed_lessons")
        ).join(Lesson, Lesson.id == LessonCompletion.lesson_id)
        course_user_progress_rows = course_user_progress_rows.group_by(
            LessonCompletion.user_id,
            Lesson.course_id
        ).all()

        students_completed_course = {}
        student_course_progress = []

        for user_id, course_id, completed_lessons in course_user_progress_rows:
            total_lessons = lesson_counts_by_course.get(course_id, 0)
            progress_percent = 0
            if total_lessons:
                progress_percent = int((completed_lessons / total_lessons) * 100)
            if total_lessons and completed_lessons >= total_lessons:
                students_completed_course[course_id] = students_completed_course.get(course_id, 0) + 1
            student_course_progress.append({
                "user_id": user_id,
                "course_id": course_id,
                "lessons_completed": completed_lessons,
                "total_lessons": total_lessons,
                "progress_percent": progress_percent,
            })

        # Build course-level summaries including lesson and completion details
        courses_data = []
        courses_list = db.query(Course).all()
        for course in courses_list:
            total_lessons = lesson_counts_by_course.get(course.id, 0)
            enrolled_students = enrollment_counts_by_course.get(course.id, 0)
            completed_students = students_completed_course.get(course.id, 0)
            course_completions = sum(
                completion_counts_by_lesson.get(lesson.id, 0)
                for lesson in course.lessons
            )
            average_lessons_completed = 0
            if enrolled_students:
                average_lessons_completed = int(course_completions / enrolled_students)

            courses_data.append({
                "id": course.id,
                "title": course.title or "Untitled",
                "description": course.description or "",
                "owner_id": course.owner_id,
                "is_paid": bool(course.is_paid),
                "prerequisite_course_id": course.prerequisite_course_id,
                "total_lessons": total_lessons,
                "enrolled_students": enrolled_students,
                "students_completed_course": completed_students,
                "total_lesson_completions": course_completions,
                "average_lessons_completed_per_student": average_lessons_completed,
                "completion_rate_percent": int((completed_students / enrolled_students) * 100) if enrolled_students else 0,
            })

        # Lesson-level completion details
        lesson_statistics = []
        lesson_rows = db.query(Lesson.id, Lesson.title, Lesson.course_id, Course.title)
        lesson_rows = lesson_rows.join(Course, Lesson.course_id == Course.id).all()
        for lesson_id, lesson_title, course_id, course_title in lesson_rows:
            lesson_statistics.append({
                "lesson_id": lesson_id,
                "lesson_title": lesson_title or "Untitled",
                "course_id": course_id,
                "course_title": course_title or "Untitled",
                "completion_count": completion_counts_by_lesson.get(lesson_id, 0),
            })

        # Get simple list of enrollments
        enrollments_list = db.query(Enrollment.id, Enrollment.user_id, Enrollment.course_id).all()
        enrollments_data = [
            {"user_id": e[1], "course_id": e[2]}
            for e in enrollments_list
        ]
        
        # Get activity logs (include all historical and current entries)
        activity_logs = get_admin_logs(db, skip=0, limit=None)
        activity_log = []
        try:
            for log in activity_logs:
                if not log.user or log.user.role == Role.admin:
                    continue
                activity_log.append({
                    "id": log.id,
                    "action": log.action,
                    "details": log.details or "",
                    "ip_address": log.ip_address or "",
                    "timestamp": str(log.created_at) if log.created_at else "",
                    "user_id": log.user_id,
                    "user_email": log.user.email,
                    "user_name": log.user.full_name,
                    "user_role": log.user.role.value,
                })
        except Exception as e:
            activity_log = [{"error": str(e)}]
        
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
                "total_completions": total_completions,
                "lesson_statistics": lesson_statistics[:100]
            },
            "student_course_progress": student_course_progress[:100],
            "activity_log": activity_log,
            "recent_activity": activity_log[:50]
        }
        
        return context
    except Exception as e:
        # Return minimal safe context
        return {
            "user_statistics": {"total_students": 0, "total_instructors": 0},
            "course_statistics": {"total_courses": 0, "courses": []},
            "enrollment_statistics": {"total_enrollments": 0, "sample_enrollments": []},
            "lesson_completion_statistics": {"total_completions": 0, "lesson_statistics": []},
            "student_course_progress": [],
            "activity_log": [],
            "recent_activity": [],
            "error": str(e)
        }