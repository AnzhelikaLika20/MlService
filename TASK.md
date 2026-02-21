# Задание для агента: Реализация дистилляции моделей

## Описание задачи

Необходимо добавить в существующий ML сервис функциональность дистилляции моделей. Дистилляция позволяет сжимать большие модели в маленькие с минимальной потерей качества.

### Этап 1: Создание структуры для дистилляции

Создай новые файлы:
service/app/ml/distillation.py # Логика дистилляции
service/app/api/distillation.py # API эндпоинты

Измени файлы:
service/app/main.py # Подключить новый роутер
service/app/ml/registry.py # Добавить сохранение дистиллированных моделей
service/app/storage.py # Добавить работу с артефактами дистилляции
dashboard/dashboard.py # Добавить вкладку дистилляции


### Этап 2: Классы и структуры данных

В `distillation.py` создать:

1. **DistillationConfig** - dataclass с параметрами:
   - temperature (float): температура для soft targets
   - alpha (float): вес между soft и hard loss
   - epochs (int): количество эпох
   - learning_rate (float): скорость обучения
   - batch_size (int): размер батча
   - validation_split (float): доля валидации

2. **DistillationMetrics** - dataclass для хранения метрик:
   - teacher_metrics: метрики учителя
   - student_metrics: метрики студента
   - distillation_loss: история лосса
   - accuracy_preserved: сохраненная точность
   - size_reduction: коэффициент сжатия
   - speedup: ускорение инференса

3. **DistillationResult** - dataclass с результатами:
   - distillation_id: уникальный ID
   - teacher_model_id: ID модели-учителя
   - student_model_id: ID модели-студента
   - config: использованная конфигурация
   - metrics: метрики дистилляции
   - status: статус процесса

4. **DistillationManager** - класс для управления:
   - `start_distillation()`: запуск процесса
   - `get_result()`: получение результатов
   - `list_distillations()`: список дистилляций

### Этап 3: API эндпоинты

В `distillation.py` (api) создать:

1. **POST /models/distill/start**
   - Принимает: teacher_model_id, student_model_type, dataset_name, config
   - Возвращает: distillation_id, status

2. **GET /models/distill/{distillation_id}**
   - Возвращает: полные результаты дистилляции

3. **GET /models/distill/list**
   - Возвращает: список дистилляций с пагинацией

4. **DELETE /models/distill/{distillation_id}**
   - Удаляет результаты дистилляции

### Этап 4: Интеграция с ClearML

Каждая дистилляция должна быть отдельным экспериментом:

- **Параметры**: сохранять конфигурацию
- **Метрики**: логировать loss графики
- **Артефакты**: сохранять графики сравнения
- **Модели**: сохранять студента как новую модель
- **Теги**: помечать дистиллированные модели

### Этап 5: Документация

Обновить:
	service/app/api/distillation.py # API эндпоинты
	service/app/ml/distillation.py # Логика дистилляции
	dashboard/dashboard.py # Добавить вкладку дистилляции





## Критерии качества

### Код должен:
- Следовать PEP 8
- Иметь type hints
- Иметь docstrings
- Проходить линтеры (flake8, mypy)
- Иметь тесты с покрытием > 70%

### Функциональность должна:
- Позволять запускать дистилляцию через API
- Сохранять результаты в ClearML
- Отображать результаты в дашборде
- Корректно обрабатывать ошибки

## Примеры использования

### Пример 1: Запуск через API
