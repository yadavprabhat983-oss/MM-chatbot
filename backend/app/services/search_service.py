from typing import List, Optional
import httpx
from app.core.config import settings
from app.core.logging import logger
from app.schemas.search import SearchResultItem, SearchResponse
from app.core.errors import SearchServiceError

class SearchService:
    def __init__(self):
        self.provider = settings.SEARCH_PROVIDER.lower().strip()
        self.tavily_key = settings.TAVILY_API_KEY

    async def search(self, query: str, max_results: Optional[int] = None) -> SearchResponse:
        count = max_results or settings.SEARCH_MAX_RESULTS
        query_clean = query.strip()
        if not query_clean:
            return SearchResponse(query="", results=[], provider=self.provider, total_results=0)

        if self.provider == "tavily":
            return await self._search_tavily(query_clean, count)
        elif self.provider == "duckduckgo":
            return await self._search_duckduckgo(query_clean, count)
        else:
            return await self._mock_search(query_clean, count)

    async def _search_tavily(self, query: str, max_results: int) -> SearchResponse:
        if not self.tavily_key:
            logger.warning("Tavily API key not found. Falling back to DuckDuckGo search.")
            return await self._search_duckduckgo(query, max_results)

        url = "https://api.tavily.com/search"
        payload = {
            "api_key": self.tavily_key,
            "query": query,
            "search_depth": "basic",
            "include_answer": False,
            "max_results": max_results
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code != 200:
                    logger.error(f"Tavily search error: {res.text}")
                    return await self._search_duckduckgo(query, max_results)

                data = res.json()
                results = []
                for item in data.get("results", []):
                    results.append(SearchResultItem(
                        title=item.get("title", "Web Page"),
                        url=item.get("url", ""),
                        snippet=item.get("content", "")[:500],
                        score=item.get("score")
                    ))
                return SearchResponse(
                    query=query,
                    results=results,
                    provider="tavily",
                    total_results=len(results)
                )
        except Exception as e:
            logger.error(f"Tavily request failed: {e}. Trying DuckDuckGo fallback.")
            return await self._search_duckduckgo(query, max_results)

    async def _search_duckduckgo(self, query: str, max_results: int) -> SearchResponse:
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                ddg_results = list(ddgs.text(query, max_results=max_results))
                items: List[SearchResultItem] = []
                for r in ddg_results:
                    items.append(SearchResultItem(
                        title=r.get("title", "Search Result"),
                        url=r.get("href", ""),
                        snippet=r.get("body", "")[:500]
                    ))
                return SearchResponse(
                    query=query,
                    results=items,
                    provider="duckduckgo",
                    total_results=len(items)
                )
        except Exception as e:
            logger.warning(f"DuckDuckGo search error: {e}. Using simulated search fallback.")
            return await self._mock_search(query, max_results)

    async def _mock_search(self, query: str, max_results: int) -> SearchResponse:
        # Graceful fallback when network search is disabled or rate-limited
        items = [
            SearchResultItem(
                title=f"Overview on {query.title()}",
                url="https://en.wikipedia.org/wiki/" + query.replace(" ", "_"),
                snippet=f"Comprehensive documentation, history, and background details regarding '{query}'.",
                score=0.95
            ),
            SearchResultItem(
                title=f"Latest Developments & Documentation: {query.title()}",
                url="https://docs.example.org/" + query.replace(" ", "-").lower(),
                snippet=f"Technical guide, latest releases, and reference information relating to {query}.",
                score=0.88
            )
        ]
        return SearchResponse(
            query=query,
            results=items[:max_results],
            provider="mock/fallback",
            total_results=len(items[:max_results])
        )

search_service = SearchService()
