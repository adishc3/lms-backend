from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_instructor, get_current_active_user
from app.schemas.course import CourseCreate, CourseRead
from app.schemas.lesson import LessonCreate, LessonRead, LessonUpdate
from app.schemas.event import EventCreate, EventRead
from app.schemas.payment import PaymentCreate, PaymentRead
from app.crud.course import get_course, get_courses, update_course, delete_course
from app.crud.lesson import get_lessons_by_course, get_lesson, create_lesson, update_lesson, delete_lesson
from app.crud.lesson_completion import (
    get_completion,
    mark_completion,
    get_completed_lessons_for_user_in_course,
    count_completed_lessons_for_user_in_course,
)
from app.crud.enrollment import get_enrollment, create_enrollment, get_enrolled_students_by_course, list_enrollments_for_user
from app.crud.event import create_event, delete_event, get_event, list_events, update_event
from app.crud.payment import (
    complete_payment,
    create_payment,
    get_completed_payment_for_course,
    list_payments_for_user,
)
from app.crud.notification import create_notification
from app.schemas.lesson_completion import LessonCompletionRead
from app.core.email import send_email
from app.core.cloudinary_storage import upload_lesson_file
from app import models

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/", response_model=list[CourseRead])
def list_courses(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return get_courses(db, skip=skip, limit=limit)


@router.get("/{course_id}", response_model=CourseRead)
def read_course(course_id: int, db: Session = Depends(get_db)):
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
def create_new_course(course_in: CourseCreate, current_user=Depends(require_instructor), db: Session = Depends(get_db)):
    # Force the owner_id to be the current logged-in instructor
    course_data = course_in.dict()
    new_course = models.course.Course(**course_data, owner_id=current_user.id)
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course


@router.put("/{course_id}", response_model=CourseRead)
def edit_course(course_id: int, course_in: CourseCreate, current_user=Depends(require_instructor), db: Session = Depends(get_db)):
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.owner_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not permitted")
    return update_course(db, course, course_in)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_course(course_id: int, current_user=Depends(require_instructor), db: Session = Depends(get_db)):
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.owner_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not permitted")
    delete_course(db, course)
    return None


@router.post("/{course_id}/enroll", response_model=CourseRead, status_code=status.HTTP_200_OK)
def enroll_course(course_id: int, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if current_user.role.value == "instructor":
        raise HTTPException(status_code=403, detail="Instructors cannot enroll in courses")
    if course.is_paid and not get_completed_payment_for_course(db, current_user.id, course_id):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Payment required. Purchase this course before enrolling.",
        )
    if get_enrollment(db, current_user.id, course_id):
        return course
    create_enrollment(db, current_user.id, course_id)
    return course


@router.post("/{course_id}/purchase", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def purchase_course(
    course_id: int,
    payment_in: PaymentCreate,
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if not course.is_paid:
        raise HTTPException(status_code=400, detail="Course does not require payment")
    if current_user.role.value == "instructor":
        raise HTTPException(status_code=403, detail="Instructors cannot purchase courses")
    if get_completed_payment_for_course(db, current_user.id, course_id):
        raise HTTPException(status_code=400, detail="Course already purchased")

    payment = create_payment(
        db,
        user_id=current_user.id,
        course_id=course.id,
        amount=course.price or 0,
        currency=payment_in.currency,
        payment_method=payment_in.payment_method,
        transaction_reference=str(uuid4()),
    )
    payment = complete_payment(db, payment, transaction_reference=payment.transaction_reference)
    if not get_enrollment(db, current_user.id, course_id):
        create_enrollment(db, current_user.id, course_id)
    return payment


@router.get("/payments", response_model=list[PaymentRead])
def my_payments(current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    return list_payments_for_user(db, current_user.id)


@router.get("/my/courses", response_model=list[CourseRead])
def my_enrolled_courses(current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    enrollments = list_enrollments_for_user(db, current_user.id)
    return [enrollment.course for enrollment in enrollments]


def ensure_course_access(course, current_user, db: Session):
    if current_user.role.value == "admin":
        return True
    if current_user.role.value == "instructor" and course.owner_id == current_user.id:
        return True
    if get_enrollment(db, current_user.id, course.id):
        return True
    raise HTTPException(status_code=403, detail="Enrollment required")


def ensure_course_owner_or_admin(course, current_user):
    if course.owner_id == current_user.id or current_user.role.value == "admin":
        return True
    raise HTTPException(status_code=403, detail="Not permitted")


@router.get("/{course_id}/events", response_model=list[EventRead])
def list_course_events(course_id: int, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    ensure_course_access(course, current_user, db)
    return list_events(db, course_id=course_id)


@router.get("/{course_id}/events/{event_id}", response_model=EventRead)
def read_course_event(course_id: int, event_id: int, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    event = get_event(db, event_id)
    if not event or event.course_id != course_id:
        raise HTTPException(status_code=404, detail="Event not found")
    ensure_course_access(course, current_user, db)
    return event


@router.post("/{course_id}/events", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_course_event(
    course_id: int,
    event_in: EventCreate,
    current_user=Depends(require_instructor),
    db: Session = Depends(get_db),
):
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    ensure_course_owner_or_admin(course, current_user)
    return create_event(db, course_id, event_in)


@router.put("/{course_id}/events/{event_id}", response_model=EventRead)
def update_course_event(
    course_id: int,
    event_id: int,
    event_in: EventCreate,
    current_user=Depends(require_instructor),
    db: Session = Depends(get_db),
):
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    event = get_event(db, event_id)
    if not event or event.course_id != course_id:
        raise HTTPException(status_code=404, detail="Event not found")
    ensure_course_owner_or_admin(course, current_user)
    return update_event(db, event, event_in)


@router.delete("/{course_id}/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course_event(
    course_id: int,
    event_id: int,
    current_user=Depends(require_instructor),
    db: Session = Depends(get_db),
):
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    event = get_event(db, event_id)
    if not event or event.course_id != course_id:
        raise HTTPException(status_code=404, detail="Event not found")
    ensure_course_owner_or_admin(course, current_user)
    delete_event(db, event)
    return None


@router.get("/{course_id}/lessons", response_model=list[LessonRead])
def list_lessons(course_id: int, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    ensure_course_access(course, current_user, db)
    return get_lessons_by_course(db, course_id)


@router.get("/{course_id}/lessons/{lesson_id}", response_model=LessonRead)
def read_lesson(course_id: int, lesson_id: int, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    lesson = get_lesson(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Lesson not found")
    ensure_course_access(course, current_user, db)
    return lesson


@router.post("/{course_id}/lessons/{lesson_id}/complete", response_model=LessonCompletionRead)
def complete_lesson(
    course_id: int,
    lesson_id: int,
    time_spent_minutes: int | None = None,
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    lesson = get_lesson(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Lesson not found")
    ensure_course_access(course, current_user, db)
    existing_completion = get_completion(db, current_user.id, lesson_id)
    completion = mark_completion(db, current_user.id, lesson_id, time_spent_minutes=time_spent_minutes)
    if not existing_completion:
        create_notification(
            db,
            current_user.id,
            title=f"Lesson completed: {lesson.title}",
            message=f"You completed '{lesson.title}' in '{course.title}'. Keep learning!",
        )
    return completion


@router.get("/{course_id}/progress")
def course_progress(course_id: int, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    ensure_course_access(course, current_user, db)
    total = len(get_lessons_by_course(db, course_id))
    completed = count_completed_lessons_for_user_in_course(db, current_user.id, course_id)
    percent = int((completed / total) * 100) if total else 0
    completed_list = [c.lesson_id for c in get_completed_lessons_for_user_in_course(db, current_user.id, course_id)]
    return {"course_id": course_id, "total_lessons": total, "completed": completed, "percent": percent, "completed_lessons": completed_list}


@router.post("/{course_id}/lessons", response_model=LessonRead, status_code=status.HTTP_201_CREATED)
def create_course_lesson(
    course_id: int,
    lesson_in: LessonCreate,
    background_tasks: BackgroundTasks,
    current_user=Depends(require_instructor),
    db: Session = Depends(get_db),
):
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.owner_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not permitted")

    lesson = create_lesson(db, lesson_in, course_id=course_id)
    students = get_enrolled_students_by_course(db, course_id)
    recipients = [student.email for student in students if student.is_active]
    if recipients:
        subject = f"New lesson published in {course.title}: {lesson.title}"
        body = (
            f"A new lesson has been added to the course '{course.title}'.\n\n"
            f"Lesson: {lesson.title}\n\n"
            f"{lesson.content[:200]}\n\n"
            "Visit the course to continue learning."
        )
        html_body = (
            f"<p>A new lesson has been added to the course '<strong>{course.title}</strong>'.</p>"
            f"<p><strong>{lesson.title}</strong></p>"
            f"<p>{lesson.content[:300]}</p>"
            f"<p>Visit the course to continue learning.</p>"
        )
        background_tasks.add_task(send_email, subject, recipients, body, html_body)

    return lesson


@router.put("/{course_id}/lessons/{lesson_id}", response_model=LessonRead)
def edit_lesson(
    course_id: int,
    lesson_id: int,
    lesson_in: LessonUpdate,
    current_user=Depends(require_instructor),
    db: Session = Depends(get_db),
):
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    lesson = get_lesson(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Lesson not found")

    if course.owner_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not permitted")

    return update_lesson(db, lesson, lesson_in)


@router.delete("/{course_id}/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_lesson(
    course_id: int,
    lesson_id: int,
    current_user=Depends(require_instructor),
    db: Session = Depends(get_db),
):
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    lesson = get_lesson(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Lesson not found")

    if course.owner_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not permitted")

    delete_lesson(db, lesson)
    return None


@router.post("/{course_id}/lessons/{lesson_id}/upload", response_model=LessonRead)
async def upload_lesson_asset(
    course_id: int,
    lesson_id: int,
    file: UploadFile = File(...),
    current_user=Depends(require_instructor),
    db: Session = Depends(get_db),
):
    """Upload a file (PDF, image, video, etc.) to a lesson using Cloudinary."""
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    lesson = get_lesson(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Lesson not found")

    if course.owner_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not permitted")

    # Upload to Cloudinary
    file_info = await upload_lesson_file(file, lesson_id)
    
    # Update lesson with file metadata
    lesson.asset_path = file_info['url']
    lesson.asset_metadata = {
        'public_id': file_info['public_id'],
        'resource_type': file_info['resource_type'],
        'file_name': file_info['file_name'],
    }
    db.commit()
    db.refresh(lesson)
    
    return lesson


@router.delete("/{course_id}/lessons/{lesson_id}/asset", response_model=LessonRead)
def delete_lesson_asset(
    course_id: int,
    lesson_id: int,
    current_user=Depends(require_instructor),
    db: Session = Depends(get_db),
):
    """Delete a file attachment from a lesson."""
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    lesson = get_lesson(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Lesson not found")

    if course.owner_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not permitted")

    if not lesson.asset_metadata:
        raise HTTPException(status_code=400, detail="No file attached to this lesson")

    # Delete from Cloudinary
    from app.core.cloudinary_storage import delete_lesson_file
    public_id = lesson.asset_metadata.get('public_id')
    resource_type = lesson.asset_metadata.get('resource_type', 'image')
    
    if public_id:
        delete_lesson_file(public_id, resource_type)

    # Clear asset fields
    lesson.asset_path = None
    lesson.asset_metadata = None
    db.commit()
    db.refresh(lesson)

    return lesson
