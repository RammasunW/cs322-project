from sqlalchemy.orm import Session
from datetime import datetime

from app import models
from app.utils.notifications import notify_manager, notify_delivery_person, notify_customer

def submit_delivery_bid(delivery_person_id: int, order_id: int, bid_amount: float, db: Session) -> int:
    delivery_person = db.query(models.User).get(delivery_person_id)
    if delivery_person is None or delivery_person.emp_type != "DELIVERY":
        raise ValueError("Unauthorized: Not a delivery person")

    order = db.query(models.Order).get(order_id)
    if order is None:
        raise ValueError("Order not found")

    if order.status != "PENDING":
        raise ValueError("Order not available for bidding")

    if bid_amount < 0:
        raise ValueError("Invalid bid amount")

    existing = db.query(models.DeliveryBid).filter(models.DeliveryBid.delivery_person_id == delivery_person_id, models.DeliveryBid.order_id == order_id).first()
    if existing:
        existing.bid_amount = bid_amount
        existing.updated_at = datetime.utcnow()
        db.commit()
        return existing.id

    bid = models.DeliveryBid(
        order_id=order_id,
        delivery_person_id=delivery_person_id,
        bid_amount=bid_amount,
        status="PENDING",
        submitted_at=datetime.utcnow()
    )
    db.add(bid)
    db.commit()
    db.refresh(bid)

    notify_manager(f"New delivery bid for Order #{order_id}")

    return bid.id


def assign_delivery(manager_id: int, order_id: int, delivery_person_id: int, memo: str, db: Session) -> int:
    manager = db.query(models.User).get(manager_id)
    if manager is None or manager.user_type != "MANAGER":
        raise ValueError("Unauthorized: Manager access required")

    bids = db.query(models.DeliveryBid).filter(models.DeliveryBid.order_id == order_id).all()
    if len(bids) == 0:
        raise ValueError("No bids available for this order")

    selected_bid = db.query(models.DeliveryBid).filter(models.DeliveryBid.order_id == order_id, models.DeliveryBid.delivery_person_id == delivery_person_id).first()
    if selected_bid is None:
        raise ValueError("Selected delivery person has not bid")

    lowest_bid = min(bids, key=lambda b: b.bid_amount)

    if selected_bid.bid_amount > lowest_bid.bid_amount:
        if not memo or len(memo) < 10:
            raise ValueError("Justification memo required for non-lowest bid")

    with db.begin():
        delivery = models.Delivery(
            order_id=order_id,
            delivery_person_id=delivery_person_id,
            bid_amount=selected_bid.bid_amount,
            status="ASSIGNED",
            assigned_by=manager_id,
            manager_memo=memo,
            assigned_at=datetime.utcnow()
        )
        db.add(delivery)
        db.flush()

        order = db.query(models.Order).get(order_id)
        order.status = "ASSIGNED"
        order.delivery_id = delivery.id
        db.add(order)

        for b in bids:
            if b.delivery_person_id == delivery_person_id:
                b.status = "ACCEPTED"
            else:
                b.status = "REJECTED"
            db.add(b)

    notify_delivery_person(delivery_person_id, f"You've been assigned Order #{order_id}")

    for b in bids:
        if b.delivery_person_id != delivery_person_id:
            notify_delivery_person(b.delivery_person_id, f"Your bid for Order #{order_id} was not selected")

    return delivery.id


def update_delivery_status(delivery_id: int, new_status: str, db: Session) -> bool:
    delivery = db.query(models.Delivery).get(delivery_id)
    if delivery is None:
        return False

    valid_transitions = {
        "ASSIGNED": ["ON_ROUTE"],
        "ON_ROUTE": ["DELIVERED"],
        "DELIVERED": []
    }

    if new_status not in valid_transitions.get(delivery.status, []):
        raise ValueError("Invalid status transition")

    with db.begin():
        delivery.status = new_status
        delivery.updated_at = datetime.utcnow()
        if new_status == "ON_ROUTE":
            delivery.picked_up_at = datetime.utcnow()
        elif new_status == "DELIVERED":
            delivery.delivered_at = datetime.utcnow()
            order = db.query(models.Order).get(delivery.order_id)
            order.status = "COMPLETED"
            db.add(order)

    # Notify customer
    order = db.query(models.Order).get(delivery.order_id)
    notify_customer(order.customer_id, "Your order has been delivered!")

    return True
