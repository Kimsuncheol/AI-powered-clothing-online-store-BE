from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.dependencies import get_product_service
from app.models.user import User
from app.schemas.product import (
    ProductAvatarConfigResponse,
    ProductAvatarConfigUpsert,
    ProductCreate,
    ProductDetail,
    ProductUpdate,
)
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


@router.post(
    "/{product_id}/avatar-config",
    response_model=ProductAvatarConfigResponse,
)
def set_product_avatar_config(
    product_id: int,
    body: ProductAvatarConfigUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service),
) -> ProductAvatarConfigResponse:
    config = product_service.upsert_product_avatar_config(
        db,
        product_id=product_id,
        seller=current_user,
        avatar_preset_id=body.avatar_preset_id,
        style_params=body.style_params,
    )
    return ProductAvatarConfigResponse(
        avatar_preset_id=config.avatar_preset_id,
        style_params=config.style_params,
    )


@router.get(
    "/{product_id}/avatar-config",
    response_model=ProductAvatarConfigResponse,
)
def get_product_avatar_config(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service),
) -> ProductAvatarConfigResponse:
    config = product_service.get_product_avatar_config(
        db,
        product_id=product_id,
        seller=current_user,
    )
    if not config:
        raise HTTPException(status_code=404, detail="Avatar config not found.")
    return ProductAvatarConfigResponse(
        avatar_preset_id=config.avatar_preset_id,
        style_params=config.style_params,
    )
