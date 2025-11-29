import pickle
import io
import json
from app.s3 import get_s3_client
from app.config import settings


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


# ДАТАСЕТЫ

def save_dataset(dataset: dict, dataset_name: str = None):
    """Сохраняет датасет в S3 в формате JSON"""
    import io

    if dataset_name is None:
        dataset_name = f"dataset_{len(list_datasets())+1}.json"

    buffer = io.BytesIO()
    buffer.write(json.dumps(dataset).encode())
    buffer.seek(0)

    s3 = get_s3_client()
    s3.put_object(
        Bucket=settings.S3_BUCKET,
        Key=f"datasets/{dataset_name}",
        Body=buffer
    )
    return dataset_name

def remove_dataset(dataset_name: str):
    """Удаляет датасет из S3"""
    key = f"datasets/{dataset_name}"

    s3 = get_s3_client()
    try:
        s3.delete_object(Bucket=settings.S3_BUCKET, Key=key)
    except s3.exceptions.NoSuchKey:
        raise FileNotFoundError(f"Dataset {dataset_name} not found")

def list_datasets():
    """Возвращает список всех датасетов в S3"""
    s3 = get_s3_client()
    response = s3.list_objects_v2(Bucket=settings.S3_BUCKET, Prefix="datasets/")
    items = response.get("Contents", [])
    return [item["Key"].split("/")[-1] for item in items]
