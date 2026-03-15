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
- Класс `TestRootEndpoint` группирует тесты по корневому эндпоинту;
- Класс `TestUploadTXTEndpoint` — тесты для загрузки TXT‑файлов.
"""

from typing import Tuple

import pytest
from fastapi.testclient import TestClient
from http import HTTPStatus
from httpx import Response

from tests.conftest import MockVectorDB


class TestRootEndpoint:
    """Набор тестов для проверки корневого эндпоинта приложения (/)."""

    def test_get_root_endpoint_available(self, client: TestClient) -> None:
        """Тест GET‑запроса к корневому эндпоинту /.

        Проверяет:
        - статус‑код 200;
        - JSON‑ответ `{"message": "Приложение запущено"}`.

        Args:
            client (TestClient): тестовый клиент FastAPI.

        Expected Result:
            - статус: 200 OK;
            - тело ответа: `{"message": "Приложение запущено!}`.

        Raises:
            AssertionError: если статус или ответ не соответствуют ожиданиям.
        """
        response = client.get("/")

        assert response.status_code == HTTPStatus.OK, (
            f"Ожидался статус 200, но получен {response.status_code}"
        )

        assert response.json() == {"message": "Приложение запущено"}, (
            f"Ожидаемый ответ {{'message': 'Приложение запущено'}}, "
            f"но получен {response.json()}"
        )


class TestUploadTXTEndpoint:
    """Набор тестов для эндпоинта загрузки TXT‑файлов (/upload-txt)."""

    async def _get_response(
        self,
        client: TestClient,
        file: Tuple[str, bytes, str]
    ) -> Response:
        """Отправляет POST‑запрос с файлом на эндпоинт /upload-txt.

        Args:
            client: тестовый клиент;
            file: тройка (имя, байты, MIME‑тип).

        Returns:
            Response: ответ сервера.
        """
        filename, file_content, content_type = file
        return client.post(
            "/upload-txt",
            files={'file': (filename, file_content, content_type)}
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "txt_file, expected_status",
        [
            ("sample_txt", HTTPStatus.OK),
            ("empty_txt", HTTPStatus.BAD_REQUEST)
        ],
        indirect=["txt_file"]
    )
    async def test_post_upload_txt_success(
        self,
        client: TestClient,
        txt_file: Tuple[str, bytes, str],
        expected_status: int
    ) -> None:
        """Тест загрузки TXT‑файла (успех/ошибка валидации).

        Проверяет статус ответа в зависимости от содержимого файла.

        Args:
            client: тестовый клиент;
            txt_file: тестовый файл (через параметризацию);
            expected_status: ожидаемый HTTP‑статус.
        """
        response = await self._get_response(client, txt_file)

        assert response.status_code == expected_status

        if expected_status == HTTPStatus.OK:
            json_response = response.json()
            assert "message" in json_response

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "txt_file",
        ["duplicate_txt"],
        indirect=["txt_file"]
    )
    async def test_post_upload_txt_duplicate_add_unique_data(
        self,
        client: TestClient,
        txt_file: Tuple[str, bytes, str],
        test_vector_db: MockVectorDB
    ) -> None:
        """Тест загрузки файла с повторяющимися блоками.

        Проверяет, что в БД сохраняется только один уникальный чанк.

        Args:
            client: тестовый клиент;
            txt_file: файл с дубликатами;
            test_vector_db: моковая БД.
        """
        response = await self._get_response(client, txt_file)
        assert response.status_code == HTTPStatus.OK
        assert test_vector_db.count_records() == 1

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "txt_file",
        ["oversized"],
        indirect=["txt_file"]
    )
    async def test_post_upload_txt_oversized_content(
        self,
        client: TestClient,
        txt_file: Tuple[str, bytes, str],
    ) -> None:
        """Тест загрузки файла, превышающего лимит размера.

        Проверяет возврат статуса 413 (Content Too Large).

        Args:
            client: тестовый клиент;
            txt_file: oversized‑файл.
        """
        response = await self._get_response(client, txt_file)
        assert response.status_code == HTTPStatus.CONTENT_TOO_LARGE

    @pytest.mark.asyncio
    async def test_post_upload_txt_add_only_new_data(
        self,
        client: TestClient,
        added_records_file: Tuple[str, bytes, str],
        new_data_file: Tuple[str, bytes, str],
        test_vector_db: MockVectorDB
    ) -> None:
        """Тест добавления только новых данных в БД.

        1. Загружает файл с существующими записями.
        2. Загружает файл с новыми данными.
        3. Проверяет, что количество записей увеличилось на 1.

        Args:
            client: тестовый клиент;
            added_records_file: файл с существующими данными;
            new_data_file: файл с новыми данными;
            test_vector_db: моковая БД.
        """
        await self._get_response(client, added_records_file)
        db_records_count: int = test_vector_db.count_records()

        response = await self._get_response(client, new_data_file)
        assert response.status_code == HTTPStatus.OK
        assert test_vector_db.count_records() == db_records_count + 1

    @pytest.mark.asyncio
    async def test_post_upload_not_txt(
        self,
        client: TestClient,
        jpg_file: Tuple[str, bytes, str],
    ) -> None:
        """Тест загрузки не‑TXT‑файла (например, JPEG).

        Проверяет возврат статуса 400 и наличие сообщения в ответе.

        Args:
            client: тестовый клиент;
            jpg_file: JPEG‑файл.
        """
        response = await self._get_response(client, jpg_file)
        assert response.status_code == HTTPStatus.BAD_REQUEST

        json_response = response.json()
        assert "message" in json_response
