from fastapi import FastAPI
from app.logger import get_logger
from app.api import health, models, datasets

logger = get_logger("main")

app = FastAPI(title="ML Manager", version="0.1")

app.include_router(health.router)
app.include_router(models.router, prefix="/models", tags=["models"])
app.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
app.include_router(datasets.router, prefix="/classes", tags=["classes"])
