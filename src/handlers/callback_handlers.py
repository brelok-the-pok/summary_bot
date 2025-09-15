"""Обработчики callback запросов от кнопок"""
import logging
from datetime import date
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from ..config.messages import (
    VOICE_INFO_MESSAGE,
    NO_MESSAGES_TODAY,
    NO_MESSAGES_FOR_SUMMARY,
    NO_TRANSCRIPTIONS,
    NO_TRANSCRIPTIONS_FOR_SUMMARY,
    NO_MESSAGES_FOR_DISPLAY,
    CREATING_SUMMARY,
    TRANSCRIPTIONS_HEADER,
    TRANSCRIPTION_ITEM,
    SUMMARY_HEADER,
    MESSAGES_HEADER,
    MESSAGE_ITEM,
    HELP_MESSAGE
)
from ..utils.keyboards import get_main_menu_keyboard
from ..utils.storage import get_user_messages, get_user_transcriptions, has_user_messages
from ..services.message_summarizer import MessageSummarizer

logger = logging.getLogger(__name__)


async def safe_edit_message(query, text, reply_markup=None):
    """Безопасное редактирование сообщения с обработкой ошибок"""
    try:
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup
        )
    except BadRequest as e:
        if "Message is not modified" in str(e):
            # Сообщение не изменилось, это нормально
            logger.debug("Message content unchanged, skipping edit")
        else:
            # Другая ошибка, логируем и пробрасываем
            logger.error(f"Error editing message: {e}")
            raise


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки меню"""
    query = update.callback_query
    await query.answer()
    
    user_id = str(update.effective_user.id)
    today = date.today().strftime('%Y-%m-%d')
    
    if query.data == "voice_info":
        await safe_edit_message(
            query,
            VOICE_INFO_MESSAGE,
            reply_markup=get_main_menu_keyboard()
        )
    
    elif query.data == "transcribe":
        if not await has_user_messages(user_id, today):
            await safe_edit_message(
                query,
                NO_MESSAGES_TODAY,
                reply_markup=get_main_menu_keyboard()
            )
            return
        
        messages = await get_user_messages(user_id, today)
        
        # Получаем транскрипции и текстовые сообщения
        transcriptions = []
        for msg in messages:
            if msg.get('message_type') == 'voice' and msg.get('transcription'):
                transcriptions.append(TRANSCRIPTION_ITEM.format(transcription=msg['transcription']))
            elif msg.get('message_type') == 'text' and msg.get('text_content'):
                transcriptions.append(TRANSCRIPTION_ITEM.format(transcription=msg['text_content']))
        
        if transcriptions:
            result = TRANSCRIPTIONS_HEADER + "\n\n".join(transcriptions)
            await safe_edit_message(
                query,
                result,
                reply_markup=get_main_menu_keyboard()
            )
        else:
            await safe_edit_message(
                query,
                NO_TRANSCRIPTIONS,
                reply_markup=get_main_menu_keyboard()
            )
    
    elif query.data == "summary":
        if not await has_user_messages(user_id, today):
            await safe_edit_message(
                query,
                NO_MESSAGES_FOR_SUMMARY,
                reply_markup=get_main_menu_keyboard()
            )
            return
        
        transcriptions = await get_user_transcriptions(user_id, today)
        
        if not transcriptions:
            await safe_edit_message(
                query,
                NO_TRANSCRIPTIONS_FOR_SUMMARY,
                reply_markup=get_main_menu_keyboard()
            )
            return
        
        # Показываем индикатор загрузки
        await safe_edit_message(
            query,
            CREATING_SUMMARY,
            reply_markup=get_main_menu_keyboard()
        )
        
        # Создаем суммаризацию
        summary = await MessageSummarizer.summarize_messages(transcriptions)
        
        # Отправляем результат
        await safe_edit_message(
            query,
            SUMMARY_HEADER.format(date=today) + summary,
            reply_markup=get_main_menu_keyboard()
        )
    
    elif query.data == "messages":
        if not await has_user_messages(user_id, today):
            await safe_edit_message(
                query,
                NO_MESSAGES_FOR_DISPLAY,
                reply_markup=get_main_menu_keyboard()
            )
            return
        
        messages = await get_user_messages(user_id, today)
        messages_text = MESSAGES_HEADER.format(date=today)
        
        for i, msg in enumerate(messages, 1):
            timestamp = msg.get('timestamp', 'Неизвестно')
            message_type = msg.get('message_type', 'voice')
            
            if message_type == 'voice':
                content = msg.get('transcription', 'Не распознано')
                prefix = "🎵"
            else:
                content = msg.get('text_content', 'Пустое сообщение')
                prefix = "📝"
            
            messages_text += f"{i}. {timestamp}\n{prefix} {content}\n\n"
        
        await safe_edit_message(
            query,
            messages_text,
            reply_markup=get_main_menu_keyboard()
        )
    
    elif query.data == "help":
        await safe_edit_message(
            query,
            HELP_MESSAGE,
            reply_markup=get_main_menu_keyboard()
        )
