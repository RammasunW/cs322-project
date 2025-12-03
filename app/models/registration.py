from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True)
    username = Column(String(30))
    email = Column(String(100))
    password_hash = Column(String(255))
    phone = Column(String(20))
    status = Column(String(20))  # PENDING, APPROVED, REJECTED

    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Blacklist(Base):
    __tablename__ = "blacklist"

    id = Column(Integer, primary_key=True)
    username = Column(String(30))
    email = Column(String(100))
    reason = Column(String(50))
    banned_date = Column(DateTime, default=datetime.utcnow)
    banned_by = Column(Integer, ForeignKey("users.id"))
