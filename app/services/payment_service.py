from typing import Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.order import OrderStatus
from app.models.payment import Payment, PaymentStatus
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.paypal_event_repository import PayPalEventRepository
from app.schemas.payment import PayPalWebhookEvent
from app.core.paypal_client import PayPalClient


class PaymentService:
    def __init__(
        self,
        payment_repo: PaymentRepository,
        order_repo: OrderRepository,
        paypal_client: PayPalClient,
        paypal_event_repo: PayPalEventRepository,
    ) -> None:
        self.payment_repo = payment_repo
        self.order_repo = order_repo
        self.paypal_client = paypal_client
        self.paypal_event_repo = paypal_event_repo

    def create_paypal_order(
        self,
        db: Session,
        *,
        order_id: int,
        user_id: int,
    ) -> Tuple[Payment, str]:
        order = self.order_repo.get_by_id(db, order_id=order_id)
        if not order or order.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        if order.status != OrderStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order is not payable",
            )
        if order.total_amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order total must be greater than zero",
            )

        paypal_response = self.paypal_client.create_order(
            order_id=order.id,
            total_amount=order.total_amount,
            currency=order.currency,
        )
        provider_payment_id = paypal_response.get("id")
        if not provider_payment_id:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="PayPal response missing order id",
            )
        approval_url = self._extract_approval_url(paypal_response)
        payment = self.payment_repo.create_payment(
            db,
            order_id=order.id,
            provider_payment_id=provider_payment_id,
            raw_response=paypal_response,
        )
        return payment, approval_url

    def capture_paypal_order(
        self,
        db: Session,
        *,
        provider_payment_id: str,
        user_id: int,
    ) -> Payment:
        payment = self.payment_repo.get_by_provider_payment_id(
            db,
            provider_payment_id=provider_payment_id,
        )
        if not payment or payment.order is None or payment.order.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

        try:
            response = self.paypal_client.capture_order(
                provider_payment_id=provider_payment_id,
            )
        except HTTPException as exc:
            self.payment_repo.update_status(
                db,
                payment=payment,
                status=PaymentStatus.FAILED,
                raw_response={"detail": exc.detail},
            )
            raise
        except Exception as exc:  # pragma: no cover - defensive programming
            self.payment_repo.update_status(
                db,
                payment=payment,
                status=PaymentStatus.FAILED,
                raw_response={"error": str(exc)},
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to capture PayPal order",
            ) from exc

        status_value = response.get("status") or response.get("result", {}).get("status")
        if status_value != "COMPLETED":
            self.payment_repo.update_status(
                db,
                payment=payment,
                status=PaymentStatus.FAILED,
                raw_response=response,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PayPal capture failed",
            )

        updated_payment = self.payment_repo.update_status(
            db,
            payment=payment,
            status=PaymentStatus.COMPLETED,
            raw_response=response,
        )
        order = updated_payment.order
        if order:
            order.status = OrderStatus.PAID
            db.add(order)
            db.commit()
            db.refresh(order)
            db.refresh(updated_payment)
        return updated_payment

    def handle_paypal_webhook(
        self,
        db: Session,
        *,
        event: PayPalWebhookEvent,
    ) -> None:
        if self.paypal_event_repo.get_by_event_id(db, event_id=event.id):
            return
        self.paypal_event_repo.save_event(
            db,
            event_id=event.id,
            event_type=event.event_type,
            payload=event.model_dump(),
        )

        provider_payment_id = self._get_provider_payment_id_from_event(event)
        if not provider_payment_id:
            return
        payment = self.payment_repo.get_by_provider_payment_id(
            db,
            provider_payment_id=provider_payment_id,
        )
        if not payment:
            return

        if event.event_type == "PAYMENT.CAPTURE.COMPLETED":
            updated_payment = self.payment_repo.update_status(
                db,
                payment=payment,
                status=PaymentStatus.COMPLETED,
                raw_response=event.resource,
            )
            order = updated_payment.order
            if order and order.status != OrderStatus.PAID:
                order.status = OrderStatus.PAID
                db.add(order)
                db.commit()
        elif event.event_type == "PAYMENT.CAPTURE.REFUNDED":
            updated_payment = self.payment_repo.update_status(
                db,
                payment=payment,
                status=PaymentStatus.CANCELLED,
                raw_response=event.resource,
            )
            order = updated_payment.order
            if order:
                order.status = OrderStatus.CANCELLED
                db.add(order)
                db.commit()

    def _extract_approval_url(self, response: dict) -> str:
        links = response.get("links", [])
        for link in links:
            if link.get("rel") in {"approve", "payer-action"}:
                return link.get("href", "")
        return ""

    def _get_provider_payment_id_from_event(self, event: PayPalWebhookEvent) -> str | None:
        resource = event.resource or {}
        related = resource.get("supplementary_data", {}).get("related_ids", {})
        provider_payment_id = related.get("order_id")
        if not provider_payment_id:
            provider_payment_id = resource.get("id")
        return provider_payment_id
