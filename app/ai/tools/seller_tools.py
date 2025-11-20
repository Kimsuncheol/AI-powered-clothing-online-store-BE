from typing import Any, Callable, Dict, List, Optional

from sqlalchemy.orm import Session

from app.services.product_service import ProductService

try:
    from langchain.tools import Tool
except ImportError:  # pragma: no cover - fallback lightweight Tool

    class Tool:  # type: ignore[override]
        def __init__(self, name: str, description: str, func: Callable[..., Any]):
            self.name = name
            self.description = description
            self.func = func

        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)


class SellerTools:
    def __init__(
        self,
        product_service: ProductService,
        db_session_factory: Callable[[], Session],
    ):
        self.product_service = product_service
        self.db_session_factory = db_session_factory

    def _get_product_detail(self, product_id: int) -> Dict[str, Any]:
        """
        Fetch product detail (name, category, price, variants, etc.)
        for AI to use in descriptions and pricing suggestions.
        """
        db = self.db_session_factory()
        try:
            product = self.product_service.get_product_for_context(
                db,
                product_id=product_id,
            )
            if not product:
                return {}
            return {
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "gender": getattr(product, "gender", None),
                "price": str(product.price) if getattr(product, "price", None) is not None else None,
                "stock": getattr(product, "stock", None),
            }
        finally:
            db.close()

    def _get_market_stats(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Optional stub — returns fixed or internal stats like:
        typical price ranges, popular styles, etc.
        """
        return {
            "category": category or "generic",
            "avg_price": "49.99",
            "min_price": "19.99",
            "max_price": "129.99",
            "notes": "Stubbed market stats for pricing suggestions.",
        }

    def to_langchain_tools(self) -> List[Tool]:
        return [
            Tool(
                name="get_product_detail",
                description="Get detailed info for a specific product to help with descriptions and pricing.",
                func=lambda product_id: self._get_product_detail(int(product_id)),
            ),
            Tool(
                name="get_market_stats",
                description="Get basic market stats (stub) to help suggest a price.",
                func=lambda category=None: self._get_market_stats(category),
            ),
        ]
