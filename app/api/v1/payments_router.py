from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.dependencies import get_payment_service
from app.models.user import User
from app.schemas.payment import (
    PayPalCaptureRequest,
    PayPalCaptureResponse,
    PayPalCreateRequest,
    PayPalCreateResponse,
    PayPalWebhookEvent,
)
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/paypal/create", response_model=PayPalCreateResponse)
def create_paypal_order(
    body: PayPalCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service),
) -> PayPalCreateResponse:
    payment, approval_url = payment_service.create_paypal_order(
        db,
        order_id=body.order_id,
        user_id=current_user.id,
    )
    return PayPalCreateResponse(
        payment_id=payment.id,
        provider_payment_id=payment.provider_payment_id,
        status=payment.status,
        approval_url=approval_url,
    )


@router.post("/paypal/capture", response_model=PayPalCaptureResponse)
def capture_paypal_order(
    body: PayPalCaptureRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service),
) -> PayPalCaptureResponse:
    payment = payment_service.capture_paypal_order(
        db,
        provider_payment_id=body.provider_payment_id,
        user_id=current_user.id,
    )
    order = payment.order
    return PayPalCaptureResponse(
        payment_id=payment.id,
        provider_payment_id=payment.provider_payment_id,
        status=payment.status,
        order_id=order.id if order else None,
        order_status=order.status if order else None,
    )


@router.post("/paypal/webhook", status_code=status.HTTP_204_NO_CONTENT)
def paypal_webhook(
    event: PayPalWebhookEvent,
    db: Session = Depends(get_db),
    payment_service: PaymentService = Depends(get_payment_service),
) -> Response:
    payment_service.handle_paypal_webhook(db, event=event)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
