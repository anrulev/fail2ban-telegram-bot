# Fail2Ban Telegram Bot

![Язык-Русский](https://img.shields.io/badge/%D0%AF%D0%B7%D1%8B%D0%BA-%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-lightgrey?logo=google-translate&style=flat) [![Language-English](https://img.shields.io/badge/Language-English-blue?logo=google-translate&style=flat)](README.en.md)

Бот для мониторинга Fail2Ban и отправки уведомлений о блокировках в Telegram.

## Особенности

- 🔍 Мониторинг лог-файла Fail2Ban в реальном времени
- 🚨 Отправка уведомлений о новых блокировках в Telegram
- 📊 Команды для проверки статуса Fail2Ban
- 🔒 Просмотр информации о конкретных "тюрьмах" (jails)
- 🐳 Работает в Docker-контейнере
- 🧱 Опциональные команды статуса (требуют доступного `fail2ban-client`): включаются флагом `ENABLE_FAIL2BAN_STATUS=true`

## Требования

- Docker и Docker Compose (для запуска в контейнере)
- Fail2Ban, уже установленный и настроенный на хост-системе
- Токен Telegram бота и ID чата для отправки уведомлений

## Установка и запуск

### 1. Подготовка Telegram бота

1. Создайте Telegram бота через [@BotFather](https://t.me/BotFather):
   - Отправьте `/newbot` боту @BotFather
   - Следуйте инструкциям для создания бота
   - Сохраните полученный токен (выглядит как `123456789:ABCDefGhIJKlmNoPQRsTUVwxyZ`)

2. Определите ID чата для отправки уведомлений:
   - Для личного чата: отправьте сообщение боту [@userinfobot](https://t.me/userinfobot) и получите ваш ID
   - Для группы: добавьте [@RawDataBot](https://t.me/RawDataBot) в группу и найдите значение `"chat":{"id":`

### 2. Клонирование репозитория

```bash
git clone https://github.com/anrulev/fail2ban-telegram-bot.git
cd fail2ban-telegram-bot
```

### 3. Настройка переменных окружения

Создайте файл `.env` на основе примера:

```bash
cp .env.example .env
```

Отредактируйте файл `.env`, указав ваш токен бота и ID чата:

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
CHECK_INTERVAL=60
MAX_ALERTS_PER_RUN=10
# Включить команды /status и /jails, если доступен fail2ban-client
ENABLE_FAIL2BAN_STATUS=false
```

### 4. Запуск с использованием скрипта

Самый простой способ запустить бота - использовать скрипт `run.sh`:

```bash
chmod +x run.sh
./run.sh
```

Скрипт проверит наличие файла `.env`, создаст директорию для логов и запустит контейнер.

### 5. Запуск с использованием Docker Compose вручную

```bash
# Создание директории для логов
mkdir -p logs
chmod 755 logs

# Запуск контейнера
docker-compose up -d --build
```

### 6. Запуск с использованием Docker напрямую

```bash
# Сборка образа
docker build -t fail2ban-telegram-bot .

# Создание директории для логов
mkdir -p logs
chmod 755 logs

# Запуск контейнера
docker run -d \
  --name fail2ban-telegram-bot \
  --restart unless-stopped \
  -v /var/log/fail2ban.log:/var/log/fail2ban.log:ro \
  -v $(pwd)/logs:/app/logs \
  -e TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here \
  -e TELEGRAM_CHAT_ID=your_chat_id_here \
  -e FAIL2BAN_LOG_FILE=/var/log/fail2ban.log \
  -e CHECK_INTERVAL=60 \
  -e MAX_ALERTS_PER_RUN=10 \
  -e ENABLE_FAIL2BAN_STATUS=false \
  fail2ban-telegram-bot
```

## Использование

После запуска бот будет автоматически мониторить лог-файл Fail2Ban и отправлять уведомления о новых блокировках в указанный чат.

### Команды бота

- `/start` или `/help` - Показать справку
- `/status` - Показать общий статус Fail2Ban (если `ENABLE_FAIL2BAN_STATUS=true` и доступен `fail2ban-client`)
- `/jails` - Показать список активных "тюрем" (если `ENABLE_FAIL2BAN_STATUS=true` и доступен `fail2ban-client`)
- `/latest` - Показать последние блокировки

## Проверка работоспособности

Чтобы проверить, что бот работает корректно:

1. Отправьте команду `/start` боту в Telegram
2. Проверьте логи контейнера:
   ```bash
   docker logs fail2ban-telegram-bot
   ```
3. Для проверки уведомлений можно временно заблокировать какой-либо IP через Fail2Ban:
   ```bash
   sudo fail2ban-client set sshd banip 192.168.1.100
   ```

## Обновление

Для обновления бота:

```bash
# Остановка и удаление старого контейнера
docker-compose down

# Получение последних изменений
git pull

# Запуск нового контейнера
docker-compose up -d --build
```

## Устранение неполадок

### Бот не отправляет уведомления

- Проверьте, что токен бота и ID чата указаны правильно
- Убедитесь, что контейнер имеет доступ к лог-файлу Fail2Ban
- Проверьте логи контейнера на наличие ошибок:
  ```bash
  docker logs fail2ban-telegram-bot
  ```

### Включение команд /status и /jails

По умолчанию эти команды отключены. Чтобы их включить, установите `ENABLE_FAIL2BAN_STATUS=true` и смонтируйте сокет Fail2Ban из хоста в контейнер, а также добавьте в образ клиент:

1) (предпочтительно) Расширьте образ и установите `fail2ban-client` внутри контейнера:

```dockerfile
# Dockerfile.status
FROM fail2ban-telegram-bot:latest
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends fail2ban \
    && rm -rf /var/lib/apt/lists/*
USER botuser
```

Соберите образ и используйте его в docker-compose вместо базового.

2) Смонтируйте сокет `fail2ban` и включите флаг:

```yaml
services:
  fail2ban-bot:
    # image: ваш-расширенный-образ
    environment:
      - ENABLE_FAIL2BAN_STATUS=true
    volumes:
      - /var/run/fail2ban/fail2ban.sock:/var/run/fail2ban/fail2ban.sock:ro
```

Без доступа к сокету и наличия клиента команды `/status` и `/jails` работать не будут.

### Ошибка доступа к лог-файлу

Убедитесь, что пользователь, от имени которого запущен Docker, имеет права на чтение лог-файла Fail2Ban:

```bash
sudo chmod a+r /var/log/fail2ban.log
```

Или добавьте пользователя в группу, имеющую доступ к файлу:

```bash
# Узнать группу файла
ls -l /var/log/fail2ban.log

# Добавить пользователя в группу
sudo usermod -a -G имя_группы $(whoami)
```

### Контейнер не запускается

Проверьте логи Docker:

```bash
docker logs fail2ban-telegram-bot
```

Если проблема связана с правами доступа, попробуйте запустить контейнер с привилегированным режимом (не рекомендуется для продакшена):

```bash
docker-compose down
```

Отредактируйте `docker-compose.yml`, добавив:

```yaml
services:
  fail2ban-bot:
    # ... существующие настройки ...
    privileged: true
```

Затем запустите снова:

```bash
docker-compose up -d
```

## Лицензия

MIT 