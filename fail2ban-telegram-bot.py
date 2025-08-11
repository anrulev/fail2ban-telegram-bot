#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import re
import logging
import subprocess
import configparser
import socket
from datetime import datetime
import shutil
import telebot
from telebot import types

# Настройка логирования
def _init_logger() -> logging.Logger:
    log_file = os.environ.get('BOT_LOG_FILE', '/app/logs/fail2ban_bot.log')
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    except Exception:
        log_file = os.path.basename(log_file)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename=log_file
    )
    return logging.getLogger(__name__)

logger = _init_logger()

# Класс для работы с конфигурацией
class Config:
    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        
        # Проверяем наличие переменных окружения
        telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        fail2ban_log = os.environ.get('FAIL2BAN_LOG_FILE', '/var/log/fail2ban.log')
        check_interval = os.environ.get('CHECK_INTERVAL', '60')
        max_alerts = os.environ.get('MAX_ALERTS_PER_RUN', '10')
        hostname = os.environ.get('HOSTNAME') or socket.gethostname()
        
        # Если есть переменные окружения, используем их
        if telegram_token and telegram_chat_id:
            self.config['Telegram'] = {
                'BOT_TOKEN': telegram_token,
                'CHAT_ID': telegram_chat_id
            }
            
            self.config['Fail2Ban'] = {
                'LOG_FILE': fail2ban_log,
                'CHECK_INTERVAL': check_interval,
                'MAX_ALERTS_PER_RUN': max_alerts,
                'HOSTNAME': hostname
            }
            logger.info("Конфигурация загружена из переменных окружения")
        # Иначе пытаемся загрузить из файла
        elif os.path.exists(config_file):
            self.config.read(config_file)
            logger.info(f"Конфигурация загружена из файла {config_file}")
        # Если ничего нет, создаем шаблон конфигурации
        else:
            self.config['Telegram'] = {
                'BOT_TOKEN': 'YOUR_TELEGRAM_BOT_TOKEN',
                'CHAT_ID': 'YOUR_CHAT_ID'
            }
            
            self.config['Fail2Ban'] = {
                'LOG_FILE': '/var/log/fail2ban.log',
                'CHECK_INTERVAL': '60',  # в секундах
                'MAX_ALERTS_PER_RUN': '10',
                'HOSTNAME': socket.gethostname()
            }
            
            with open(config_file, 'w') as f:
                self.config.write(f)
            
            logger.info(f"Создан файл конфигурации {config_file}. Пожалуйста, заполните данные.")
    
    def get(self, section, key):
        return self.config.get(section, key)

# Класс для работы с Fail2Ban
class Fail2BanMonitor:
    def __init__(self, config):
        self.config = config
        self.log_file = config.get('Fail2Ban', 'LOG_FILE')
        self.check_interval = int(config.get('Fail2Ban', 'CHECK_INTERVAL'))
        self.max_alerts = int(config.get('Fail2Ban', 'MAX_ALERTS_PER_RUN'))
        self.last_position = 0
        # Поддержка разных форматов строк Fail2Ban
        self.ban_pattern = re.compile(
            r'^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)\s+'
            r'\S+\s+\[\d+\]:?\s+'
            r'(?P<level>[A-Z]+)\s+\[(?P<jail>[^\]]+)\]\s+'
            r'Ban\s+(?P<ip>[0-9a-fA-F\.:]+)'
        )
        
        # Инициализация последней позиции в файле
        self._init_file_position()
    
    def _init_file_position(self):
        if os.path.exists(self.log_file):
            self.last_position = os.path.getsize(self.log_file)
            logger.info(f"Инициализирована позиция в логе: {self.last_position}")
        else:
            logger.error(f"Файл лога {self.log_file} не существует!")
    
    def get_new_bans(self):
        bans = []
        
        try:
            if not os.path.exists(self.log_file):
                logger.error(f"Файл лога {self.log_file} не существует!")
                return bans
            
            current_size = os.path.getsize(self.log_file)
            
            # Если файл был обрезан (например, из-за ротации логов)
            if current_size < self.last_position:
                logger.info("Обнаружена ротация лога, сбрасываем позицию")
                self.last_position = 0
            
            # Если есть новые данные
            if current_size > self.last_position:
                with open(self.log_file, 'r') as f:
                    f.seek(self.last_position)
                    new_lines = f.readlines()
                    self.last_position = f.tell()
                
                count = 0
                for line in new_lines:
                    match = self.ban_pattern.search(line)
                    if match and count < self.max_alerts:
                        groups = match.groupdict()
                        bans.append({
                            'timestamp': groups.get('timestamp'),
                            'level': groups.get('level'),
                            'jail': groups.get('jail'),
                            'ip': groups.get('ip')
                        })
                        count += 1
        
        except Exception as e:
            logger.error(f"Ошибка при чтении лог-файла: {e}")
        
        return bans
    
    def get_jail_status(self):
        try:
            if shutil.which('fail2ban-client') is None:
                return "Команда fail2ban-client недоступна в контейнере"
            result = subprocess.run(['fail2ban-client', 'status'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout
            else:
                logger.error(f"Ошибка при выполнении fail2ban-client: {result.stderr}")
                return "Ошибка при получении статуса Fail2Ban"
        except Exception as e:
            logger.error(f"Исключение при выполнении fail2ban-client: {e}")
            return f"Ошибка: {str(e)}"
    
    def get_jail_details(self, jail_name):
        try:
            if shutil.which('fail2ban-client') is None:
                return "Команда fail2ban-client недоступна в контейнере"
            result = subprocess.run(['fail2ban-client', 'status', jail_name], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout
            else:
                logger.error(f"Ошибка при выполнении fail2ban-client для тюрьмы {jail_name}: {result.stderr}")
                return f"Ошибка при получении данных о тюрьме {jail_name}"
        except Exception as e:
            logger.error(f"Исключение при выполнении fail2ban-client для тюрьмы {jail_name}: {e}")
            return f"Ошибка: {str(e)}"

# Класс для работы с Telegram API
class TelegramBot:
    def __init__(self, config):
        self.config = config
        self.token = config.get('Telegram', 'BOT_TOKEN')
        self.chat_id = config.get('Telegram', 'CHAT_ID')
        self.bot = telebot.TeleBot(self.token)
        self.fail2ban = Fail2BanMonitor(config)
        # Флаг для включения команд, требующих fail2ban-client
        env_flag = os.environ.get('ENABLE_FAIL2BAN_STATUS')
        file_flag = None
        try:
            if config.config.has_section('Fail2Ban'):
                file_flag = config.config.get('Fail2Ban', 'ENABLE_FAIL2BAN_STATUS', fallback='false')
        except Exception:
            file_flag = 'false'
        value = env_flag if env_flag is not None else file_flag or 'false'
        self.enable_status_commands = str(value).strip().lower() in ('1', 'true', 'yes')
        self._setup_handlers()
    
    def _setup_handlers(self):
        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            welcome_text = (
                "👋 Привет! Я бот для мониторинга Fail2Ban.\n\n"
                "Доступные команды:\n"
                "/status - Общий статус Fail2Ban\n"
                "/jails - Список активных тюрем\n"
                "/latest - Последние блокировки\n"
                "/help - Показать это сообщение"
            )
            self.bot.reply_to(message, welcome_text)
        
        if self.enable_status_commands and shutil.which('fail2ban-client') is not None:
            @self.bot.message_handler(commands=['status'])
            def send_status(message):
                status = self.fail2ban.get_jail_status()
                self.bot.reply_to(message, f"Статус Fail2Ban:\n```\n{status}\n```", parse_mode='Markdown')

            @self.bot.message_handler(commands=['jails'])
            def send_jails(message):
                status = self.fail2ban.get_jail_status()
                jails = []

                for line in status.split('\n'):
                    if 'Jail list:' in line:
                        jail_list = line.split('Jail list:')[1].strip()
                        jails = [jail.strip() for jail in jail_list.split(',')]
                        break

                if not jails:
                    self.bot.reply_to(message, "Активные тюрьмы не найдены")
                    return

                markup = types.InlineKeyboardMarkup(row_width=2)
                buttons = [
                    types.InlineKeyboardButton(jail, callback_data=f"jail_{jail}")
                    for jail in jails
                ]
                markup.add(*buttons)
                self.bot.reply_to(
                    message,
                    "Выберите тюрьму для получения подробной информации:",
                    reply_markup=markup
                )

            @self.bot.callback_query_handler(func=lambda call: call.data.startswith('jail_'))
            def jail_callback(call):
                jail_name = call.data.split('jail_')[1]
                jail_info = self.fail2ban.get_jail_details(jail_name)
                self.bot.send_message(
                    call.message.chat.id,
                    f"Информация о тюрьме {jail_name}:\n```\n{jail_info}\n```",
                    parse_mode='Markdown'
                )
                self.bot.answer_callback_query(call.id)
        else:
            @self.bot.message_handler(commands=['status', 'jails'])
            def not_available(message):
                self.bot.reply_to(
                    message,
                    "Команды /status и /jails недоступны в данном окружении. Включите ENABLE_FAIL2BAN_STATUS и установите fail2ban-client на хосте/в контейнере."
                )
        
        @self.bot.message_handler(commands=['latest'])
        def send_latest_bans(message):
            bans = self.fail2ban.get_new_bans()
            if bans:
                response = "Последние блокировки:\n\n"
                for ban in bans:
                    response += (
                        f"⏰ {ban['timestamp']}\n"
                        f"🖥️ Сервер: {self.config.get('Fail2Ban', 'HOSTNAME')}\n"
                        f"🔒 Тюрьма: {ban['jail']}\n"
                        f"🔴 IP: {ban['ip']}\n\n"
                    )
                self.bot.reply_to(message, response)
            else:
                self.bot.reply_to(message, "Новых блокировок не обнаружено")
    
    def send_notification(self, ban):
        hostname = self.config.get('Fail2Ban', 'HOSTNAME')
        message = (
            f"🚨 *Новая блокировка в Fail2Ban*\n\n"
            f"🖥️ Сервер: {hostname}\n"
            f"⏰ Время: {ban['timestamp']}\n"
            f"🔒 Тюрьма: {ban['jail']}\n"
            f"🔴 IP-адрес: {ban['ip']}"
        )
        
        try:
            self.bot.send_message(self.chat_id, message, parse_mode='Markdown')
            logger.info(f"Отправлено уведомление о блокировке IP {ban['ip']} в тюрьме {ban['jail']}")
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления: {e}")
    
    def start_monitoring(self):
        logger.info("Запуск мониторинга Fail2Ban")
        
        while True:
            try:
                bans = self.fail2ban.get_new_bans()
                for ban in bans:
                    self.send_notification(ban)
                
                time.sleep(self.fail2ban.check_interval)
            
            except KeyboardInterrupt:
                logger.info("Мониторинг остановлен пользователем")
                break
            
            except Exception as e:
                logger.error(f"Ошибка в цикле мониторинга: {e}")
                time.sleep(10)  # Подождать и попробовать снова
    
    def run(self):
        from threading import Thread
        
        # Запуск мониторинга в отдельном потоке
        monitor_thread = Thread(target=self.start_monitoring)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        logger.info("Запуск Telegram бота")
        self.bot.infinity_polling()

# Главная функция
def main():
    try:
        config = Config()
        bot = TelegramBot(config)
        bot.run()
    
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}")
        exit(1)

if __name__ == "__main__":
    main()
