from app.config import settings
from app.logger import get_logger
from fastapi import APIRouter

router = APIRouter()
logger = get_logger("health")


@router.get("/health", tags=["system"])
def check_health():
    logger.info("Health check requested")
    return {"status": "ok", "env": settings.ENV}
