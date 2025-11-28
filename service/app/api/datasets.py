from fastapi import APIRouter
from app.services.dataset_manager import DatasetManager
from app.logger import get_logger

router = APIRouter()
logger = get_logger("datasets")

@router.get("/")
def list_datasets():
    logger.info("List datasets")
    return DatasetManager.list_datasets()
