"""
src/api/routes.py

Модуль определяет HTTP‑эндпоинты API для DocAssist‑Agent.

Функциональность:
- базовый маршрут для проверки запуска приложения (/);
- эндпоинт для загрузки TXT‑файлов (/upload-txt).

Использует APIRouter из FastAPI для модульной организации маршрутов.

Экземпляр router:
- позволяет группировать маршруты;
- подключается к основному приложению FastAPI.
"""

from typing import Any, Dict

from fastapi import APIRouter, Request, UploadFile
from src.api.services import TxtUploadProcessingService


router = APIRouter()
"""Экземпляр APIRouter для регистрации эндпоинтов.

Позволяет:
- группировать маршруты;
- подключать их к основному приложению.
"""


@router.get("/")
def root_endpoint(request: Request) -> dict:
    """Обработчик GET‑запроса к корневому пути /.

    Используется для быстрой проверки, что приложение запущено
    и принимает запросы.

    Args:
        request (Request): объект запроса FastAPI.

    Returns:
        dict: словарь с сообщением о статусе приложения:
            {
                "message": "Приложение запущено"
            }
    """
    return {"message": "Приложение запущено"}


@router.post("/upload-txt")
async def upload_txt(file: UploadFile) -> Dict[str, Any]:
    """Обработчик POST‑запроса для загрузки TXT‑файла.

    Принимает загруженный файл, создаёт сервис обработки
    и инициирует загрузку данных в векторную БД.

    Args:
        file (UploadFile): загруженный файл из запроса.

    Returns:
        Dict[str, Any]: результат операции загрузки, возвращаемый
            методом TxtUploadProcessingService.upload_db. Обычно содержит:
            - 'message': текстовое описание результата;
            - 'success': флаг успеха (True/False).

    Raises:
        HTTPException: может быть поднята в случае ошибок валидации
            или при сохранении в БД (обрабатывается на уровне сервиса).

    Example:
        Успешный ответ:
            {
                "message": "Добавлено 5 записей.",
                "success": True
            }
        Ошибка:
            HTTPException с кодом 400 или 500.
    """
    service = TxtUploadProcessingService(file)
    return await service.upload_db()
