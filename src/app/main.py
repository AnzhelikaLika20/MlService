# Подключить новый роутер
from fastapi import FastAPI
from .distillation import router as distillation_router

app = FastAPI()
app.include_router(distillation_router)