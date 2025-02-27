import telebot
import json
import re
from datetime import datetime

SERVICES_DATA_FILE = 'services.json'
MASTERS_DATA_FILE = 'masters.json'
ORDERS_DATA_FILE = 'orders.json'

def load_services():
    try:
        with open(SERVICES_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_masters():
    try:
        with open(MASTERS_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_orders():
    try:
        with open(ORDERS_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_orders(orders):
    with open(ORDERS_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(orders, f, indent=4)

class OrderHandler:
    def __init__(self, bot):
        self.bot = bot
        self.services = load_services()
        self.masters = load_masters()
        self.orders = load_orders()
        self.current_order = {}

    def handle(self, message):
        chat_id = message.chat.id
        self.current_order[chat_id] = {}
        self.show_services(chat_id)

    def show_services(self, chat_id):
        markup = telebot.types.InlineKeyboardMarkup()
        for service_id, service in self.services.items():
            markup.add(telebot.types.InlineKeyboardButton(service['name'], callback_data=f'service_{service_id}'))
        self.bot.send_message(chat_id, "Выберите услугу:", reply_markup=markup)

    def process_service(self, chat_id, service_id):
        self.current_order[chat_id]['service_id'] = service_id
        self.show_masters(chat_id, service_id)

    def show_masters(self, chat_id, service_id):
        service = self.services[service_id]
        markup = telebot.types.InlineKeyboardMarkup()
        for master_id in service['masters']:
            master = self.masters[master_id]
            markup.add(telebot.types.InlineKeyboardButton(master['name'], callback_data=f'master_{master_id}'))
        self.bot.send_message(chat_id, "Выберите мастера:", reply_markup=markup)

    def process_master(self, chat_id, master_id):
        self.current_order[chat_id]['master_id'] = master_id
        # self.bot.send_message(chat_id, "Введите дату в формате ДД.ММ.ГГГГ:")
        self.bot.register_next_step_handler(self.bot.send_message(chat_id, "Введите дату в формате ДД.ММ.ГГГГ:"), self.process_date, chat_id)

    def process_date(self, message, chat_id):
        date = message.text
        if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', date):
            self.bot.send_message(chat_id, "Неверный формат даты. Введите дату в формате ДД.ММ.ГГГГ:")
            self.bot.register_next_step_handler(self.bot.send_message(chat_id, "Введите дату в формате ДД.ММ.ГГГГ:"), self.process_date, chat_id)
            return
        self.current_order[chat_id]['date'] = date
        self.show_available_times(chat_id, self.current_order[chat_id]['service_id'], self.current_order[chat_id]['master_id'])

    def show_available_times(self, chat_id, service_id, master_id):
        service = self.services[service_id]
        master = self.masters[master_id]
        available_times = service['available_times']
        orders = load_orders()
        occupied_times = [order['time'] for order in orders.values() if order['master'] == master['name'] and order['date'] == self.current_order[chat_id]['date']]

        markup = telebot.types.InlineKeyboardMarkup()
        for time in available_times:
            if time in occupied_times:
                button_text = f" {time}"
                callback_data = "occupied"
            else:
                button_text = f"🟢 {time}"
                callback_data = f"time_{time}"
            markup.add(telebot.types.InlineKeyboardButton(button_text, callback_data=callback_data))
        self.bot.send_message(chat_id, "Выберите время:", reply_markup=markup)

    def process_time(self, chat_id, time):
        self.current_order[chat_id]['time'] = time
        self.confirm_order(chat_id)

    def confirm_order(self, chat_id):
        order = self.current_order[chat_id]
        service = self.services[order['service_id']]
        master = self.masters[order['master_id']]
        message = f"Вы выбрали услугу: {service['name']}\nМастер: {master['name']}\nДата: {order['date']}\nВремя: {order['time']}\nПодтвердить заказ?"
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("Подтвердить", callback_data="confirm_order"))
        markup.add(telebot.types.InlineKeyboardButton("Отменить", callback_data="cancel_order"))
        self.bot.send_message(chat_id, message, reply_markup=markup)

    def complete_order(self, chat_id):
        order = self.current_order[chat_id]
        service = self.services[order['service_id']]
        master = self.masters[order['master_id']]
        order_id = str(len(self.orders) + 1)
        self.orders[order_id] = {
            'service': service['name'],
            'master': master['name'],
            'chat_id': chat_id,
            'time': order['time'],
            'date': order['date']
        }
        save_orders(self.orders)
        self.bot.send_message(chat_id, "Заказ успешно оформлен!")
        del self.current_order[chat_id]

    def cancel_order(self, chat_id):
        self.bot.send_message(chat_id, "Заказ отменен.")
        del self.current_order[chat_id]