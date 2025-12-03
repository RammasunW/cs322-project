from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from app import models
from app.utils.validators import is_valid_url
from app.utils.notifications import log_activity

def create_dish(chef_id: int, name: str, description: str, price: float, image_url: str, db: Session) -> int:
    chef = db.query(models.User).get(chef_id)
    if chef is None or chef.emp_type != "CHEF":
        raise ValueError("Unauthorized: Not a chef")

    if price <= 0:
        raise ValueError("Price must be positive")

    if not (1 <= len(name) <= 100):
        raise ValueError("Invalid dish name length")

    if db.query(models.Dish).filter(models.Dish.chef_id == chef_id, models.Dish.name == name).first():
        raise ValueError("Dish name already exists in your menu")

    if image_url and not is_valid_url(image_url):
        raise ValueError("Invalid image URL")

    dish = models.Dish(
        chef_id=chef_id,
        name=name,
        description=description,
        price=price,
        image_url=image_url,
        active=True,
        created_at=datetime.utcnow(),
        rating=0.0,
        rating_count=0
    )
    db.add(dish)
    db.commit()
    db.refresh(dish)

    log_activity(chef_id, f"Created dish: {name}")
    return dish.id


def get_personalized_menu(user_id: Optional[int], db: Session) -> dict:
    menu_data = {}

    if user_id:
        # Order history
        order_history = db.query(models.Order).filter(models.Order.customer_id == user_id).all()
        dish_freq = {}
        for o in order_history:
            items = db.query(models.OrderItem).filter(models.OrderItem.order_id == o.id).all()
            for it in items:
                dish_freq[it.dish_id] = dish_freq.get(it.dish_id, 0) + it.quantity

        most_ordered_ids = sorted(dish_freq, key=lambda k: dish_freq[k], reverse=True)[:5]
        menu_data['mostOrdered'] = db.query(models.Dish).filter(models.Dish.id.in_(most_ordered_ids)).all()

        # user ratings (assume a Rating table if exists; fallback none)
        user_ratings = db.query(models.Dish).join(models.User, models.Dish.chef_id == models.User.id).all()  # placeholder
        # We'll return topRated from user's rating data if such table exists; otherwise empty
        menu_data['topRated'] = []  # implement if you have a ratings table
    else:
        popular = (db.query(models.OrderItem.dish_id, func.count(models.OrderItem.id).label("order_count"))
                   .group_by(models.OrderItem.dish_id)
                   .order_by(desc("order_count"))
                   .limit(10)
                   .all())
        popular_ids = [r.dish_id for r in popular]
        menu_data['popular'] = db.query(models.Dish).filter(models.Dish.id.in_(popular_ids)).all()

        highest_rated = db.query(models.Dish).filter(models.Dish.rating_count > 5).order_by(models.Dish.rating.desc()).limit(10).all()
        menu_data['topRated'] = highest_rated

    # featured chefs
    top_chefs = (db.query(models.Dish.chef_id, func.avg(models.Dish.rating).label("avg_rating"))
                 .filter(models.Dish.active == True)
                 .group_by(models.Dish.chef_id)
                 .order_by(desc("avg_rating"))
                 .limit(3)
                 .all())
    chef_ids = [r.chef_id for r in top_chefs]
    menu_data['featuredChefs'] = db.query(models.User).filter(models.User.id.in_(chef_ids)).all()

    menu_data['allDishes'] = db.query(models.Dish).filter(models.Dish.active == True).all()

    return menu_data
