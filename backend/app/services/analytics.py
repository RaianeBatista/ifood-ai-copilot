from collections import Counter
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Order
from app.schemas.order import OperationalSummary


def date_bounds(start_date: date | None, end_date: date | None) -> tuple[datetime | None, datetime | None]:
    start = (
        datetime.combine(start_date, time.min, tzinfo=timezone.utc)
        if start_date is not None
        else None
    )
    end = (
        datetime.combine(end_date + timedelta(days=1), time.min, tzinfo=timezone.utc)
        if end_date is not None
        else None
    )
    return start, end


def orders_for_period(
    db: Session,
    restaurant_id: str,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[Order]:
    start, end = date_bounds(start_date, end_date)
    statement = select(Order).where(Order.restaurant_id == restaurant_id)
    if start is not None:
        statement = statement.where(Order.created_at >= start)
    if end is not None:
        statement = statement.where(Order.created_at < end)
    return list(db.scalars(statement.order_by(Order.created_at)))


def summarize_orders(restaurant_id: str, orders: list[Order]) -> OperationalSummary:
    by_status = Counter(order.status for order in orders)
    by_hour = Counter(order.created_at.hour for order in orders if order.status != "cancelled")
    delivered = [order for order in orders if order.status == "delivered"]
    revenue = sum((order.amount for order in delivered), start=Decimal("0.00"))
    average = revenue / len(delivered) if delivered else Decimal("0.00")

    return OperationalSummary(
        restaurant_id=restaurant_id,
        total_orders=len(orders),
        completed_orders=len(delivered),
        cancelled_orders=by_status["cancelled"],
        revenue=revenue.quantize(Decimal("0.01")),
        average_order_value=average.quantize(Decimal("0.01")),
        orders_by_status=dict(by_status),
        orders_by_hour=[
            {"hour": hour, "orders": by_hour[hour]} for hour in range(24)
        ],
    )
