from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(20))  # PENDING, ASSIGNED, COMPLETED, REFUNDED

    subtotal = Column(Float)
    discount = Column(Float)
    total = Column(Float)

    delivery_address = Column(Text)
    free_delivery = Column(Boolean, default=False)

    order_date = Column(DateTime, default=datetime.utcnow)
    delivery_id = Column(Integer, ForeignKey("deliveries.id"), nullable=True)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    dish_id = Column(Integer, ForeignKey("dishes.id"))
    quantity = Column(Integer)
    price = Column(Float)

    chef_id = Column(Integer, ForeignKey("users.id"))
