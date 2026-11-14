from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Order
from app.schemas.order import OrderCreate, OrderUpdate


def create_order(db: Session, payload: OrderCreate) -> Order:
    created_at = payload.created_at
    if created_at is not None and created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    order = Order(
        restaurant_id=payload.restaurant_id,
        amount=payload.amount,
        items_count=payload.items_count,
        status=payload.status.value,
        created_at=created_at or datetime.now(timezone.utc),
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_order(db: Session, restaurant_id: str, order_id: str) -> Order | None:
    return db.scalar(
        select(Order).where(Order.restaurant_id == restaurant_id, Order.id == order_id)
    )


def list_orders(db: Session, restaurant_id: str, limit: int, offset: int) -> list[Order]:
    statement = (
        select(Order)
        .where(Order.restaurant_id == restaurant_id)
        .order_by(Order.created_at.desc(), Order.id)
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(statement))


def update_order(db: Session, order: Order, payload: OrderUpdate) -> Order:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(order, field, value.value if hasattr(value, "value") else value)
    db.commit()
    db.refresh(order)
    return order


def delete_order(db: Session, order: Order) -> None:
    db.delete(order)
    db.commit()
