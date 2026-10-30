import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class DocumentVersionResponse(BaseModel):
    id: int
    version_number: int
    content_text: str
    change_summary: Optional[str] = None
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class DocumentResponse(BaseModel):
    id: int
    title: str
    filename: str
    file_type: str
    file_size: int
    status: str  # 'indexing' | 'indexed' | 'failed'
    error_message: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    chunk_count: int = 0

    model_config = ConfigDict(from_attributes=True)

class DocumentDetailResponse(DocumentResponse):
    content_text: str
    versions: List[DocumentVersionResponse] = []

    model_config = ConfigDict(from_attributes=True)

class DocumentCreateRequest(BaseModel):
    title: str
    content_text: str

class DocumentUpdateRequest(BaseModel):
    title: Optional[str] = None
    content_text: str
    change_summary: Optional[str] = "Manual user update"

class DocumentAIEditRequest(BaseModel):
    instruction: str
    action: str = "custom"  # 'rewrite' | 'summarize' | 'expand' | 'grammar' | 'custom'

class DocumentAIEditResponse(BaseModel):
    original_text: str
    proposed_text: str
    diff_summary: str
