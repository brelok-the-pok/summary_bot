"""Утилиты для работы с хранилищем данных"""
import asyncio
from typing import Any, Dict, List
from datetime import date, datetime

from ..models.user_message import UserMessage
from ..services.database import db_service


async def get_user_messages(user_id: str, target_date: str = None) -> List[Dict[str, Any]]:
    """Получает сообщения пользователя за определенную дату"""
    if target_date is None:
        target_date = date.today().strftime('%Y-%m-%d')
    
    messages = await db_service.get_user_messages(user_id, target_date)
    
    # Конвертируем модели в словари для обратной совместимости
    result = []
    for msg in messages:
        result.append({
            'message_id': msg.message_id,
            'timestamp': msg.timestamp,
            's3_key': msg.s3_key,
            'transcription': msg.transcription,
            'text_content': msg.text_content,
            'message_type': msg.message_type
        })
    
    return result


async def add_user_message(user_id: str, message_data: Dict[str, Any], target_date: str = None):
    """Добавляет сообщение пользователя"""
    if target_date is None:
        target_date = date.today().strftime('%Y-%m-%d')
    
    # Создаем модель сообщения
    message = UserMessage(
        user_id=user_id,
        message_id=message_data.get('message_id', 0),
        date=target_date,
        timestamp=message_data.get('timestamp', datetime.now().isoformat()),
        s3_key=message_data.get('s3_key'),
        transcription=message_data.get('transcription'),
        text_content=message_data.get('text_content'),
        message_type=message_data.get('message_type', 'voice')
    )
    
    # Сохраняем в базе данных
    await db_service.add_user_message(message)


async def get_user_transcriptions(user_id: str, target_date: str = None) -> List[str]:
    """Получает транскрипции пользователя за определенную дату"""
    if target_date is None:
        target_date = date.today().strftime('%Y-%m-%d')
    
    return await db_service.get_user_transcriptions(user_id, target_date)


async def has_user_messages(user_id: str, target_date: str = None) -> bool:
    """Проверяет, есть ли у пользователя сообщения за определенную дату"""
    if target_date is None:
        target_date = date.today().strftime('%Y-%m-%d')
    
    return await db_service.has_user_messages(user_id, target_date)


# Синхронные обертки для обратной совместимости
def get_user_messages_sync(user_id: str, target_date: str = None) -> List[Dict[str, Any]]:
    """Синхронная обертка для получения сообщений пользователя"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(get_user_messages(user_id, target_date))


def add_user_message_sync(user_id: str, message_data: Dict[str, Any], target_date: str = None):
    """Синхронная обертка для добавления сообщения пользователя"""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(add_user_message(user_id, message_data, target_date))


def get_user_transcriptions_sync(user_id: str, target_date: str = None) -> List[str]:
    """Синхронная обертка для получения транскрипций пользователя"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(get_user_transcriptions(user_id, target_date))


def has_user_messages_sync(user_id: str, target_date: str = None) -> bool:
    """Синхронная обертка для проверки наличия сообщений пользователя"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(has_user_messages(user_id, target_date))
