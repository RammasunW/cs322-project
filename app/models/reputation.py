from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True)
    from_user_id = Column(Integer, ForeignKey("users.id"))
    to_user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String(20))  # CHEF, DELIVERY, CUSTOMER
    description = Column(Text)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)

    status = Column(String(20))  # PENDING, UPHOLD, DISMISS, CANCELLED
    weight = Column(Integer, default=1)

    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    manager_id = Column(Integer, ForeignKey("users.id"))
    manager_note = Column(Text)

class Warning(Base):
    __tablename__ = "warnings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Compliment(Base):
    __tablename__ = "compliments"

    id = Column(Integer, primary_key=True)
    from_user_id = Column(Integer, ForeignKey("users.id"))
    to_user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String(20))  # CHEF, DELIVERY
    description = Column(Text)

    weight = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    cancelled_complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=True)
