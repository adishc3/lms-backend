from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_instructor, get_current_active_user
from app.schemas.quiz import (
    QuizCreate,
    QuizRead,
    QuizAttemptCreate,
    QuizAttemptRead,
)
from app.crud.quiz import (
    create_quiz,
    get_quiz,
    get_quizzes_by_course,
    get_quiz_attempt,
    get_attempts_for_quiz,
    get_attempts_for_user,
    submit_quiz_attempt,
)
from app.crud.course import get_course
from app.crud.enrollment import get_enrollment

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


def ensure_quiz_access(course, current_user, db: Session):
    if current_user.role.value == "admin":
        return True
    if current_user.role.value == "instructor":
        if course.owner_id == current_user.id:
            return True
        raise HTTPException(status_code=403, detail="Course ownership required for instructors")
    if get_enrollment(db, current_user.id, course.id):
        return True
    raise HTTPException(status_code=403, detail="Enrollment required")


@router.post("/", response_model=QuizRead, status_code=status.HTTP_201_CREATED)
def create_new_quiz(quiz_in: QuizCreate, current_user=Depends(require_instructor), db: Session = Depends(get_db)):
    course = get_course(db, quiz_in.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.owner_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not permitted")
    return create_quiz(db, quiz_in, owner_id=current_user.id)


@router.get("/course/{course_id}", response_model=list[QuizRead])
def list_course_quizzes(course_id: int, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    ensure_quiz_access(course, current_user, db)
    return get_quizzes_by_course(db, course_id)


@router.get("/{quiz_id}", response_model=QuizRead)
def read_quiz(quiz_id: int, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    quiz = get_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    course = get_course(db, quiz.course_id)
    ensure_quiz_access(course, current_user, db)
    return quiz


@router.post("/{quiz_id}/attempts", response_model=QuizAttemptRead, status_code=status.HTTP_201_CREATED)
def submit_attempt(quiz_id: int, attempt_in: QuizAttemptCreate, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    quiz = get_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    course = get_course(db, quiz.course_id)
    ensure_quiz_access(course, current_user, db)
    attempt = submit_quiz_attempt(db, current_user.id, quiz_id, attempt_in)
    if not attempt:
        raise HTTPException(status_code=400, detail="Unable to submit quiz attempt")
    return attempt


@router.get("/{quiz_id}/attempts", response_model=list[QuizAttemptRead])
def list_attempts(quiz_id: int, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    quiz = get_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    course = get_course(db, quiz.course_id)
    if current_user.role.value in ["admin"] or course.owner_id == current_user.id:
        return get_attempts_for_quiz(db, quiz_id)
    if get_enrollment(db, current_user.id, course.id):
        return get_attempts_for_user(db, current_user.id, quiz_id=quiz_id)
    raise HTTPException(status_code=403, detail="Access denied")


@router.get("/{quiz_id}/attempts/{attempt_id}", response_model=QuizAttemptRead)
def read_attempt(quiz_id: int, attempt_id: int, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    quiz = get_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    attempt = get_quiz_attempt(db, attempt_id)
    if not attempt or attempt.quiz_id != quiz_id:
        raise HTTPException(status_code=404, detail="Attempt not found")
    course = get_course(db, quiz.course_id)
    if current_user.role.value in ["admin"] or course.owner_id == current_user.id or attempt.user_id == current_user.id:
        return attempt
    raise HTTPException(status_code=403, detail="Access denied")
