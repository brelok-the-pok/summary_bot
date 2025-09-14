"""Обработчики сообщений бота"""
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from ..config.messages import (
    TEXT_MESSAGE_RESPONSE,
    PROCESSING_VOICE,
    VOICE_ERROR
)
from ..utils.keyboards import get_main_menu_keyboard
from ..utils.storage import add_user_message
from ..services.voice_processor import VoiceProcessor
from ..services.s3_uploader import S3Uploader

logger = logging.getLogger(__name__)

# Инициализируем S3 загрузчик
s3_uploader = S3Uploader()


async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик голосовых сообщений"""
    user_id = str(update.effective_user.id)
    message_id = update.message.message_id
    
    # Показываем индикатор обработки
    processing_msg = await update.message.reply_text(PROCESSING_VOICE)
    
    try:
        # Скачиваем голосовое сообщение
        audio_data = await VoiceProcessor.download_voice_file(update.message.voice, context)
        
        # Загружаем в S3
        s3_key = await s3_uploader.upload_voice_file(audio_data, update.effective_user.id, message_id)
        
        # Транскрибируем
        transcription = await VoiceProcessor.transcribe_voice(audio_data)
        
        # Сохраняем в базе данных
        message_data = {
            'message_id': message_id,
            'timestamp': datetime.now().isoformat(),
            's3_key': s3_key,
            'transcription': transcription
        }
        await add_user_message(user_id, message_data)
        
        # Удаляем индикатор загрузки
        await processing_msg.delete()
        
        # Отправляем результат
        await update.message.reply_text(
            transcription,
            reply_markup=get_main_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Ошибка обработки голосового сообщения: {e}")
        await processing_msg.edit_text(VOICE_ERROR)


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    await update.message.reply_text(
        TEXT_MESSAGE_RESPONSE,
        reply_markup=get_main_menu_keyboard()
    )
