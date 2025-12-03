from sqlalchemy.orm import Session
from datetime import datetime

from app import models
from app.utils.notifications import notify_manager, notify_user, notify_customer

def file_complaint(from_user_id: int, to_user_id: int, type_: str, description: str, order_id: int | None, db: Session) -> int:
    from_user = db.query(models.User).get(from_user_id)
    to_user = db.query(models.User).get(to_user_id)
    if from_user is None or to_user is None:
        raise ValueError("Invalid user(s)")

    if from_user_id == to_user_id:
        raise ValueError("Cannot file complaint against yourself")

    if len(description) < 20:
        raise ValueError("Description must be at least 20 characters")

    if order_id is not None:
        order = db.query(models.Order).get(order_id)
        if order is None:
            raise ValueError("Order not found")

        involved = False
        if type_ == "CHEF":
            involved = db.query(models.OrderItem).filter(models.OrderItem.order_id == order_id, models.OrderItem.chef_id == to_user_id).count() > 0
        elif type_ == "DELIVERY":
            involved = (order.delivery_id is not None) and (db.query(models.Delivery).get(order.delivery_id).delivery_person_id == to_user_id)
        elif type_ == "CUSTOMER":
            involved = order.customer_id == to_user_id or order.customer_id == from_user_id

        if not involved:
            raise ValueError("No transaction history with target user")

    duplicate = db.query(models.Complaint).filter(models.Complaint.from_user_id == from_user_id, models.Complaint.to_user_id == to_user_id, models.Complaint.order_id == order_id, models.Complaint.status == "PENDING").first()
    if duplicate:
        raise ValueError("Complaint already filed for this issue")

    weight = 2 if from_user.is_vip else 1

    complaint = models.Complaint(
        from_user_id=from_user_id,
        to_user_id=to_user_id,
        type=type_,
        description=description,
        order_id=order_id,
        status="PENDING",
        weight=weight,
        created_at=datetime.utcnow()
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    notify_manager(f"New complaint filed: #{complaint.id}")
    notify_user(to_user_id, f"A complaint has been filed against you. ID: #{complaint.id}")

    return complaint.id


def resolve_complaint(complaint_id: int, manager_id: int, decision: str, manager_note: str, db: Session) -> bool:
    manager = db.query(models.User).get(manager_id)
    if manager is None or manager.user_type != "MANAGER":
        raise ValueError("Unauthorized: Manager access required")

    complaint = db.query(models.Complaint).get(complaint_id)
    if complaint is None or complaint.status != "PENDING":
        raise ValueError("Invalid complaint or already resolved")

    from_user = db.query(models.User).get(complaint.from_user_id)
    to_user = db.query(models.User).get(complaint.to_user_id)

    with db.begin():
        complaint.status = decision
        complaint.manager_id = manager_id
        complaint.manager_note = manager_note
        complaint.resolved_at = datetime.utcnow()
        db.add(complaint)

        if decision == "UPHOLD":
            w = models.Warning(user_id=to_user.id, reason=f"Complaint upheld: {complaint.description}", created_at=datetime.utcnow())
            db.add(w)
            to_user.warnings += 1

            if complaint.type == "CHEF":
                chef_complaints = db.query(models.Complaint).filter(models.Complaint.to_user_id == to_user.id, models.Complaint.status == "UPHOLD", models.Complaint.type == "CHEF").count()
                if chef_complaints >= 3:
                    # demoteChef
                    to_user.emp_type = "DEMERIT_CHEF"  # placeholder - call HR service
            elif complaint.type == "DELIVERY":
                delivery_complaints = db.query(models.Complaint).filter(models.Complaint.to_user_id == to_user.id, models.Complaint.status == "UPHOLD", models.Complaint.type == "DELIVERY").count()
                if delivery_complaints >= 3:
                    to_user.emp_type = "DEMERIT_DELIVERY"
            elif complaint.type == "CUSTOMER":
                if to_user.warnings >= 3:
                    to_user.status = "DEREGISTERED"
                elif to_user.is_vip and to_user.warnings >= 2:
                    to_user.is_vip = False

        elif decision == "DISMISS":
            w = models.Warning(user_id=from_user.id, reason="Complaint dismissed as without merit", created_at=datetime.utcnow())
            db.add(w)
            from_user.warnings += 1
            if from_user.warnings >= 3:
                from_user.status = "DEREGISTERED"

    notify_user(from_user.id, f"Your complaint has been {decision} by management.")
    notify_user(to_user.id, f"The complaint against you has been {decision}.")

    return True


def file_compliment(from_user_id: int, to_user_id: int, type_: str, description: str, db: Session) -> int:
    from_user = db.query(models.User).get(from_user_id)
    to_user = db.query(models.User).get(to_user_id)
    if from_user is None or to_user is None:
        raise ValueError("Invalid user(s)")

    weight = 2 if from_user.is_vip else 1
    compliment = models.Compliment(
        from_user_id=from_user_id,
        to_user_id=to_user_id,
        type=type_,
        description=description,
        weight=weight,
        created_at=datetime.utcnow()
    )
    db.add(compliment)
    db.commit()
    db.refresh(compliment)

    # cancel oldest active complaint if exists
    active_complaints = db.query(models.Complaint).filter(models.Complaint.to_user_id == to_user_id, models.Complaint.status == "PENDING").order_by(models.Complaint.created_at).all()
    if active_complaints:
        complaint = active_complaints[0]
        complaint.status = "CANCELLED"
        complaint.cancelled_by = compliment.id if hasattr(complaint, 'cancelled_by') else None
        db.add(complaint)
        # remove associated warning if any (implement removeWarning)
        # removeWarning(to_user_id, complaint.id) -- left for helper implementation

    # track compliments for performance (count)
    compliment_count = db.query(models.Compliment).filter(models.Compliment.to_user_id == to_user_id, models.Compliment.type == type_).count()
    if type_ == "CHEF" and compliment_count >= 3:
        # giveChefBonus
        pass
    elif type_ == "DELIVERY" and compliment_count >= 3:
        # giveDeliveryBonus
        pass

    notify_user(to_user_id, "You received a compliment!")
    return compliment.id
