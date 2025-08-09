#!/bin/bash

echo "Настройка GitHub репозитория для fail2ban-telegram-bot"
echo "=================================================="

# Проверяем, что мы в правильной директории
if [ ! -f "fail2ban-telegram-bot.py" ]; then
    echo "❌ Ошибка: запустите скрипт из директории проекта"
    exit 1
fi

echo "✅ Директория проекта найдена"

# Проверяем статус git
if [ ! -d ".git" ]; then
    echo "❌ Git не инициализирован. Сначала выполните: git init"
    exit 1
fi

echo "✅ Git инициализирован"

# Проверяем remote
if git remote get-url origin >/dev/null 2>&1; then
    echo "✅ Remote origin уже настроен: $(git remote get-url origin)"
else
    echo "❌ Remote origin не настроен"
    echo "Выполните команду:"
    echo "git remote add origin https://github.com/anrulev/fail2ban-telegram-bot.git"
    exit 1
fi

echo ""
echo "📋 Инструкции по созданию репозитория на GitHub:"
echo "1. Перейдите на https://github.com/new"
echo "2. Repository name: fail2ban-telegram-bot"
echo "3. Description: Telegram bot for Fail2Ban monitoring and notifications"
echo "4. Visibility: Public"
echo "5. НЕ создавайте README, .gitignore или license (у нас уже есть)"
echo "6. Нажмите 'Create repository'"
echo ""
echo "После создания репозитория выполните:"
echo "git push -u origin main"
echo ""
echo "Или используйте этот скрипт снова после создания репозитория"
