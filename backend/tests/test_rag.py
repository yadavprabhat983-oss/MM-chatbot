import pytest
from app.models.document import Document
from app.models.chunk import DocumentChunk
from app.services.rag_service import rag_service

@pytest.mark.asyncio
async def test_rag_ingestion_and_retrieval(db_session):
    # 1. Create a sample document
    doc = Document(
        title="Python Fastapi Guide",
        filename="fastapi_guide.md",
        file_type="md",
        file_size=200,
        content_text="FastAPI is a modern, fast web framework for building APIs with Python 3.8+ based on standard Python type hints.",
        status="indexing"
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)

    # 2. Ingest document
    chunk_count = await rag_service.index_document(db_session, doc)
    assert chunk_count >= 1
    assert doc.status == "indexed"

    # Verify chunks in DB
    chunks = db_session.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).all()
    assert len(chunks) == chunk_count
    assert chunks[0].embedding is not None

    # 3. Retrieve relevant chunks
    query = "What is FastAPI?"
    context, citations = await rag_service.retrieve_relevant_chunks(db_session, query, top_k=2, threshold=0.1)
    
    assert "FastAPI" in context
    assert len(citations) >= 1
    assert citations[0].title == "Python Fastapi Guide"
    assert citations[0].source_type == "document"

    # 4. Re-indexing cleans old chunks
    doc.content_text = "Updated Guide: FastAPI uses Pydantic for validation and SQLAlchemy for database access."
    db_session.commit()
    new_chunk_count = await rag_service.index_document(db_session, doc)
    
    # Verify no orphaned chunks
    updated_chunks = db_session.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).all()
    assert len(updated_chunks) == new_chunk_count
