from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.payment import Payment, PaymentStatus


class PaymentRepository:
    def create_payment(
        self,
        db: Session,
        *,
        order_id: int,
        provider_payment_id: str,
        raw_response: Dict[str, Any],
    ) -> Payment:
        payment = Payment(
            order_id=order_id,
            provider_payment_id=provider_payment_id,
            raw_response=raw_response,
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment

    def get_by_provider_payment_id(
        self,
        db: Session,
        *,
        provider_payment_id: str,
    ) -> Optional[Payment]:
        return (
            db.query(Payment)
            .filter(Payment.provider_payment_id == provider_payment_id)
            .first()
        )

    def update_status(
        self,
        db: Session,
        *,
        payment: Payment,
        status: PaymentStatus,
        raw_response: Optional[Dict[str, Any]] = None,
    ) -> Payment:
        payment.status = status
        if raw_response is not None:
            payment.raw_response = raw_response
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment
