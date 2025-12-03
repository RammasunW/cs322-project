from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class KBEntry(Base):
    __tablename__ = "kb_entries"

    id = Column(Integer, primary_key=True)
    question = Column(Text)
    answer = Column(Text)
    author_id = Column(Integer, ForeignKey("users.id"))

    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)

    flagged = Column(Boolean, default=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_note = Column(Text)
    reviewed_at = Column(DateTime)


class KBRating(Base):
    __tablename__ = "kb_ratings"

    id = Column(Integer, primary_key=True)
    kb_id = Column(Integer, ForeignKey("kb_entries.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)


class KBUsageLog(Base):
    __tablename__ = "kb_usage_logs"

    id = Column(Integer, primary_key=True)
    kb_id = Column(Integer, ForeignKey("kb_entries.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    question = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


class LLMUsageLog(Base):
    __tablename__ = "llm_usage_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question = Column(Text)
    response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
