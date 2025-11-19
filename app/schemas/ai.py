from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class StylistChatRequest(BaseModel):
    userMessage: str
    productId: Optional[int] = None
    conversationId: Optional[str] = None


class ProductRecommendationSummary(BaseModel):
    id: int
    title: str
    price: Decimal
    image: Optional[str] = None


class StylistChatResponse(BaseModel):
    replyText: str
    conversationId: str
    recommendations: List[ProductRecommendationSummary] = Field(default_factory=list)
