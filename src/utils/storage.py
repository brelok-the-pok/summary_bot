"""Утилиты для работы с хранилищем данных"""
from typing import Any, Dict, List
from datetime import date


# Хранилище для сообщений (в реальном проекте используйте БД)
daily_messages: Dict[str, List[Dict[str, Any]]] = {}


def get_user_messages(user_id: str, target_date: str = None) -> List[Dict[str, Any]]:
    """Получает сообщения пользователя за определенную дату"""
    if target_date is None:
        target_date = date.today().strftime('%Y-%m-%d')
    
    if user_id not in daily_messages or target_date not in daily_messages[user_id]:
        return []
    
    return daily_messages[user_id][target_date]


def add_user_message(user_id: str, message_data: Dict[str, Any], target_date: str = None):
    """Добавляет сообщение пользователя"""
    if target_date is None:
        target_date = date.today().strftime('%Y-%m-%d')
    
    if user_id not in daily_messages:
        daily_messages[user_id] = {}
    if target_date not in daily_messages[user_id]:
        daily_messages[user_id][target_date] = []
    
    daily_messages[user_id][target_date].append(message_data)


def get_user_transcriptions(user_id: str, target_date: str = None) -> List[str]:
    """Получает транскрипции пользователя за определенную дату"""
    messages = get_user_messages(user_id, target_date)
    return [msg['transcription'] for msg in messages if 'transcription' in msg]


def has_user_messages(user_id: str, target_date: str = None) -> bool:
    """Проверяет, есть ли у пользователя сообщения за определенную дату"""
    messages = get_user_messages(user_id, target_date)
    return len(messages) > 0
