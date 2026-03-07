import re
from typing import List
from fastapi import UploadFile


async def get_content(file: UploadFile) -> str:
    # Асинхронное чтение байтов из файла
    contents = await file.read()

    # Декодирование байтов в строку (UTF-8)
    text = contents.decode("utf-8")

    return text


def split_by_blocks(text: str) -> List[str]:
    """
    Разбивает текст на семантические блоки (абзацы, заголовки, списки).
    """
    text.replace('\r', '')
    # Разделяем по переносам (абзацы)
    blocks = re.split(r'\n', text)
    # Фильтруем пустые блоки
    return [block.strip() for block in blocks if block.strip()]


async def chunked(file: UploadFile):
    content = await get_content(file)
    chunks = split_by_blocks(content)
    return [chunk for chunk in chunks]
