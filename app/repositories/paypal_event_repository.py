from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.paypal_event import PayPalEvent


class PayPalEventRepository:
    def get_by_event_id(
        self,
        db: Session,
        *,
        event_id: str,
    ) -> Optional[PayPalEvent]:
        return (
            db.query(PayPalEvent)
            .filter(PayPalEvent.event_id == event_id)
            .first()
        )

    def save_event(
        self,
        db: Session,
        *,
        event_id: str,
        event_type: str,
        payload: Dict[str, Any],
    ) -> PayPalEvent:
        event = PayPalEvent(
            event_id=event_id,
            event_type=event_type,
            payload=payload,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
