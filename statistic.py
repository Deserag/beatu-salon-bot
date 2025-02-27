import telebot
import json
from datetime import datetime

ORDERS_DATA_FILE = 'orders.json'
MASTERS_DATA_FILE = 'masters.json'
SERVICES_DATA_FILE = 'services.json'

def load_orders():
    try:
        with open(ORDERS_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_masters():
    try:
        with open(MASTERS_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_services():
    try:
        with open(SERVICES_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

class StatisticHandler:
    def __init__(self, bot):
        self.bot = bot

    def handle(self, message):
        chat_id = message.chat.id
        orders = load_orders()
        masters = load_masters()
        services = load_services()
        today = datetime.now().strftime("%d.%m.%Y")
        today_orders = []
        total_profit = 0

        for order_id, order in orders.items():
            if order['date'] == today:
                today_orders.append(order)
                for service_id, service in services.items():
                    if service['name'] == order['service']:
                        total_profit += service['price']
                        break

        today_masters = set()
        for order in today_orders:
            for master_id, master in masters.items():
                if master['name'] == order['master']:
                    today_masters.add(master['name'])
                    break

        message_text = f"Статистика за {today}:\n\n"
        message_text += f"Прибыль за сегодня: {total_profit} руб.\n"
        message_text += f"Количество оказанных услуг: {len(today_orders)}\n"
        message_text += f"Сегодня работают: {', '.join(today_masters)}"

        self.bot.send_message(chat_id, message_text)