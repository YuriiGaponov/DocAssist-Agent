"""
src/settings.py

Модуль содержит конфигурацию приложения через класс Settings на базе
Pydantic Settings.

Основная задача — централизованное управление настройками приложения:
- загрузка из .env‑файла;
- валидация типов;
- предоставление доступа к настройкам через единый экземпляр.

Ключевые параметры:
- режим отладки (DEBUG);
- настройки логирования (LOG_FILENAME, LOG_DIR);
- параметры векторной БД (VECTOR_DB, VECTOR_DB_HOST и др.);
- ограничения API (UPLOAD_FILE_MAX_SIZE);
- настройки RAG (EMBEDDING_MODEL).

Используемые объекты:
- Settings: класс конфигурации с валидируемыми полями;
- settings: готовый экземпляр Settings для импорта.

Настройки загрузки окружения:
- env_file: путь к .env‑файлу (относительно BASE_DIR);
- env_file_encoding: 'utf-8';
- extra: 'ignore' (игнорирование неизвестных переменных).
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Класс конфигурации приложения на базе Pydantic Settings.

    Поля с дефолтными значениями:
    - DEBUG: режим отладки (False).
    - LOG_FILENAME: имя файла логов ('log').
    - LOG_DIR: директория для логов ('logs').
    - VECTOR_DB: название векторной БД ('chroma').
    - VECTOR_DB_HOST: хост БД ('localhost').
    - VECTOR_DB_PORT: порт БД (8000).
    - VECTOR_DB_DIR: директория хранения данных ('data').
    - COLLECTION_NAME: имя коллекции ('docs').
    - EMBEDDING_MODEL: модель для эмбеддингов ('all-MiniLM-L6-v2').
    - UPLOAD_FILE_MAX_SIZE: макс. размер загружаемого файла (10 МБ).

    Конфигурация загрузки:
    - env_file: .env из BASE_DIR.
    - env_file_encoding: 'utf-8'.
    - extra: 'ignore' (пропускать неизвестные переменные).
    """

    DEBUG: bool = False

    LOG_FILENAME: str = 'log'
    LOG_DIR: str = 'logs'

    VECTOR_DB: str = 'chroma'
    VECTOR_DB_HOST: str = 'localhost'
    VECTOR_DB_PORT: int = 8000
    VECTOR_DB_DIR: str = 'data'
    COLLECTION_NAME: str = 'docs'

    EMBEDDING_MODEL: str = 'all-MiniLM-L6-v2'

    UPLOAD_FILE_MAX_SIZE: int = 10 * 1024 * 1024

    model_config = SettingsConfigDict(
        env_file=(BASE_DIR / '.env'),
        env_file_encoding='utf-8',
        extra='ignore'
    )


# Экземпляр класса Settings, доступный для импорта в других модулях
settings = Settings()
