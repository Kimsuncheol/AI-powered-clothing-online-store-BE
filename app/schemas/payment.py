from decimal import Decimal
from typing import Any, Dict

from pydantic import BaseModel

from app.models.order import OrderStatus
from app.models.payment import PaymentStatus


class PayPalCreateRequest(BaseModel):
    order_id: int


class PayPalCreateResponse(BaseModel):
    payment_id: int
    provider_payment_id: str
    status: PaymentStatus
    approval_url: str


class PayPalCaptureRequest(BaseModel):
    provider_payment_id: str


class PayPalCaptureResponse(BaseModel):
    payment_id: int
    provider_payment_id: str
    status: PaymentStatus
    order_id: int
    order_status: OrderStatus


class PayPalWebhookEvent(BaseModel):
    id: str
    event_type: str
    resource: Dict[str, Any]
