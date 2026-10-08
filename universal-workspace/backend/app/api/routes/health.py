from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db


router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
    }


@router.get("/health/database")
def database_health(
    db: Session = Depends(get_db)
):
    db.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": "connected"
    }