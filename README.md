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

Swagger доступен по `http://130.193.59.50:8000/docs`

## Работа с моделями

1. Обучение c сохранением в minio

``` bash
curl -X POST http://localhost:8000/models/linear/train -H "Content-Type: application/json" -d '{"X": [[1], [2]], "y": [2, 4]}'
```
Результат `{"status":"trained","stored_as":"linear.pkl"}`

2. Предсказания моделью из minio

```bash
curl -X POST http://localhost:8000/models/linear/predict 
-H "Content-Type: application/json" 
-d '{"X": [[3], [4]]}'
```

Результат `{"predictions":[7.999999999999999,10.0]}`

## Работа с датасетами
1. Создать датасет
``` bash
curl -X POST http://localhost:8000/datasets \
-H "Content-Type: application/json" \
-d '{
    "dataset_name": "my_dataset.json",
    "data": [
        {"X": [1,2], "y": 3},
        {"X": [4,5], "y": 9}
    ]
}'
```