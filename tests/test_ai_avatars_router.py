from app.dependencies import get_ai_avatar_service
from app.schemas.avatar import AvatarRenderResponse
from main import app


def test_render_avatar_requires_auth(client):
    response = client.post("/api/v1/ai/avatars/render", json={"avatarPresetId": 1})
    assert response.status_code == 401


def test_render_avatar_returns_request_id_and_image_urls(
    client,
    create_seller,
    auth_header_factory,
):
    user = create_seller()
    headers = auth_header_factory(user)

    class DummyService:
        def render_avatars(self, *args, **kwargs):
            return AvatarRenderResponse(requestId="req-1", imageUrls=["img"])

    app.dependency_overrides[get_ai_avatar_service] = lambda: DummyService()
    try:
        response = client.post(
            "/api/v1/ai/avatars/render",
            headers=headers,
            json={
                "avatarPresetId": 123,
                "imageCount": 1,
            },
        )
    finally:
        del app.dependency_overrides[get_ai_avatar_service]

    assert response.status_code == 200
    data = response.json()
    assert data["requestId"] == "req-1"
    assert data["imageUrls"] == ["img"]
