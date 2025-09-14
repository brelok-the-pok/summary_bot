"""Модель для хранения сообщений пользователей"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UserMessage:
    """Модель сообщения пользователя"""
    id: Optional[int] = None
    user_id: str = ""
    message_id: int = 0
    date: str = ""
    timestamp: str = ""
    s3_key: Optional[str] = None
    transcription: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Инициализация после создания объекта"""
        if self.created_at is None:
            self.created_at = datetime.now()
