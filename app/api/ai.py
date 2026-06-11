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
    
    # Use course-specific system prompt if available
    course_system_prompt = (course.ai_system_prompt or "").strip()
    if not course_system_prompt:
        course_system_prompt = (
            f\"You are an AI tutor specifically for the '{course.title}' course. \"
            \"Your role is to help students understand ONLY the material covered in this course. \"
            \"Use ONLY the lesson content provided below. \"
            \"If a question is not related to the course material, politely explain that you can only help with questions related to this course. \"
            \"Do not provide general knowledge or information from outside this course.\"
        )
    
    try:
        answer = await query_ai(prompt, context, system_prompt=course_system_prompt)
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

    course_system_prompt = (course.ai_system_prompt or "").strip()
    if not course_system_prompt:
        course_system_prompt = (
            f\"You are an AI tutor specifically for the '{course.title}' course. \"
            \"IMPORTANT: You can ONLY answer questions about the course material provided below. \"
            \"If a question is not related to this course or its lessons, respond with: 'I can only help with questions related to this course. Please ask something about [course topic].' \"
            \"Always cite which lesson the answer comes from. \"
            \"Do NOT provide external knowledge or information from other sources.\"
        )

    try:
        answer = await query_ai(request.question, context, system_prompt=course_system_prompt)
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
    
    # Build quiz-specific system prompt
    quiz_system_prompt = (
        f\"You are an expert quiz generator for the '{course.title}' course. \"
        \"Create multiple-choice quiz questions based ONLY on the lesson content provided. \"
        \"Each question should test student understanding of the course material. \"
        \"Do not create questions about topics outside this lesson or course.\"
    )
    
    try:
        quiz_text = await generate_quiz(context, request.question_count, system_prompt=quiz_system_prompt)
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
