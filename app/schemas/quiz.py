from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional


class OptionCreate(BaseModel):
    text: str
    is_correct: bool = False


class QuestionCreate(BaseModel):
    text: str
    options: List[OptionCreate]


class QuizCreate(BaseModel):
    title: str
    description: Optional[str] = None
    course_id: int
    questions: List[QuestionCreate]


class OptionRead(BaseModel):
    id: int
    text: str

    model_config = {
        "from_attributes": True,
    }


class QuestionRead(BaseModel):
    id: int
    text: str
    options: List[OptionRead]

    model_config = {
        "from_attributes": True,
    }


class QuizRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    course_id: int
    owner_id: int
    questions: List[QuestionRead]

    model_config = {
        "from_attributes": True,
    }


class QuizAttemptAnswerCreate(BaseModel):
    question_id: int
    selected_option_id: int


class QuizAttemptCreate(BaseModel):
    answers: List[QuizAttemptAnswerCreate]


class QuizAttemptAnswerRead(BaseModel):
    question_id: int
    selected_option_id: int
    is_correct: bool

    model_config = {
        "from_attributes": True,
    }


class QuizAttemptRead(BaseModel):
    id: int
    quiz_id: int
    user_id: int
    score: int
    total: int
    submitted_at: datetime
    answers: List[QuizAttemptAnswerRead]

    model_config = {
        "from_attributes": True,
    }
