from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True)
    '''email = Column(String(100), unique=True)
    password_hash = Column(String(255))
    phone = Column(String(20))

    user_type = Column(String(20))  # CUSTOMER, VIP, EMPLOYEE, MANAGER
    emp_type = Column(String(20), nullable=True)  # CHEF, DELIVERY

    status = Column(String(20), default="ACTIVE")  # ACTIVE, DEREGISTERED, TERMINATED
    warnings = Column(Integer, default=0)

    is_vip = Column(Boolean, default=False)
    orders = Column(Integer, default=0)
    spent = Column(Float, default=0.0)

    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    wallet = relationship("Wallet", uselist=False, back_populates="user")'''
