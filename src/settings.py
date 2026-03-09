"""
src/settings.py

Модуль содержит конфигурацию приложения через класс Settings
на базе Pydantic Settings.

Основные функции:
- определяет базовые пути (BASE_DIR);
- задаёт параметры логирования;
- настраивает параметры векторной БД;
- загружает настройки из .env‑файла.

Используемые классы и объекты:
- Settings: класс конфигурации с параметрами приложения;
- settings: экземпляр Settings для импорта в других модулях.

Поля класса Settings:
- DEBUG: флаг режима отладки (по умолчанию False);
- LOG_FILENAME: имя файла логов (по умолчанию 'log');
- LOG_DIR: директория для логов (по умолчанию 'logs');
- VECTOR_DB: название векторной БД (по умолчанию 'chroma');
- VECTOR_DB_HOST: хост векторной БД (по умолчанию 'localhost');
- VECTOR_DB_PORT: порт векторной БД (по умолчанию 8000).

Настройки загрузки окружения:
- env_file: путь к .env‑файлу;
- env_file_encoding: кодировка .env‑файла ('utf-8');
- extra: игнорирование неизвестных переменных окружения.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    Класс конфигурации приложения на базе Pydantic Settings.
    """

    # === Режим отладки ===
    DEBUG: bool = False

    # === Параметры логирования ===
    LOG_FILENAME: str = 'log'
    LOG_DIR: str = 'logs'

    # === Настройки векторной БД ===
    VECTOR_DB: str = 'chroma'
    VECTOR_DB_HOST: str = 'locallhost'
    VECTOR_DB_PORT: int = 8000
    VECTOR_DB_DIR: str = 'data'
    COLLECTION_NAME: str = 'docs'

    # === Настройки RAG ===
    EMBEDDING_MODEL: str = 'all-MiniLM-L6-v2'

    # === Настройки загрузки из окружения ===
    model_config = SettingsConfigDict(
        env_file=(BASE_DIR / '.env'),
        env_file_encoding='utf-8',
        extra='ignore'
    )


# Экземпляр класса Settings, доступный для импорта в других модулях
settings = Settings()
