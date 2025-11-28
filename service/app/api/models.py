from fastapi import APIRouter
from app.services.model_registry import ModelRegistry
from app.logger import get_logger

router = APIRouter()
logger = get_logger("models")

@router.get("/classes")
def list_model_classes():
    logger.info("List available model classes")
    return ModelRegistry.list_models()
