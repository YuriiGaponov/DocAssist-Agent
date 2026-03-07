"""
Модуль src/routes.py

Определяет HTTP‑эндпоинты API для DocAssist‑Agent.
Содержит базовый маршрут для проверки запуска приложения.

Использует APIRouter из FastAPI для модульной организации маршрутов.
"""

from fastapi import APIRouter, Request, UploadFile

from src.api_validators import upload_txt_validator
from src.rag import chunked


router = APIRouter()
"""
Экземпляр APIRouter для регистрации эндпоинтов.
Позволяет группировать маршруты и подключать их к основному приложению.
"""


@router.get("/")
def root_endpoint(request: Request) -> dict:
    """
    Обработчик GET‑запроса к корневому пути /.

    Используется для быстрой проверки, что приложение запущено
    и принимает запросы.

    Args:
        request (Request): Объект запроса FastAPI.

    Returns:
        dict: Словарь с сообщением о статусе приложения:
            {
                "message": "Приложение запущено"
            }
    """
    return {"message": "Приложение запущено"}


@router.post("/upload-txt")
async def upload_txt(file: UploadFile) -> list:

    upload_txt_validator(file)
    return await chunked(file)
