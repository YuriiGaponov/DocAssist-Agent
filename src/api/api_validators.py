"""
src/api/api_validators.py

Модуль содержит функции валидации входящих данных для API‑эндпоинтов.


Текущая реализация:
- upload_txt_validator: проверяет загруженный файл на:
  * наличие файла;
  * корректность имени;
  * расширение (.txt).
"""

from fastapi import UploadFile, HTTPException


def upload_txt_validator(file: UploadFile) -> None:
    """
    Валидатор для загружаемого TXT‑файла.


    Проверяет базовые условия: файл присутствует, имеет имя
    и нужное расширение.

    Args:
        file (UploadFile): загруженный файл от клиента.

    Raises:
        HTTPException: если файл не передан (400,
            "Файл не загружен").
        HTTPException: если имя файла не определено (400,
            "Не удалось определить имя файла").
        HTTPException: если расширение не .txt (400,
            "Разрешены только файлы с расширением .txt").
    """
    # 1. Проверяем, что файл загружен
    if not file:
        raise HTTPException(
            status_code=400,
            detail="Файл не загружен"
        )

    # 2. Получаем имя файла и проверяем, что оно не None
    filename = file.filename
    if filename is None:
        raise HTTPException(
            status_code=400,
            detail="Не удалось определить имя файла"
        )

    # 3. Проверяем расширение файла
    if not filename.lower().endswith(".txt"):
        raise HTTPException(
            status_code=400,
            detail="Разрешены только файлы с расширением .txt"
        )
