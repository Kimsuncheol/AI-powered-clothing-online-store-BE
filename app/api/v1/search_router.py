from typing import Optional

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.security import get_optional_user
from app.db.session import get_db
from app.dependencies import get_search_service
from app.models.user import User
from app.schemas.search import (
    SearchHistoryListResponse,
    SearchSuggestResponse,
)
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/history", response_model=SearchHistoryListResponse)
def get_search_history(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
    search_service: SearchService = Depends(get_search_service),
):
    items = search_service.get_history_for_user(
        db,
        user_id=current_user.id if current_user else None,
    )
    return SearchHistoryListResponse(items=items)


@router.delete("/history/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_search_history_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
    search_service: SearchService = Depends(get_search_service),
):
    search_service.delete_history_item(
        db,
        item_id=item_id,
        user_id=current_user.id if current_user else None,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/suggest", response_model=SearchSuggestResponse)
def suggest_keywords(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    search_service: SearchService = Depends(get_search_service),
):
    items = search_service.suggest_keywords(db, query=q, limit=10)
    return SearchSuggestResponse(items=items)
