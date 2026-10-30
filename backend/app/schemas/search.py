from pydantic import BaseModel
from typing import List, Optional

class SearchRequest(BaseModel):
    query: str
    max_results: int = 5

class SearchResultItem(BaseModel):
    title: str
    url: str
    snippet: str
    published_date: Optional[str] = None
    score: Optional[float] = None

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
    provider: str
    total_results: int
