# Fail2Ban Telegram Bot

[![Язык-Русский](https://img.shields.io/badge/%D0%AF%D0%B7%D1%8B%D0%BA-%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-green?logo=google-translate&style=flat)](README.md) ![Language-English](https://img.shields.io/badge/Language-English-lightgrey?logo=google-translate&style=flat)

Bot for monitoring Fail2Ban and sending ban notifications to Telegram.

## Features

- 🔍 Real-time monitoring of the Fail2Ban log file
- 🚨 Sending notifications about new bans to Telegram
- 📊 Commands to check Fail2Ban status
- 🔒 View information about specific jails
- 🐳 Runs in a Docker container
- 🧱 Optional status commands (require accessible `fail2ban-client`): enabled via `ENABLE_FAIL2BAN_STATUS=true`

## Requirements

- Docker and Docker Compose (to run in a container)
- Fail2Ban installed and configured on the host system
- Telegram bot token and chat ID for notifications

## Installation and Run

### 1. Prepare the Telegram bot

1. Create a Telegram bot via [@BotFather](https://t.me/BotFather):
   - Send `/newbot` to @BotFather
   - Follow the instructions to create the bot
   - Save the token (looks like `123456789:ABCDefGhIJKlmNoPQRsTUVwxyZ`)

2. Get a chat ID for notifications:
   - For a private chat: send any message to [@userinfobot](https://t.me/userinfobot) to get your ID
   - For a group: add [@RawDataBot](https://t.me/RawDataBot) to the group and find the value of `"chat":{"id":`

### 2. Clone the repository

```bash
git clone https://github.com/anrulev/fail2ban-telegram-bot.git
cd fail2ban-telegram-bot
```

### 3. Configure environment variables

Create a `.env` file based on the example:

```bash
cp .env.example .env
```

Edit `.env` and set your bot token and chat ID:

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
CHECK_INTERVAL=60
MAX_ALERTS_PER_RUN=10
# Optional: server name (auto-detected from system)
HOSTNAME=your-server-name
# Enable /status and /jails if fail2ban-client is available
ENABLE_FAIL2BAN_STATUS=false
```

### 4. Run using the helper script

The simplest way to start the bot is to use `run.sh`:

```bash
chmod +x run.sh
./run.sh
```

The script will check for `.env`, create a logs directory, and start the container.

### 5. Run with Docker Compose manually

```bash
# Create logs directory
mkdir -p logs
chmod 755 logs

# Start the container
docker-compose up -d --build
```

### 6. Run with Docker directly

```bash
# Build image
docker build -t fail2ban-telegram-bot .

# Create logs directory
mkdir -p logs
chmod 755 logs

# Run container
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
  -e HOSTNAME=your-server-name \
  -e ENABLE_FAIL2BAN_STATUS=false \
  fail2ban-telegram-bot
```

## Usage

After starting, the bot automatically monitors the Fail2Ban log file and sends notifications about new bans to the specified chat.

### Bot commands

- `/start` or `/help` - Show help
- `/status` - Show overall Fail2Ban status (if `ENABLE_FAIL2BAN_STATUS=true` and `fail2ban-client` is available)
- `/jails` - Show active jails (if `ENABLE_FAIL2BAN_STATUS=true` and `fail2ban-client` is available)
- `/latest` - Show latest bans

## Health check

To verify the bot works correctly:

1. Send `/start` to the bot in Telegram
2. Check container logs:
   ```bash
   docker logs fail2ban-telegram-bot
   ```
3. To test notifications you can temporarily ban an IP via Fail2Ban:
   ```bash
   sudo fail2ban-client set sshd banip 192.168.1.100
   ```

## Update

To update the bot:

```bash
# Stop and remove old container
docker-compose down

# Pull latest changes
git pull

# Start new container
docker-compose up -d --build
```

## Troubleshooting

### Bot does not send notifications

- Ensure the bot token and chat ID are correct
- Ensure the container has access to the Fail2Ban log file
- Check container logs for errors:
  ```bash
  docker logs fail2ban-telegram-bot
  ```

### Enabling /status and /jails commands

By default these commands are disabled. To enable them, set `ENABLE_FAIL2BAN_STATUS=true`, mount the Fail2Ban socket from host into the container, and also add the client into the image:

1) (preferred) Extend the image and install `fail2ban-client` inside the container:

```dockerfile
# Dockerfile.status
FROM fail2ban-telegram-bot:latest
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends fail2ban \
    && rm -rf /var/lib/apt/lists/*
USER botuser
```

Build the image and use it in docker-compose instead of the base one.

2) Mount the `fail2ban` socket and enable the flag:

```yaml
services:
  fail2ban-bot:
    # image: your-extended-image
    environment:
      - ENABLE_FAIL2BAN_STATUS=true
    volumes:
      - /var/run/fail2ban/fail2ban.sock:/var/run/fail2ban/fail2ban.sock:ro
```

Without access to the socket and the client present, `/status` and `/jails` will not work.

### Log file access error

Make sure the user running Docker has read access to the Fail2Ban log file:

```bash
sudo chmod a+r /var/log/fail2ban.log
```

Or add the user to the group that has access to the file:

```bash
# Check the file's group
ls -l /var/log/fail2ban.log

# Add the user to the group
sudo usermod -a -G group_name $(whoami)
```

### Container does not start

Check Docker logs:

```bash
docker logs fail2ban-telegram-bot
```

If the issue is related to permissions, try running the container in privileged mode (not recommended for production):

```bash
docker-compose down
```

Edit `docker-compose.yml` by adding:

```yaml
services:
  fail2ban-bot:
    # ... existing settings ...
    privileged: true
```

Then start again:

```bash
docker-compose up -d
```

<details>
  <summary>For maintainers</summary>

- Docker Hub publishing docs: [`docs/maintainers/DOCKER_HUB.md`](docs/maintainers/DOCKER_HUB.md)
- Helper scripts: [`scripts/maintainers/`](scripts/maintainers/)

</details>

## License

MIT