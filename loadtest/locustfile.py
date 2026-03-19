"""
Locust-нагрузка на ML Service API.

Запуск (из каталога loadtest):
  pip install -r requirements-loadtest.txt
  locust --host=http://127.0.0.1:8000

Переменные окружения:
  LOCUST_INCLUDE_PREDICT=1|0   — вызывать POST predict (по умолчанию 1)
  LOCUST_PREDICT_MODEL=linear   — имя модели для predict
  LOCUST_INCLUDE_CLEARML=1|0   — GET /models/trained-models (нужен ClearML)
  LOCUST_INCLUDE_DATASETS=1|0   — GET /datasets/ (DVC, по умолчанию 1)
"""

from __future__ import annotations

import os

from locust import HttpUser, between, task

INCLUDE_PREDICT = os.environ.get("LOCUST_INCLUDE_PREDICT", "1") == "1"
INCLUDE_CLEARML = os.environ.get("LOCUST_INCLUDE_CLEARML", "0") == "1"
INCLUDE_DATASETS = os.environ.get("LOCUST_INCLUDE_DATASETS", "1") == "1"
PREDICT_MODEL = os.environ.get("LOCUST_PREDICT_MODEL", "linear")


class MLServiceUser(HttpUser):
    """Виртуальный пользователь: смесь read-only и (опционально) predict."""

    wait_time = between(0.3, 1.5)

    @task(40)
    def health(self) -> None:
        """Проверка живости и типичный «лёгкий» GET."""
        with self.client.get("/health", catch_response=True, name="GET /health") as r:
            if r.status_code != 200:
                r.failure(f"status {r.status_code}")

    @task(25)
    def metrics(self) -> None:
        """Имитация частого скрейпа Prometheus/VictoriaMetrics (тяжелее по объёму ответа)."""
        with self.client.get("/metrics", catch_response=True, name="GET /metrics") as r:
            if r.status_code != 200:
                r.failure(f"status {r.status_code}")

    @task(25)
    def supported_models(self) -> None:
        """Справочник типов моделей без ClearML."""
        with self.client.get(
            "/models/supported-models",
            catch_response=True,
            name="GET /models/supported-models",
        ) as r:
            if r.status_code != 200:
                r.failure(f"status {r.status_code}")

    @task(6)
    def datasets_list(self) -> None:
        """Список датасетов через DVC; может быть медленным и давать 5xx при проблемах с данными."""
        if not INCLUDE_DATASETS:
            return
        with self.client.get("/datasets/", catch_response=True, name="GET /datasets/") as r:
            if r.status_code >= 400:
                r.failure(f"status {r.status_code}")

    @task(3)
    def trained_models(self) -> None:
        """Список моделей в ClearML; без доступного apiserver даст ошибки — отключено по умолчанию."""
        if not INCLUDE_CLEARML:
            return
        with self.client.get(
            "/models/trained-models",
            catch_response=True,
            name="GET /models/trained-models",
        ) as r:
            if r.status_code != 200:
                r.failure(f"status {r.status_code}")

    @task(6)
    def predict(self) -> None:
        """Инференс: основная CPU-нагрузка и метрика ml_inference_duration_seconds."""
        if not INCLUDE_PREDICT:
            return
        payload = {"X": [[1.0, 2.0], [3.0, 4.0], [0.5, 1.5]]}
        path = f"/models/{PREDICT_MODEL}/predict"
        with self.client.post(
            path,
            json=payload,
            catch_response=True,
            name="POST /models/{model}/predict",
        ) as r:
            if r.status_code == 404:
                r.failure("model not found (train/deploy model or set LOCUST_PREDICT_MODEL)")
            elif r.status_code != 200:
                r.failure(f"status {r.status_code}")
