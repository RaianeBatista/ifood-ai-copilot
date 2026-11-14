from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.order import OperationalSummary
from app.services.analytics import orders_for_period, summarize_orders
from app.services.forecast import forecast_daily_orders

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=OperationalSummary)
def operational_summary(
    restaurant_id: str = Query(min_length=1, max_length=100),
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
) -> OperationalSummary:
    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(status_code=422, detail="start_date deve ser anterior a end_date.")
    orders = orders_for_period(db, restaurant_id, start_date, end_date)
    return summarize_orders(restaurant_id, orders)


@router.get("/forecast")
def demand_forecast(
    restaurant_id: str = Query(min_length=1, max_length=100),
    days: int = Query(default=7, ge=1, le=30),
    history_days: int = Query(default=90, ge=7, le=365),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    try:
        forecast = forecast_daily_orders(db, restaurant_id, history_days, days)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "restaurant_id": restaurant_id,
        "history_days": history_days,
        "forecast": forecast,
    }
