from fastapi import APIRouter
from app.logger import get_logger
from app.config import settings

router = APIRouter()
logger = get_logger("health")

@router.get("/health", tags=["system"])
def check_health():
    logger.info("Health check requested")
    return {
        "status": "ok",
        "env": settings.ENV
    }
