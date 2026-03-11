"""
src/db.py

Модуль реализует абстракцию для работы с векторными базами данных.

Функциональность:
- определяет интерфейс VectorDBInterface для взаимодействия с векторной БД;
- предоставляет адаптер ChromaAdapter для работы с ChromaDB;
- содержит фабрику get_vector_db для получения экземпляра БД по настройкам.

Используемые компоненты:
- VectorDBInterface: протокол, задающий контракт для работы с векторной БД;
- ChromaAdapter: реализация интерфейса для ChromaDB;
- get_vector_db: функция‑фабрика для инициализации БД.
"""

from typing import Any, Mapping, Protocol, List

import chromadb
from chromadb.api import ClientAPI
from chromadb.api.types import EmbeddingFunction
from chromadb.utils.embedding_functions import (
    SentenceTransformerEmbeddingFunction
)

from src.settings import settings
from src.logger import db_logger


class VectorDBInterface(Protocol):
    """
    Протокол, определяющий базовый интерфейс для работы с векторной БД.

    Методы:
        client: свойство, возвращающее клиентское соединение с БД.
        create_collection: метод для создания/получения коллекции.
    """

    @property
    def client(self):
        """Клиентское соединение с векторной БД."""
        raise NotImplementedError

    def get_or_create_collection(self):
        """Создание или получение коллекции в векторной БД."""
        raise NotImplementedError

    def add_records(self, ids: Any, documents: Any, metadatas: Any):
        raise NotImplementedError


class ChromaAdapter(VectorDBInterface):
    """
    Адаптер для работы с ChromaDB.

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

    @property
    def client(self) -> ClientAPI:
        """
        Возвращает клиентское соединение с ChromaDB.

        Логирует действие на уровне DEBUG.
        """
        return self._client

    def get_or_create_collection(self) -> chromadb.Collection:
        """
        Создаёт или получает коллекцию в ChromaDB.

        Использует модель эмбеддингов из настроек приложения.
        Логирует результат на уровне INFO.

        Returns:
            chromadb.Collection: экземпляр коллекции ChromaDB.
        """
        emb_func: EmbeddingFunction = SentenceTransformerEmbeddingFunction(
            model_name=settings.EMBEDDING_MODEL
        )
        collection = self.client.get_or_create_collection(
            name=settings.COLLECTION_NAME,
            embedding_function=emb_func
        )
        db_logger.info("Коллекция создана")
        return collection

    def add_records(
            self,
            ids: List[str],
            documents: List[str] | None,
            metadatas: List[Mapping[str, Any]]
    ):
        collection = self.get_or_create_collection()
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        return {'message': f'Добавлено {len(ids)} записей.'}


def get_vector_db() -> VectorDBInterface:
    """
    Фабрика для получения экземпляра векторной БД по настройкам приложения.

    На основе значения settings.VECTOR_DB возвращает соответствующий адаптер.
    В текущей реализации поддерживает только ChromaDB.

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


vector_db = get_vector_db()
