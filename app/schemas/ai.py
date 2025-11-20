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


class SellerChatRequest(BaseModel):
    userMessage: str
    productId: Optional[int] = None
    conversationId: Optional[str] = None


class SellerChatResponse(BaseModel):
    replyText: str
    conversationId: str
    generatedTitle: Optional[str] = None
    generatedDescription: Optional[str] = None
    generatedTags: Optional[List[str]] = None


class GenerateDescriptionRequest(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    gender: Optional[str] = None
    price: Optional[Decimal] = None
    style_keywords: Optional[List[str]] = None
    target_audience: Optional[str] = None
    existing_description: Optional[str] = None


class GenerateDescriptionResponse(BaseModel):
    title: str
    description: str
    tags: List[str]
