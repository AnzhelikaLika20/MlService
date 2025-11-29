import os
import numpy as np
from fastapi import APIRouter, HTTPException
from app.ml.registry import list_models, get_model


router = APIRouter()

MODELS_DIR = "saved_models"
os.makedirs(MODELS_DIR, exist_ok=True)


@router.get("/classes")
def get_model_classes():
    return {"classes": list_models()}


@router.post("/{model_name}/train")
def train_model(model_name: str, payload: dict):
    if "X" not in payload or "y" not in payload:
        raise HTTPException(status_code=400, detail="Need X and y")

    model = get_model(model_name)

    model.train(payload["X"], payload["y"], **payload.get("params", {}))

    path = f"{MODELS_DIR}/{model_name}.pkl"
    model.save(path)

    return {"status": "trained", "path": path}


@router.post("/{model_name}/predict")
def predict(model_name: str, payload: dict):
    path = f"{MODELS_DIR}/{model_name}.pkl"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Model not trained")

    model = get_model(model_name)
    model.load(path)

    preds = model.predict(payload["X"])
    return {"predictions": preds}
