from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem


class OrderRepository:
    def create_order(
        self,
        db: Session,
        *,
        user_id: int,
        total_amount: Decimal,
        currency: str,
        items_data: List[Dict[str, Any]],
    ) -> Order:
        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            currency=currency,
        )
        db.add(order)
        db.flush()

        order.items = [
            OrderItem(
                product_id=item["product_id"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                variant_data=item.get("variant_data"),
            )
            for item in items_data
        ]
        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    def get_by_id_and_user(
        self,
        db: Session,
        *,
        order_id: int,
        user_id: int,
    ) -> Optional[Order]:
        return (
            db.query(Order)
            .filter(Order.id == order_id, Order.user_id == user_id)
            .first()
        )

    def get_by_id(self, db: Session, *, order_id: int) -> Optional[Order]:
        return db.query(Order).filter(Order.id == order_id).first()

    def list_by_user(self, db: Session, *, user_id: int) -> List[Order]:
        return (
            db.query(Order)
            .filter(Order.user_id == user_id)
            .order_by(desc(Order.created_at))
            .all()
        )
