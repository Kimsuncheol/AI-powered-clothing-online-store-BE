from app.models.avatar_preset import AvatarPresetStatus
from app.repositories.avatar_preset_repository import AvatarPresetRepository
from app.schemas.avatar import AvatarPresetCreate, AvatarPresetParameters


def test_list_avatar_presets_returns_active_items(client, db_session):
    repo = AvatarPresetRepository()
    repo.create(
        db_session,
        AvatarPresetCreate(
            name="Preset A",
            parameters=AvatarPresetParameters(body_type="athletic"),
            status=AvatarPresetStatus.ACTIVE,
        ),
    )
    repo.create(
        db_session,
        AvatarPresetCreate(
            name="Preset B",
            parameters=AvatarPresetParameters(),
            status=AvatarPresetStatus.INACTIVE,
        ),
    )

    response = client.get("/api/v1/avatars/presets")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Preset A"


def test_admin_can_create_preset(client, create_admin, auth_header_factory):
    admin = create_admin()
    headers = auth_header_factory(admin)
    payload = {
        "name": "Admin Preset",
        "parameters": {"gender": "unisex"},
    }

    response = client.post(
        "/api/v1/admin/avatars/presets",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Admin Preset"


def test_non_admin_cannot_create_preset(client, create_seller, auth_header_factory):
    seller = create_seller()
    headers = auth_header_factory(seller)
    payload = {
        "name": "Seller Preset",
        "parameters": {"gender": "female"},
    }

    response = client.post(
        "/api/v1/admin/avatars/presets",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 403
