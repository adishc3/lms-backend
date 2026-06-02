import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class Role(enum.Enum):
    student = "student"
    instructor = "instructor"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(Role), default=Role.student)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    owned_courses = relationship("Course", back_populates="owner")
    admin_logs = relationship("AdminLog", back_populates="user")
    submissions = relationship("Submission", foreign_keys="[Submission.user_id]", back_populates="user")
    graded_submissions = relationship("Submission", foreign_keys="[Submission.graded_by]", back_populates="grader")
    user_badges = relationship("UserBadge", back_populates="user", cascade="all, delete-orphan")
