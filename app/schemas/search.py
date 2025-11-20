from datetime import datetime
from typing import List

from pydantic import BaseModel


class SearchHistoryItem(BaseModel):
    id: int
    keyword: str
    destination: str
    created_at: datetime

    class Config:
        orm_mode = True


class SearchHistoryListResponse(BaseModel):
    items: List[SearchHistoryItem]


class SearchSuggestItem(BaseModel):
    keyword: str
    destination: str


class SearchSuggestResponse(BaseModel):
    items: List[SearchSuggestItem]
