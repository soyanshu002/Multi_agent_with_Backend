from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.database import get_db
from app.core.config import settings
import redis.asyncio as aioredis

router = APIRouter(prefix="/health", tags=["Health"])


# ── Main Health Check ─────────────────────────────
@router.get("")
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# ── Detailed Health Check ─────────────────────────
@router.get("/details")
async def health_details(db: AsyncSession = Depends(get_db)):

    # check database
    db_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    # check redis
    redis_status = "ok"
    try:
        r = aioredis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.aclose()
    except Exception as e:
        redis_status = f"error: {str(e)}"

    return {
        "status": "ok" if db_status == "ok" and redis_status == "ok" else "degraded",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "services": {
            "database": db_status,
            "redis":    redis_status,
        }
    }
