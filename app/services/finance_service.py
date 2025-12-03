from sqlalchemy.orm import Session
from datetime import datetime

from app import models
from app.utils.notifications import notify_user

def deposit_funds(user_id: int, amount: float, db: Session) -> int:
    if amount <= 0:
        raise ValueError("Deposit amount must be positive")

    wallet = db.query(models.Wallet).filter(models.Wallet.user_id == user_id).first()
    if wallet is None:
        raise ValueError("Wallet not found")

    with db.begin():
        wallet.balance += amount
        wallet.last_updated = datetime.utcnow()
        db.add(wallet)

        txn = models.Transaction(
            wallet_id=wallet.id,
            type="DEPOSIT",
            amount=amount,
            description="Deposit to wallet",
            timestamp=datetime.utcnow(),
            balance_after=wallet.balance
        )
        db.add(txn)
        db.flush()

    notify_user(user_id, f"Deposit successful. New balance: ${wallet.balance:.2f}")
    return txn.id


def process_refund(order_id: int, reason: str, db: Session) -> bool:
    order = db.query(models.Order).get(order_id)
    if order is None:
        raise ValueError("Order not found")

    if order.status == "REFUNDED":
        raise ValueError("Order already refunded")

    wallet = db.query(models.Wallet).filter(models.Wallet.user_id == order.customer_id).with_for_update().first()
    if wallet is None:
        raise ValueError("Wallet not found")

    with db.begin():
        wallet.balance += order.total
        wallet.last_updated = datetime.utcnow()
        db.add(wallet)

        txn = models.Transaction(
            wallet_id=wallet.id,
            type="REFUND",
            amount=order.total,
            description=f"Refund for Order #{order_id}: {reason}",
            timestamp=datetime.utcnow(),
            balance_after=wallet.balance
        )
        db.add(txn)

        order.status = "REFUNDED"
        order.refund_reason = reason
        order.refunded_at = datetime.utcnow()
        db.add(order)

    notify_user(order.customer_id, f"Refund processed: ${order.total:.2f} for Order #{order_id}")
    return True


def close_account(user_id: int, manager_id: int | None, reason: str, db: Session) -> bool:
    if reason != "VOLUNTARY":
        manager = db.query(models.User).get(manager_id)
        if manager is None or manager.user_type != "MANAGER":
            raise ValueError("Unauthorized")

    user = db.query(models.User).get(user_id)
    wallet = db.query(models.Wallet).filter(models.Wallet.user_id == user_id).first()
    if user is None:
        raise ValueError("User not found")

    refund_amount = 0.0
    with db.begin():
        if wallet and wallet.balance > 0:
            txn = models.Transaction(
                wallet_id=wallet.id,
                type="WITHDRAWAL",
                amount=-wallet.balance,
                description="Account closure refund",
                timestamp=datetime.utcnow(),
                balance_after=0.0
            )
            db.add(txn)
            refund_amount = wallet.balance
            wallet.balance = 0
            wallet.last_updated = datetime.utcnow()
            db.add(wallet)

        active_orders = db.query(models.Order).filter(models.Order.customer_id == user_id, models.Order.status.in_(["PENDING", "ASSIGNED"])).all()
        for o in active_orders:
            process_refund(o.id, "Account closed", db)

        user.status = "DEREGISTERED"
        user.deregistered_at = datetime.utcnow()
        user.deregistered_by = manager_id
        user.deregistration_reason = reason
        db.add(user)

        if reason in ("KICKED", "BLACKLIST"):
            bl = models.Blacklist(
                username=user.username,
                email=user.email,
                reason=reason,
                banned_date=datetime.utcnow(),
                banned_by=manager_id
            )
            db.add(bl)

    if refund_amount > 0:
        notify_user(user_id, f"Account closed. Refund of ${refund_amount:.2f} processed.")

    return True
