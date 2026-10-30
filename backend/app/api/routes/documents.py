from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, Response, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.document_service import document_service
from app.schemas.document import (
    DocumentResponse,
    DocumentDetailResponse,
    DocumentCreateRequest,
    DocumentUpdateRequest,
    DocumentAIEditRequest,
    DocumentAIEditResponse
)
from app.core.config import settings
from app.core.errors import InvalidFileError

router = APIRouter(prefix="/api/documents", tags=["Documents"])

@router.get("", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    return document_service.list_documents(db)

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    # Validate file size
    file_bytes = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise InvalidFileError(f"File size exceeds maximum allowed of {settings.MAX_UPLOAD_SIZE_MB}MB")

    filename = file.filename or "uploaded_document.txt"
    doc = await document_service.upload_document(
        db=db,
        file_bytes=file_bytes,
        filename=filename,
        title=title or filename
    )
    return document_service.get_document_detail(db, doc.id)

@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    data: DocumentCreateRequest,
    db: Session = Depends(get_db)
):
    doc = await document_service.create_document(
        db=db,
        title=data.title,
        content_text=data.content_text
    )
    return document_service.get_document_detail(db, doc.id)

@router.get("/{id}", response_model=DocumentDetailResponse)
def get_document(id: int, db: Session = Depends(get_db)):
    return document_service.get_document_detail(db, id)

@router.put("/{id}", response_model=DocumentDetailResponse)
async def update_document(
    id: int,
    data: DocumentUpdateRequest,
    db: Session = Depends(get_db)
):
    await document_service.update_document(
        db=db,
        doc_id=id,
        content_text=data.content_text,
        title=data.title,
        change_summary=data.change_summary
    )
    return document_service.get_document_detail(db, id)

@router.post("/{id}/ai-edit", response_model=DocumentAIEditResponse)
async def ai_edit_document(
    id: int,
    data: DocumentAIEditRequest,
    db: Session = Depends(get_db)
):
    return await document_service.ai_edit(
        db=db,
        doc_id=id,
        action=data.action,
        instruction=data.instruction
    )

@router.post("/{id}/reindex")
async def reindex_document(id: int, db: Session = Depends(get_db)):
    chunk_count = await document_service.reindex_document(db, id)
    return {"message": "Document re-indexed successfully", "document_id": id, "chunk_count": chunk_count}

@router.get("/{id}/download")
def download_document(id: int, format: str = "md", db: Session = Depends(get_db)):
    content, filename, media_type = document_service.export_document(db, id, format)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(id: int, db: Session = Depends(get_db)):
    document_service.delete_document(db, id)
    return None
