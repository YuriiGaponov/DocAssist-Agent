"""
tests/conftest.py

Модуль предоставляет тестовые фикстуры для запуска интеграционных тестов
веб‑приложения DocAssist‑Agent.

Основная цель — создать изолированную среду для тестирования HTTP‑эндпоинтов
без запуска полноценного сервера. Для этого используется TestClient из FastAPI,
который имитирует запросы к приложению и позволяет проверять ответы.

Требования:
- pytest (для работы с фикстурами и запуска тестов);
- FastAPI (для использования TestClient);
- основное приложение должно быть доступно через src.main.app.

Использование:
Фикстура `client` автоматически доступна во всех тестовых файлах,
расположенных в директории tests/ (при условии корректной настройки pytest).
"""

from typing import Tuple
import pytest
from pytest import FixtureRequest
from fastapi.testclient import TestClient

from src.main import app
from src.db import VectorDBInterface, get_vector_db


class MockVectorDB(VectorDBInterface):
    def __init__(self):
        self.storage = []

    def get_or_create_collection(self):
        return "test_collection"

    def add_records(self, ids, documents, metadatas):
        for i, doc, meta in zip(ids, documents, metadatas):
            self.storage.append({"id": i, "doc": doc, "meta": meta})
        return {"message": f"Добавлено {len(ids)} записей", "success": True}

    def count_records(self) -> int:
        return len(self.storage)


@pytest.fixture
def client(test_vector_db: MockVectorDB):
    """
    Фикстура для создания тестового клиента FastAPI.

    Создаёт экземпляр TestClient, привязанный к основному приложению (app),
    что позволяет отправлять HTTP‑запросы к эндпоинтам в рамках тестов.

    Фикстура автоматически инициализируется перед каждым тестом,
    который её использует, и закрывается после завершения теста.

    Returns:
        TestClient: Объект тестового клиента для взаимодействия
                     с FastAPI‑приложением через HTTP.

    Пример использования в тесте:
        def test_root_endpoint(client):
            response = client.get("/")
            assert response.status_code == 200
            assert response.json() == {"message": "Приложение запущено"}
    """
    app.dependency_overrides[get_vector_db] = lambda: test_vector_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def test_vector_db():
    """Возвращает экземпляр тестовой векторной БД."""
    return MockVectorDB()


@pytest.fixture
def sample_txt_content() -> str:
    """Тестовый TXT‑файл (3 абзаца, UTF‑8)."""
    return (
        "Это первый абзац. Он станет чанком.\n\n"
        "Второй абзац — ещё один чанк.\n"
        "Третий абзац, достаточно длинный для минимальной длины."
    )


@pytest.fixture
def empty_txt_content() -> str:
    """Тестовый TXT‑файл (3 абзаца, UTF‑8)."""
    return ''


@pytest.fixture
def duplicate_txt_content() -> str:
    """Тестовый TXT‑файл (3 абзаца, UTF‑8)."""
    return (
        "Абзац с одинаковыми данными. Один чанк.\n\n"
        "Абзац с одинаковыми данными. Один чанк.\n"
        "Абзац с одинаковыми данными. Один чанк."
    )


@pytest.fixture
def added_records_file() -> Tuple[str, bytes, str]:
    return (
        "added_records.txt",
        "Записи, ранее добавленные в векторную базу данных.".encode("utf-8"),
        "text/plain"
    )


@pytest.fixture
def new_data_file() -> Tuple[str, bytes, str]:
    return (
        "new_data.txt",
        (
            "Записи, ранее добавленные в векторную базу данных.\n\n"
            "Новые данные для добавления в векторную базу данных."
        ).encode("utf-8"),
        "text/plain"
    )


@pytest.fixture(
    params=("sample_txt", "empty_txt", "duplicate_txt", "new_data_txt")
)
def txt_file(
    request: FixtureRequest,
    sample_txt_content: str,
    empty_txt_content: str,
    duplicate_txt_content: str
) -> Tuple[str, bytes, str]:
    file_name = ''
    file_content = ''
    if request.param == "sample_txt":
        file_name, file_content = "sample.txt", sample_txt_content
    elif request.param == "empty_txt":
        file_name, file_content = "empty.txt", empty_txt_content
    elif request.param == "duplicate_txt":
        file_name, file_content = "duplicate.txt", duplicate_txt_content
    else:
        pytest.fail(f"Неизвестный параметр: {request.param}")
    return file_name, file_content.encode("utf-8"), "text/plain"


@pytest.fixture
def jpg_file() -> Tuple[str, bytes, str]:
    """Тестовый файл не‑текстового формата (JPEG)."""
    # Миниатюрный валидный JPEG (1×1 пиксель, чёрный)
    jpeg_data = (
        b'\xff\xd8\xff\xe0\x00\x10\x4a\x46\x49\x46\x00\x01\x01\x01'
        b'\x00\x48\x00\x48\x00\x00\xff\xdb\x00\x43\x00\x02\x01\x01'
        b'\x01\x01\x01\x02\x01\x01\x01\x02\x02\x02\x02\x02\x04\x03'
        b'\x02\x02\x02\x02\x05\x04\x04\x03\x04\x06\x05\x06\x06\x06'
        b'\x05\x05\x07\x08\x07\x06\x07\x06\x05\x05\x09\x09\x08\x09'
        b'\x0b\x0a\x0b\x0b\x0a\x0a\x0a\x0d\x0d\x0c\x0d\x0e\x11\x10'
        b'\x11\x11\x10\x0f\x0f\x10\x14\x15\x16\x15\x14\x17\x13\x14'
        b'\x14\x13\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03\x01\x22'
        b'\x00\x02\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01'
        b'\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02'
        b'\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\xff\xc4\x00\xb5\x10'
        b'\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00'
        b'\x01\x7d\x01\x02\x03\x00\x04\x11\x05\x12\x21\x31\x41\x06'
        b'\x13\x51\x61\x07\x22\x71\x14\x32\x81\x91\xa1\x08\x23\x42'
        b'\xb1\xc1\x15\x52\xd1\xf0\x24\x33\x62\x72\x82\x09\x0a\x16'
        b'\x17\x18\x19\x1a\x25\x26\x27\x28\x29\x2a\x34\x35\x36\x37'
        b'\x38\x39\x3a\x43\x44\x45\x46\x47\x48\x49\x4a\x53\x54\x55'
        b'\x56\x57\x58\x59\x5a\x63\x64\x65\x66\x67\x68\x69\x6a\x73'
        b'\x74\x75\x76\x77\x78\x79\x7a\x83\x84\x85\x86\x87\x88\x89'
        b'\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5'
        b'\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2'
        b'\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7'
        b'\xd8\xd9\xda\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf2\xf3'
        b'\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00'
        b'\x00\x00\x00\xff\xd9'
    )
    return "image.jpg", jpeg_data, "image/jpeg"
