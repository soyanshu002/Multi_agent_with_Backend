from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from app.services.llm.factory import get_llm_provider
from app.core.security import verify_access_token
from app.core.config import settings

router = APIRouter()
bearer = HTTPBearer()


# ── Request Schema ─────────────────────────────────────
class ChatRequest(BaseModel):
    messages: list[dict]           # [{"role": "user", "content": "Hello"}]
    provider: str = "groq"
    model: str = None              # uses default from config if None
    stream: bool = False


class ChatResponse(BaseModel):
    response: str
    provider: str
    model: str


# ── Single Response ────────────────────────────────────
@router.post("/send", response_model=ChatResponse)
async def send_message(
    req: ChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer)
):
    user_id = verify_access_token(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    provider = get_llm_provider(req.provider)
    model = req.model or settings.__dict__.get(f"DEFAULT_{req.provider.upper()}_MODEL", settings.DEFAULT_GROQ_MODEL)

    if req.stream:
        async def generator():
            async for chunk in provider.stream_chat(req.messages, model):
                yield chunk
        return StreamingResponse(generator(), media_type="text/plain")

    response = await provider.chat(req.messages, model)
    return ChatResponse(response=response, provider=req.provider, model=model)


# ── Get Available Models ───────────────────────────────
@router.get("/models")
async def get_models(
    provider: str = "groq",
    credentials: HTTPAuthorizationCredentials = Depends(bearer)
):
    verify_access_token(credentials.credentials)
    llm = get_llm_provider(provider)
    return {
        "provider": provider,
        "models": llm.get_available_models()
    }


# ── Get All Providers ──────────────────────────────────
@router.get("/providers")
async def get_providers(
    credentials: HTTPAuthorizationCredentials = Depends(bearer)
):
    verify_access_token(credentials.credentials)
    return {"providers": settings.LLM_PROVIDERS}