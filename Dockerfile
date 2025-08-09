FROM python:3.12-slim

LABEL maintainer="Your Name <your.email@example.com>"
LABEL description="Telegram bot for Fail2Ban monitoring and notifications"
LABEL version="1.0"

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --upgrade pip

# Копирование кода бота
COPY fail2ban-telegram-bot.py .

# Создание директорий для логов
RUN mkdir -p /var/log /app/logs && touch /var/log/fail2ban.log && \
    chmod 644 /var/log/fail2ban.log

# Настройка переменных окружения по умолчанию
ENV TELEGRAM_BOT_TOKEN=""
ENV TELEGRAM_CHAT_ID=""
ENV FAIL2BAN_LOG_FILE="/var/log/fail2ban.log"
ENV CHECK_INTERVAL="60"
ENV MAX_ALERTS_PER_RUN="10"
ENV ENABLE_FAIL2BAN_STATUS="false"
ENV BOT_LOG_FILE="/app/logs/fail2ban_bot.log"

# Создание пользователя без привилегий
RUN adduser --disabled-password --gecos "" botuser && \
    chown -R botuser:botuser /app /var/log /app/logs
USER botuser

# Запуск бота
CMD ["python", "fail2ban-telegram-bot.py"] 