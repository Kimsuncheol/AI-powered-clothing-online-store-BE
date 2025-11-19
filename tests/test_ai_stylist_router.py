from decimal import Decimal

from app.dependencies import get_ai_stylist_service
from app.schemas.ai import ProductRecommendationSummary, StylistChatResponse
from main import app


def test_stylist_chat_requires_auth(client):
    response = client.post(
        "/api/v1/ai/stylist/chat",
        json={"userMessage": "Hello stylist"},
    )
    assert response.status_code == 401


def test_stylist_chat_returns_reply_and_conversation_id(
    client,
    create_buyer,
    auth_header_factory,
):
    user = create_buyer()
    headers = auth_header_factory(user)

    class DummyService:
        def handle_chat(self, *args, **kwargs):
            return StylistChatResponse(
                replyText="Hi there!",
                conversationId="conv-abc",
                recommendations=[
                    ProductRecommendationSummary(
                        id=1,
                        title="Midi Dress",
                        price=Decimal("99.00"),
                        image="img",
                    )
                ],
            )

    app.dependency_overrides[get_ai_stylist_service] = lambda: DummyService()

    response = client.post(
        "/api/v1/ai/stylist/chat",
        headers=headers,
        json={"userMessage": "Need something for a wedding"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["replyText"] == "Hi there!"
    assert payload["conversationId"] == "conv-abc"
    assert payload["recommendations"][0]["title"] == "Midi Dress"

    del app.dependency_overrides[get_ai_stylist_service]
