from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class OrderStatus(str, Enum):
    pending = "pending"
    preparing = "preparing"
    delivered = "delivered"
    cancelled = "cancelled"


class OrderCreate(BaseModel):
    restaurant_id: str = Field(min_length=1, max_length=100)
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    items_count: int = Field(ge=1)
    status: OrderStatus = OrderStatus.pending
    created_at: datetime | None = None


class OrderUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    items_count: int | None = Field(default=None, ge=1)
    status: OrderStatus | None = None

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "OrderUpdate":
        if not self.model_fields_set:
            raise ValueError("Informe ao menos um campo para atualizar.")
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("Os campos de atualização não podem ser nulos.")
        return self


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    restaurant_id: str
    amount: Decimal
    items_count: int
    status: OrderStatus
    created_at: datetime


class HourMetric(BaseModel):
    hour: int
    orders: int


class OperationalSummary(BaseModel):
    restaurant_id: str
    total_orders: int
    completed_orders: int
    cancelled_orders: int
    revenue: Decimal
    average_order_value: Decimal
    orders_by_status: dict[str, int]
    orders_by_hour: list[HourMetric]
