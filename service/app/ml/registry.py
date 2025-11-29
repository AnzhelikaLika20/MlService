from app.ml.linear_model import LinearModel
from app.ml.tree_model import TreeModel

MODEL_REGISTRY = {
    LinearModel.name: LinearModel,
    TreeModel.name: TreeModel,
}

def list_models():
    return list(MODEL_REGISTRY.keys())

def get_model(name: str):
    if name not in MODEL_REGISTRY:
        raise ValueError("Unknown model")
    return MODEL_REGISTRY[name]()
