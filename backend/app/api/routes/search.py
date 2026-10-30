from fastapi import APIRouter
from app.services.search_service import search_service
from app.schemas.search import SearchRequest, SearchResponse

router = APIRouter(prefix="/api/search", tags=["Search"])

@router.post("", response_model=SearchResponse)
async def search_endpoint(request: SearchRequest):
    return await search_service.search(request.query, request.max_results)
