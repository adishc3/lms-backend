from pydantic import BaseModel
from typing import Optional


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
