from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.product import ProductStatus
from app.models.user import UserRole


class ProductImageSchema(BaseModel):
    id: Optional[int] = None
    url: str
    is_avatar_preview: bool = False
    sort_order: int = 0

    model_config = ConfigDict(from_attributes=True)


class ProductAvatarConfigSchema(BaseModel):
    id: Optional[int] = None
    avatar_preset_id: int
    style_params: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class ProductAvatarConfigUpsert(BaseModel):
    avatar_preset_id: int
    style_params: Optional[Dict[str, Any]] = None


class ProductAvatarConfigResponse(BaseModel):
    avatar_preset_id: int
    style_params: Optional[Dict[str, Any]] = None


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    category: Optional[str] = None
    gender: Optional[str] = None
    size_options: Optional[List[str]] = None
    color_options: Optional[List[str]] = None
    variants: Optional[Dict[str, Any]] = None
    stock: int


class ProductCreate(ProductBase):
    images: Optional[List[ProductImageSchema]] = None
    avatar_configs: Optional[List[ProductAvatarConfigSchema]] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    category: Optional[str] = None
    gender: Optional[str] = None
    size_options: Optional[List[str]] = None
    color_options: Optional[List[str]] = None
    variants: Optional[Dict[str, Any]] = None
    stock: Optional[int] = None
    status: Optional[ProductStatus] = None
    images: Optional[List[ProductImageSchema]] = None
    avatar_configs: Optional[List[ProductAvatarConfigSchema]] = None


class ProductSellerInfo(BaseModel):
    id: int
    email: EmailStr
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class ProductDetail(ProductBase):
    id: int
    seller: ProductSellerInfo
    status: ProductStatus
    images: List[ProductImageSchema] = Field(default_factory=list)
    avatar_configs: List[ProductAvatarConfigSchema] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductListItem(BaseModel):
    id: int
    name: str
    price: Decimal
    category: Optional[str]
    gender: Optional[str]
    main_image_url: Optional[str]
    seller_id: int

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    items: List[ProductListItem]
    total: int
    page: int
    page_size: int
