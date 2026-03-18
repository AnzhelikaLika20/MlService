# Agent Rules for ML Service Development

## Project Context
- FastAPI сервис для управления ML моделями
- Две базовые модели: Linear и Tree
- Интеграция с ClearML для экспериментального трекинга
- Streamlit дашборд для UI
- Деплой в Minikube

## Development Rules

### 1. Code Style
- Используй type hints для всех функций
- Докстринги на русском или английском (docstrings)
- Имена переменных и функций на английском
- Следуй PEP 8

### 2. Project Structure
service/app/
├── api/ # Роуты FastAPI
├── ml/ # ML модели и логика
├── scripts/ # Утилиты
└── storage.py # Работа с хранилищами


### 3. Feature Implementation Process
1. Сначала создай план в `PLAN.md`
2. Реализуй backend изменения
3. Обнови API документацию
4. Добавь тесты
5. Запусти линтеры: `flake8`, `mypy`
6. Обнови CHANGELOG.md
7. Обнови дашборд

### 4. Commit Messages

feat: add A/B testing endpoint
fix: correct model loading in comparison
docs: update API.md with A/B testing
test: add tests for model comparison
chore: update dependencies


### 5. Testing Rules
- Все новые эндпоинты должны иметь тесты
- Используй pytest
- Минимальное покрытие: 70%

### 6. API Design
- RESTful принципы
- Версионирование через URL (/api/v1/...)
- JSON для запросов/ответов
- Правильные HTTP статусы

### 7. ClearML Integration
- Каждое A/B тестирование = отдельный эксперимент
- Метрики сохранять как artifacts
- Использовать теги для группировки

### 8. Dashboard Updates
- Добавлять новые вкладки в навигацию
- Использовать st.cache для загрузки данных
- Обрабатывать ошибки API