from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr

from app.models.order import OrderStatus
from app.models.product import ProductStatus
from app.models.user import UserRole, UserStatus


# User list DTO for admin
class AdminUserListItem(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    status: UserStatus
    created_at: datetime

    class Config:
        orm_mode = True


class AdminUserListResponse(BaseModel):
    items: List[AdminUserListItem]
    total: int
    page: int
    page_size: int


# Product list DTO for admin
class AdminProductListItem(BaseModel):
    id: int
    name: str
    seller_id: int
    seller_email: Optional[EmailStr] = None
    status: ProductStatus
    is_flagged: bool
    flag_reason: Optional[str] = None
    is_hidden: bool
    created_at: datetime

    class Config:
        orm_mode = True


class AdminProductListResponse(BaseModel):
    items: List[AdminProductListItem]
    total: int
    page: int
    page_size: int


# Order list DTO for admin
class AdminOrderListItem(BaseModel):
    id: int
    user_id: int
    user_email: Optional[EmailStr] = None
    total_amount: Decimal
    currency: str
    status: OrderStatus
    created_at: datetime

    class Config:
        orm_mode = True


class AdminOrderListResponse(BaseModel):
    items: List[AdminOrderListItem]
    total: int
    page: int
    page_size: int


# Product moderation input
class AdminProductModerationUpdate(BaseModel):
    action: Literal["approve", "hide", "unhide", "flag", "unflag"]
    flag_reason: Optional[str] = None
