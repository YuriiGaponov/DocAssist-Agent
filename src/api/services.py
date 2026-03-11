import re
from typing import Dict, List, Protocol

from fastapi import UploadFile

from src.db import get_vector_db
from src.settings import settings
from src.rag.services import generate_content_id, get_file_metadata
from src.api.api_validators import upload_txt_validator


class UploadProcessingService(Protocol):
    async def upload_db(self) -> Dict[str, str | None]:
        pass


class TxtUploadProcessingService(UploadProcessingService):
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

    async def upload_db(self) -> Dict[str, str | None]:
        upload_txt_validator(self.file)
        file_metadata = get_file_metadata(self.file)
        documents = await self.chunked()
        ids = [
            generate_content_id(chunk, settings.ID_LENGTH)
            for chunk in documents
        ]
        metadatas = [file_metadata] * len(ids)

        vector_db = get_vector_db()
        vector_db.add_records(ids, documents, metadatas)

        return {'message': f'Добавлено {len(ids)} записей.'}
