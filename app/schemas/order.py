from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict

from app.models.order import OrderStatus


class OrderItemSchema(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    variant_data: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class OrderCreateResponse(BaseModel):
    id: int
    total_amount: Decimal
    currency: str


class OrderDetailSchema(BaseModel):
    id: int
    user_id: int
    total_amount: Decimal
    currency: str
    status: OrderStatus
    items: List[OrderItemSchema]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderListItemSchema(BaseModel):
    id: int
    total_amount: Decimal
    currency: str
    status: OrderStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderListResponse(BaseModel):
    items: List[OrderListItemSchema]
