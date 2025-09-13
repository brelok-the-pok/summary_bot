"""Сервис для загрузки файлов в S3"""
import logging
import boto3
from datetime import date
from typing import Optional

from ..config.settings import (
    AWS_ACCESS_KEY_ID, 
    AWS_SECRET_ACCESS_KEY, 
    AWS_REGION, 
    S3_BUCKET_NAME
)
from ..config.messages import S3_ERROR

logger = logging.getLogger(__name__)


class S3Uploader:
    """Класс для загрузки файлов в S3"""
    
    def __init__(self):
        """Инициализация S3 клиента"""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
            endpoint_url='https://storage.yandexcloud.net'
        )
    
    async def upload_voice_file(self, audio_data: bytes, user_id: int, message_id: int) -> str:
        """Загружает голосовое сообщение в S3"""
        try:
            today = date.today().strftime('%Y-%m-%d')
            key = f"voice_messages/{user_id}/{today}/{message_id}.ogg"
            
            self.s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=key,
                Body=audio_data,
                ContentType='audio/ogg'
            )
            
            return key
        except Exception as e:
            logger.error(f"Ошибка загрузки в S3: {e}")
            return ""
