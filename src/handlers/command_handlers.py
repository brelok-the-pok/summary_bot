"""Обработчики команд бота"""
import logging
from datetime import date
from telegram import Update
from telegram.ext import ContextTypes

from ..config.messages import (
    WELCOME_MESSAGE, 
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
    MESSAGE_ITEM
)
from ..config.messages import WORK_SUMMARIZATION_PROMPT
from ..utils.keyboards import get_main_menu_keyboard
from ..utils.storage import get_user_messages, get_user_transcriptions, has_user_messages
from ..services.message_summarizer import MessageSummarizer

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        WELCOME_MESSAGE,
        reply_markup=get_main_menu_keyboard()
    )


async def transcribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /transcribe"""
    user_id = str(update.effective_user.id)
    today = date.today().strftime('%Y-%m-%d')
    
    if not await has_user_messages(user_id, today):
        await update.message.reply_text(NO_MESSAGES_TODAY)
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
        await update.message.reply_text(result)
    else:
        await update.message.reply_text(NO_TRANSCRIPTIONS)


async def summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /summary"""
    user_id = str(update.effective_user.id)
    today = date.today().strftime('%Y-%m-%d')
    
    if not await has_user_messages(user_id, today):
        await update.message.reply_text(NO_MESSAGES_FOR_SUMMARY)
        return
    
    transcriptions = await get_user_transcriptions(user_id, today)
    
    if not transcriptions:
        await update.message.reply_text(NO_TRANSCRIPTIONS_FOR_SUMMARY)
        return
    
    # Показываем индикатор загрузки
    processing_msg = await update.message.reply_text(CREATING_SUMMARY)
    
    summary = await MessageSummarizer.summarize_messages(transcriptions)
    
    # Удаляем индикатор загрузки
    await processing_msg.delete()
    
    # Отправляем результат
    await update.message.reply_text(SUMMARY_HEADER.format(date=today) + summary)

async def work_summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /summary"""
    user_id = str(update.effective_user.id)
    today = date.today().strftime('%Y-%m-%d')
    
    if not await has_user_messages(user_id, today):
        await update.message.reply_text(NO_MESSAGES_FOR_SUMMARY)
        return
    
    transcriptions = await get_user_transcriptions(user_id, today)
    
    if not transcriptions:
        await update.message.reply_text(NO_TRANSCRIPTIONS_FOR_SUMMARY)
        return
    
    # Показываем индикатор загрузки
    processing_msg = await update.message.reply_text(CREATING_SUMMARY)
    
    summary = await MessageSummarizer.summarize_messages(transcriptions, WORK_SUMMARIZATION_PROMPT)
    
    # Удаляем индикатор загрузки
    await processing_msg.delete()
    
    # Отправляем результат
    await update.message.reply_text(SUMMARY_HEADER.format(date=today) + summary)


async def messages_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /messages"""
    user_id = str(update.effective_user.id)
    today = date.today().strftime('%Y-%m-%d')
    
    if not await has_user_messages(user_id, today):
        await update.message.reply_text(NO_MESSAGES_FOR_DISPLAY)
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
    
    await update.message.reply_text(messages_text)
