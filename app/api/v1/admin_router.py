from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_admin
from app.db.session import get_db
from app.dependencies import get_admin_service
from app.models.order import OrderStatus
from app.models.product import ProductStatus
from app.models.user import User, UserRole, UserStatus
from app.schemas.admin import (
    AdminOrderListResponse,
    AdminProductListItem,
    AdminProductListResponse,
    AdminProductModerationUpdate,
    AdminUserListResponse,
)
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["admin"])


# 1. List/search users
@router.get("/users", response_model=AdminUserListResponse)
def admin_list_users(
    search: Optional[str] = Query(None),
    role: Optional[UserRole] = Query(None),
    status: Optional[UserStatus] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
    admin_service: AdminService = Depends(get_admin_service),
):
    users, total = admin_service.list_users(
        db,
        search=search,
        role=role,
        status=status,
        page=page,
        page_size=page_size,
    )
    return AdminUserListResponse(
        items=users,
        total=total,
        page=page,
        page_size=page_size,
    )


# 2. List/verify products
@router.get("/products", response_model=AdminProductListResponse)
def admin_list_products(
    search: Optional[str] = Query(None),
    seller_id: Optional[int] = Query(None),
    status: Optional[ProductStatus] = Query(None),
    is_flagged: Optional[bool] = Query(None),
    is_hidden: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
    admin_service: AdminService = Depends(get_admin_service),
):
    products, total = admin_service.list_products(
        db,
        search=search,
        seller_id=seller_id,
        status=status,
        is_flagged=is_flagged,
        is_hidden=is_hidden,
        page=page,
        page_size=page_size,
    )
    # Map seller email etc. in response (Pydantic will handle orm_mode)
    return AdminProductListResponse(
        items=products,
        total=total,
        page=page,
        page_size=page_size,
    )


# 3. Flag / hide / approve product
@router.patch("/products/{product_id}", response_model=AdminProductListItem)
def admin_moderate_product(
    product_id: int,
    body: AdminProductModerationUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
    admin_service: AdminService = Depends(get_admin_service),
):
    product = admin_service.moderate_product(
        db,
        product_id=product_id,
        action=body.action,
        flag_reason=body.flag_reason,
    )
    return product


# 4. Review orders
@router.get("/orders", response_model=AdminOrderListResponse)
def admin_list_orders(
    user_id: Optional[int] = Query(None),
    status: Optional[OrderStatus] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
    admin_service: AdminService = Depends(get_admin_service),
):
    orders, total = admin_service.list_orders(
        db,
        user_id=user_id,
        status=status,
        page=page,
        page_size=page_size,
    )
    return AdminOrderListResponse(
        items=orders,
        total=total,
        page=page,
        page_size=page_size,
    )
