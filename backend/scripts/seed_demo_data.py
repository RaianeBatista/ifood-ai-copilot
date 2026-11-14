import argparse
import hashlib
import random
from datetime import datetime, time, timedelta, timezone
from decimal import Decimal
from uuid import NAMESPACE_URL, uuid5

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.models import Order

DEFAULT_RESTAURANT_ID = "demo-restaurant"
DEFAULT_DAYS = 90
MAX_DAYS = 365


def generate_demo_orders(
    restaurant_id: str,
    days: int = DEFAULT_DAYS,
    now: datetime | None = None,
) -> list[Order]:
    if not restaurant_id or len(restaurant_id) > 100:
        raise ValueError("restaurant_id deve ter entre 1 e 100 caracteres.")
    if not 1 <= days <= MAX_DAYS:
        raise ValueError(f"days deve estar entre 1 e {MAX_DAYS}.")

    current_time = now or datetime.now(timezone.utc)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)
    today = current_time.astimezone(timezone.utc).date()
    first_day = today - timedelta(days=days - 1)
    preferred_hours = [11, 11, 12, 12, 13, 14, 18, 18, 19, 19, 20, 21]
    orders: list[Order] = []

    for day_offset in range(days):
        order_date = first_day + timedelta(days=day_offset)
        seed_bytes = hashlib.sha256(
            f"{restaurant_id}:{order_date.isoformat()}".encode("utf-8")
        ).digest()[:8]
        generator = random.Random(int.from_bytes(seed_bytes, "big"))

        base_count = (
            8 if order_date.weekday() in (4, 5)
            else 6 if order_date.weekday() == 6
            else 4
        )
        order_count = base_count + generator.randint(0, 3)
        available_hours = preferred_hours
        if order_date == today:
            available_hours = [hour for hour in preferred_hours if hour <= current_time.hour]
            if not available_hours:
                available_hours = [current_time.hour]

        for index in range(order_count):
            hour = generator.choice(available_hours)
            latest_minute = (
                current_time.minute
                if order_date == today and hour == current_time.hour
                else 59
            )
            minute = generator.randint(0, latest_minute)
            items_count = generator.choices(
                [1, 2, 3, 4, 5],
                weights=[15, 35, 28, 16, 6],
                k=1,
            )[0]
            amount = (
                Decimal("12.50") * items_count
                + Decimal(generator.randint(0, 2199)) / Decimal("100")
            ).quantize(Decimal("0.01"))
            status = generator.choices(
                ["delivered", "preparing", "pending", "cancelled"],
                weights=[78, 10, 7, 5],
                k=1,
            )[0]
            order_id = str(
                uuid5(
                    NAMESPACE_URL,
                    f"ifood-ai-copilot-demo:{restaurant_id}:{order_date.isoformat()}:{index}",
                )
            )

            orders.append(
                Order(
                    id=order_id,
                    restaurant_id=restaurant_id,
                    amount=amount,
                    items_count=items_count,
                    status=status,
                    created_at=datetime.combine(
                        order_date,
                        time(hour=hour, minute=minute),
                        tzinfo=timezone.utc,
                    ),
                )
            )

    return orders


def seed_demo_orders(
    db: Session,
    restaurant_id: str = DEFAULT_RESTAURANT_ID,
    days: int = DEFAULT_DAYS,
    now: datetime | None = None,
) -> tuple[int, int]:
    orders = generate_demo_orders(restaurant_id, days, now)
    order_ids = [order.id for order in orders]
    existing_ids = set(
        db.scalars(select(Order.id).where(Order.id.in_(order_ids)))
    )
    new_orders = [order for order in orders if order.id not in existing_ids]

    db.add_all(new_orders)
    db.commit()
    return len(new_orders), len(existing_ids)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Insere pedidos sintéticos para demonstrar o dashboard."
    )
    parser.add_argument(
        "--restaurant-id",
        default=DEFAULT_RESTAURANT_ID,
        help=f"Identificador do restaurante (padrão: {DEFAULT_RESTAURANT_ID}).",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=DEFAULT_DAYS,
        help=f"Quantidade de dias de histórico, entre 1 e {MAX_DAYS} (padrão: {DEFAULT_DAYS}).",
    )
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        inserted_count, existing_count = seed_demo_orders(
            db,
            restaurant_id=args.restaurant_id,
            days=args.days,
        )

    print(
        f"Massa de demonstração: {inserted_count} pedidos adicionados; "
        f"{existing_count} já existiam para '{args.restaurant_id}'."
    )


if __name__ == "__main__":
    main()
