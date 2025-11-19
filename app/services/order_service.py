from decimal import Decimal
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.product import ProductStatus
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.order import (
    OrderCreateResponse,
    OrderDetailSchema,
    OrderListItemSchema,
    OrderListResponse,
)


class OrderService:
    def __init__(
        self,
        cart_repo: CartRepository,
        order_repo: OrderRepository,
        product_repo: ProductRepository,
    ):
        self.cart_repo = cart_repo
        self.order_repo = order_repo
        self.product_repo = product_repo

    def create_order_from_cart(
        self,
        db: Session,
        user_id: int,
        currency: str = "USD",
    ) -> OrderCreateResponse:
        cart = self.cart_repo.get_cart(db, user_id)
        if cart is None or not cart.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty",
            )

        items_payload: List[dict] = []
        total_amount = Decimal("0.00")
        for item in cart.items:
            product = self.product_repo.get(db, item.product_id)
            if not product or product.status != ProductStatus.ACTIVE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Product in cart is unavailable",
                )
            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient stock for product",
                )

            unit_price = Decimal(product.price)
            total_amount += unit_price * item.quantity
            items_payload.append(
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": unit_price,
                    "variant_data": item.variant_data,
                }
            )
            product.stock -= item.quantity
            db.add(product)

        order = self.order_repo.create_order(
            db,
            user_id=user_id,
            total_amount=total_amount,
            currency=currency,
            items_data=items_payload,
        )

        for cart_item in list(cart.items):
            db.delete(cart_item)
        db.commit()

        return OrderCreateResponse(
            id=order.id,
            total_amount=order.total_amount,
            currency=order.currency,
        )

    def get_order_detail_for_user(
        self,
        db: Session,
        user_id: int,
        order_id: int,
    ) -> OrderDetailSchema:
        order = self._get_order_or_404(db, order_id, user_id)
        return OrderDetailSchema.model_validate(order)

    def list_orders_for_user(
        self,
        db: Session,
        user_id: int,
    ) -> OrderListResponse:
        orders = self.order_repo.list_by_user(db, user_id=user_id)
        items = [OrderListItemSchema.model_validate(order) for order in orders]
        return OrderListResponse(items=items)

    def _get_order_or_404(
        self,
        db: Session,
        order_id: int,
        user_id: int,
    ) -> Order:
        order = self.order_repo.get_by_id_and_user(
            db,
            order_id=order_id,
            user_id=user_id,
        )
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )
        return order
