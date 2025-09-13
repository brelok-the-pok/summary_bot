"""Основной файл запуска бота"""
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from .config.settings import TELEGRAM_TOKEN
from .handlers.command_handlers import start_command, transcribe_command, summary_command, messages_command
from .handlers.message_handlers import handle_voice_message, handle_text_message
from .handlers.callback_handlers import button_callback

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Основная функция запуска бота"""
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", start_command))
    application.add_handler(CommandHandler("transcribe", transcribe_command))
    application.add_handler(CommandHandler("summary", summary_command))
    application.add_handler(CommandHandler("messages", messages_command))
    
    # Добавляем обработчики callback запросов
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Добавляем обработчики сообщений
    application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # Запускаем бота
    logger.info("Запуск бота...")
    application.run_polling()


if __name__ == '__main__':
    main()
