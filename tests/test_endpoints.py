"""
tests/test_endpoints.py

Модуль содержит тестовые сценарии для проверки HTTP‑эндпоинтов
веб‑приложения DocAssist‑Agent.

Использует pytest и TestClient из FastAPI для имитации запросов
и валидации ответов сервера.

Требования:
- pytest (для запуска тестов и использования фикстур);
- FastAPI (для TestClient);
- фикстура `client` должна быть доступна из conftest.py.

Структура:
- Класс `TestRootEndpoint` группирует тесты по эндпоинтам приложения.
"""

from typing import Tuple

import pytest
from fastapi.testclient import TestClient
from http import HTTPStatus

from tests.conftest import MockVectorDB


class TestRootEndpoint:
    """
    Набор тестов для проверки работоспособности HTTP‑эндпоинтов приложения.

    Каждый метод класса представляет отдельный тестовый сценарий
    для конкретного эндпоинта.
    """

    def test_get_root_endpoint_available(self, client: TestClient) -> None:
        """
        Тест для GET‑запроса к корневому эндпоинту /.

        Проверяет:
        - успешность выполнения запроса (статус‑код 200);
        - корректность возвращаемого JSON‑ответа.

        Args:
            client (TestClient): Экземпляр тестового клиента FastAPI,
                                 предоставленный фикстурой из conftest.py.

        Шаги теста:
        1. Отправка GET‑запроса к эндпоинту /.
        2. Проверка статуса ответа (должен быть 200 OK).
        3. Проверка содержимого ответа (должен возвращать ожидаемый JSON).

        Expected Result:
            Статус‑код: 200
            Тело ответа: {"message": "Приложение запущено"}

        Raises:
            AssertionError: Если статус‑код не равен 200
                          или ответ не соответствует ожидаемому.
        """
        response = client.get("/")

        assert response.status_code == HTTPStatus.OK, (
            f"Ожидался статус 200, но получен {response.status_code}"
        )

        assert response.json() == {"message": "Приложение запущено"}, (
            f"Ожидаемый ответ {'message': 'Приложение запущено'}, "
            f"но получен {response.json()}"
        )


class TestUploadTXTEndpoint:

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "file, expected_status",
        [
            ("sample_txt", HTTPStatus.OK),
            ("empty_txt", HTTPStatus.BAD_REQUEST)
        ],
        indirect=["file"]
    )
    async def test_post_upload_txt_success(
        self,
        client: TestClient,
        file: Tuple[str, bytes, str],
        expected_status: int
    ) -> None:

        filename, file_content, content_type = file
        response = client.post(
            "/upload-txt",
            files={'file': (filename, file_content, content_type)}
        )

        assert response.status_code == expected_status

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "file",
        ["duplicate_txt"],
        indirect=["file"]
    )
    async def test_post_upload_txt_duplicate_add_unique_data(
        self,
        client: TestClient,
        file: Tuple[str, bytes, str],
        test_vector_db: MockVectorDB
    ):
        filename, file_content, content_type = file
        client.post(
            "/upload-txt",
            files={'file': (filename, file_content, content_type)}
        )
        assert test_vector_db.count_records() == 1

    @pytest.mark.asyncio
    async def test_post_upload_txt_add_only_new_data(
        self,
        client: TestClient,
        added_records_file: Tuple[str, bytes, str],
        new_data_file: Tuple[str, bytes, str],
        test_vector_db: MockVectorDB
    ):
        filename, file_content, content_type = added_records_file
        client.post(
            "/upload-txt",
            files={'file': (filename, file_content, content_type)}
        )
        db_records_count: int = test_vector_db.count_records()

        filename, file_content, content_type = new_data_file
        client.post(
            "/upload-txt",
            files={'file': (filename, file_content, content_type)}
        )
        assert test_vector_db.count_records() == db_records_count + 1
