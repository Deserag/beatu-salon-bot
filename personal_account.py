import telebot
import re
from datetime import datetime

class ProfileHandler:
    def __init__(self, bot):
        self.bot = bot
        self.prisma = None

    def handle(self, message):
        chat_id = message.chat.id
        user = self.prisma.user.find_first(where={'telegramId': str(chat_id)})

        if user:
            self.show_profile(chat_id, user)
        else:
            self.bot.send_message(chat_id, "Профиль не найден. Пожалуйста, зарегистрируйтесь.")

    def show_profile(self, chat_id, user):
        message = f"Ваш профиль:\n\n"
        message += f"Имя: {user.firstName}\n"
        message += f"Фамилия: {user.lastName}\n"
        message += f"Отчество: {user.middleName}\n"
        message += f"Дата рождения: {user.birthDate.strftime('%d.%m.%Y')}\n"
        message += f"Номер телефона: {user.login}\n"

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
        self.update_user_field(chat_id, 'firstName', name)
        self.bot.send_message(chat_id, "Имя изменено.")
        user = self.prisma.user.find_first(where={'telegramId': str(chat_id)})
        self.show_profile(chat_id, user)

    def edit_surname(self, call):
        chat_id = call.message.chat.id
        self.bot.send_message(chat_id, "Введите новую фамилию:")
        self.bot.register_next_step_handler(call.message, self.process_new_surname, chat_id)

    def process_new_surname(self, message, chat_id):
        surname = message.text
        self.update_user_field(chat_id, 'lastName', surname)
        self.bot.send_message(chat_id, "Фамилия изменена.")
        user = self.prisma.user.find_first(where={'telegramId': str(chat_id)})
        self.show_profile(chat_id, user)

    def edit_secondname(self, call):
        chat_id = call.message.chat.id
        self.bot.send_message(chat_id, "Введите новое отчество:")
        self.bot.register_next_step_handler(call.message, self.process_new_secondname, chat_id)

    def process_new_secondname(self, message, chat_id):
        secondname = message.text
        self.update_user_field(chat_id, 'middleName', secondname)
        self.bot.send_message(chat_id, "Отчество изменено.")
        user = self.prisma.user.find_first(where={'telegramId': str(chat_id)})
        self.show_profile(chat_id, user)

    def edit_birthdate(self, call):
        chat_id = call.message.chat.id
        self.bot.send_message(chat_id, "Введите новую дату рождения (ДД.ММ.ГГГГ):")
        self.bot.register_next_step_handler(call.message, self.process_new_birthdate, chat_id)

    def process_new_birthdate(self, message, chat_id):
        birthdate_str = message.text
        if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', birthdate_str):
            self.bot.send_message(chat_id, "Неверный формат даты. Введите дату в формате ДД.ММ.ГГГГ:")
            self.bot.register_next_step_handler(message, self.process_new_birthdate, chat_id)
            return
        try:
            birthdate = datetime.strptime(birthdate_str, '%d.%m.%Y').date()
        except ValueError:
            self.bot.send_message(chat_id, "Неверный формат даты. Введите дату в формате ДД.ММ.ГГГГ:")
            self.bot.register_next_step_handler(message, self.process_new_birthdate, chat_id)
            return
        self.update_user_field(chat_id, 'birthDate', birthdate)
        self.bot.send_message(chat_id, "Дата рождения изменена.")
        user = self.prisma.user.find_first(where={'telegramId': str(chat_id)})
        self.show_profile(chat_id, user)

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
        self.update_user_field(chat_id, 'login', phone)
        self.bot.send_message(chat_id, "Номер телефона изменен.")
        user = self.prisma.user.find_first(where={'telegramId': str(chat_id)})
        self.show_profile(chat_id, user)

    def update_user_field(self, chat_id, field, value):
        self.prisma.user.update(
            where={'telegramId': str(chat_id)},
            data={field: value}
        )