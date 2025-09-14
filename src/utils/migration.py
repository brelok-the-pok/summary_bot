"""Утилиты для миграции данных из памяти в базу данных"""
import logging
from typing import Dict, List, Any

from ..services.database import db_service
from ..models.user_message import UserMessage

logger = logging.getLogger(__name__)


async def migrate_from_memory_storage(memory_data: Dict[str, List[Dict[str, Any]]]):
    """Мигрирует данные из памяти в базу данных"""
    logger.info("Начинаем миграцию данных из памяти в базу данных...")
    
    # Инициализируем базу данных
    await db_service.initialize()
    
    migrated_count = 0
    
    for user_id, user_dates in memory_data.items():
        for date_str, messages in user_dates.items():
            for message_data in messages:
                try:
                    # Создаем модель сообщения
                    message = UserMessage(
                        user_id=user_id,
                        message_id=message_data.get('message_id', 0),
                        date=date_str,
                        timestamp=message_data.get('timestamp', ''),
                        s3_key=message_data.get('s3_key'),
                        transcription=message_data.get('transcription')
                    )
                    
                    # Сохраняем в базе данных
                    await db_service.add_user_message(message)
                    migrated_count += 1
                    
                except Exception as e:
                    logger.error(f"Ошибка миграции сообщения: {e}")
                    continue
    
    logger.info(f"Миграция завершена. Перенесено {migrated_count} сообщений")
    return migrated_count


def get_memory_data_backup() -> Dict[str, List[Dict[str, Any]]]:
    """Создает резервную копию данных из памяти (для отладки)"""
    # Импортируем старое хранилище для создания резервной копии
    try:
        from .storage import daily_messages
        return daily_messages.copy()
    except ImportError:
        logger.warning("Старое хранилище не найдено")
        return {}


async def cleanup_old_messages(days_to_keep: int = 30):
    """Очищает старые сообщения из базы данных"""
    logger.info(f"Очищаем сообщения старше {days_to_keep} дней...")
    
    deleted_count = await db_service.delete_old_messages(days_to_keep)
    logger.info(f"Удалено {deleted_count} старых сообщений")
    
    return deleted_count
