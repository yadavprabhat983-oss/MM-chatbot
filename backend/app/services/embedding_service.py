from typing import List
from app.core.config import settings
from app.core.logging import logger
from app.services.ai_provider import get_ai_provider

class EmbeddingService:
    def __init__(self):
        self.provider = get_ai_provider()

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        try:
            return await self.provider.generate_embeddings(texts)
        except Exception as e:
            logger.error(f"Error in EmbeddingService: {e}")
            # Fallback to mock embeddings if API call fails
            from app.services.ai_provider import MockAIProvider
            fallback = MockAIProvider()
            return await fallback.generate_embeddings(texts)

    async def get_single_embedding(self, text: str) -> List[float]:
        results = await self.get_embeddings([text])
        return results[0] if results else []

embedding_service = EmbeddingService()
