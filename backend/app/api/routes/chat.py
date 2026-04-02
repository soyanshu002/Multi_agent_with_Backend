from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from app.agents.agent_service import agent_service
from app.services.llm.factory import get_llm_provider
from app.core.security import verify_access_token
from app.core.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ── Request Schema ─────────────────────────────────
class ChatRequest(BaseModel):
    messages:        list[dict]           # [{"role": "user", "content": "Hello"}]
    provider:        str  = "groq"
    model:           str  = None
    stream:          bool = False
    conversation_id: str  = "default"
    usecase:         str  = "auto"        # auto | basic_chat | document_qa
    has_documents:   bool = False


# ── Send Message (Main Endpoint) ───────────────────
@router.post("/send")
async def send_message(
    req: ChatRequest,
    token: str = Depends(oauth2_scheme)
):
    user_id = verify_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    model = req.model or settings.__dict__.get(
        f"DEFAULT_{req.provider.upper()}_MODEL",
        settings.DEFAULT_GROQ_MODEL
    )

    # streaming — bypass agent, call LLM directly
    if req.stream:
        provider = get_llm_provider(req.provider)
        async def generator():
            async for chunk in provider.stream_chat(req.messages, model):
                yield chunk
        return StreamingResponse(generator(), media_type="text/plain")

    # non-streaming — run through LangGraph agent
    result = await agent_service.run(
        user_message=req.messages[-1]["content"],
        user_id=user_id,
        conversation_id=req.conversation_id,
        provider=req.provider,
        model=model,
        usecase=req.usecase,
        has_documents=req.has_documents,
    )

    return result


# ── Get Available Models ───────────────────────────
@router.get("/models")
async def get_models(
    provider: str = "groq",
    token: str = Depends(oauth2_scheme)
):
    verify_access_token(token)
    llm = get_llm_provider(provider)
    return {
        "provider": provider,
        "models": llm.get_available_models()
    }


# ── Get All Providers ──────────────────────────────
@router.get("/providers")
async def get_providers(
    token: str = Depends(oauth2_scheme)
):
    verify_access_token(token)
    return {"providers": settings.LLM_PROVIDERS}