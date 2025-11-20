from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.avatar_preset import AvatarPreset, AvatarPresetStatus
from app.schemas.avatar import AvatarPresetCreate, AvatarPresetUpdate


class AvatarPresetRepository:
    def list_active(self, db: Session) -> List[AvatarPreset]:
        return (
            db.query(AvatarPreset)
            .filter(AvatarPreset.status == AvatarPresetStatus.ACTIVE)
            .order_by(AvatarPreset.created_at.desc())
            .all()
        )

    def create(self, db: Session, data: AvatarPresetCreate) -> AvatarPreset:
        preset = AvatarPreset(
            name=data.name,
            description=data.description,
            status=data.status,
            parameters=data.parameters.model_dump(),
        )
        db.add(preset)
        db.commit()
        db.refresh(preset)
        return preset

    def update(self, db: Session, preset_id: int, data: AvatarPresetUpdate) -> AvatarPreset:
        preset = self.get_by_id(db, preset_id)
        if not preset:
            raise ValueError("Avatar preset not found")
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "parameters" and value is not None:
                value = value.model_dump()
            setattr(preset, field, value)
        db.add(preset)
        db.commit()
        db.refresh(preset)
        return preset

    def get_by_id(self, db: Session, preset_id: int) -> Optional[AvatarPreset]:
        return db.query(AvatarPreset).filter(AvatarPreset.id == preset_id).first()
