from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_product_service
from app.schemas.product import ProductDetail, ProductListResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductListResponse)
def list_products(
    category: Optional[str] = None,
    price_min: Optional[Decimal] = None,
    price_max: Optional[Decimal] = None,
    size: Optional[str] = None,
    color: Optional[str] = None,
    gender: Optional[str] = None,
    sort: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    product_service: ProductService = Depends(get_product_service),
) -> ProductListResponse:
    return product_service.list_products(
        db,
        category=category,
        price_min=price_min,
        price_max=price_max,
        size=size,
        color=color,
        gender=gender,
        sort=sort,
        page=page,
        page_size=page_size,
    )


@router.get("/{product_id}", response_model=ProductDetail)
def get_product_detail(
    product_id: int,
    db: Session = Depends(get_db),
    product_service: ProductService = Depends(get_product_service),
) -> ProductDetail:
    return product_service.get_product_detail(db, product_id=product_id)
