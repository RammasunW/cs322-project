from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class HRAction(Base):
    __tablename__ = "hr_actions"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("users.id"))
    action_type = Column(String(20))  # PROMOTION, DEMOTION, TERMINATION
    reason = Column(Text)

    salary_change = Column(Float, nullable=True)
    bonus = Column(Float, nullable=True)

    timestamp = Column(DateTime, default=datetime.utcnow)
