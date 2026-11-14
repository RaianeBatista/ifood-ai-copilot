from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Order
from scripts.seed_demo_data import generate_demo_orders, seed_demo_orders


def test_seed_demo_orders_is_repeatable_and_does_not_duplicate():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=test_engine)
    now = datetime(2026, 11, 14, 15, 0, tzinfo=timezone.utc)

    try:
        with Session(test_engine) as db:
            inserted, existing = seed_demo_orders(
                db, restaurant_id="demo-restaurant", days=7, now=now
            )
            repeated_inserted, repeated_existing = seed_demo_orders(
                db, restaurant_id="demo-restaurant", days=7, now=now
            )
            total = db.scalar(
                select(func.count()).select_from(Order).where(
                    Order.restaurant_id == "demo-restaurant"
                )
            )

        generated = generate_demo_orders("demo-restaurant", days=7, now=now)
        assert inserted == len(generated)
        assert existing == 0
        assert repeated_inserted == 0
        assert repeated_existing == len(generated)
        assert total == len(generated)
    finally:
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


def test_seed_demo_orders_rejects_invalid_history_length():
    with pytest.raises(ValueError, match="days deve estar entre"):
        generate_demo_orders("demo-restaurant", days=0)
