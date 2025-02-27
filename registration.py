import telebot
import os
from dotenv import load_dotenv
from prisma.generated import Prisma
from prisma.errors import PrismaError
import re

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

bot = telebot.TeleBot(BOT_TOKEN)
prisma = Prisma(datasource_url=DATABASE_URL)
prisma.connect()

class StartHandler:
    def __init__(self, bot, prisma):
        self.bot = bot
        self.prisma = prisma

    def handle(self, message):
        chat_id = str(message.chat.id)
        try:
            user = self.prisma.client.find_first(where={"telegramId": chat_id})
            if user:
                self.bot.send_message(message.chat.id, "Вы уже зарегистрированы!")
                self.show_menu(message.chat.id)
            else:
                self.bot.send_message(message.chat.id, "Добро пожаловать! Давайте зарегистрируемся. Введите ваше Имя:")
                self.bot.register_next_step_handler(message, self.process_name)
        except PrismaError as e:
            self.bot.send_message(message.chat.id, f"Ошибка базы данных: {e}")

    def process_name(self, message):
        chat_id = message.chat.id
        name = message.text
        self.bot.send_message(chat_id, "Введите вашу фамилию:")
        self.bot.register_next_step_handler(message, self.process_surname, name)

    def process_surname(self, message, name):
        chat_id = message.chat.id
        surname = message.text
        self.bot.send_message(chat_id, "Введите ваше отчество:")
        self.bot.register_next_step_handler(message, self.process_middle_name, name, surname)

    def process_middle_name(self, message, name, surname):
        chat_id = message.chat.id
        middle_name = message.text
        self.bot.send_message(chat_id, "Введите вашу дату рождения (в формате ДД.ММ.ГГГГ):")
        self.bot.register_next_step_handler(message, self.process_birthdate, name, surname, middle_name)

    def process_birthdate(self, message, name, surname, middle_name):
        chat_id = message.chat.id
        birthdate = message.text

        if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', birthdate):
            self.bot.send_message(chat_id, "Неверный формат даты. Введите дату в формате ДД.ММ.ГГГГ:")
            self.bot.register_next_step_handler(message, self.process_birthdate, name, surname, middle_name)
            return

        try:
            self.prisma.client.create(
                data={
                    "telegramId": str(message.chat.id),
                    "firstName": name,
                    "lastName": surname,
                    "middleName": middle_name,
                    "birthDate": birthdate,
                }
            )
            self.bot.send_message(chat_id, "Регистрация завершена!")
            self.show_menu(chat_id)
        except PrismaError as e:
            self.bot.send_message(chat_id, f"Ошибка базы данных: {e}")

    def show_menu(self, chat_id):
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
        markup.add('Запись на прием', 'История посещений', 'Профиль')
        self.bot.send_message(chat_id, "Основное меню:", reply_markup=markup)

start_handler = StartHandler(bot, prisma)

@bot.callback_query_handler(func=lambda call: call.data == "evaluate")
def handle_evaluation_callback(call):
    bot.send_message(call.message.chat.id, "Спасибо за оценку!")

@bot.message_handler(commands=['start'])
def start(message):
    start_handler.handle(message)

if __name__ == '__main__':
    bot.polling()