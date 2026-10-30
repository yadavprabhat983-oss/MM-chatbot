from typing import List, Tuple, Optional
import math
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from app.models.document import Document
from app.models.chunk import DocumentChunk
from app.schemas.chat import SourceCitation
from app.core.config import settings
from app.core.logging import logger
from app.utils.chunker import chunk_text
from app.services.embedding_service import embedding_service

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class RAGService:
    async def index_document(self, db: Session, document: Document) -> int:
        """
        Splits document text, generates embeddings, and saves chunks.
        """
        try:
            # 1. Remove existing chunks if re-indexing
            db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document.id))
            db.commit()

            # 2. Chunk text
            chunks_data = chunk_text(
                document.content_text,
                chunk_size=settings.RAG_CHUNK_SIZE,
                chunk_overlap=settings.RAG_CHUNK_OVERLAP
            )
            if not chunks_data:
                document.status = "indexed"
                db.commit()
                return 0

            # 3. Generate embeddings
            texts = [c["text"] for c in chunks_data]
            embeddings = await embedding_service.get_embeddings(texts)

            # 4. Save chunks
            for chunk_meta, emb in zip(chunks_data, embeddings):
                chunk = DocumentChunk(
                    document_id=document.id,
                    chunk_index=chunk_meta["chunk_index"],
                    text=chunk_meta["text"],
                    embedding=emb,
                    meta={"char_length": chunk_meta["char_length"]}
                )
                db.add(chunk)

            document.status = "indexed"
            document.error_message = None
            db.commit()
            logger.info(f"Successfully indexed document {document.id} with {len(chunks_data)} chunks.")
            return len(chunks_data)

        except Exception as e:
            logger.error(f"Failed indexing document {document.id}: {e}")
            db.rollback()
            document.status = "failed"
            document.error_message = str(e)
            db.commit()
            raise e

    async def retrieve_relevant_chunks(
        self,
        db: Session,
        query: str,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None
    ) -> Tuple[str, List[SourceCitation]]:
        """
        Performs vector similarity search against all indexed document chunks.
        Returns (context_string, list_of_citations).
        """
        limit = top_k or settings.RAG_TOP_K
        sim_threshold = threshold or settings.RAG_SIMILARITY_THRESHOLD

        query_embedding = await embedding_service.get_single_embedding(query)
        if not query_embedding:
            return "", []

        dialect_name = db.bind.dialect.name if db.bind else "postgresql"

        citations: List[SourceCitation] = []
        context_parts: List[str] = []

        if dialect_name == "postgresql":
            try:
                # Use pgvector cosine distance: distance = 1 - similarity
                # Max distance allowed = 1.0 - sim_threshold
                max_distance = max(0.0, 1.0 - sim_threshold)
                stmt = (
                    select(DocumentChunk, Document.title)
                    .join(Document, Document.id == DocumentChunk.document_id)
                    .where(Document.status == "indexed")
                    .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
                    .limit(limit)
                )
                results = db.execute(stmt).all()
                for chunk, doc_title in results:
                    citations.append(SourceCitation(
                        title=doc_title,
                        doc_id=chunk.document_id,
                        chunk_index=chunk.chunk_index,
                        snippet=chunk.text[:200] + ("..." if len(chunk.text) > 200 else ""),
                        source_type="document"
                    ))
                    context_parts.append(
                        f"[Document: '{doc_title}' (Chunk {chunk.chunk_index})]:\n{chunk.text}"
                    )
                return "\n\n".join(context_parts), citations
            except Exception as e:
                logger.warning(f"pgvector query fell back: {e}")

        # Fallback (e.g. SQLite tests or dialect fallback): In-memory cosine similarity
        stmt = (
            select(DocumentChunk, Document.title)
            .join(Document, Document.id == DocumentChunk.document_id)
            .where(Document.status == "indexed")
        )
        all_chunks = db.execute(stmt).all()
        scored_chunks = []
        for chunk, doc_title in all_chunks:
            if chunk.embedding:
                # chunk.embedding may be list or Vector
                emb_list = list(chunk.embedding)
                sim = cosine_similarity(query_embedding, emb_list)
                if sim >= sim_threshold:
                    scored_chunks.append((sim, chunk, doc_title))

        # Sort descending by similarity
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_chunks = scored_chunks[:limit]

        for sim, chunk, doc_title in top_chunks:
            citations.append(SourceCitation(
                title=doc_title,
                doc_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                snippet=chunk.text[:200] + ("..." if len(chunk.text) > 200 else ""),
                source_type="document"
            ))
            context_parts.append(
                f"[Document: '{doc_title}' (Chunk {chunk.chunk_index})]:\n{chunk.text}"
            )

        return "\n\n".join(context_parts), citations

rag_service = RAGService()
