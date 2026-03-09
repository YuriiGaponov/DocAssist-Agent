import hashlib
import re
from typing import Dict, List
from fastapi import UploadFile


class TxtProcessor:
    """
    Класс для обработки текстового содержимого из загруженного файла.
    Предоставляет методы для чтения, разбивки на блоки и чанкирования текста.
    """

    def __init__(self, file: UploadFile):
        self.file = file

    @staticmethod
    async def _get_content(file: UploadFile) -> str:
        """
        Асинхронное чтение байтов из файла и декодирование в строку (UTF‑8).

        Args:
            file (UploadFile): Загруженный файл.

        Returns:
            str: Декодированное текстовое содержимое файла.
        """
        contents = await file.read()
        text = contents.decode("utf-8")
        return text

    @staticmethod
    def _split_by_blocks(text: str) -> List[str]:
        """
        Разбивает текст на семантические блоки (абзацы, заголовки, списки).

        Args:
            text (str): Исходный текст.

        Returns:
            List[str]: Список непустых блоков текста после разбивки.
        """

        return [
            block.strip()
            for block in re.split(r'\n', text.replace('\r', ''))
            if block.strip()
        ]

    async def chunked(self) -> List[str]:
        """
        Читает содержимое файла и разбивает его на чанки (семантические блоки).

        Args:
            file (UploadFile): Загруженный файл.

        Returns:
            List[str]: Список чанков (блоков текста).
        """

        return self._split_by_blocks(await self._get_content(self.file))


def generate_content_id(content: str, length: int = 12) -> Dict[str, str]:
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
    return {hex_dig[:length]: content}
