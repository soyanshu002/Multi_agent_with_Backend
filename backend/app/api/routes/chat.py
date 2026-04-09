from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
from app.agents.agent_service import agent_service
from app.services.llm.factory import get_llm_provider
from app.services.rag.rag_services import rag_service
from app.services.audio_service import get_audio_service
from app.core.security import verify_access_token
from app.core.config import settings, get_models_for_provider

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ── Request Schemas ────────────────────────────────
class ChatRequest(BaseModel):
    messages:        list[dict]
    provider:        str           = "groq"
    model:           Optional[str] = None
    stream:          bool          = False
    conversation_id: str           = "default"
    usecase:         str           = "auto"
    has_documents:   bool          = False
    namespace:       str           = ""        # ← NEW

class NamespaceRequest(BaseModel):
    namespace: str


class TextToSpeechRequest(BaseModel):
    text: str
    voice: str = "alloy"
    speed: float = 1.0
    language: str = "en"


class SpeechToTextRequest(BaseModel):
    language: str = "en"
    prompt: Optional[str] = None


# ── Send Message ───────────────────────────────────
@router.post("/send")
async def send_message(
    req: ChatRequest,
    token: str = Depends(oauth2_scheme)
):
    user_id = verify_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    llm = get_llm_provider(req.provider)
    available_models = llm.get_available_models()
    default_model = settings.__dict__.get(
        f"DEFAULT_{req.provider.upper()}_MODEL",
        settings.DEFAULT_GROQ_MODEL
    )
    model = req.model or default_model
    if model not in available_models:
        model = default_model if default_model in available_models else available_models[0]

    if req.stream:
        async def generator():
            async for chunk in llm.stream_chat(req.messages, model):
                yield chunk
        return StreamingResponse(generator(), media_type="text/plain")

    result = await agent_service.run(
        user_message=req.messages[-1]["content"],
        user_id=user_id,
        conversation_id=req.conversation_id,
        provider=req.provider,
        model=model,
        usecase=req.usecase,
        has_documents=req.has_documents,
        namespace=req.namespace,               # ← NEW
    )
    return result


# ── Upload Document ────────────────────────────────
@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    namespace: str = Form(...),
    token: str = Depends(oauth2_scheme)
):
    user_id = verify_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    file_bytes = await file.read()
    result = await rag_service.index_document(
        file_bytes=file_bytes,
        filename=file.filename,
        namespace=namespace
    )
    return result


# ── Delete Namespace ───────────────────────────────
@router.post("/delete-namespace")
async def delete_namespace(
    req: NamespaceRequest,
    token: str = Depends(oauth2_scheme)
):
    user_id = verify_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return await rag_service.delete_document(req.namespace)


# ── Get Available Models ───────────────────────────
@router.get("/models")
async def get_models(
    provider: str = "groq",
    token: str = Depends(oauth2_scheme)
):
    verify_access_token(token)
    models = get_models_for_provider(provider)
    return {"provider": provider, "models": models}


# ── Get All Providers ──────────────────────────────
@router.get("/providers")
async def get_providers(token: str = Depends(oauth2_scheme)):
    verify_access_token(token)
    return {"providers": settings.LLM_PROVIDERS}


# ── Audio: Speech-to-Text ──────────────────────────
@router.post("/speech-to-text")
async def speech_to_text(
    file: UploadFile = File(...),
    language: str = Form("en"),
    prompt: Optional[str] = Form(None),
    token: str = Depends(oauth2_scheme)
):
    """Convert audio file to text using Groq Whisper API."""
    user_id = verify_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        audio_bytes = await file.read()
        audio_service = get_audio_service()
        result = await audio_service.speech_to_text(
            audio_bytes,
            language=language,
            prompt=prompt
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Audio: Text-to-Speech ──────────────────────────
@router.post("/text-to-speech")
async def text_to_speech(
    req: TextToSpeechRequest,
    token: str = Depends(oauth2_scheme)
):
    """Convert text to speech using OpenAI TTS API."""
    user_id = verify_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        audio_service = get_audio_service()
        result = await audio_service.text_to_speech(
            text=req.text,
            voice=req.voice,
            speed=req.speed,
            language=req.language
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Audio: Available Voices ────────────────────────
@router.get("/audio/voices")
async def get_voices(token: str = Depends(oauth2_scheme)):
    """Get list of available TTS voices."""
    verify_access_token(token)
    audio_service = get_audio_service()
    return {"voices": audio_service.get_available_voices()}


# ── Audio: Available Languages ────────────────────
@router.get("/audio/languages")
async def get_languages(token: str = Depends(oauth2_scheme)):
    """Get list of supported STT languages."""
    verify_access_token(token)
    audio_service = get_audio_service()
    return {"languages": audio_service.get_available_languages()}