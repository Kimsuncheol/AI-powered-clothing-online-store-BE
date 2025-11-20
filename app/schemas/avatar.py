from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, conint

from app.models.avatar_preset import AvatarPresetStatus


class AvatarPresetParameters(BaseModel):
    body_type: Optional[str] = None
    gender: Optional[str] = None
    skin_tone: Optional[str] = None
    style_keywords: Optional[List[str]] = None
    extra: Optional[Dict[str, Any]] = None


class AvatarPresetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    status: AvatarPresetStatus = AvatarPresetStatus.ACTIVE
    parameters: AvatarPresetParameters


class AvatarPresetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[AvatarPresetStatus] = None
    parameters: Optional[AvatarPresetParameters] = None


class AvatarPresetSchema(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: AvatarPresetStatus
    parameters: AvatarPresetParameters

    model_config = ConfigDict(from_attributes=True)


class AvatarPresetListResponse(BaseModel):
    items: List[AvatarPresetSchema]


class AvatarRenderRequest(BaseModel):
    productId: Optional[int] = None
    avatarPresetId: int
    styleParams: Optional[Dict[str, Any]] = None
    imageCount: conint(ge=1, le=4) = 1


class AvatarRenderResponse(BaseModel):
    requestId: str
    imageUrls: List[str]
