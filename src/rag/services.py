"""
src/rag/services.py

Модуль содержит сервисные функции для работы с RAG‑системой:
- генерация уникальных ID на основе хеша содержимого;
- сбор метаданных загруженных файлов.

Функции:
- generate_content_id: создаёт ID через хеширование строки (SHA‑256).
- get_file_metadata: извлекает метаданные из объекта UploadFile.
"""

import hashlib
from datetime import datetime

from fastapi import UploadFile

from src.logger import app_logger
from src.types import Metadata


def generate_content_id(content: str) -> str:
    """Создаёт ID на основе хеша содержимого (SHA‑256).

    Args:
        content (str): текст или данные для хеширования.

    Returns:
        str: шестнадцатеричное представление хеша SHA‑256.

    Raises:
        ValueError: если content пуст или состоит
            только из пробелов.
    """
    if not content.strip():
        raise ValueError("content не может быть пустым")

    hash_obj = hashlib.sha256(content.encode('utf-8'))
    return hash_obj.hexdigest()


def get_file_metadata(file: UploadFile) -> Metadata:
    """Извлекает метаданные загруженного файла.

    Собирает информацию о файле: имя, MIME‑тип,
    размер и время загрузки. При ошибке возвращает
    словарь с None для всех полей.

    Args:
        file (UploadFile): объект загруженного
            файла из FastAPI.

    Returns:
        Metadata: типизированный словарь с полями:
        - filename: имя файла (str | None);
        - content_type: MIME‑тип (str | None);
        - size: размер в байтах (int | None);
        - uploaded_at: ISO‑форматированная строка
          времени загрузки (str | None).
    """
    try:
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": file.size,
            "uploaded_at": datetime.now().isoformat(),
        }
    except Exception as e:
        app_logger.error(
            "Ошибка при сборе метаданных файла: %s", e
        )
        return {
            "filename": None,
            "content_type": None,
            "size": None,
            "uploaded_at": None,
        }
