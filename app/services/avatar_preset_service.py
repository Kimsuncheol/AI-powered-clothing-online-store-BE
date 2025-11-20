from typing import List, Optional, Union

from sqlalchemy.orm import Session

from app.models.avatar_preset import AvatarPreset
from app.repositories.avatar_preset_repository import AvatarPresetRepository
from app.schemas.avatar import AvatarPresetCreate, AvatarPresetUpdate


class AvatarPresetService:
    def __init__(self, preset_repo: AvatarPresetRepository):
        self.preset_repo = preset_repo

    def list_active_presets(self, db: Session) -> List[AvatarPreset]:
        return self.preset_repo.list_active(db)

    def create_or_update_preset(
        self,
        db: Session,
        *,
        preset_id: Optional[int],
        data: Union[AvatarPresetCreate, AvatarPresetUpdate],
    ) -> AvatarPreset:
        if preset_id:
            if not isinstance(data, AvatarPresetUpdate):
                raise ValueError("Update payload must be AvatarPresetUpdate")
            return self.preset_repo.update(db, preset_id=preset_id, data=data)
        assert isinstance(data, AvatarPresetCreate)
        return self.preset_repo.create(db, data=data)
