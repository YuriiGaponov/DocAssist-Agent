"""
src/api/api_validators.py

Модуль предоставляет функции валидации входных данных для API‑эндпоинтов.

Основная задача — проверка корректности входящих данных с генерацией
HTTP‑исключений при нарушении правил валидации.

Реализованные валидаторы:
- `upload_txt_validator`: проверяет загружаемый TXT‑файл по критериям:
  - наличие файла;
  - определённость имени файла;
  - MIME‑тип (должен быть «text/plain»);
  - размер (не превышает лимит из настроек).

Все функции модуля генерируют `HTTPException` с соответствующими
кодами статусов и понятными сообщениями об ошибках.
"""

from http import HTTPStatus

from fastapi import UploadFile, HTTPException

from src.settings import settings


def upload_txt_validator(file: UploadFile) -> None:
    """Валидатор для загружаемого TXT‑файла.

    Проверяет:
    - наличие файла;
    - определённость имени файла;
    - MIME‑тип («text/plain»);
    - размер (в пределах лимита из настроек).

    Args:
        file (UploadFile): загруженный файл от клиента.

    Raises:
        HTTPException: если файл не передан (статус 400,
            деталь «Файл не загружен»).
        HTTPException: если имя файла не определено (статус 400,
            деталь «Не удалось определить имя файла»).
        HTTPException: если MIME‑тип не «text/plain» (статус 400,
            деталь «Только TXT‑файлы»).
        HTTPException: если размер файла превышает лимит (статус 413,
            деталь «Файл слишком большой»).
    """
    # Проверяем, что файл загружен
    if not file:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Файл не загружен"
        )

    # Получаем имя файла и проверяем, что оно не None
    filename = file.filename
    if filename is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Не удалось определить имя файла"
        )

    # Проверяем MIME‑тип файла
    if file.content_type != "text/plain":
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Только TXT‑файлы"
        )

    # Проверяем размер файла
    file_size = file.size if file.size is not None else 0
    if file_size > settings.UPLOAD_FILE_MAX_SIZE:
        raise HTTPException(
            status_code=HTTPStatus.CONTENT_TOO_LARGE,
            detail="Файл слишком большой"
        )
