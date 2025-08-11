#!/bin/bash

# Внутренний скрипт для мейнтейнеров: подсказки по настройке GitHub remote

set -euo pipefail

echo "Настройка GitHub репозитория для fail2ban-telegram-bot"
echo "=================================================="

if [ ! -f "fail2ban-telegram-bot.py" ]; then
  echo "❌ Ошибка: запустите скрипт из директории проекта"
  exit 1
fi

if [ ! -d ".git" ]; then
  echo "❌ Git не инициализирован. Сначала выполните: git init"
  exit 1
fi

if git remote get-url origin >/dev/null 2>&1; then
  echo "✅ Remote origin уже настроен: $(git remote get-url origin)"
else
  echo "❌ Remote origin не настроен"
  echo "Выполните команду:"
  echo "git remote add origin https://github.com/anrulev/fail2ban-telegram-bot.git"
  exit 1
fi

echo "Готово."


