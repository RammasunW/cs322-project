from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Dish(Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True)
    chef_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100))
    description = Column(Text)
    price = Column(Float)
    image_url = Column(String(500))

    active = Column(Boolean, default=True)
    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
