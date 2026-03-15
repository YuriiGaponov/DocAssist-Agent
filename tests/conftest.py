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


class TestVectorDB(VectorDBInterface):
    def __init__(self):
        self.storage = []

    def get_or_create_collection(self):
        return "test_collection"

    def add_records(self, ids, documents, metadatas):
        for i, doc, meta in zip(ids, documents, metadatas):
            self.storage.append({"id": i, "doc": doc, "meta": meta})
        return {"message": f"Добавлено {len(ids)} записей", "success": True}


@pytest.fixture
def client(test_vector_db: TestVectorDB):
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
    return TestVectorDB()


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


@pytest.fixture(
    params=("sample_txt", "empty_txt")
)
def file(
    request: FixtureRequest,
    sample_txt_content: str,
    empty_txt_content: str
) -> Tuple[str, bytes, str]:
    if request.param in ("sample_txt", "empty_txt"):
        file_name = ''
        file_content = ''
        if request.param == "sample_txt":
            file_name, file_content = "sample_txt", sample_txt_content
        elif request.param == "empty_txt":
            file_name, file_content = "empty_txt", empty_txt_content
        return file_name, file_content.encode("utf-8"), "text/plain"
    else:
        pytest.fail(f"Неизвестный параметр: {request.param}")
