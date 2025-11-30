import os
import subprocess
from pathlib import Path

import joblib
from clearml import Model, OutputModel

MODEL_LOCAL_PATH = "./models"
os.makedirs(MODEL_LOCAL_PATH, exist_ok=True)

CACHE_DIR = "saved_models/cache"
TASK_ID_FILE = os.path.join(CACHE_DIR, "task_id.json")
os.makedirs(CACHE_DIR, exist_ok=True)
DVC_DATASETS_DIR = "data"

# DVC

BASE = Path("/app")
DATA = BASE / "data"


def dvc_add(file_path: str):
    subprocess.check_call(["dvc", "add", file_path], cwd=BASE)
    subprocess.check_call(["dvc", "push"], cwd=BASE)


def dvc_remove(file_path: str):
    subprocess.check_call(["dvc", "remove", "--outs", file_path + ".dvc"], cwd=BASE)
    subprocess.check_call(["dvc", "push"], cwd=BASE)


def dvc_list(path=".", recursive=False):
    """
    Возвращает список файлов и папок, отслеживаемых DVC.

    Args:
        path (str): путь в репозитории DVC
        recursive (bool): если True, будет рекурсивно проходить папки
    """
    cmd = ["dvc", "list", ".", path]
    if recursive:
        cmd.append("-R")
    result = subprocess.check_output(cmd, cwd=BASE)
    lines = [line.strip() for line in result.decode().splitlines()]

    files = [f for f in lines if not f.endswith(".dvc")]
    return files


def dvc_restore_file(filename: str) -> str:
    """
    Скачивает (dvc pull) файл filename из DVC, если надо.
    Возвращает абсолютный путь к файлу **если он существует после dvc pull**,
    иначе кидает исключение.
    """
    safe_fn = os.path.basename(filename)
    abs_path = os.path.join(DVC_DATASETS_DIR, safe_fn)
    if not os.path.exists(abs_path):
        subprocess.run(
            ["dvc", "pull", abs_path], check=True, capture_output=True, text=True
        )
    return abs_path


# МОДЕЛИ


def save_model_clearml(model, model_name, clearml_task):
    path = os.path.join(MODEL_LOCAL_PATH, f"{model_name}.pkl")
    joblib.dump(model, path)
    output_model = OutputModel(task=clearml_task, name=model_name)
    output_model.update_weights(path)
    output_model.publish()
    return output_model


def load_model_from_clearml(model_name: str):
    local_path = os.path.join(MODEL_LOCAL_PATH, f"{model_name}.pkl")

    model_list = Model.query_models(
        model_name=model_name,
        only_published=True,
    )
    if not model_list:
        raise FileNotFoundError(f"No model artifact found for {model_name} in ClearML")
    model_entry = sorted(
        model_list, key=lambda m: getattr(m, "last_update", ""), reverse=True
    )[0]
    fp = model_entry.get_local_copy()
    os.replace(fp, local_path)

    return joblib.load(local_path)


def delete_model_from_clearml(model_name: str):
    """Удаляет модель из S3"""
    model_list = Model.query_models(
        model_name=model_name,
        only_published=True,
    )
    if not model_list:
        raise FileNotFoundError(f"No model artifact found for {model_name} in ClearML")
    model_entry = sorted(
        model_list, key=lambda m: getattr(m, "last_update", ""), reverse=True
    )[0]

    Model.remove(model_entry)
