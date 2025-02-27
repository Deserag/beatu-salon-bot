import telebot
import json
import re
from menu import Menu

USERS_DATA_FILE = 'users.json'

def load_users():
    try:
        with open(USERS_DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    except FileNotFoundError:
        return {}

def save_users(users):
    with open(USERS_DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)

class StartHandler:
    def __init__(self, bot, menu):
        self.bot = bot
        self.menu = menu

    def handle(self, message):
        users = load_users()
        chat_id = message.chat.id

        if str(chat_id) in users:
            self.menu.show_menu(chat_id, users[str(chat_id)]['role'])
        else:
            self.bot.send_message(chat_id, "Добро пожаловать! Давайте зарегистрируемся. Введите ваше Имя:")
            self.bot.register_next_step_handler(message, self.process_name)

    def process_name(self, message):
        chat_id = message.chat.id
        name = message.text
        self.bot.send_message(chat_id, "Введите вашу фамилию:")
        self.bot.register_next_step_handler(message, self.process_surname, name)

    def process_surname(self, message, name):
        chat_id = message.chat.id
        surname = message.text
        self.bot.send_message(chat_id, "Введите ваше отчество:")
        self.bot.register_next_step_handler(message, self.process_secondname, name, surname)

    def process_secondname(self, message, name, surname):
        chat_id = message.chat.id
        secondname = message.text
        self.bot.send_message(chat_id, "Введите вашу дату рождения (в формате ДД.ММ.ГГГГ):")
        self.bot.register_next_step_handler(message, self.process_birthdate, name, surname, secondname)

    def process_birthdate(self, message, name, surname, secondname):
        chat_id = message.chat.id
        birthdate = message.text

        if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', birthdate):
            self.bot.send_message(chat_id, "Неверный формат даты. Введите дату в формате ДД.ММ.ГГГГ:")
            self.bot.register_next_step_handler(message, self.process_birthdate, name, surname, secondname)
            return

        self.bot.send_message(chat_id, "Введите ваш номер телефона (только цифры):")
        self.bot.register_next_step_handler(message, self.process_phone, name, surname, secondname, birthdate)

    def process_phone(self, message, name, surname, secondname, birthdate):
        chat_id = message.chat.id
        phone = message.text

        if not re.match(r'^\d+$', phone):
            self.bot.send_message(chat_id, "Неверный формат номера. Введите только цифры:")
            self.bot.register_next_step_handler(message, self.process_phone, name, surname, secondname, birthdate)
            return

        users = load_users()
        users[str(chat_id)] = {
            'name': name,
            'surname': surname,
            'secondname': secondname,
            'birthdate': birthdate,
            'phone': phone,
            'role': 'User'
        }
        save_users(users)
        self.bot.send_message(chat_id, "Регистрация завершена!")
        self.menu.show_menu(chat_id, 'User')