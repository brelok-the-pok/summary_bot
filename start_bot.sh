#!/bin/bash

# Скрипт для запуска Telegram бота на Ubuntu 24
# Использование: ./start_bot.sh [start|stop|restart|status|logs]

BOT_DIR="/opt/summary_bot"
BOT_USER="botuser"
SERVICE_NAME="summary-bot"
SCREEN_SESSION="summary_bot"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Проверка прав root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "Этот скрипт должен быть запущен с правами root (sudo)"
        exit 1
    fi
}

# Создание пользователя для бота
create_bot_user() {
    if ! id "$BOT_USER" &>/dev/null; then
        log "Создание пользователя $BOT_USER..."
        useradd -r -s /bin/bash -d "$BOT_DIR" "$BOT_USER"
        mkdir -p "$BOT_DIR"
        chown -R "$BOT_USER:$BOT_USER" "$BOT_DIR"
    else
        log "Пользователь $BOT_USER уже существует"
    fi
}

# Установка зависимостей
install_dependencies() {
    log "Обновление пакетов..."
    apt update
    
    log "Установка Python и зависимостей..."
    apt install -y python3 python3-pip python3-venv screen htop
    
    # Установка ffmpeg для обработки аудио
    apt install -y ffmpeg
}

# Настройка виртуального окружения
setup_venv() {
    log "Настройка виртуального окружения..."
    cd "$BOT_DIR"
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    chown -R "$BOT_USER:$BOT_USER" "$BOT_DIR"
}

# Создание systemd service
create_systemd_service() {
    log "Создание systemd service..."
    
    cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=Summary Bot Telegram
After=network.target

[Service]
Type=simple
User=$BOT_USER
WorkingDirectory=$BOT_DIR
Environment=PATH=$BOT_DIR/venv/bin
ExecStart=$BOT_DIR/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"
}

# Создание скрипта для запуска через screen
create_screen_script() {
    log "Создание скрипта для screen..."
    
    cat > "$BOT_DIR/run_bot_screen.sh" << 'EOF'
#!/bin/bash
cd /opt/summary_bot
source venv/bin/activate
python main.py
EOF

    chmod +x "$BOT_DIR/run_bot_screen.sh"
    chown "$BOT_USER:$BOT_USER" "$BOT_DIR/run_bot_screen.sh"
}

# Функции управления
start_bot() {
    log "Запуск бота..."
    
    # Проверяем, запущен ли уже бот
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        warning "Бот уже запущен через systemd"
        return 0
    fi
    
    # Запускаем через systemd
    systemctl start "$SERVICE_NAME"
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log "Бот успешно запущен через systemd"
    else
        error "Ошибка запуска бота через systemd"
        systemctl status "$SERVICE_NAME"
        return 1
    fi
}

stop_bot() {
    log "Остановка бота..."
    systemctl stop "$SERVICE_NAME"
    log "Бот остановлен"
}

restart_bot() {
    log "Перезапуск бота..."
    systemctl restart "$SERVICE_NAME"
    log "Бот перезапущен"
}

status_bot() {
    log "Статус бота:"
    systemctl status "$SERVICE_NAME" --no-pager
}

show_logs() {
    log "Последние логи бота:"
    journalctl -u "$SERVICE_NAME" -f --no-pager
}

# Запуск через screen (альтернативный способ)
start_screen() {
    log "Запуск бота через screen..."
    
    # Проверяем, есть ли уже сессия
    if screen -list | grep -q "$SCREEN_SESSION"; then
        warning "Сессия $SCREEN_SESSION уже существует"
        log "Для подключения к сессии используйте: screen -r $SCREEN_SESSION"
        return 0
    fi
    
    # Запускаем новую сессию screen
    sudo -u "$BOT_USER" screen -dmS "$SCREEN_SESSION" "$BOT_DIR/run_bot_screen.sh"
    
    if screen -list | grep -q "$SCREEN_SESSION"; then
        log "Бот запущен в screen сессии: $SCREEN_SESSION"
        log "Для подключения к сессии используйте: screen -r $SCREEN_SESSION"
        log "Для отключения от сессии нажмите Ctrl+A, затем D"
    else
        error "Ошибка запуска бота в screen"
        return 1
    fi
}

stop_screen() {
    log "Остановка screen сессии..."
    screen -S "$SCREEN_SESSION" -X quit
    log "Screen сессия остановлена"
}

# Установка бота
install_bot() {
    log "Начинаем установку бота..."
    
    check_root
    create_bot_user
    install_dependencies
    
    # Копируем файлы бота
    log "Копирование файлов бота..."
    cp -r . "$BOT_DIR/"
    chown -R "$BOT_USER:$BOT_USER" "$BOT_DIR"
    
    setup_venv
    create_systemd_service
    create_screen_script
    
    log "Установка завершена!"
    log "Не забудьте настроить переменные окружения в файле $BOT_DIR/.env"
    log "Для запуска используйте: sudo ./start_bot.sh start"
}

# Основная логика
case "${1:-}" in
    "install")
        install_bot
        ;;
    "start")
        check_root
        start_bot
        ;;
    "stop")
        check_root
        stop_bot
        ;;
    "restart")
        check_root
        restart_bot
        ;;
    "status")
        check_root
        status_bot
        ;;
    "logs")
        check_root
        show_logs
        ;;
    "screen")
        check_root
        start_screen
        ;;
    "stop-screen")
        check_root
        stop_screen
        ;;
    *)
        echo "Использование: $0 {install|start|stop|restart|status|logs|screen|stop-screen}"
        echo ""
        echo "Команды:"
        echo "  install     - Установка бота на сервер"
        echo "  start       - Запуск бота через systemd"
        echo "  stop        - Остановка бота"
        echo "  restart     - Перезапуск бота"
        echo "  status      - Показать статус бота"
        echo "  logs        - Показать логи бота в реальном времени"
        echo "  screen      - Запуск бота через screen (альтернативный способ)"
        echo "  stop-screen - Остановка screen сессии"
        echo ""
        echo "Примеры использования:"
        echo "  sudo ./start_bot.sh install    # Первоначальная установка"
        echo "  sudo ./start_bot.sh start      # Запуск бота"
        echo "  sudo ./start_bot.sh screen     # Запуск через screen"
        echo "  screen -r summary_bot          # Подключение к screen сессии"
        exit 1
        ;;
esac
