import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, Response, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.chat_service import chat_service
from app.services.ai_provider import get_ai_provider
from app.schemas.chat import ChatRequest, ChatResponse
from app.core.config import settings
from app.core.errors import InvalidFileError

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    return await chat_service.process_chat(db, request)

@router.post("/transcribe")
async def transcribe_audio_file(file: UploadFile = File(...)):
    provider = get_ai_provider()
    audio_bytes = await file.read()
    if not audio_bytes:
        raise InvalidFileError("Uploaded audio file is empty.")
    transcription = await provider.transcribe_audio(audio_bytes, file.filename or "audio.wav")
    return {"filename": file.filename, "transcription": transcription}

@router.post("/tts")
async def generate_speech_endpoint(text: str = Form(...), voice: str = Form("alloy")):
    provider = get_ai_provider()
    speech_bytes = await provider.generate_speech(text, voice)
    return Response(content=speech_bytes, media_type="audio/wav")

@router.get("/audio/{filename}")
def get_audio_file(filename: str):
    # Sanitize filename
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(file_path, media_type="audio/wav")
