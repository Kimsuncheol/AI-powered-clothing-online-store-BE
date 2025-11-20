from app.repositories.search_repository import SearchRepository
from app.repositories.product_repository import ProductRepository
from app.services.search_service import SearchService
from tests.conftest import create_product
from app.models.search_keyword import SearchKeyword


def _service() -> SearchService:
    return SearchService(SearchRepository(), ProductRepository())


def test_generate_ngrams_basic():
    service = _service()
    result = service.generate_ngrams("Blue", n=2)
    assert result == ["bl", "lu", "ue"]


def test_suggest_keywords_combines_search_keywords_and_product_names(db_session, create_seller):
    seller = create_seller()
    create_product(db_session, seller_id=seller.id, name="Blue Shirt")
    db_session.add(
        SearchKeyword(user_id=None, keyword="Blue hoodie", destination="/products?query=blue")
    )
    db_session.commit()

    service = _service()
    suggestions = service.suggest_keywords(db_session, query="Blu", limit=5)
    keywords = [s["keyword"] for s in suggestions]
    assert "blue shirt" in keywords
    assert "blue hoodie" in keywords


def test_suggest_keywords_limits_results(db_session):
    service = _service()
    # seed many keywords
    for i in range(20):
        db_session.add(
            SearchKeyword(user_id=None, keyword=f"item {i}", destination=f"/products?query=item{i}")
        )
    db_session.commit()

    suggestions = service.suggest_keywords(db_session, query="item", limit=10)
    assert len(suggestions) == 10
