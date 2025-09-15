"""Утилиты для создания клавиатур"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu_keyboard():
    """Создает главное меню с кнопками"""
    keyboard = [
        [
            InlineKeyboardButton("🎵 Отправить голосовое", callback_data="voice_info"),
            InlineKeyboardButton("📝 Транскрибации", callback_data="transcribe"),
        ],
        [
            InlineKeyboardButton("📊 Личная суммаризация", callback_data="personal_summary"),
            InlineKeyboardButton("📋 Все сообщения", callback_data="messages")
        ],
        [
            InlineKeyboardButton("📊 Рабочая суммаризация", callback_data="work_summary")
        ],
        [
            InlineKeyboardButton("ℹ️ Помощь", callback_data="help")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
