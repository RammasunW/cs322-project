from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, unique=True)
    delivery_person_id = Column(Integer, ForeignKey("users.id"))

    bid_amount = Column(Float)
    status = Column(String(20))  # ASSIGNED, ON_ROUTE, DELIVERED

    assigned_by = Column(Integer, ForeignKey("users.id"))
    manager_memo = Column(Text)

    assigned_at = Column(DateTime)
    picked_up_at = Column(DateTime)
    delivered_at = Column(DateTime)
    updated_at = Column(DateTime)


class DeliveryBid(Base):
    __tablename__ = "delivery_bids"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    delivery_person_id = Column(Integer, ForeignKey("users.id"))

    bid_amount = Column(Float)
    status = Column(String(20))  # PENDING, ACCEPTED, REJECTED
    submitted_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)
