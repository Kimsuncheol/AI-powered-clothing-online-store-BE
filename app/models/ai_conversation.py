import enum
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, JSON, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class AiConversationType(str, enum.Enum):
    STYLIST = "STYLIST"
    SELLER = "SELLER"

class AiConversation(Base):
    __tablename__ = "ai_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(Enum(AiConversationType), nullable=False)
    conversation_id = Column(String(128), unique=True, index=True, nullable=False)
    messages = Column(JSON, nullable=False, default=list)  # [{role, content, timestamp}, ...]
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User")
