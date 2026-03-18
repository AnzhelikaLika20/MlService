# Деплой в Minikube

## Последовательность запуска (сервис + дашборд)

### 1. Запустить Minikube и использовать его Docker

```bash
minikube start
eval $(minikube docker-env)
```

### 2. Собрать образ ML Service

```bash
cd ..   # корень репозитория MlService
docker build -t ml-service:latest -f service/Dockerfile service/
```

### 3. Применить манифесты по порядку

```bash
cd deploy
kubectl apply -f pvc.yaml -f minio.yaml -f api.yaml
```

Дождаться, пока поды `ml-service` и MinIO станут Ready (`kubectl get pods`).

```bash
# VictoriaMetrics (сбор метрик с ml-service)
kubectl apply -f victoriametrics-config.yaml -f victoriametrics.yaml

# Grafana: datasource, провайдер дашбордов, сам дашборд, деплой
kubectl apply -f grafana-datasources.yaml -f grafana-dashboards-provider.yaml
kubectl create configmap grafana-ml-service-dashboard --from-file=ml-service.json=grafana-dashboard-ml-service.json -o yaml --dry-run=client | kubectl apply -f -
kubectl apply -f grafana.yaml
```

### 4. Открыть дашборд в браузере

```bash
minikube service grafana --url
```

В открывшейся вкладке: логин **admin**, пароль **admin**.  
В меню: **Dashboards** → **ML Service**.

### 5. (Опционально) Сгенерировать трафик для метрик

Чтобы на дашборде появились графики, нужны запросы к API:

```bash
# URL API (в отдельном терминале)
export API_URL=$(minikube service ml-service --url)

# health
curl "$API_URL/health"

# метрики (то, что скрейпит VictoriaMetrics)
curl "$API_URL/metrics"

# пример predict (если есть обученная модель)
curl -X POST "$API_URL/models/linear/predict" -H "Content-Type: application/json" -d '{"X": [[1,2],[3,4]]}'
```

Повторите запросы или дайте небольшой нагрузочный тест — через 10–30 секунд данные появятся в Grafana.

---

## Доступ к сервисам

| Сервис        | Как открыть                          |
|---------------|--------------------------------------|
| **ML Service API** | `minikube service ml-service --url` (порт 30001) |
| **Grafana**   | `minikube service grafana --url` (порт 30300), логин/пароль **admin** / **admin** |
| **VictoriaMetrics** | только внутри кластера: `victoriametrics:8428` |

## Метрики и дашборд

Сервис отдаёт Prometheus-метрики на `GET /metrics`. VictoriaMetrics скрейпит их каждые 10 с.

В Grafana после деплоя доступен дашборд **ML Service**:
- RPS по эндпоинтам
- Лэтенси p50 / p95 / p99
- Error rate (% 4xx и 5xx)
- Время инференса модели p50 / p95
