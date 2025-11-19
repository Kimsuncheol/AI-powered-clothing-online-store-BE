from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.dependencies import get_order_service
from app.models.user import User
from app.schemas.order import (
    OrderCreateResponse,
    OrderDetailSchema,
    OrderListResponse,
)
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderCreateResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
) -> OrderCreateResponse:
    return order_service.create_order_from_cart(db, current_user.id)


@router.get("", response_model=OrderListResponse)
def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
) -> OrderListResponse:
    return order_service.list_orders_for_user(db, current_user.id)


@router.get("/{order_id}", response_model=OrderDetailSchema)
def get_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
) -> OrderDetailSchema:
    return order_service.get_order_detail_for_user(db, current_user.id, order_id)
