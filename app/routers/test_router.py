from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

router = APIRouter(prefix="/test", tags=["Test"])

@router.post("/create_user")
def create_user(username: str, db: Session = Depends(get_db)):
    user = User(username=username)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username}

@router.get("/users")
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()
