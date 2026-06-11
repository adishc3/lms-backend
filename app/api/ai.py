from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.schemas.ai import AIStudyRequest, AIStudyResponse, AIQuizRequest, AIQuizResponse, AIChatRequest, AIChatResponse
from app.core.ai import query_ai, generate_quiz
from app.crud.lesson import get_lesson, get_lessons_by_course
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


@router.post("/chat", response_model=AIChatResponse)
async def ai_chat(request: AIChatRequest, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    course = get_course(db, request.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    ensure_course_access(course, current_user, db)
    lessons = get_lessons_by_course(db, course.id)
    if not lessons:
        raise HTTPException(status_code=404, detail="No lessons found for this course")

    selected_lesson = None
    if request.lesson_id is not None:
        selected_lesson = get_lesson(db, request.lesson_id)
        if not selected_lesson or selected_lesson.course_id != course.id:
            raise HTTPException(status_code=404, detail="Lesson not found for this course")

    lesson_summaries = []
    for idx, lesson in enumerate(lessons, start=1):
        snippet = "".join(lesson.content.splitlines())[:280]
        lesson_summaries.append(f"{idx}. {lesson.title}\n{snippet}{'...' if len(snippet) < len(lesson.content) else ''}")

    context = f"Course title: {course.title}\nCourse description: {course.description or ''}\n\nLessons:\n" + "\n\n".join(lesson_summaries)
    if selected_lesson:
        context += f"\n\nSelected lesson title: {selected_lesson.title}\n{selected_lesson.content}"

    prompt = (
        "You are an AI tutor helping a student understand course material. Use only the given course and lesson context. "
        "If the question refers to a topic or concept, identify the most relevant lesson and mention it by title. "
        "If a specific lesson is selected, answer based on that lesson. "
        "Do not invent other sources.\n\n"
        f"Student question: {request.question}"
    )

    try:
        answer = await query_ai(prompt, context)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    create_ai_usage(
        db,
        user_id=current_user.id,
        feature="chat_tutor",
        prompt=f"Context: {context}\n\nQuestion: {request.question}",
        response=answer,
        lesson_id=selected_lesson.id if selected_lesson else None,
    )
    return AIChatResponse(answer=answer)


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
