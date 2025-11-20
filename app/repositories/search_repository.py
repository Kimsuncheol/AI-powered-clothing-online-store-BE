from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.search_keyword import SearchKeyword


class SearchRepository:
    def get_history_for_user(
        self, db: Session, *, user_id: Optional[int], limit: int = 20
    ) -> List[SearchKeyword]:
        query = db.query(SearchKeyword)
        if user_id is not None:
            query = query.filter(SearchKeyword.user_id == user_id)
        else:
            query = query.filter(SearchKeyword.user_id.is_(None))
        return (
            query.order_by(desc(SearchKeyword.created_at))
            .limit(limit)
            .all()
        )

    def delete_history_item(
        self, db: Session, *, item_id: int, user_id: Optional[int]
    ) -> None:
        query = db.query(SearchKeyword).filter(SearchKeyword.id == item_id)
        if user_id is not None:
            query = query.filter(SearchKeyword.user_id == user_id)
        else:
            query = query.filter(SearchKeyword.user_id.is_(None))
        item = query.first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="History item not found",
            )
        db.delete(item)
        db.commit()

    def create_history_item(
        self,
        db: Session,
        *,
        user_id: Optional[int],
        keyword: str,
        destination: str,
    ) -> SearchKeyword:
        item = SearchKeyword(
            user_id=user_id,
            keyword=keyword,
            destination=destination,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def fetch_search_keywords_from_table(
        self, db: Session, *, limit: int = 200
    ) -> List[str]:
        rows = (
            db.query(SearchKeyword.keyword)
            .distinct()
            .order_by(desc(SearchKeyword.created_at))
            .limit(limit)
            .all()
        )
        return [row[0] for row in rows]
