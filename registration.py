import telebot
import re
from menu import Menu
from datetime import datetime

class StartHandler:
    def __init__(self, bot, menu):
        self.bot = bot
        self.menu = menu
        self.prisma = None

    def handle(self, message):
        chat_id = message.chat.id
        user = self.prisma.user.find_first(where={'telegramId': str(chat_id)})
        if user:
            self.menu.show_menu(chat_id, user.roleId)
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
        birthdate_str = message.text
        if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', birthdate_str):
            self.bot.send_message(chat_id, "Неверный формат даты. Введите дату в формате ДД.ММ.ГГГГ:")
            self.bot.register_next_step_handler(message, self.process_birthdate, name, surname, secondname)
            return
        try:
            birthdate = datetime.strptime(birthdate_str, '%d.%m.%Y').date()
        except ValueError:
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
        try:
            self.prisma.user.create({
                'telegramId': str(chat_id),
                'lastName': surname,
                'firstName': name,
                'middleName': secondname,
                'birthDate': birthdate,
                'login': phone,
                'email': f'{phone}@example.com',
                'password': 'password',
                'roleId': 'User'
            })
            self.bot.send_message(chat_id, "Регистрация завершена!")
            self.menu.show_menu(chat_id, 'User')
        except Exception as e:
            self.bot.send_message(chat_id, f"Произошла ошибка при регистрации: {e}")