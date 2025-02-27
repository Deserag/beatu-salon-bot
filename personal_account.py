import telebot
import json
import re

USERS_DATA_FILE = 'users.json'

def load_users():
    try:
        with open(USERS_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open(USERS_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4)

class ProfileHandler:
    def __init__(self, bot):
        self.bot = bot

    def handle(self, message):
        chat_id = message.chat.id
        users = load_users()
        user = users.get(str(chat_id))

        if user:
            self.show_profile(chat_id, user)
        else:
            self.bot.send_message(chat_id, "Профиль не найден. Пожалуйста, зарегистрируйтесь.")

    def show_profile(self, chat_id, user):
        message = f"Ваш профиль:\n\n"
        message += f"Имя: {user['name']}\n"
        message += f"Фамилия: {user['surname']}\n"
        message += f"Отчество: {user['secondname']}\n"
        message += f"Дата рождения: {user['birthdate']}\n"
        message += f"Номер телефона: {user['phone']}\n"

        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("Изменить имя", callback_data="edit_name"))
        markup.add(telebot.types.InlineKeyboardButton("Изменить фамилию", callback_data="edit_surname"))
        markup.add(telebot.types.InlineKeyboardButton("Изменить отчество", callback_data="edit_secondname"))
        markup.add(telebot.types.InlineKeyboardButton("Изменить дату рождения", callback_data="edit_birthdate"))
        markup.add(telebot.types.InlineKeyboardButton("Изменить номер телефона", callback_data="edit_phone"))
        self.bot.send_message(chat_id, message, reply_markup=markup)

    def edit_name(self, call):
        chat_id = call.message.chat.id
        self.bot.send_message(chat_id, "Введите новое имя:")
        self.bot.register_next_step_handler(call.message, self.process_new_name, chat_id)

    def process_new_name(self, message, chat_id):
        name = message.text
        self.update_user_field(chat_id, 'name', name)
        self.bot.send_message(chat_id, "Имя изменено.")
        self.show_profile(chat_id, load_users().get(str(chat_id)))

    def edit_surname(self, call):
        chat_id = call.message.chat.id
        self.bot.send_message(chat_id, "Введите новую фамилию:")
        self.bot.register_next_step_handler(call.message, self.process_new_surname, chat_id)

    def process_new_surname(self, message, chat_id):
        surname = message.text
        self.update_user_field(chat_id, 'surname', surname)
        self.bot.send_message(chat_id, "Фамилия изменена.")
        self.show_profile(chat_id, load_users().get(str(chat_id)))

    def edit_secondname(self, call):
        chat_id = call.message.chat.id
        self.bot.send_message(chat_id, "Введите новое отчество:")
        self.bot.register_next_step_handler(call.message, self.process_new_secondname, chat_id)

    def process_new_secondname(self, message, chat_id):
        secondname = message.text
        self.update_user_field(chat_id, 'secondname', secondname)
        self.bot.send_message(chat_id, "Отчество изменено.")
        self.show_profile(chat_id, load_users().get(str(chat_id)))

    def edit_birthdate(self, call):
        chat_id = call.message.chat.id
        self.bot.send_message(chat_id, "Введите новую дату рождения (ДД.ММ.ГГГГ):")
        self.bot.register_next_step_handler(call.message, self.process_new_birthdate, chat_id)

    def process_new_birthdate(self, message, chat_id):
        birthdate = message.text
        if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', birthdate):
            self.bot.send_message(chat_id, "Неверный формат даты. Введите дату в формате ДД.ММ.ГГГГ:")
            self.bot.register_next_step_handler(message, self.process_new_birthdate, chat_id)
            return
        self.update_user_field(chat_id, 'birthdate', birthdate)
        self.bot.send_message(chat_id, "Дата рождения изменена.")
        self.show_profile(chat_id, load_users().get(str(chat_id)))

    def edit_phone(self, call):
        chat_id = call.message.chat.id
        self.bot.send_message(chat_id, "Введите новый номер телефона (только цифры):")
        self.bot.register_next_step_handler(call.message, self.process_new_phone, chat_id)

    def process_new_phone(self, message, chat_id):
        phone = message.text
        if not re.match(r'^\d+$', phone):
            self.bot.send_message(chat_id, "Неверный формат номера. Введите только цифры:")
            self.bot.register_next_step_handler(message, self.process_new_phone, chat_id)
            return
        self.update_user_field(chat_id, 'phone', phone)
        self.bot.send_message(chat_id, "Номер телефона изменен.")
        self.show_profile(chat_id, load_users().get(str(chat_id)))

    def update_user_field(self, chat_id, field, value):
        users = load_users()
        user = users.get(str(chat_id))
        if user:
            user[field] = value
            save_users(users)