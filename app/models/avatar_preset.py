import enum

from sqlalchemy import Column, DateTime, Enum, Integer, JSON, String, Text, func

from app.db.base_class import Base


class AvatarPresetStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class AvatarPreset(Base):
    __tablename__ = "avatar_presets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(AvatarPresetStatus), nullable=False, default=AvatarPresetStatus.ACTIVE)
    parameters = Column(JSON, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
