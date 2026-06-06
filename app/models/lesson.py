from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base

class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=True)
    asset_path = Column(String(255), nullable=True)
    asset_metadata = Column(JSON, nullable=True)  # Stores file info from Cloudinary
    duration = Column(String(80), nullable=True)
    is_mandatory = Column(Boolean, default=True, nullable=False)
    sequence = Column(Integer, nullable=True)
    course_id = Column(Integer, ForeignKey("courses.id"))

    course = relationship("Course", back_populates="lessons")
    comments = relationship("Comment", back_populates="lesson", cascade="all, delete-orphan")
