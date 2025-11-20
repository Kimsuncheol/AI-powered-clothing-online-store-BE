import enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    func,
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class AiAvatarRequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AiAvatarRequest(Base):
    __tablename__ = "ai_avatar_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(128), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)
    avatar_preset_id = Column(Integer, ForeignKey("avatar_presets.id"), nullable=False)
    style_params = Column(JSON, nullable=True)
    image_count = Column(Integer, nullable=False, default=1)
    status = Column(Enum(AiAvatarRequestStatus), nullable=False, default=AiAvatarRequestStatus.PENDING)
    image_urls = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User")
    product = relationship("Product")
    preset = relationship("AvatarPreset")
