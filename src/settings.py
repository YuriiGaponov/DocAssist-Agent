"""
src/settings.py

Модуль содержит конфигурацию приложения через класс Settings на базе
Pydantic Settings.

Основные функции:
- определяет базовые пути (BASE_DIR);
- задаёт параметры логирования (имя файла, директория);
- загружает настройки из .env‑файла.

Используемые классы и объекты:
- Settings: класс конфигурации с полями LOG_FILENAME, LOG_DIR
  и свойством LOG_PATH;
- settings: экземпляр класса Settings, доступный для импорта
  в других модулях.

Поля класса Settings:
- LOG_FILENAME: имя файла логов (по умолчанию 'log');
- LOG_DIR: директория для логов (по умолчанию 'logs');
- LOG_PATH: вычисляемое свойство — полный путь к директории логов.

Настройки загрузки окружения:
- env_file: путь к .env‑файлу (в корне проекта);
- env_file_encoding: кодировка .env‑файла ('utf-8');
- extra: поведение при неизвестных переменных окружения ('ignore').
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    Класс конфигурации приложения на базе Pydantic Settings.
    """

    # === Параметры логирования ===
    LOG_FILENAME: str = 'log'
    LOG_DIR: str = 'logs'

    @property
    def LOG_PATH(self) -> Path:
        """Полный путь к директории логов (на основе BASE_DIR и LOG_DIR)."""
        return BASE_DIR / self.LOG_DIR

    # === Настройки загрузки из окружения ===
    model_config = SettingsConfigDict(
        env_file=(BASE_DIR / '.env'),
        env_file_encoding='utf-8',
        extra='ignore'
    )


# Экземпляр класса Settings, доступный для импорта в других модулях
settings = Settings()
