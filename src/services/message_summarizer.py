"""Сервис для суммаризации сообщений"""
import logging
import requests
from typing import List

from ..config.settings import YANDEX_API_KEY, YANDEX_FOLDER_ID, YANDEX_GPT_URL
from ..config.messages import SUMMARIZATION_PROMPT, GPT_ERROR, SUMMARIZATION_ERROR, WORK_SUMMARIZATION_PROMPT

logger = logging.getLogger(__name__)





class MessageSummarizer:
    """Класс для суммаризации сообщений через Yandex GPT"""
    
    @staticmethod
    async def summarize_messages(messages: List[str], promt=SUMMARIZATION_PROMPT) -> str:
        """Создает суммаризацию сообщений через Yandex GPT HTTP API"""
        try:
            if not messages:
                return "Нет сообщений для суммаризации"
            
            # Объединяем все сообщения
            formated_messages = ''
            for i, message in enumerate(messages):
                formated_messages += f'Сообщение №{i}: {message}'
            
            prompt = promt.format(combined_text=formated_messages)

            # Заголовки для запроса
            headers = {
                'Authorization': f'Api-Key {YANDEX_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            # Тело запроса для Yandex GPT
            data = {
                "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt",
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.7,
                    "maxTokens": 1000
                },
                "messages": [
                    {
                        "role": "system",
                        "text": "Ты помощник для суммаризации голосовых и текстовых сообщений. Отвечай на русском языке."
                    },
                    {
                        "role": "user",
                        "text": prompt
                    }
                ]
            }
            
            # Выполняем HTTP запрос
            response = requests.post(YANDEX_GPT_URL, headers=headers, json=data)
            response.raise_for_status()
            
            # Извлекаем текст из ответа
            result = response.json()
            
            if 'result' in result and 'alternatives' in result['result']:
                return result['result']['alternatives'][0]['message']['text']
            else:
                return GPT_ERROR
            
        except Exception as e:
            logger.error(f"Ошибка суммаризации: {e}")
            return SUMMARIZATION_ERROR
    
    @staticmethod
    async def summarize_work_messages(messages: List[str]) -> str:
        """Создает рабочую суммаризацию сообщений через Yandex GPT HTTP API"""
        return await MessageSummarizer.summarize_messages(messages, WORK_SUMMARIZATION_PROMPT)
