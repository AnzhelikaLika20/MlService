import pickle
import io
import json
from app.s3 import get_s3_client
from app.config import settings
import subprocess
from pathlib import Path
import subprocess

# DVC

BASE = Path("/app")
DATA = BASE / "data"


def dvc_add(file_path: str):
    subprocess.check_call(["dvc", "add", file_path], cwd=BASE)
    subprocess.check_call(["dvc", "push"], cwd=BASE)


def dvc_remove(file_path: str):
    subprocess.check_call(["dvc", "remove", file_path], cwd=BASE)
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


# МОДЕЛИ

def load_model(model_name: str):
    s3 = get_s3_client()

    response = s3.get_object(
        Bucket=settings.S3_BUCKET,
        Key=f"{model_name}.pkl"
    )

    return pickle.loads(response["Body"].read())


def save_model(model, model_name: str):
    """Сохраняет обученную модель в S3"""
    import pickle
    from io import BytesIO

    buffer = BytesIO()
    pickle.dump(model, buffer)
    buffer.seek(0)

    s3 = get_s3_client()
    s3.put_object(
        Bucket=settings.S3_BUCKET,
        Key=f"models/{model_name}.pkl",
        Body=buffer
    )

def delete_model(model_name: str):
    """Удаляет модель из S3"""
    key = f"models/{model_name}.pkl"

    s3 = get_s3_client()
    try:
        s3.delete_object(Bucket=settings.S3_BUCKET, Key=key)
    except s3.exceptions.NoSuchKey:
        raise FileNotFoundError(f"Model {model_name} not found")


def trained_models():
    """Возвращает список всех моделей в S3"""
    s3 = get_s3_client()
    response = s3.list_objects_v2(Bucket=settings.S3_BUCKET, Prefix="models/")
    items = response.get("Contents", [])
    return [item["Key"].split("/")[-1].replace(".pkl", "") for item in items]
