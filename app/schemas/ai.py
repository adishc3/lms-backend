from pydantic import BaseModel


class AIStudyRequest(BaseModel):
    lesson_id: int
    question: str


class AIStudyResponse(BaseModel):
    answer: str


class AIQuizRequest(BaseModel):
    lesson_id: int
    question_count: int = 5


class AIQuizResponse(BaseModel):
    quiz: str


class AIChatRequest(BaseModel):
    course_id: int
    lesson_id: int | None = None
    question: str


class AIChatResponse(BaseModel):
    answer: str


class AdminAIInsightRequest(BaseModel):
    query: str


class AdminAIInsightResponse(BaseModel):
    insight: str


class AdminCoursePromptUpdate(BaseModel):
    ai_system_prompt: str | None = None


class AICourseGeneratorRequest(BaseModel):
    title: str
    description: str
    level: str = "beginner"  # beginner, intermediate, advanced
    duration_weeks: int = 4
    num_lessons: int = 8


class LessonPlan(BaseModel):
    title: str
    content: str
    order: int


class AICourseGeneratorResponse(BaseModel):
    course_title: str
    course_description: str
    syllabus: str
    lessons: list[LessonPlan]
