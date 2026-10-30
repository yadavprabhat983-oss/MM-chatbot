from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.db.session import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.conversation import (
    ConversationResponse,
    ConversationDetailResponse,
    ConversationCreate
)
from app.core.errors import ConversationNotFoundError

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])

@router.get("", response_model=List[ConversationResponse])
def list_conversations(db: Session = Depends(get_db)):
    conversations = db.execute(select(Conversation).order_by(Conversation.updated_at.desc())).scalars().all()
    results = []
    for conv in conversations:
        msg_count = db.query(func.count(Message.id)).filter(Message.conversation_id == conv.id).scalar() or 0
        results.append(ConversationResponse(
            id=conv.id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=msg_count
        ))
    return results

@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(data: ConversationCreate, db: Session = Depends(get_db)):
    conv = Conversation(title=data.title or "New Conversation")
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=0
    )

@router.get("/{id}", response_model=ConversationDetailResponse)
def get_conversation(id: int, db: Session = Depends(get_db)):
    conv = db.execute(select(Conversation).where(Conversation.id == id)).scalar_one_or_none()
    if not conv:
        raise ConversationNotFoundError(id)
    return conv

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(id: int, db: Session = Depends(get_db)):
    conv = db.execute(select(Conversation).where(Conversation.id == id)).scalar_one_or_none()
    if not conv:
        raise ConversationNotFoundError(id)
    db.delete(conv)
    db.commit()
    return None
