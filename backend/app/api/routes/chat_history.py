from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select

from app.db.database import get_db
from app.db.models import Conversation, Message, User
from app.core.security import verify_access_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class MessageSchema(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationSchema(BaseModel):
    id: str
    title: str
    provider: str
    model: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationDetailSchema(ConversationSchema):
    messages: list[MessageSchema]


class CreateConversationRequest(BaseModel):
    title: str = "New Conversation"
    provider: str = "groq"
    model: str = "llama-3.3-70b-versatile"


class AddMessageRequest(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    token_count: int = 0


# ── Get All Conversations for User ────────────────────────
@router.get("/conversations")
async def get_conversations(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Fetch all conversations for the logged-in user, sorted by most recent"""
    user_id = verify_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        result = await db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(desc(Conversation.updated_at))
        )
        conversations = result.scalars().all()

        return {
            "conversations": [
                {
                    "id": c.id,
                    "title": c.title,
                    "provider": c.provider,
                    "model": c.model,
                    "created_at": c.created_at.isoformat(),
                    "updated_at": c.updated_at.isoformat(),
                }
                for c in conversations
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Create New Conversation ────────────────────────────────
@router.post("/conversations")
async def create_conversation(
    req: CreateConversationRequest,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Create a new conversation for the logged-in user"""
    user_id = verify_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        # Verify user exists
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        conversation = Conversation(
            user_id=user_id,
            title=req.title,
            provider=req.provider,
            model=req.model,
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

        return {
            "id": conversation.id,
            "title": conversation.title,
            "provider": conversation.provider,
            "model": conversation.model,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ── Get Conversation with Messages ────────────────────────
@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Fetch a specific conversation with all its messages"""
    user_id = verify_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        msg_result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        messages = msg_result.scalars().all()

        return {
            "id": conversation.id,
            "title": conversation.title,
            "provider": conversation.provider,
            "model": conversation.model,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "messages": [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "created_at": m.created_at.isoformat(),
                }
                for m in messages
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Add Message to Conversation ────────────────────────────
@router.post("/conversations/{conversation_id}/messages")
async def add_message(
    conversation_id: str,
    req: AddMessageRequest,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Add a message to a conversation"""
    user_id = verify_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        message = Message(
            conversation_id=conversation_id,
            role=req.role,
            content=req.content,
            token_count=req.token_count,
        )
        db.add(message)

        # Update conversation's updated_at timestamp
        conversation.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(message)

        return {
            "id": message.id,
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ── Update Conversation Title ──────────────────────────────
@router.patch("/conversations/{conversation_id}")
async def update_conversation(
    conversation_id: str,
    req: dict,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Update conversation title or other fields"""
    user_id = verify_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        if "title" in req:
            conversation.title = req["title"]
        conversation.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(conversation)

        return {
            "id": conversation.id,
            "title": conversation.title,
            "provider": conversation.provider,
            "model": conversation.model,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ── Delete Conversation ────────────────────────────────────
@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Delete a conversation and all its messages"""
    user_id = verify_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        db.delete(conversation)
        await db.commit()

        return {"message": "Conversation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
