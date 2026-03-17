"""
src/logger.py

Модуль настраивает систему логирования приложения.

Функциональность:
- конфигурирует базовый логгер с параметрами из объекта settings;
- создаёт именованный логгер 'app_logger' для использования в приложении.
"""

import logging
from logging import Logger
from logging.handlers import RotatingFileHandler

from src.settings import settings


# Обработчик с ротацией файлов
handler = RotatingFileHandler(
    f'{settings.LOG_DIR}/{settings.LOG_FILENAME}',
    maxBytes=10*1024*1024,  # 10 МБ на файл
    backupCount=5,             # максимум 5 файлов (всего ~50 МБ)
    encoding='utf-8'
)

# Фформат вывода логов
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)


# Настройка базового конфигуратора логирования
logging.basicConfig(
    handlers=[handler],
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
)

# Именованные логгеры для разных компонентов
app_logger: Logger = logging.getLogger('app_logger')
"""Логгер для общего логирования приложения."""

db_logger: Logger = logging.getLogger('db_logger')
"""Логгер для логирования операций с базой данных."""
