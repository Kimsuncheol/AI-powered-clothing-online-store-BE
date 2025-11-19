from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.dependencies import get_product_service
from app.models.user import User
from app.schemas.product import ProductCreate, ProductDetail, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter(prefix="/seller/products", tags=["seller-products"])


@router.post(
    "",
    response_model=ProductDetail,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    body: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service),
) -> ProductDetail:
    return product_service.create_product_for_seller(
        db,
        seller=current_user,
        data=body,
    )


@router.patch("/{product_id}", response_model=ProductDetail)
def update_product(
    product_id: int,
    body: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service),
) -> ProductDetail:
    return product_service.update_seller_product(
        db,
        product_id=product_id,
        seller=current_user,
        data=body,
    )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service),
) -> None:
    product_service.soft_delete_product(
        db,
        product_id=product_id,
        seller=current_user,
    )
