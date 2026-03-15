"""
src/api/services.py

Модуль содержит сервисы для обработки загруженных файлов и взаимодействия
с векторной БД в рамках API.

Основная функциональность:
- валидация и чтение загруженных TXT‑файлов;
- разбивка текста на семантические блоки (чанки);
- загрузка данных в векторную БД.

Ключевые компоненты:
- UploadProcessingService: протокол для сервисов обработки загрузки;
- TxtUploadProcessingService: реализация для TXT‑файлов.
"""

from http import HTTPStatus
import re
from typing import Any, Dict, List, Protocol

from fastapi import HTTPException, UploadFile

from src.api.api_validators import upload_txt_validator
from src.db import VectorDBInterface
from src.logger import app_logger
from src.rag.services import generate_content_id, get_file_metadata
from src.settings import settings


class UploadProcessingService(Protocol):
    """Протокол для сервисов обработки загруженных файлов.

    Определяет контракт метода upload_db для загрузки данных в БД.
    """
    async def upload_db(self) -> Dict[str, Any]:
        ...


class TxtUploadProcessingService(UploadProcessingService):
    """Сервис для обработки текстового содержимого из загруженного TXT‑файла.

    Предоставляет методы для:
    - чтения файла;
    - разбивки текста на семантические блоки;
    - загрузки данных в векторную БД.

    Args:
        file (UploadFile): загруженный файл из FastAPI.
        vector_db (VectorDBInterface): экземпляр векторной БД
    """

    def __init__(
        self,
        file: UploadFile,
        vector_db: VectorDBInterface
    ):
        self.file = file
        self.vector_db = vector_db

    @staticmethod
    async def _get_content(file: UploadFile) -> str:
        """Читает содержимое файла и декодирует его как UTF‑8.

        Args:
            file (UploadFile): загруженный файл.

        Returns:
            str: декодированное содержимое файла.

        Raises:
            ValueError: если файл не является текстовым (ошибка декодирования).
        """
        try:
            contents = await file.read()
            return contents.decode("utf-8")
        except UnicodeDecodeError as e:
            raise ValueError(f"Файл не является текстовым (UTF-8): {e}")

    @staticmethod
    def _split_by_blocks(text: str) -> List[str]:
        """Разбивает текст на семантические блоки (абзацы, заголовки, списки).

        Использует перевод строки как разделитель, удаляет пустые блоки
        и фильтрует по минимальной длине (CHUNK_MIN_LENGTH).

        Args:
            text (str): исходный текст.

        Returns:
            List[str]: список непустых блоков текста после разбивки.
        """
        return [
            block.strip()
            for block in re.split(r'\n', text.replace('\r', ''))
            if len(block.strip()) >= settings.CHUNK_MIN_LENGTH
        ]

    async def chunked(self) -> List[str]:
        """Читает содержимое файла и разбивает его на семантические блоки.

        Returns:
            List[str]: список чанков (блоков текста).
        """
        return self._split_by_blocks(await self._get_content(self.file))

    async def upload_db(self) -> Dict[str, Any]:
        """Загружает данные из файла в векторную БД.

        Выполняет:
        - валидацию файла;
        - чтение и разбивку на чанки;
        - генерацию ID для чанков;
        - сбор метаданных;
        - добавление записей в БД.

        Логирует этапы выполнения и обрабатывает ошибки.

        Returns:
            Dict[str, Any]: словарь с результатом операции:
                {
                    'message': f'Добавлено {len(ids)} записей.',
                    'success': True
                }

        Raises:
            HTTPException: с кодом 400 при валидационных ошибках
                или отсутствии чанков.
            HTTPException: с кодом 500 при ошибках загрузки в БД.
        """
        app_logger.info(f"Начало обработки файла: {self.file.filename}")
        try:
            upload_txt_validator(self.file)
            documents = await self.chunked()

            if not documents:
                raise ValueError("Не найдено валидных текстовых блоков")

            ids = [
                generate_content_id(chunk)
                for chunk in documents
            ]
            metadatas = [get_file_metadata(self.file) for _ in documents]

            self.vector_db.add_records(ids, documents, metadatas)
            app_logger.info(
                f"Добавление данных из файла: {self.file.filename} завершено"
            )
            return {
                'message': f'Добавлено {len(ids)} записей.',
                'success': True
            }
        except ValueError as e:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail=str(e)
            )
        except Exception as e:
            app_logger.error(f"Ошибка загрузки в БД: {e}")
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail="Ошибка сохранения в векторную БД"
            )
