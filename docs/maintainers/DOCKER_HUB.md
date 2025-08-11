# Fail2Ban Telegram Bot — Docker Hub (для мейнтейнеров)

Этот документ предназначен для мейнтейнеров репозитория. Не публикуется в основном README.

## Что делает этот образ

Этот Docker-образ запускает Telegram-бота, который:
- 🔍 Мониторит лог-файл Fail2Ban в реальном времени
- 🚨 Отправляет уведомления о новых блокировках в Telegram
- 📊 Предоставляет команды для проверки статуса Fail2Ban
- 🔒 Позволяет просматривать информацию о конкретных "тюрьмах" (jails)

## Как использовать этот образ

### Предварительные требования

- Fail2Ban, уже установленный и настроенный на хост-системе
- Токен Telegram бота (получите через [@BotFather](https://t.me/BotFather))
- ID чата для отправки уведомлений

### Быстрый старт

```bash
docker run -d \
  --name fail2ban-telegram-bot \
  --restart unless-stopped \
  -v /var/log/fail2ban.log:/var/log/fail2ban.log:ro \
  -e TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here \
  -e TELEGRAM_CHAT_ID=your_chat_id_here \
  yourusername/fail2ban-telegram-bot
```

### Запуск с использованием Docker Compose

Создайте файл `docker-compose.yml`:

```yaml
version: '3'

services:
  fail2ban-bot:
    image: yourusername/fail2ban-telegram-bot
    container_name: fail2ban-telegram-bot
    restart: unless-stopped
    volumes:
      - /var/log/fail2ban.log:/var/log/fail2ban.log:ro
      - ./logs:/app/logs
    environment:
      - TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
      - TELEGRAM_CHAT_ID=your_chat_id_here
      - FAIL2BAN_LOG_FILE=/var/log/fail2ban.log
      - CHECK_INTERVAL=60
      - MAX_ALERTS_PER_RUN=10
```

Затем запустите:

```bash
mkdir -p logs
docker-compose up -d
```

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `TELEGRAM_BOT_TOKEN` | Токен Telegram бота | (обязательно) |
| `TELEGRAM_CHAT_ID` | ID чата для отправки уведомлений | (обязательно) |
| `FAIL2BAN_LOG_FILE` | Путь к лог-файлу Fail2Ban внутри контейнера | `/var/log/fail2ban.log` |
| `CHECK_INTERVAL` | Интервал проверки лога (в секундах) | `60` |
| `MAX_ALERTS_PER_RUN` | Максимальное количество уведомлений за одну проверку | `10` |
| `ENABLE_FAIL2BAN_STATUS` | Включить команды `/status` и `/jails` (требуется доступ к `fail2ban-client`) | `false` |
| `BOT_LOG_FILE` | Путь к лог-файлу бота | `/app/logs/fail2ban_bot.log` |

## Тома (Volumes)

| Путь в контейнере | Описание |
|-------------------|----------|
| `/var/log/fail2ban.log` | Лог-файл Fail2Ban (только для чтения) |
| `/app/logs` | Директория для логов самого бота |

## Команды бота

- `/start` или `/help` - Показать справку
- `/status` - Показать общий статус Fail2Ban
- `/jails` - Показать список активных "тюрем" (jails)
- `/latest` - Показать последние блокировки

## Безопасность

- Контейнер запускается от имени непривилегированного пользователя
- Лог-файл Fail2Ban монтируется только для чтения
- Не требуется доступ к сокету Fail2Ban или другим системным ресурсам

## Примечания

- Этот образ не устанавливает и не настраивает Fail2Ban. Предполагается, что Fail2Ban уже установлен и настроен на хост-системе.
- Контейнер должен иметь доступ к лог-файлу Fail2Ban. Убедитесь, что файл доступен для чтения:
  ```bash
  sudo chmod a+r /var/log/fail2ban.log
  ```

## Устранение неполадок

### Бот не отправляет уведомления

- Проверьте, что токен бота и ID чата указаны правильно
- Убедитесь, что контейнер имеет доступ к лог-файлу Fail2Ban
- Проверьте логи контейнера:
  ```bash
  docker logs fail2ban-telegram-bot
  ```

### Ошибка доступа к лог-файлу

Если контейнер не может прочитать лог-файл Fail2Ban, вы можете:

1. Изменить права доступа к файлу:
   ```bash
   sudo chmod a+r /var/log/fail2ban.log
   ```

2. Или запустить контейнер с привилегированным режимом (не рекомендуется для продакшена):
   ```yaml
   services:
     fail2ban-bot:
       # ... существующие настройки ...
       privileged: true
   ```

## Исходный код

Исходный код доступен на [GitHub](https://github.com/anrulev/fail2ban-telegram-bot).


