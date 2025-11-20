from app.models.search_keyword import SearchKeyword
from app.repositories.search_repository import SearchRepository
from app.services.search_service import SearchService


def test_get_search_history_returns_items(client, db_session, create_buyer, auth_header_factory):
    user = create_buyer()
    other = create_buyer(email="other@example.com")

    db_session.add(SearchKeyword(user_id=user.id, keyword="dress", destination="/products?query=dress"))
    db_session.add(SearchKeyword(user_id=other.id, keyword="shoes", destination="/products?query=shoes"))
    db_session.commit()

    resp = client.get("/api/v1/search/history", headers=auth_header_factory(user))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["keyword"] == "dress"


def test_delete_search_history_item_removes_item_and_respects_user(client, db_session, create_buyer, auth_header_factory):
    user = create_buyer()
    other = create_buyer(email="other2@example.com")

    owned = SearchKeyword(user_id=user.id, keyword="hat", destination="/products?query=hat")
    foreign = SearchKeyword(user_id=other.id, keyword="bag", destination="/products?query=bag")
    db_session.add_all([owned, foreign])
    db_session.commit()

    # cannot delete other user's item
    resp_forbidden = client.delete(
        f"/api/v1/search/history/{foreign.id}", headers=auth_header_factory(user)
    )
    assert resp_forbidden.status_code == 404

    # delete own item
    resp = client.delete(
        f"/api/v1/search/history/{owned.id}", headers=auth_header_factory(user)
    )
    assert resp.status_code == 204

    remaining = db_session.query(SearchKeyword).filter_by(user_id=user.id).all()
    assert len(remaining) == 0


def test_suggest_keywords_returns_suggestions_for_query(client, db_session, create_seller):
    seller = create_seller()
    from tests.conftest import create_product

    create_product(db_session, seller_id=seller.id, name="Green Jacket")
    db_session.add(SearchKeyword(user_id=None, keyword="Green shirt", destination="/products?query=green"))
    db_session.commit()

    resp = client.get("/api/v1/search/suggest?q=green")
    assert resp.status_code == 200
    data = resp.json()
    keywords = [item["keyword"] for item in data["items"]]
    assert "green jacket" in keywords
    assert "green shirt" in keywords
