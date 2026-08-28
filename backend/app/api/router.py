from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.api import tasks
from backend.app.core.config import settings
from backend.app.database.session import get_db

api_router = APIRouter(prefix="/api/v1")

# Include sub-routers
api_router.include_router(tasks.router)


@api_router.get("/health", tags=["System"])
async def health_check(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Health check endpoint validating database connectivity."""
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "demo_mode": settings.DEMO_MODE,
        "database": db_status,
    }
