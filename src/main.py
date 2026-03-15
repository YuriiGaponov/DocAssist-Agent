"""
DocAssist‑Agent — AI‑агент для обработки запросов к внутренней документации.

Модуль реализует FastAPI‑приложение, которое:
- принимает HTTP‑запросы (POST /ask, GET /health);
- валидирует входные данные;
- определяет тип запроса;
- взаимодействует с RAG‑модулем и state‑менеджером;
- формирует и возвращает JSON‑ответ;
- логирует действия и ошибки.

Основные эндпоинты:
- POST /ask: обработка запроса (поля user_id, query);
- GET /health: проверка работоспособности.

Требования: Python 3.10+, зависимости из requirements.txt, папка docs/.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from src.logger import app_logger
from src.api.routes import router
from src.db import get_vector_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Менеджер жизненного цикла FastAPI‑приложения.

    При запуске:
    - инициализирует векторную БД (создаёт коллекцию, если её нет);
    - логирует успех или ошибку.

    При завершении:
    - логирует остановку приложения.

    Args:
        app: экземпляр FastAPI.

    Yields:
        None

    Raises:
        Exception: если инициализация БД завершилась ошибкой.
    """
    try:
        vector_db = get_vector_db()
        vector_db.get_or_create_collection()
        app_logger.info('Коллекция векторов инициализирована.')
        yield
    except Exception as e:
        app_logger.error(f'Ошибка при инициализации БД: {e}')
        raise
    finally:
        app_logger.info('Приложение DocAssist‑Agent остановлено.')


app = FastAPI(lifespan=lifespan)
"""
Экземпляр FastAPI с менеджером жизненного цикла (lifespan).
Включает роутер с эндпоинтами /ask и /health.
"""

app.include_router(router)
app_logger.info('Приложение DocAssist‑Agent запущено.')
