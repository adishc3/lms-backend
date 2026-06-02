from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    badge_code = Column(String(64), unique=True, nullable=False, index=True)
    badge_name = Column(String(255), nullable=False)
    badge_description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    user_badges = relationship("UserBadge", back_populates="badge", cascade="all, delete-orphan")
