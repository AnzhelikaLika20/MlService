# ML Manager — проект

## Быстрый старт
1. Скопировать `.env.example` -> `.env` и заполнить переменные.

2. Перейти в корень проекта
```bash
cd ~/MlService
```
3. Полностью удалить старые контейнеры и образы
```bash
make clean
```
4. Пересобрать образы
```bash
make build
```
5. Поднять сервисы в фоне
```bash
make up
```
**Или одной командой**

```bash
make rebuild
```

Протестировать работоспособность можно по запросом по `curl http://0.0.0.0:8000/health`

## Работа с моделями

1. Обучение

``` bash
curl -X POST http://localhost:8000/models/linear/train \
 -H "Content-Type: application/json" \
 -d '{"X":[[1],[2],[3]], "y":[2,4,6]}'
```
Результат `{"status":"trained","path":"saved_models/linear.pkl"}`

2. Предсказания

```bash
curl -X POST http://localhost:8000/models/linear/predict \
 -H "Content-Type: application/json" \
 -d '{"X":[[4],[5]]}'
```

Результат `{"predictions":[7.999999999999999,10.0]}`