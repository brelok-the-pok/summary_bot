"""Сервис для работы с базой данных"""
import aiosqlite
import logging
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from ..models.user_message import UserMessage

logger = logging.getLogger(__name__)


class DatabaseService:
    """Сервис для работы с базой данных SQLite"""
    
    def __init__(self, db_path: str = "summary_bot.db"):
        self.db_path = db_path
        self._initialized = False
    
    async def initialize(self):
        """Инициализация базы данных и создание таблиц"""
        if self._initialized:
            return
            
        async with aiosqlite.connect(self.db_path) as db:
            # Создаем таблицу для сообщений пользователей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    message_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    s3_key TEXT,
                    transcription TEXT,
                    text_content TEXT,
                    message_type TEXT DEFAULT 'voice',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, message_id, date)
                )
            """)
            
            # Создаем индексы для быстрого поиска
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_messages_user_date 
                ON user_messages(user_id, date)
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_messages_user_id 
                ON user_messages(user_id)
            """)
            
            # Добавляем новые поля, если они не существуют (миграция)
            try:
                await db.execute("ALTER TABLE user_messages ADD COLUMN text_content TEXT")
            except:
                pass  # Поле уже существует
            
            try:
                await db.execute("ALTER TABLE user_messages ADD COLUMN message_type TEXT DEFAULT 'voice'")
            except:
                pass  # Поле уже существует
            
            await db.commit()
        
        self._initialized = True
        logger.info("База данных инициализирована")
    
    async def add_user_message(self, message: UserMessage) -> int:
        """Добавляет сообщение пользователя в базу данных"""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT OR REPLACE INTO user_messages 
                (user_id, message_id, date, timestamp, s3_key, transcription, text_content, message_type, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                message.user_id,
                message.message_id,
                message.date,
                message.timestamp,
                message.s3_key,
                message.transcription,
                message.text_content,
                message.message_type,
                message.created_at.isoformat() if message.created_at else None
            ))
            await db.commit()
            return cursor.lastrowid
    
    async def get_user_messages(self, user_id: str, date: str) -> List[UserMessage]:
        """Получает сообщения пользователя за определенную дату"""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT id, user_id, message_id, date, timestamp, s3_key, transcription, text_content, message_type, created_at
                FROM user_messages 
                WHERE user_id = ? AND date = ?
                ORDER BY created_at ASC
            """, (user_id, date))
            
            rows = await cursor.fetchall()
            messages = []
            
            for row in rows:
                message = UserMessage(
                    id=row[0],
                    user_id=row[1],
                    message_id=row[2],
                    date=row[3],
                    timestamp=row[4],
                    s3_key=row[5],
                    transcription=row[6],
                    text_content=row[7],
                    message_type=row[8] or "voice",
                    created_at=datetime.fromisoformat(row[9]) if row[9] else None
                )
                messages.append(message)
            
            return messages
    
    async def get_user_transcriptions(self, user_id: str, date: str) -> List[str]:
        """Получает транскрипции и текстовые сообщения пользователя за определенную дату"""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT 
                    CASE 
                        WHEN message_type = 'text' AND text_content IS NOT NULL THEN text_content
                        WHEN message_type = 'voice' AND transcription IS NOT NULL THEN transcription
                        ELSE NULL
                    END as content
                FROM user_messages 
                WHERE user_id = ? AND date = ? 
                AND (
                    (message_type = 'text' AND text_content IS NOT NULL) OR 
                    (message_type = 'voice' AND transcription IS NOT NULL)
                )
                ORDER BY created_at ASC
            """, (user_id, date))
            
            rows = await cursor.fetchall()
            return [row[0] for row in rows if row[0]]
    
    async def has_user_messages(self, user_id: str, date: str) -> bool:
        """Проверяет, есть ли у пользователя сообщения за определенную дату"""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT COUNT(*) 
                FROM user_messages 
                WHERE user_id = ? AND date = ?
            """, (user_id, date))
            
            count = await cursor.fetchone()
            return count[0] > 0
    
    async def get_user_messages_by_date_range(self, user_id: str, start_date: str, end_date: str) -> List[UserMessage]:
        """Получает сообщения пользователя за диапазон дат"""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT id, user_id, message_id, date, timestamp, s3_key, transcription, text_content, message_type, created_at
                FROM user_messages 
                WHERE user_id = ? AND date BETWEEN ? AND ?
                ORDER BY created_at ASC
            """, (user_id, start_date, end_date))
            
            rows = await cursor.fetchall()
            messages = []
            
            for row in rows:
                message = UserMessage(
                    id=row[0],
                    user_id=row[1],
                    message_id=row[2],
                    date=row[3],
                    timestamp=row[4],
                    s3_key=row[5],
                    transcription=row[6],
                    text_content=row[7],
                    message_type=row[8] or "voice",
                    created_at=datetime.fromisoformat(row[9]) if row[9] else None
                )
                messages.append(message)
            
            return messages
    
    async def delete_old_messages(self, days_to_keep: int = 30):
        """Удаляет старые сообщения (старше указанного количества дней)"""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                DELETE FROM user_messages 
                WHERE created_at < datetime('now', '-{} days')
            """.format(days_to_keep))
            
            deleted_count = cursor.rowcount
            await db.commit()
            logger.info(f"Удалено {deleted_count} старых сообщений")
            return deleted_count


# Глобальный экземпляр сервиса базы данных
db_service = DatabaseService()
