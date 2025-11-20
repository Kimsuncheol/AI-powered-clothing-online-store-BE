import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ProductStatus(str, enum.Enum):
    ACTIVE = "active"
    DRAFT = "draft"
    DELETED = "deleted"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    category = Column(String(100), index=True)
    gender = Column(String(50), index=True)
    size_options = Column(JSON, nullable=True)
    color_options = Column(JSON, nullable=True)
    variants = Column(JSON, nullable=True)
    stock = Column(Integer, nullable=False, default=0)
    status = Column(Enum(ProductStatus), nullable=False, default=ProductStatus.ACTIVE)

    # Admin moderation fields
    is_flagged = Column(Boolean, nullable=False, default=False)
    flag_reason = Column(String(500), nullable=True)
    is_hidden = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    seller = relationship("User", backref="products")
    images = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
    )
    avatar_configs = relationship(
        "ProductAvatarConfig",
        back_populates="product",
        cascade="all, delete-orphan",
    )
