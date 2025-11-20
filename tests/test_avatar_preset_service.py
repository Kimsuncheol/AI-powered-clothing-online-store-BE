from app.models.avatar_preset import AvatarPresetStatus
from app.repositories.avatar_preset_repository import AvatarPresetRepository
from app.schemas.avatar import AvatarPresetCreate, AvatarPresetParameters, AvatarPresetUpdate
from app.services.avatar_preset_service import AvatarPresetService


def _service() -> AvatarPresetService:
    repo = AvatarPresetRepository()
    return AvatarPresetService(repo)


def test_list_active_presets_returns_only_active(db_session):
    service = _service()
    repo = service.preset_repo
    repo.create(
        db_session,
        AvatarPresetCreate(
            name="Active",
            description="desc",
            status=AvatarPresetStatus.ACTIVE,
            parameters=AvatarPresetParameters(body_type="slim"),
        ),
    )
    repo.create(
        db_session,
        AvatarPresetCreate(
            name="Inactive",
            description=None,
            status=AvatarPresetStatus.INACTIVE,
            parameters=AvatarPresetParameters(body_type="tall"),
        ),
    )

    presets = service.list_active_presets(db_session)

    assert len(presets) == 1
    assert presets[0].name == "Active"


def test_create_preset_creates_record(db_session):
    service = _service()
    data = AvatarPresetCreate(
        name="New Preset",
        parameters=AvatarPresetParameters(gender="female"),
    )

    preset = service.create_or_update_preset(db_session, preset_id=None, data=data)

    assert preset.id is not None
    assert preset.parameters["gender"] == "female"


def test_update_preset_updates_fields(db_session):
    service = _service()
    created = service.create_or_update_preset(
        db_session,
        preset_id=None,
        data=AvatarPresetCreate(
            name="Original",
            parameters=AvatarPresetParameters(),
        ),
    )

    updated = service.create_or_update_preset(
        db_session,
        preset_id=created.id,
        data=AvatarPresetUpdate(name="Updated"),
    )

    assert updated.name == "Updated"
