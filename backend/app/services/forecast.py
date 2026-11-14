from collections import Counter
from datetime import date, datetime, time, timedelta, timezone

from sklearn.linear_model import LinearRegression
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Order


def forecast_daily_orders(
    db: Session,
    restaurant_id: str,
    history_days: int,
    forecast_days: int,
) -> list[dict[str, int | date]]:
    today = datetime.now(timezone.utc).date()
    first_day = today - timedelta(days=history_days - 1)
    start = datetime.combine(first_day, time.min, tzinfo=timezone.utc)
    end = datetime.combine(today + timedelta(days=1), time.min, tzinfo=timezone.utc)
    statement = select(Order.created_at).where(
        Order.restaurant_id == restaurant_id,
        Order.status != "cancelled",
        Order.created_at >= start,
        Order.created_at < end,
    )
    order_dates = [created_at.date() for created_at in db.scalars(statement)]
    active_days = set(order_dates)
    if len(active_days) < 2:
        raise ValueError("São necessários pedidos em pelo menos dois dias para prever a demanda.")

    counts = Counter(order_dates)
    history = [
        (first_day + timedelta(days=offset), counts[first_day + timedelta(days=offset)])
        for offset in range(history_days)
    ]
    x_values = [[offset] for offset in range(history_days)]
    y_values = [count for _, count in history]

    model = LinearRegression()
    model.fit(x_values, y_values)
    next_values = model.predict([[history_days + offset] for offset in range(forecast_days)])

    return [
        {
            "date": today + timedelta(days=offset + 1),
            "predicted_orders": max(0, round(float(value))),
        }
        for offset, value in enumerate(next_values)
    ]
