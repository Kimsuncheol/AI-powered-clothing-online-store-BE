from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.dependencies import get_cart_service
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartSchema
from app.services.cart_service import CartService

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("", response_model=CartSchema)
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service),
) -> CartSchema:
    return cart_service.get_cart_for_user(db, current_user.id)


@router.post("/items", response_model=CartSchema, status_code=status.HTTP_201_CREATED)
def add_cart_item(
    body: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service),
) -> CartSchema:
    return cart_service.add_item_to_cart(db, current_user.id, body)


@router.patch("/items/{item_id}", response_model=CartSchema)
def update_cart_item(
    item_id: int,
    body: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service),
) -> CartSchema:
    return cart_service.update_cart_item_quantity(
        db,
        current_user.id,
        item_id,
        body.quantity,
    )


@router.delete("/items/{item_id}", response_model=CartSchema)
def delete_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service),
) -> CartSchema:
    return cart_service.remove_cart_item(db, current_user.id, item_id)
