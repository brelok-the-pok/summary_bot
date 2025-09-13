"""Утилиты для создания клавиатур"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu_keyboard():
    """Создает главное меню с кнопками"""
    keyboard = [
        [
            InlineKeyboardButton("🎵 Отправить голосовое", callback_data="voice_info"),
            InlineKeyboardButton("📝 Транскрипции", callback_data="transcribe")
        ],
        [
            InlineKeyboardButton("📊 Суммаризация", callback_data="summary"),
            InlineKeyboardButton("📋 Мои сообщения", callback_data="messages")
        ],
        [
            InlineKeyboardButton("ℹ️ Помощь", callback_data="help")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
