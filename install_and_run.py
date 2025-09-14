#!/usr/bin/env python3
"""
Скрипт для установки зависимостей и запуска бота
"""

import subprocess
import sys
import os

def install_requirements():
    """Устанавливает зависимости"""
    print("📦 Устанавливаю зависимости...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Зависимости установлены успешно")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки зависимостей: {e}")
        return False

def check_env_file():
    """Проверяет наличие .env файла"""
    if not os.path.exists('.env'):
        print("⚠️ Файл .env не найден!")
        print("Создайте файл .env на основе env_example.txt")
        print("И заполните необходимые переменные окружения")
        return False
    return True

def main():
    """Основная функция"""
    print("🚀 Установка и запуск телеграм бота\n")
    
    # Проверяем .env файл
    if not check_env_file():
        return
    
    # Устанавливаем зависимости
    if not install_requirements():
        return
    
    print("\n🤖 Запускаю бота...")
    try:
        # Импортируем и запускаем main
        from src.main import run_bot
        run_bot()
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка запуска бота: {e}")

if __name__ == '__main__':
    main()
