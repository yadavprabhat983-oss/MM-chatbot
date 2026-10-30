import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any, Dict

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender: str
    text: str
    meta: Optional[Dict[str, Any]] = None
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"

class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    message_count: int = 0

    model_config = ConfigDict(from_attributes=True)

class ConversationDetailResponse(BaseModel):
    id: int
    title: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    messages: List[MessageResponse] = []

    model_config = ConfigDict(from_attributes=True)
