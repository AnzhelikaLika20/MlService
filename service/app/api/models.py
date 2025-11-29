import os
import numpy as np
from fastapi import APIRouter, HTTPException
from app.ml.registry import list_models, get_model
from app.logger import get_logger
from app.storage import save_model, load_model, trained_models, delete_model

router = APIRouter()
logger = get_logger("models")

MODELS_DIR = "saved_models"
os.makedirs(MODELS_DIR, exist_ok=True)


@router.get("/supported-models")
def get_model_classes():
    return {"models": list_models()}


@router.get("/trained-models")
def get_all_models():
    """Возвращает список всех обученных моделей"""
    return {"models": trained_models()}


@router.post("/{model_name}/train")
def train_model(model_name: str, payload: dict):
    if "X" not in payload or "y" not in payload:
        raise HTTPException(status_code=400, detail="Need X and y")

    model = get_model(model_name)

    model.train(payload["X"], payload["y"], **payload.get("params", {}))

    save_model(model, model_name)

    return {"status": "trained", "stored_as": f"{model_name}.pkl"}


@router.post("/{model_name}/predict")
def predict(model_name: str, payload: dict):
    try:
        model = load_model(model_name)
    except Exception:
        raise HTTPException(status_code=404, detail="Model not found in storage")

    preds = model.predict(payload["X"])

    return {"predictions": preds}


@router.delete("/models/{model_name}")
def delete_model(model_name: str):
    from app.storage import delete_model
    try:
        delete_model(model_name)
        logger.info(f"Model {model_name} deleted.")
        return {"status": "deleted", "model": model_name}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Model not found")

