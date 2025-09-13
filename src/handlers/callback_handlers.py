"""Обработчики callback запросов от кнопок"""
import logging
from datetime import date
from telegram import Update
from telegram.ext import ContextTypes

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


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки меню"""
    query = update.callback_query
    await query.answer()
    
    user_id = str(update.effective_user.id)
    today = date.today().strftime('%Y-%m-%d')
    
    if query.data == "voice_info":
        await query.edit_message_text(
            VOICE_INFO_MESSAGE,
            reply_markup=get_main_menu_keyboard()
        )
    
    elif query.data == "transcribe":
        if not has_user_messages(user_id, today):
            await query.edit_message_text(
                NO_MESSAGES_TODAY,
                reply_markup=get_main_menu_keyboard()
            )
            return
        
        messages = get_user_messages(user_id, today)
        
        # Получаем транскрипции
        transcriptions = []
        for msg in messages:
            if 'transcription' in msg:
                transcriptions.append(TRANSCRIPTION_ITEM.format(transcription=msg['transcription']))
        
        if transcriptions:
            result = TRANSCRIPTIONS_HEADER + "\n\n".join(transcriptions)
            await query.edit_message_text(
                result,
                reply_markup=get_main_menu_keyboard()
            )
        else:
            await query.edit_message_text(
                NO_TRANSCRIPTIONS,
                reply_markup=get_main_menu_keyboard()
            )
    
    elif query.data == "summary":
        if not has_user_messages(user_id, today):
            await query.edit_message_text(
                NO_MESSAGES_FOR_SUMMARY,
                reply_markup=get_main_menu_keyboard()
            )
            return
        
        transcriptions = get_user_transcriptions(user_id, today)
        
        if not transcriptions:
            await query.edit_message_text(
                NO_TRANSCRIPTIONS_FOR_SUMMARY,
                reply_markup=get_main_menu_keyboard()
            )
            return
        
        # Показываем индикатор загрузки
        await query.edit_message_text(
            CREATING_SUMMARY,
            reply_markup=get_main_menu_keyboard()
        )
        
        # Создаем суммаризацию
        summary = await MessageSummarizer.summarize_messages(transcriptions)
        
        # Отправляем результат
        await query.edit_message_text(
            SUMMARY_HEADER.format(date=today) + summary,
            reply_markup=get_main_menu_keyboard()
        )
    
    elif query.data == "messages":
        if not has_user_messages(user_id, today):
            await query.edit_message_text(
                NO_MESSAGES_FOR_DISPLAY,
                reply_markup=get_main_menu_keyboard()
            )
            return
        
        messages = get_user_messages(user_id, today)
        messages_text = MESSAGES_HEADER.format(date=today)
        
        for i, msg in enumerate(messages, 1):
            timestamp = msg.get('timestamp', 'Неизвестно')
            transcription = msg.get('transcription', 'Не распознано')
            messages_text += MESSAGE_ITEM.format(
                index=i, 
                timestamp=timestamp, 
                transcription=transcription
            )
        
        await query.edit_message_text(
            messages_text,
            reply_markup=get_main_menu_keyboard()
        )
    
    elif query.data == "help":
        await query.edit_message_text(
            HELP_MESSAGE,
            reply_markup=get_main_menu_keyboard()
        )
