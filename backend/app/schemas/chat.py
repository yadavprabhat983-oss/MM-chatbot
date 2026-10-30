from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class AttachmentItem(BaseModel):
    type: str  # 'image' | 'audio' | 'document'
    filename: str
    content_base64: Optional[str] = None
    mime_type: Optional[str] = None
    url: Optional[str] = None

class SourceCitation(BaseModel):
    title: str
    url: Optional[str] = None
    doc_id: Optional[int] = None
    chunk_index: Optional[int] = None
    snippet: str
    source_type: str  # 'document' | 'web'

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    search_web: bool = False
    emotional_mode: bool = False
    generate_tts: bool = False
    generate_image: bool = False
    attachments: List[AttachmentItem] = []

class ChatResponse(BaseModel):
    conversation_id: int
    message_id: int
    reply: str
    citations: List[SourceCitation] = []
    audio_url: Optional[str] = None
    generated_image_url: Optional[str] = None
    emotional_mode_active: bool = False
    attachments_processed: List[str] = []
