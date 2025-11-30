from fastapi import APIRouter, UploadFile
from app.services.dataset_manager import DatasetManager
from app.logger import get_logger
import os
from app.storage import dvc_add, dvc_remove, dvc_list

router = APIRouter()
logger = get_logger("datasets")


@router.get("/")
def list_datasets():
    logger.info("Datasets listing requested")
    return dvc_list(path="data", recursive=True)


@router.post("/")
def upload_dataset(file: UploadFile):
    logger.info("Datasets saving requested")
    path = f"/app/data/{file.filename}"

    os.makedirs("/app/data", exist_ok=True)

    with open(path, "wb") as f:
        f.write(file.file.read())

    dvc_add(path)
    return {"status": "ok", "file": file.filename}


@router.delete("/{name}")
def delete_dataset(name: str):
    logger.info("Datasets delition requested")
    path = f"/app/data/{name}"
    dvc_remove(path)
    return {"status": "deleted"}
