from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app import models
from app.utils.hash import hash_password, verify_password
from app.utils.validators import is_valid_email
from app.utils.notifications import notify_manager, send_email
from app.utils.tokens import generate_token

SESSION_DURATION = timedelta(days=7)

def register_user(username: str, email: str, password: str, phone: str, db: Session) -> int:
    if not is_valid_email(email):
        raise ValueError("Invalid email format")

    if len(password) < 8:
        raise ValueError("Password too short")

    if db.query(models.User).filter(models.User.username == username).first():
        raise ValueError("Username already registered")

    if db.query(models.User).filter(models.User.email == email).first():
        raise ValueError("Email already registered")

    # blacklist check
    if db.query(models.Blacklist).filter((models.Blacklist.username == username) | (models.Blacklist.email == email)).first():
        raise ValueError("Account banned from registration")

    password_hash = hash_password(password)

    reg = models.Registration(
        username=username,
        email=email,
        password_hash=password_hash,
        phone=phone,
        status="PENDING",
        created_at=datetime.utcnow()
    )
    db.add(reg)
    db.commit()
    db.refresh(reg)

    notify_manager(f"New registration pending: {username}")

    return reg.id


def login(username: str, password: str, db: Session) -> str:
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        # log failed attempt (skipped)
        raise ValueError("Invalid credentials")

    if not verify_password(password, user.password_hash):
        # log failed attempt
        raise ValueError("Invalid credentials")

    if user.status == "DEREGISTERED":
        raise ValueError("Account deactivated")

    if user.warnings >= 3 and user.user_type == "CUSTOMER":
        raise ValueError("Account suspended due to warnings")

    token = generate_token()
    expires = datetime.utcnow() + SESSION_DURATION

    session = models.SessionToken(
        user_id=user.id,
        token=token,
        expires=expires,
        last_activity=datetime.utcnow()
    )
    db.add(session)
    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(session)

    return session.token


def approve_registration(registration_id: int, manager_id: int, db: Session) -> int:
    manager = db.query(models.User).get(manager_id)
    if manager is None or manager.user_type != "MANAGER":
        raise ValueError("Unauthorized")

    reg = db.query(models.Registration).get(registration_id)
    if reg is None or reg.status != "PENDING":
        raise ValueError("Invalid registration")

    with db.begin():
        user = models.User(
            username=reg.username,
            email=reg.email,
            password_hash=reg.password_hash,
            phone=reg.phone,
            user_type="CUSTOMER",
            created_at=datetime.utcnow(),
            warnings=0
        )
        db.add(user)
        db.flush()  # get user.id

        wallet = models.Wallet(
            user_id=user.id,
            balance=0.0,
            last_updated=datetime.utcnow()
        )
        db.add(wallet)

        reg.status = "APPROVED"
        reg.approved_by = manager_id
        reg.approved_at = datetime.utcnow()

    send_email(user.email, "Account approved! Welcome to our restaurant.")

    return user.id
