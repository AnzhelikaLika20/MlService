from fastapi import APIRouter
from app.services.dataset_manager import DatasetManager
from app.logger import get_logger

router = APIRouter()
logger = get_logger("datasets")

@router.get("/datasets")
def list_datasets():
    from app.storage import list_datasets
    datasets = list_datasets()
    return {"datasets": datasets}


@router.post("/datasets")
def upload_dataset(dataset: dict):
    from app.storage import save_dataset
    save_dataset(dataset)
    logger.info("Dataset uploaded.")
    return {"status": "uploaded"}


@router.delete("/datasets/{dataset_name}")
def delete_dataset(dataset_name: str):
    from app.storage import remove_dataset
    try:
        remove_dataset(dataset_name)
        logger.info(f"Dataset {dataset_name} deleted.")
        return {"status": "deleted", "dataset": dataset_name}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dataset not found")
