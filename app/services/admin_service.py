from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from app.models.order import Order, OrderStatus
from app.models.product import Product, ProductStatus
from app.models.user import User, UserRole, UserStatus
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository


class AdminService:
    def __init__(
        self,
        user_repo: UserRepository,
        product_repo: ProductRepository,
        order_repo: OrderRepository,
    ):
        self.user_repo = user_repo
        self.product_repo = product_repo
        self.order_repo = order_repo

    # 1. Users

    def list_users(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[User], int]:
        """
        Returns (users, total_count) filtered by email/name search, role, status.
        """
        query = db.query(User)

        if search:
            pattern = f"%{search}%"
            query = query.filter(User.email.ilike(pattern))
        
        if role:
            query = query.filter(User.role == role)
        
        if status:
            query = query.filter(User.status == status)

        total = query.count()
        items = (
            query.order_by(desc(User.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    # 2. Products

    def list_products(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
        seller_id: Optional[int] = None,
        status: Optional[ProductStatus] = None,
        is_flagged: Optional[bool] = None,
        is_hidden: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Product], int]:
        """
        Returns (products, total_count) for admin review.
        """
        query = db.query(Product)

        if search:
            pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Product.name.ilike(pattern),
                    Product.category.ilike(pattern),
                )
            )

        if seller_id is not None:
            query = query.filter(Product.seller_id == seller_id)
        
        if status:
            query = query.filter(Product.status == status)
        
        if is_flagged is not None:
            query = query.filter(Product.is_flagged == is_flagged)
        
        if is_hidden is not None:
            query = query.filter(Product.is_hidden == is_hidden)

        total = query.count()
        items = (
            query.order_by(desc(Product.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def moderate_product(
        self,
        db: Session,
        *,
        product_id: int,
        action: str,
        flag_reason: Optional[str],
    ) -> Product:
        """
        Admin moderation actions:
        - approve: set is_hidden=False, is_flagged=False, flag_reason=None
        - hide: set is_hidden=True
        - unhide: set is_hidden=False
        - flag: set is_flagged=True, flag_reason=...
        - unflag: set is_flagged=False, flag_reason=None
        """
        product = self.product_repo.get(db, product_id=product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        if action == "approve":
            product.is_hidden = False
            product.is_flagged = False
            product.flag_reason = None
        elif action == "hide":
            product.is_hidden = True
        elif action == "unhide":
            product.is_hidden = False
        elif action == "flag":
            product.is_flagged = True
            product.flag_reason = flag_reason
        elif action == "unflag":
            product.is_flagged = False
            product.flag_reason = None
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid action",
            )
        
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    # 3. Orders

    def list_orders(
        self,
        db: Session,
        *,
        user_id: Optional[int] = None,
        status: Optional[OrderStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Order], int]:
        """
        Returns (orders, total_count) for admin review.
        """
        query = db.query(Order)

        if user_id is not None:
            query = query.filter(Order.user_id == user_id)
        
        if status:
            query = query.filter(Order.status == status)

        total = query.count()
        items = (
            query.order_by(desc(Order.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total
