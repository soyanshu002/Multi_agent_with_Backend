from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
import uuid
import httpx
from app.db.database import get_db
from app.db.models import User
from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token, verify_access_token


router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ── Schemas ───────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: str


class SupabaseExchangeRequest(BaseModel):
    access_token: str


class SupabasePublicConfig(BaseModel):
    configured: bool
    url: str = ""
    anon_key: str = ""


async def _get_supabase_profile(access_token: str) -> dict:
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        raise HTTPException(
            status_code=500,
            detail="Supabase is not configured on backend. Set SUPABASE_URL and SUPABASE_ANON_KEY."
        )

    profile_url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/user"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.SUPABASE_ANON_KEY,
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(profile_url, headers=headers)
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="Unable to reach Supabase auth service")

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid Supabase access token")

    return response.json()


# ── Register ──────────────────────────────────────
@router.post("/register", response_model=TokenResponse)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    token = create_access_token(str(new_user.id))
    return TokenResponse(
        access_token=token,
        user_id=str(new_user.id),
        email=new_user.email,
        full_name=new_user.full_name or "",
    )


# ── Login ─────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == form.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")

    token = create_access_token(str(user.id))
    return TokenResponse(
        access_token=token,
        user_id=str(user.id),
        email=user.email,
        full_name=user.full_name or "",
    )


# ── Get Me ────────────────────────────────────────
@router.get("/me")
async def get_me(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    user_id = verify_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "created_at": user.created_at,
    }


@router.post("/supabase/exchange", response_model=TokenResponse)
async def supabase_exchange(
    data: SupabaseExchangeRequest,
    db: AsyncSession = Depends(get_db)
):
    profile = await _get_supabase_profile(data.access_token)
    email = profile.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Supabase profile has no email")

    metadata = profile.get("user_metadata") or {}
    full_name = metadata.get("full_name") or metadata.get("name") or ""

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            email=email,
            hashed_password=hash_password(str(uuid.uuid4())),
            full_name=full_name,
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    elif full_name and not user.full_name:
        user.full_name = full_name
        await db.commit()
        await db.refresh(user)

    token = create_access_token(str(user.id))
    return TokenResponse(
        access_token=token,
        user_id=str(user.id),
        email=user.email,
        full_name=user.full_name or "",
    )


@router.get("/supabase/config", response_model=SupabasePublicConfig)
async def supabase_config():
    configured = bool(settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY)
    if not configured:
        return SupabasePublicConfig(configured=False)

    return SupabasePublicConfig(
        configured=True,
        url=settings.SUPABASE_URL,
        anon_key=settings.SUPABASE_ANON_KEY,
    )