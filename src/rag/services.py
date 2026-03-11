import hashlib
from typing import Dict
from datetime import datetime

from fastapi import UploadFile


def generate_content_id(content: str, length: int = 12) -> str:
    """
    Создаёт ID на основе хеша содержимого.

    Args:
        content (str): Текст или данные для хеширования.
        length (int): Длина результирующего ID.

    Returns:
        Dict[str, str]: Словарь, где:
            - ключ — сгенерированный ID (обрезанный хеш SHA‑256),
            - значение — исходный контент (параметр `content`).
    """
    hash_obj = hashlib.sha256(content.encode('utf-8'))
    hex_dig = hash_obj.hexdigest()
    return hex_dig[:length]


def get_file_metadata(
        file: UploadFile
) -> Dict[str, str | None]:
    return {
        "filename": file.filename,
        "uploaded_at": datetime.now().isoformat(),
    }
