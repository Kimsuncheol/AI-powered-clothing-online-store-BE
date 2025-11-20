from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_admin
from app.db.session import get_db
from app.dependencies import get_avatar_preset_service
from app.models.user import User
from app.schemas.avatar import AvatarPresetCreate, AvatarPresetSchema
from app.services.avatar_preset_service import AvatarPresetService

router = APIRouter(prefix="/admin/avatars", tags=["admin-avatars"])


@router.post("/presets", response_model=AvatarPresetSchema)
def create_preset(
    body: AvatarPresetCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
    avatar_preset_service: AvatarPresetService = Depends(get_avatar_preset_service),
) -> AvatarPresetSchema:
    preset = avatar_preset_service.create_or_update_preset(
        db,
        preset_id=None,
        data=body,
    )
    return preset
