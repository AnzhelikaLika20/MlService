from app.api import datasets, health, models
from app.logger import get_logger
from app.metrics import PrometheusMiddleware, get_metrics_content
from fastapi import FastAPI
from fastapi.responses import Response

logger = get_logger("main")

app = FastAPI(title="ML Manager", version="0.1")
app.add_middleware(PrometheusMiddleware)

app.include_router(health.router)
app.include_router(models.router, prefix="/models", tags=["models"])
app.include_router(datasets.router, prefix="/datasets", tags=["datasets"])


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    """Prometheus scrape endpoint."""
    return Response(
        content=get_metrics_content(),
        media_type="text/plain; charset=utf-8",
    )
