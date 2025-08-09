#!/bin/bash

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo "Файл .env не найден. Создаю шаблон..."
    cat > .env <<'EOF'
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
CHECK_INTERVAL=60
MAX_ALERTS_PER_RUN=10
ENABLE_FAIL2BAN_STATUS=false
EOF
    echo "Пожалуйста, отредактируйте файл .env и укажите ваш токен бота и ID чата."
fi

# Создание директории для логов
mkdir -p logs
chmod 755 logs

# Подсказка по доступу к лог-файлу Fail2Ban
if [ ! -r /var/log/fail2ban.log ]; then
    echo "ВНИМАНИЕ: Лог-файл /var/log/fail2ban.log недоступен для чтения пользователем $(whoami)."
    echo "Решения:"
    echo "  1) sudo chmod a+r /var/log/fail2ban.log"
    echo "  2) sudo usermod -a -G $(stat -f %Sg /var/log/fail2ban.log) $(whoami); затем relogin"
    echo "  3) Временно запускать docker-compose с sudo"
fi

# Запуск контейнера
echo "Запуск Fail2Ban Telegram Bot..."
docker-compose up -d

echo "Проверка статуса..."
sleep 3
docker-compose ps

echo "Для просмотра логов используйте команду: docker-compose logs -f" 