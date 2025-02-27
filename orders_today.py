import telebot
import json
from datetime import datetime

ORDERS_DATA_FILE = 'orders.json'

def load_orders():
    try:
        with open(ORDERS_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

class OrdersTodayHandler:
    def __init__(self, bot):
        self.bot = bot

    def handle_today(self, message):
        chat_id = message.chat.id
        orders = load_orders()
        today = datetime.now().strftime("%d.%m.%Y")
        today_orders = []

        for order_id, order in orders.items():
            try:
                if order['date'] == today:
                    today_orders.append(order)
            except KeyError:
                continue

        if today_orders:
            message_text = "Сегодняшние записи:\n\n"
            for order in today_orders:
                message_text += f"Услуга: {order['service']}\nМастер: {order['master']}\nДата: {order['date']}\nВремя: {order['time']}\n\n"
            self.bot.send_message(chat_id, message_text)
        else:
            self.bot.send_message(chat_id, "На сегодня записей нет.")

    def handle_history(self, message):
        chat_id = message.chat.id
        orders = load_orders()
        user_orders = []

        for order_id, order in orders.items():
            if order['chat_id'] == chat_id:
                user_orders.append(order)

        if user_orders:
            message_text = "История посещений:\n\n"
            for order in user_orders:
                message_text += f"Услуга: {order['service']}\nМастер: {order['master']}\nДата: {order['date']}\nВремя: {order['time']}\n\n"
            self.bot.send_message(chat_id, message_text)
        else:
            self.bot.send_message(chat_id, "История посещений пуста.")