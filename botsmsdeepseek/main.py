import json
import os
from datetime import datetime
import time
from deepseek import chat_stream

# Конфигурация бота
ADMIN_NUMBERS = ["+79193362806", "+79088232358", "+79090951906", "+79090941107", "+79193331607"]
BOT_NAME = "TermuxBot"
TIME_START = datetime.now()
READ_MESSAGES = []


def log_message(message):
    """Запись логов"""
    with open("sms_bot.log", "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

def send_sms(phone, message):
    """Отправка SMS через Termux API"""
    if phone not in ADMIN_NUMBERS:
        return False

    try:
        # Экранируем специальные символы
        clean_message = message.replace('"', '\\"').replace("'", "\\'")
        
        # Формируем команду для Termux
        command = f'termux-sms-send -n "{phone}" "{clean_message}"'
        os.system(command)
        
        log_message(f"Отправлено SMS на {phone}: {message}")
        return True
    except Exception as e:
        print(e)
        log_message(f"Ошибка отправки: {str(e)}")
        return False

def check_new_messages():
    """Проверка новых сообщений"""
    try:
        # Получаем последние 10 SMS (только входящие)
        result = os.popen('termux-sms-list -t inbox -l 10').read()
        messages = json.loads(result) if result.strip() else []
        
        for msg in messages:
            sender = msg["number"]
            date = msg["received"]
            date = date.split()
            year, month, day = map(int, date[0].split('-'))
            hour, minute, sec = map(int, date[1].split(':'))
            fdate = datetime(year, month, day, hour, minute, sec)
            if (sender in ADMIN_NUMBERS) and (msg['_id'] not in READ_MESSAGES) and (fdate > TIME_START):
                text = msg['body']
                print(READ_MESSAGES)
                print(text.lstrip()[0])
                if text.lstrip()[:1] == "*":
                    sms = chat_stream(text[1:] + "(Ответь сплошным текстом)")
                    send_sms(sender, "sms")
                    log_message(f"Новое сообщение от {sender}: {text}")
                if len(READ_MESSAGES) > 10:
                    READ_MESSAGES.pop(0)
                READ_MESSAGES.append(msg['_id'])
    except Exception as e:
        print(e)
        log_message(f"Ошибка обработки: {str(e)}")
        
	
while True:
    time.sleep(3)
    check_new_messages()
