from sqlalchemy.orm import Session
from datetime import datetime

from app import models
from app.utils.notifications import notify_user

def demote_chef(chef_id: int, db: Session) -> bool:
    chef = db.query(models.User).get(chef_id)
    if chef is None or chef.emp_type != "CHEF":
        raise ValueError("Invalid chef")

    with db.begin():
        chef.demotions = (chef.demotions or 0) + 1
        chef.salary = (chef.salary or 0.0) * 0.85

        action = models.HRAction(
            employee_id=chef_id,
            action_type="DEMOTION",
            reason="Performance below standards",
            salary_change=-0.15,
            timestamp=datetime.utcnow()
        )
        db.add(action)

        if chef.demotions >= 2:
            # fireEmployee
            chef.status = "TERMINATED"
            chef.termination_date = datetime.utcnow()
            chef.termination_reason = "Two consecutive demotions"

    notify_user(chef_id, f"Performance review: You have been demoted. New salary: ${chef.salary:.2f}")
    return True


def promote_chef(chef_id: int, db: Session) -> bool:
    chef = db.query(models.User).get(chef_id)
    if chef is None or chef.emp_type != "CHEF":
        raise ValueError("Invalid chef")

    with db.begin():
        chef.demotions = 0
        bonus_amount = (chef.salary or 0.0) * 0.20
        chef.salary = (chef.salary or 0.0) * 1.10

        action = models.HRAction(
            employee_id=chef_id,
            action_type="PROMOTION",
            reason="Excellent performance",
            salary_change=0.10,
            bonus=bonus_amount,
            timestamp=datetime.utcnow()
        )
        db.add(action)

        # clear compliments/complaint counts if you track them separately

    notify_user(chef_id, f"Congratulations! You've earned a bonus of ${bonus_amount:.2f} and a 10% raise. New salary: ${chef.salary:.2f}")
    return True


def fire_employee(employee_id: int, reason: str, db: Session) -> bool:
    employee = db.query(models.User).get(employee_id)
    if employee is None:
        raise ValueError("Employee not found")

    if employee.user_type != "EMPLOYEE":
        raise ValueError("Not an employee")

    with db.begin():
        employee.status = "TERMINATED"
        employee.termination_date = datetime.utcnow()
        employee.termination_reason = reason
        db.add(employee)

        if employee.emp_type == "CHEF":
            db.query(models.Dish).filter(models.Dish.chef_id == employee_id).update({"active": False})
        if employee.emp_type == "DELIVERY":
            active_deliveries = db.query(models.Delivery).filter(models.Delivery.delivery_person_id == employee_id, models.Delivery.status.in_(["ASSIGNED", "ON_ROUTE"])).all()
            for d in active_deliveries:
                d.status = "UNASSIGNED"
                db.add(d)
                # requeue bidding
                # createDeliveryBiddingQueue(d.order_id) -- call out to your queue creator

        hr_action = models.HRAction(
            employee_id=employee_id,
            action_type="TERMINATION",
            reason=reason,
            timestamp=datetime.utcnow()
        )
        db.add(hr_action)

    notify_user(employee_id, f"Employment terminated. Reason: {reason}")
    return True
