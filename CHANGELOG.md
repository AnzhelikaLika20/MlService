# Changelog

## [Unreleased]

### Added
- Prometheus-метрики в ML Service: счётчик запросов, гистограммы латентности и времени инференса
- Эндпоинт `GET /metrics` для сбора метрик
- Деплой VictoriaMetrics и Grafana (deploy/victoriametrics*.yaml, deploy/grafana*.yaml)
- Дашборд Grafana «ML Service»: RPS по эндпоинтам, latency p50/p95/p99, error rate, inference time p50/p95
