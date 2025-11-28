from fastapi import FastAPI
from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)
app = FastAPI(title="ML Manager", version="0.1.0")

@app.get("/health", tags=["system"])
def health():
    logger.info("Health check")
    return {"status": "ok", "env": settings.ENV}
