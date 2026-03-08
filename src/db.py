from typing import Protocol

import chromadb

from src.settings import settings
from src.logger import db_logger


class VectorDBInterface(Protocol):
    def client(self):
        raise NotImplementedError


class ChromaAdapter(VectorDBInterface):
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def client(self):
        db_logger.debug("Создан клиент 'chromadb.Client'")
        return chromadb.Client()


def get_vector_db() -> VectorDBInterface:
    db: str = settings.VECTOR_DB
    if db == 'chroma':
        db_logger.debug(f"В приложении используется БД: {db}")
        return ChromaAdapter(
            host=settings.VECTOR_DB_HOST,
            port=settings.VECTOR_DB_PORT
        )
    else:
        db_logger.error(f"Неизвестная БД: {db}")
        raise ValueError(f"Неизвестная БД: {db}")
