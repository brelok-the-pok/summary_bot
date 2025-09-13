"""Сервис для обработки голосовых сообщений"""
import logging
import requests
from typing import Optional
from telegram import Voice
from telegram.ext import ContextTypes

from ..config.settings import YANDEX_API_KEY, YANDEX_STT_URL
from ..config.messages import STT_ERROR

logger = logging.getLogger(__name__)


class VoiceProcessor:
    """Класс для обработки голосовых сообщений"""
    
    @staticmethod
    async def download_voice_file(voice: Voice, context: ContextTypes.DEFAULT_TYPE) -> bytes:
        """Скачивает голосовое сообщение"""
        file = await context.bot.get_file(voice.file_id)
        return await file.download_as_bytearray()
    
    @staticmethod
    async def transcribe_voice(audio_data: bytes) -> str:
        """Транскрибирует голосовое сообщение через Yandex SpeechKit HTTP API"""
        try:
            headers = {
                'Authorization': f'Api-Key {YANDEX_API_KEY}',
                'Content-Type': 'application/json'
            }

            response = requests.post(YANDEX_STT_URL, headers=headers, data=audio_data)
            logger.info(f"STT Response: {response.json()}")
            response.raise_for_status()
            
            # Извлекаем текст из ответа
            result = response.json()
            if 'result' in result:
                return result['result']
            else:
                return STT_ERROR
        except Exception as e:
            logger.error(f"Ошибка транскрибации: {e}")
            return STT_ERROR
