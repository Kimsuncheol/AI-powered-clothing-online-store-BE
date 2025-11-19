from sqlalchemy import Column, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ProductAvatarConfig(Base):
    __tablename__ = "product_avatar_configs"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    avatar_preset_id = Column(Integer, nullable=False)
    style_params = Column(JSON, nullable=True)

    product = relationship("Product", back_populates="avatar_configs")
