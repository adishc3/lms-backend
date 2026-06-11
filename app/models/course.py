from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    cover_image_url = Column(String(1024), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    duration = Column(String(80), nullable=True)
    category = Column(String(100), nullable=True)
    track = Column(String(120), nullable=True)
    price = Column(Integer, nullable=True, default=0)
    is_paid = Column(Boolean, default=False, nullable=False)
    prerequisite_course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    ai_system_prompt = Column(Text, nullable=True)

    owner = relationship("User", back_populates="owned_courses")
    prerequisite_course = relationship("Course", remote_side=[id], backref="dependent_courses")
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="course", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="course", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="course", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="course", cascade="all, delete-orphan")

    @property
    def total_lessons(self):
        return len(self.lessons or [])
