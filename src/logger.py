"""
src/logger.py

Модуль настраивает систему логирования приложения.

Функциональность:
- конфигурирует базовый логгер с параметрами из объекта settings;
- создаёт именованный логгер 'app_logger' для использования в приложении.
"""

import logging

from src.settings import settings


# Настройка базового конфигуратора логирования
logging.basicConfig(
    filename=f'{settings.LOG_PATH}/{settings.LOG_FILENAME}',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    encoding='utf-8'
)

# Создание именованного логгера для приложения
app_logger = logging.getLogger('app_logger')
