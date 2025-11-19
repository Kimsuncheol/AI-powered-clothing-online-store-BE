from decimal import Decimal
from typing import Generator, List, Optional

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.security import get_password_hash
from app.core.security import create_access_token
from app.db.base import Base
from app.db.session import get_db
from app.models.product import Product, ProductStatus
from app.models.product_avatar_config import ProductAvatarConfig
from app.models.product_image import ProductImage
from app.models.user import User, UserRole, UserStatus
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_test_database() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    try:
        yield session
        session.commit()
    finally:
        session.close()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def create_user(
    db: Session,
    *,
    email: str,
    password: str = "password123",
    role: UserRole = UserRole.BUYER,
    status: UserStatus = UserStatus.ACTIVE,
) -> User:
    user = User(
        email=email,
        password_hash=get_password_hash(password),
        role=role,
        status=status,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def create_admin(db_session: Session):
    def _create_admin(email: str = "admin@example.com", password: str = "password123"):
        return create_user(
            db_session,
            email=email,
            password=password,
            role=UserRole.ADMIN,
        )

    return _create_admin


@pytest.fixture()
def create_buyer(db_session: Session):
    def _create_buyer(email: str = "buyer@example.com", password: str = "password123"):
        return create_user(
            db_session,
            email=email,
            password=password,
            role=UserRole.BUYER,
        )

    return _create_buyer


@pytest.fixture()
def create_seller(db_session: Session):
    def _create_seller(
        email: str = "seller@example.com", password: str = "password123"
    ):
        return create_user(
            db_session,
            email=email,
            password=password,
            role=UserRole.SELLER,
        )

    return _create_seller


def create_product(
    db: Session,
    *,
    seller_id: int,
    name: str = "Test Product",
    price: Decimal = Decimal("10.00"),
    category: Optional[str] = None,
    gender: Optional[str] = None,
    size_options: Optional[List[str]] = None,
    color_options: Optional[List[str]] = None,
    stock: int = 10,
    status: ProductStatus = ProductStatus.ACTIVE,
    images: Optional[List[dict]] = None,
    avatar_configs: Optional[List[dict]] = None,
) -> Product:
    product = Product(
        seller_id=seller_id,
        name=name,
        description="desc",
        price=price,
        category=category,
        gender=gender,
        size_options=size_options,
        color_options=color_options,
        stock=stock,
        status=status,
    )
    if images:
        product.images = [
            ProductImage(
                url=image["url"],
                is_avatar_preview=image.get("is_avatar_preview", False),
                sort_order=image.get("sort_order", 0),
            )
            for image in images
        ]
    if avatar_configs:
        product.avatar_configs = [
            ProductAvatarConfig(
                avatar_preset_id=config["avatar_preset_id"],
                style_params=config.get("style_params"),
            )
            for config in avatar_configs
        ]
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@pytest.fixture()
def auth_header_factory():
    def _factory(user: User):
        token = create_access_token({"sub": str(user.id), "role": user.role.value})
        return {"Authorization": f"Bearer {token}"}

    return _factory
