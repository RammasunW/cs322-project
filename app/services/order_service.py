from typing import List, Dict
from sqlalchemy.orm import Session
from datetime import datetime

from app import models
from app.utils.notifications import notify_chef, notify_manager
from app.services.menu_service import get_personalized_menu  # optional
from sqlalchemy import func

def place_order(customer_id: int, cart_items: List[Dict], delivery_address: str, db: Session) -> int:
    customer = db.query(models.User).get(customer_id)
    if not customer:
        raise ValueError("Customer not found")

    if customer.warnings >= 3:
        raise ValueError("Account suspended. Cannot place orders.")

    subtotal = 0.0
    order_items = []
    for item in cart_items:
        dish = db.query(models.Dish).get(item['dishId'])
        if dish is None or dish.active is False:
            raise ValueError(f"Dish unavailable: {item['dishId']}")
        item_total = dish.price * item['quantity']
        subtotal += item_total
        order_items.append({
            'dish_id': dish.id,
            'quantity': item['quantity'],
            'price': dish.price,
            'chef_id': dish.chef_id
        })

    discount = 0.0
    free_delivery = False
    is_vip = customer.is_vip

    if is_vip:
        discount = subtotal * 0.05
        vip_orders = db.query(models.Order).filter(models.Order.customer_id == customer_id, models.Order.status == "COMPLETED").count()
        if vip_orders % 3 == 2:
            free_delivery = True

    total = subtotal - discount

    wallet = db.query(models.Wallet).filter(models.Wallet.user_id == customer_id).with_for_update().first()
    if wallet is None:
        raise ValueError("Wallet not found")

    if wallet.balance < total:
        # issue warning (create Warning model entry)
        warning = models.Warning(user_id=customer_id, reason="Insufficient balance for order", created_at=datetime.utcnow())
        db.add(warning)
        db.commit()
        raise ValueError("Insufficient funds. Please deposit money.")

    with db.begin():
        order = models.Order(
            customer_id=customer_id,
            status="PENDING",
            subtotal=subtotal,
            discount=discount,
            total=total,
            delivery_address=delivery_address,
            free_delivery=free_delivery,
            order_date=datetime.utcnow()
        )
        db.add(order)
        db.flush()  # get order.id

        for it in order_items:
            oi = models.OrderItem(
                order_id=order.id,
                dish_id=it['dish_id'],
                quantity=it['quantity'],
                price=it['price'],
                chef_id=it['chef_id']
            )
            db.add(oi)

        wallet.balance -= total
        wallet.last_updated = datetime.utcnow()
        db.add(models.Transaction(
            wallet_id=wallet.id,
            type="ORDER",
            amount=-total,
            description=f"Order #{order.id}",
            timestamp=datetime.utcnow(),
            balance_after=wallet.balance
        ))

        # update customer stats
        if is_vip:
            customer.spent = (customer.spent or 0) + total
        else:
            customer.spent = (customer.spent or 0) + total
            customer.orders = (customer.orders or 0) + 1
            if customer.spent > 100 and customer.orders >= 3:
                complaints = db.query(models.Complaint).filter(models.Complaint.from_user_id == customer_id, models.Complaint.status == "PENDING").count()
                if complaints == 0:
                    customer.is_vip = True  # promoteToVIP

    # notify chefs
    unique_chefs = {it['chef_id'] for it in order_items}
    for chef_id in unique_chefs:
        notify_chef(chef_id, f"New order received: Order #{order.id}")

    # create delivery bidding queue (implementation detail: insert into some queue table or call external system)
    notify_manager(f"Order #{order.id} queued for delivery bidding")

    return order.id
