import telebot
import re
import psycopg2

class StartHandler:
    def __init__(self, bot, connect_to_db):
        self.bot = bot
        self.connect_to_db = connect_to_db

    def handle(self, message):
        chat_id = str(message.chat.id)
        conn = self.connect_to_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT telegramId FROM Client WHERE telegramId = %s", (chat_id,))
            user = cursor.fetchone()
            if user:
                self.bot.send_message(message.chat.id, "Вы уже зарегистрированы!")
                self.show_menu(message.chat.id)
            else:
                self.bot.send_message(message.chat.id, "Добро пожаловать! Давайте зарегистрируемся. Введите ваше Имя:")
                self.bot.register_next_step_handler(message, self.process_name)
            cursor.close()
            conn.close()
        else:
            self.bot.send_message(message.chat.id, "Ошибка подключения к базе данных.")

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

        conn = self.connect_to_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO client (telegramId, firstName, lastName, middleName, birthDate) VALUES (%s, %s, %s, %s, %s)",
                (str(message.chat.id), name, surname, middle_name, birthdate)
            )
            conn.commit()
            cursor.close()
            conn.close()
            self.bot.send_message(chat_id, "Регистрация завершена!")
            self.show_menu(chat_id)
        else:
            self.bot.send_message(chat_id, "Ошибка подключения к базе данных.")

    def show_menu(self, chat_id):
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
        markup.add('Запись на прием', 'История посещений', 'Профиль')
        self.bot.send_message(chat_id, "Основное меню:", reply_markup=markup)