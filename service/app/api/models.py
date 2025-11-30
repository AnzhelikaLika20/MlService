import os

from app.logger import get_logger
from app.ml.registry import get_model, list_models
from app.storage import (
    delete_model_from_clearml,
    load_model_from_clearml,
    save_model_clearml,
)
from clearml import Model, Task
from fastapi import APIRouter, HTTPException

router = APIRouter()
logger = get_logger("models")

MODELS_DIR = "saved_models"
os.makedirs(MODELS_DIR, exist_ok=True)


@router.get("/supported-models")
def get_model_classes():
    return {"models": list_models()}


@router.get("/trained-models")
def get_all_models():
    """
    Возвращает список всех обученных моделей в ClearML,
    включая имя, id, проект и дату обновления.
    """
    models = Model.query_models(only_published=True)
    result = []
    for m in sorted(models, key=lambda m: getattr(m, "last_update", ""), reverse=True):
        result.append(
            {
                "id": m.id,
                "name": m.name,
                "project": m.project,
                "framework": getattr(m, "framework", None),
                "last_update": getattr(m, "last_update", None),
                "tags": getattr(m, "tags", []),
                "uri": getattr(m, "uri", None),
            }
        )
    return {"models": result}


@router.post("/{model_name}/train")
def train_model(model_name: str, payload: dict):
    if "X" not in payload or "y" not in payload:
        raise HTTPException(status_code=400, detail="Need X and y")
    X, y = payload["X"], payload["y"]
    params = payload.get("params", {})

    task = Task.init(
        project_name="ML_Service",
        task_name=f"train_{model_name}",
        task_type=Task.TaskTypes.training,
    )

    model = get_model(model_name)
    model.train(X, y, **params)
    output_model = save_model_clearml(model, model_name, task)
    task.upload_artifact(name=f"{model_name}_model_file", artifact_object=model)
    task.close()

    return {"status": "trained", "model_id": output_model.id, "name": output_model.name}


@router.post("/{model_name}/predict")
def predict(model_name: str, payload: dict):
    if "X" not in payload:
        raise HTTPException(status_code=400, detail="Missing 'X' in request body")
    try:
        model = load_model_from_clearml(model_name)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Model not found: {e}")

    preds = model.predict(payload["X"])
    return {"predictions": preds}


@router.delete("/models/{model_name}")
def delete_model(model_name: str):
    try:
        delete_model_from_clearml(model_name)
        logger.info(f"Model {model_name} deleted.")
        return {"status": "deleted", "model": model_name}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Model not found")
