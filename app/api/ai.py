from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.schemas.ai import AIStudyRequest, AIStudyResponse, AIQuizRequest, AIQuizResponse
from app.core.ai import query_ai, generate_quiz
from app.crud.lesson import get_lesson
from app.crud.course import get_course
from app.crud.enrollment import get_enrollment
from app.crud.ai import create_ai_usage

router = APIRouter(prefix="/ai", tags=["ai"])


def ensure_course_access(course, current_user, db: Session):
    if current_user.role.value == "admin":
        return True
    if current_user.role.value == "instructor":
        if course.owner_id == current_user.id:
            return True
        raise HTTPException(status_code=403, detail="Course ownership required for instructors")
    if get_enrollment(db, current_user.id, course.id):
        return True
    raise HTTPException(status_code=403, detail="Enrollment required")


@router.post("/study-assistant", response_model=AIStudyResponse)
async def study_assistant(request: AIStudyRequest, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    lesson = get_lesson(db, request.lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    course = get_course(db, lesson.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    ensure_course_access(course, current_user, db)

    context = f"Lesson title: {lesson.title}\n\n{lesson.content}"
    prompt = request.question
    try:
        answer = await query_ai(prompt, context)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    create_ai_usage(
        db,
        user_id=current_user.id,
        feature="study_assistant",
        prompt=f"Question: {prompt}\n\nContext: {context}",
        response=answer,
        lesson_id=lesson.id,
    )
    return AIStudyResponse(answer=answer)


@router.post("/quiz-generator", response_model=AIQuizResponse)
async def quiz_generator(request: AIQuizRequest, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    lesson = get_lesson(db, request.lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    course = get_course(db, lesson.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    ensure_course_access(course, current_user, db)

    context = f"Lesson title: {lesson.title}\n\n{lesson.content}"
    try:
        quiz_text = await generate_quiz(context, request.question_count)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    create_ai_usage(
        db,
        user_id=current_user.id,
        feature="quiz_generator",
        prompt=f"Generate {request.question_count} questions. Context: {context}",
        response=quiz_text,
        lesson_id=lesson.id,
    )
    return AIQuizResponse(quiz=quiz_text)
