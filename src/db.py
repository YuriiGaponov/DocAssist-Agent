"""
src/db.py

Модуль реализует абстракцию для работы с векторными базами данных.

Функциональность:
- определяет интерфейс VectorDBInterface для взаимодействия
  с векторной БД;
- предоставляет адаптер ChromaAdapter для работы с ChromaDB;
- содержит фабрику get_vector_db для получения экземпляра БД
  по настройкам.

Используемые компоненты:
- VectorDBInterface: протокол, задающий контракт для работы
  с векторной БД;
- ChromaAdapter: реализация интерфейса для ChromaDB;
- get_vector_db: функция‑фабрика для инициализации БД.
"""

from typing import Any, Dict, Protocol, List

import chromadb
from chromadb.api import ClientAPI
from chromadb.api.types import EmbeddingFunction
from chromadb.utils.embedding_functions import (
    SentenceTransformerEmbeddingFunction
)

from src.settings import settings
from src.types import Metadata
from src.logger import db_logger


class VectorDBInterface(Protocol):
    """Базовый интерфейс для работы с векторной БД.

    Свойства:
        client: клиентское соединение с БД.

    Методы:
        get_or_create_collection: создание или получение коллекции.
        add_records: добавление записей в коллекцию.
    """

    @property
    def client(self) -> ClientAPI:
        """Возвращает клиентское соединение с векторной БД."""
        raise NotImplementedError

    def get_or_create_collection(self) -> chromadb.Collection:
        """Создаёт или получает коллекцию в векторной БД.

        Returns:
            chromadb.Collection: экземпляр коллекции.
        """
        raise NotImplementedError

    def add_records(
        self,
        ids: List[str],
        documents: List[str] | None,
        metadatas: Metadata | List[Metadata] | None
    ) -> Dict[str, Any]:
        """Добавляет записи в коллекцию.

        Args:
            ids (List[str]): список идентификаторов записей.
            documents (List[str] | None): список текстов документов.
            metadatas (Metadata | List[Metadata] | None):
                список метаданных или одиночный объект метаданных.

        Returns:
            Dict[str, Any]: словарь с результатами операции:
                - 'message': описание результата;
                - 'success': флаг успеха (True/False);
                - 'error': текст ошибки (если есть).
        """
        raise NotImplementedError


class ChromaAdapter(VectorDBInterface):
    """Адаптер для работы с ChromaDB.

    Args:
        host (str): хост сервера ChromaDB.
        port (int): порт сервера ChromaDB.
    """

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self._client = chromadb.PersistentClient(
            path=settings.VECTOR_DB_DIR
        )
        db_logger.debug("Создан клиент 'chromadb.Client'")
        self._collection: chromadb.Collection | None = None
        self._embedding_function: EmbeddingFunction | None = None

    @property
    def client(self) -> ClientAPI:
        """Возвращает клиентское соединение с ChromaDB.

        Логирует действие на уровне DEBUG.
        """
        return self._client

    @property
    def embedding_function(self) -> EmbeddingFunction:
        if self._embedding_function is None:
            self._embedding_function = SentenceTransformerEmbeddingFunction(
                model_name=settings.EMBEDDING_MODEL
            )
        return self._embedding_function

    def get_or_create_collection(self) -> chromadb.Collection:
        """Создаёт или получает коллекцию в ChromaDB.

        Использует модель эмбеддингов из настроек приложения.
        Логирует результат на уровне INFO.

        Returns:
            chromadb.Collection: экземпляр коллекции ChromaDB.
        """
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=settings.COLLECTION_NAME,
                embedding_function=self.embedding_function
            )
            db_logger.info("Коллекция создана")
        return self._collection

    def add_records(
        self,
        ids: List[str],
        documents: List[str] | None,
        metadatas: Metadata | List[Metadata] | None
    ) -> Dict[str, Any]:
        """Добавляет записи в коллекцию ChromaDB.

        Args:
            ids (List[str]): список идентификаторов записей.
            documents (List[str] | None): список текстов документов.
            metadatas (Metadata | List[Metadata] | None):
                список метаданных или одиночный объект метаданных.

        Returns:
            Dict[str, Any]: словарь с результатами операции:
                - 'message': описание результата;
                - 'success': флаг успеха (True/False);
                - 'error': текст ошибки (если есть).

        Raises:
            Exception: при ошибке добавления записей в БД (логируется).
        """
        try:
            collection = self.get_or_create_collection()
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            db_logger.info(f'Добавлено {len(ids)} записей.')
            return {
                'message': f'Добавлено {len(ids)} записей.',
                'success': True
            }
        except Exception as e:
            db_logger.error(f"Ошибка при добавлении записей в ChromaDB: {e}")
            return {
                'message': 'Ошибка при добавлении записей',
                'success': False,
                'error': str(e)
            }


def get_vector_db() -> VectorDBInterface:
    """Возвращает экземпляр векторной БД по настройкам приложения.

    На основе значения settings.VECTOR_DB возвращает соответствующий
    адаптер. В текущей реализации поддерживает только ChromaDB.

    Returns:
        VectorDBInterface: экземпляр адаптера для работы с векторной БД.

    Raises:
        ValueError: если указанный тип БД не поддерживается.
    """
    db: str = settings.VECTOR_DB
    if db == 'chroma':
        db_logger.info(f"В приложении используется БД: {db}")
        return ChromaAdapter(
            host=settings.VECTOR_DB_HOST,
            port=settings.VECTOR_DB_PORT
        )
    else:
        db_logger.error(f"Неизвестная БД: {db}")
        raise ValueError(f"Неизвестная БД: {db}")


# Экземпляр векторной БД, доступный для импорта в других модулях
vector_db = get_vector_db()
