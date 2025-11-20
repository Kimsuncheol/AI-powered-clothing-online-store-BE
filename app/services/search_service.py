from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.search_keyword import SearchKeyword
from app.repositories.product_repository import ProductRepository
from app.repositories.search_repository import SearchRepository


class SearchService:
    def __init__(self, search_repo: SearchRepository, product_repo: ProductRepository):
        self.search_repo = search_repo
        self.product_repo = product_repo

    def generate_ngrams(self, text: str, n: int = 2) -> List[str]:
        """
        Generate n-grams from normalized text. Lightweight for memory.
        """
        normalized = (text or "").lower().strip()
        if not normalized:
            return []
        if len(normalized) <= n:
            return [normalized]
        return [normalized[i : i + n] for i in range(len(normalized) - n + 1)]

    def fetch_search_keywords_from_search_keyword_table(
        self, db: Session, *, limit: int = 200
    ) -> List[str]:
        return self.search_repo.fetch_search_keywords_from_table(db, limit=limit)

    def fetch_product_names_from_product_table(
        self, db: Session, *, limit: int = 500
    ) -> List[str]:
        return self.product_repo.fetch_product_names(db, limit=limit)

    def suggest_keywords(
        self, db: Session, *, query: str, limit: int = 10
    ) -> List[Dict[str, str]]:
        q = (query or "").strip()
        if not q:
            return []

        q_lower = q.lower()
        ngrams = self.generate_ngrams(q_lower, n=2)

        search_keywords = self.fetch_search_keywords_from_search_keyword_table(
            db, limit=200
        )
        product_names = self.fetch_product_names_from_product_table(db, limit=500)

        candidates: Dict[str, int] = {}

        def add_candidate(text: str, base_score: int) -> None:
            key = text.lower()
            if not key:
                return
            score = candidates.get(key, 0)
            score += base_score
            if key.startswith(q_lower):
                score += 3
            for ng in ngrams:
                if ng in key:
                    score += 1
            candidates[key] = score

        for kw in search_keywords:
            add_candidate(kw, base_score=3)

        for name in product_names:
            add_candidate(name, base_score=1)

        sorted_items = sorted(
            candidates.items(),
            key=lambda kv: (-kv[1], kv[0]),
        )

        suggestions: List[Dict[str, str]] = []
        for key, _ in sorted_items[:limit]:
            suggestions.append(
                {
                    "keyword": key,
                    "destination": f"/products?query={key}",
                }
            )
        return suggestions

    def get_history_for_user(
        self, db: Session, user_id: Optional[int]
    ) -> List[SearchKeyword]:
        return self.search_repo.get_history_for_user(db, user_id=user_id)

    def delete_history_item(
        self, db: Session, *, item_id: int, user_id: Optional[int]
    ) -> None:
        self.search_repo.delete_history_item(db, item_id=item_id, user_id=user_id)

    def add_history_item(
        self,
        db: Session,
        *,
        user_id: Optional[int],
        keyword: str,
        destination: str,
    ) -> SearchKeyword:
        return self.search_repo.create_history_item(
            db, user_id=user_id, keyword=keyword, destination=destination
        )
