import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator
from pgvector.sqlalchemy import Vector
from app.db.base import Base
from app.core.config import settings

class EmbeddingType(TypeDecorator):
    impl = Vector(settings.EMBEDDING_DIMENSIONS)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "sqlite":
            return dialect.type_descriptor(JSON())
        return dialect.type_descriptor(Vector(settings.EMBEDDING_DIMENSIONS))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "sqlite":
            if isinstance(value, list):
                return value
            return list(value)
        return value

    def process_result_value(self, value, dialect):
        return value

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    embedding = Column(EmbeddingType, nullable=True)
    meta = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    document = relationship("Document", back_populates="chunks")
