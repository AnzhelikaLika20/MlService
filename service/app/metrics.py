"""
Prometheus metrics for ML service.

- RPS by endpoint (request counter)
- Request latency p50/p95/p99 (histogram)
- Error rate (4xx, 5xx)
- Model inference time p50/p95 (histogram)
"""

import time
from typing import Callable

from prometheus_client import Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_class"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

ML_INFERENCE_DURATION_SECONDS = Histogram(
    "ml_inference_duration_seconds",
    "Model inference latency in seconds",
    ["model_name"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5),
)


def _status_class(status_code: int) -> str:
    """Return status class for grouping: 2xx, 4xx, 5xx."""
    if status_code < 300:
        return "2xx"
    if status_code < 500:
        return "4xx"
    return "5xx"


def _get_path_template(request: Request) -> str:
    """Return route path template to avoid high cardinality (e.g. /models/{model_name}/predict)."""
    route = request.scope.get("route")
    if route and hasattr(route, "path"):
        return route.path
    return request.url.path


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware that records request count, status class and latency for Prometheus."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path == "/metrics":
            return await call_next(request)

        method = request.method
        path = _get_path_template(request)
        start = time.perf_counter()

        response = await call_next(request)
        duration = time.perf_counter() - start

        status_class = _status_class(response.status_code)
        HTTP_REQUESTS_TOTAL.labels(method=method, path=path, status_class=status_class).inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(method=method, path=path).observe(duration)

        return response


def get_metrics_content() -> bytes:
    """Return Prometheus exposition format for /metrics endpoint."""
    return generate_latest()


def record_inference_duration(model_name: str, duration_seconds: float) -> None:
    """Record model inference duration for histogram (p50/p95)."""
    ML_INFERENCE_DURATION_SECONDS.labels(model_name=model_name).observe(duration_seconds)
