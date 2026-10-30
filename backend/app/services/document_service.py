from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.chunk import DocumentChunk
from app.schemas.document import (
    DocumentResponse,
    DocumentDetailResponse,
    DocumentAIEditResponse
)
from app.core.errors import DocumentNotFoundError, InvalidFileError
from app.utils.text_extractor import extract_text_from_file
from app.services.rag_service import rag_service
from app.services.ai_provider import get_ai_provider
from app.core.logging import logger

class DocumentService:
    def list_documents(self, db: Session) -> List[DocumentResponse]:
        docs = db.execute(select(Document).order_by(Document.updated_at.desc())).scalars().all()
        result = []
        for d in docs:
            chunk_count = db.query(func.count(DocumentChunk.id)).filter(DocumentChunk.document_id == d.id).scalar() or 0
            res = DocumentResponse(
                id=d.id,
                title=d.title,
                filename=d.filename,
                file_type=d.file_type,
                file_size=d.file_size,
                status=d.status,
                error_message=d.error_message,
                created_at=d.created_at,
                updated_at=d.updated_at,
                chunk_count=chunk_count
            )
            result.append(res)
        return result

    def get_document(self, db: Session, doc_id: int) -> Document:
        doc = db.execute(select(Document).where(Document.id == doc_id)).scalar_one_or_none()
        if not doc:
            raise DocumentNotFoundError(doc_id)
        return doc

    def get_document_detail(self, db: Session, doc_id: int) -> DocumentDetailResponse:
        doc = self.get_document(db, doc_id)
        chunk_count = db.query(func.count(DocumentChunk.id)).filter(DocumentChunk.document_id == doc.id).scalar() or 0
        return DocumentDetailResponse(
            id=doc.id,
            title=doc.title,
            filename=doc.filename,
            file_type=doc.file_type,
            file_size=doc.file_size,
            status=doc.status,
            error_message=doc.error_message,
            content_text=doc.content_text,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
            chunk_count=chunk_count,
            versions=doc.versions
        )

    async def upload_document(
        self,
        db: Session,
        file_bytes: bytes,
        filename: str,
        title: Optional[str] = None
    ) -> Document:
        content_text, file_type = extract_text_from_file(file_bytes, filename)
        doc_title = title or filename

        doc = Document(
            title=doc_title,
            filename=filename,
            file_type=file_type,
            file_size=len(file_bytes),
            content_text=content_text,
            status="indexing"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        # Initial version
        version = DocumentVersion(
            document_id=doc.id,
            version_number=1,
            content_text=content_text,
            change_summary="Initial upload"
        )
        db.add(version)
        db.commit()

        # Ingest into RAG vector index
        await rag_service.index_document(db, doc)
        db.refresh(doc)
        return doc

    async def create_document(
        self,
        db: Session,
        title: str,
        content_text: str
    ) -> Document:
        clean_text = content_text.strip()
        filename = f"{title.lower().replace(' ', '_')}.md"
        doc = Document(
            title=title,
            filename=filename,
            file_type="md",
            file_size=len(clean_text.encode("utf-8")),
            content_text=clean_text,
            status="indexing"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        version = DocumentVersion(
            document_id=doc.id,
            version_number=1,
            content_text=clean_text,
            change_summary="Initial document creation"
        )
        db.add(version)
        db.commit()

        await rag_service.index_document(db, doc)
        db.refresh(doc)
        return doc

    async def update_document(
        self,
        db: Session,
        doc_id: int,
        content_text: str,
        title: Optional[str] = None,
        change_summary: Optional[str] = None
    ) -> Document:
        doc = self.get_document(db, doc_id)
        current_version_count = len(doc.versions)
        new_version_num = current_version_count + 1

        doc.content_text = content_text
        if title:
            doc.title = title
        doc.file_size = len(content_text.encode("utf-8"))
        doc.status = "indexing"

        # Save new version record
        version = DocumentVersion(
            document_id=doc.id,
            version_number=new_version_num,
            content_text=content_text,
            change_summary=change_summary or f"Version {new_version_num} update"
        )
        db.add(version)
        db.commit()

        # Re-index for RAG
        await rag_service.index_document(db, doc)
        db.refresh(doc)
        return doc

    async def ai_edit(
        self,
        db: Session,
        doc_id: int,
        action: str,
        instruction: str
    ) -> DocumentAIEditResponse:
        doc = self.get_document(db, doc_id)
        provider = get_ai_provider()

        system_prompt = (
            "You are an expert document editor. "
            "Follow the user's specific editing instructions precisely. "
            "Return ONLY the revised document text without markdown meta-commentary."
        )

        user_prompt = f"""Target Document Title: {doc.title}
Requested Action: {action.upper()}
Instructions: {instruction}

Original Document Content:
\"\"\"
{doc.content_text}
\"\"\"
"""
        messages = [{"role": "user", "content": user_prompt}]
        proposed = await provider.generate_text(messages, system_prompt=system_prompt)

        diff_summary = f"AI {action.title()} applied: {instruction}"
        return DocumentAIEditResponse(
            original_text=doc.content_text,
            proposed_text=proposed.strip(),
            diff_summary=diff_summary
        )

    async def reindex_document(self, db: Session, doc_id: int) -> int:
        doc = self.get_document(db, doc_id)
        doc.status = "indexing"
        db.commit()
        return await rag_service.index_document(db, doc)

    def delete_document(self, db: Session, doc_id: int) -> bool:
        doc = self.get_document(db, doc_id)
        db.delete(doc)
        db.commit()
        return True

    def export_document(self, db: Session, doc_id: int, fmt: str = "md") -> Tuple[str, str, str]:
        doc = self.get_document(db, doc_id)
        safe_title = doc.title.replace(" ", "_").lower()
        if fmt.lower() == "txt":
            filename = f"{safe_title}.txt"
            media_type = "text/plain"
        else:
            filename = f"{safe_title}.md"
            media_type = "text/markdown"
        return doc.content_text, filename, media_type

document_service = DocumentService()
