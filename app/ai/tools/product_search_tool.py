from typing import Any, Callable, Dict, List

from sqlalchemy.orm import Session

from app.services.product_service import ProductService

try:
    from langchain.tools import Tool
except ImportError:
    class Tool:  # pragma: no cover - fallback class for environments without LangChain
        def __init__(self, name: str, description: str, func: Callable[..., Any]):
            self.name = name
            self.description = description
            self.func = func

        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)


class ProductSearchTool:
    def __init__(
        self,
        product_service: ProductService,
        db_session_factory: Callable[[], Session],
        *,
        default_limit: int = 5,
    ):
        self.product_service = product_service
        self.db_session_factory = db_session_factory
        self.default_limit = default_limit

    def _search(self, query: str) -> List[Dict[str, Any]]:
        """
        Run a text search via the domain ProductService and map results into a
        lightweight dict that the LLM can reason over.
        """
        db = self.db_session_factory()
        try:
            products = self.product_service.search_products(
                db,
                query=query,
                limit=self.default_limit,
            )
            return [
                {
                    "id": product.id,
                    "title": product.name,
                    "price": str(product.price),
                    "image": product.images[0].url if product.images else None,
                }
                for product in products
            ]
        finally:
            db.close()

    def to_langchain_tool(self) -> Tool:
        return Tool(
            name="search_products",
            description="Search fashion products based on user style needs, keywords, or occasion.",
            func=self._search,
        )
