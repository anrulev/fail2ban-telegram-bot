#!/bin/bash

# Проверка статуса контейнера
echo "Проверка статуса контейнера..."
CONTAINER_STATUS=$(docker ps -f name=fail2ban-telegram-bot --format "{{.Status}}")

if [ -z "$CONTAINER_STATUS" ]; then
    echo "❌ Контейнер fail2ban-telegram-bot не запущен!"
    echo "Запустите контейнер командой: ./run.sh"
    exit 1
else
    echo "✅ Контейнер запущен: $CONTAINER_STATUS"
fi

# Проверка логов на наличие ошибок
echo -e "\nПроверка логов на наличие ошибок..."
ERROR_COUNT=$(docker logs fail2ban-telegram-bot 2>&1 | grep -i "error\|exception\|critical" | wc -l)

if [ $ERROR_COUNT -gt 0 ]; then
    echo "⚠️ В логах обнаружены ошибки ($ERROR_COUNT):"
    docker logs fail2ban-telegram-bot 2>&1 | grep -i "error\|exception\|critical" | tail -5
    echo "Для просмотра полных логов используйте: docker logs fail2ban-telegram-bot"
else
    echo "✅ Ошибок в логах не обнаружено"
fi

# Проверка доступа к лог-файлу Fail2Ban
echo -e "\nПроверка доступа к лог-файлу Fail2Ban..."
if [ ! -r /var/log/fail2ban.log ]; then
    echo "❌ Лог-файл /var/log/fail2ban.log недоступен для чтения!"
    echo "Выполните команду: sudo chmod a+r /var/log/fail2ban.log"
else
    echo "✅ Лог-файл Fail2Ban доступен для чтения"
    
    # Проверка, монтируется ли лог-файл в контейнер
    MOUNT_CHECK=$(docker exec fail2ban-telegram-bot ls -l /var/log/fail2ban.log 2>/dev/null)
    if [ $? -ne 0 ]; then
        echo "❌ Лог-файл не монтируется в контейнер!"
        echo "Проверьте настройки монтирования в docker-compose.yml"
    else
        echo "✅ Лог-файл корректно монтируется в контейнер"
    fi
fi

# Проверка переменных окружения
echo -e "\nПроверка переменных окружения..."
ENV_CHECK=$(docker exec fail2ban-telegram-bot env | grep -E "TELEGRAM_BOT_TOKEN|TELEGRAM_CHAT_ID|ENABLE_FAIL2BAN_STATUS|BOT_LOG_FILE")
if [[ $ENV_CHECK == *"TELEGRAM_BOT_TOKEN="* && $ENV_CHECK == *"TELEGRAM_CHAT_ID="* ]]; then
    echo "✅ Переменные окружения настроены"
else
    echo "❌ Переменные окружения не настроены корректно!"
    echo "Проверьте файл .env и перезапустите контейнер"
fi

echo -e "\n✨ Проверка завершена!"
echo "Для тестирования бота отправьте команду /start в Telegram" 