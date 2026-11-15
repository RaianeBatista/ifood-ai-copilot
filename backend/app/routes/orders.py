from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.auth import DemoAccount, ensure_restaurant_access, get_current_account
from app.database import get_db
from app.models import Order
from app.schemas.order import OrderCreate, OrderRead, OrderUpdate
from app.services.orders import (
    create_order,
    delete_order,
    get_order,
    list_orders,
    update_order,
)

router = APIRouter(prefix="/orders", tags=["orders"])


def find_order_or_404(db: Session, restaurant_id: str, order_id: str) -> Order:
    order = get_order(db, restaurant_id, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    return order


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order_endpoint(
    payload: OrderCreate,
    account: DemoAccount = Depends(get_current_account),
    db: Session = Depends(get_db),
) -> Order:
    ensure_restaurant_access(payload.restaurant_id, account)
    return create_order(db, payload)


@router.get("", response_model=list[OrderRead])
def list_orders_endpoint(
    restaurant_id: str = Query(min_length=1, max_length=100),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    account: DemoAccount = Depends(get_current_account),
    db: Session = Depends(get_db),
) -> list[Order]:
    ensure_restaurant_access(restaurant_id, account)
    return list_orders(db, restaurant_id, limit, offset)


@router.get("/{order_id}", response_model=OrderRead)
def get_order_endpoint(
    order_id: str,
    restaurant_id: str = Query(min_length=1, max_length=100),
    account: DemoAccount = Depends(get_current_account),
    db: Session = Depends(get_db),
) -> Order:
    ensure_restaurant_access(restaurant_id, account)
    return find_order_or_404(db, restaurant_id, order_id)


@router.patch("/{order_id}", response_model=OrderRead)
def update_order_endpoint(
    order_id: str,
    payload: OrderUpdate,
    restaurant_id: str = Query(min_length=1, max_length=100),
    account: DemoAccount = Depends(get_current_account),
    db: Session = Depends(get_db),
) -> Order:
    ensure_restaurant_access(restaurant_id, account)
    order = find_order_or_404(db, restaurant_id, order_id)
    return update_order(db, order, payload)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_endpoint(
    order_id: str,
    restaurant_id: str = Query(min_length=1, max_length=100),
    account: DemoAccount = Depends(get_current_account),
    db: Session = Depends(get_db),
) -> Response:
    ensure_restaurant_access(restaurant_id, account)
    order = find_order_or_404(db, restaurant_id, order_id)
    delete_order(db, order)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
