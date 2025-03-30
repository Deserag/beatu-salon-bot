import telebot
from config import get_db_connection

class Menu:
    def __init__(self, bot):
        self.bot = bot

    def show_menu(self, chat_id, role):
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            if role == 'User':
                markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
                markup.add('Запись на прием', 'История посещений', 'Профиль')
                self.bot.send_message(chat_id, "Основное меню:", reply_markup=markup)
            elif role == 'Worker':
                markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
                markup.add('Запись на прием','Сегодняшние записи','Текущая запись', 'Статистика','История посещений', 'Профиль')
                self.bot.send_message(chat_id, "Меню работника:", reply_markup=markup)
            elif role == 'Admin':
                markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
                markup.add('Запись на прием','Сегодняшние записи', 'Статистика', 'Профиль','История посещений')
                self.bot.send_message(chat_id, "Меню администратора:", reply_markup=markup)
        finally:
            cur.close()
            conn.close()

    def handle_menu_item(self, message, order_handler, profile_handler, orders_today_handler, statistic_handler, role):
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            if message.text == 'Запись на прием':
                order_handler.handle(message)
            elif message.text == 'Профиль':
                profile_handler.handle(message)
            elif message.text == 'Сегодняшние записи':
                if role in ['Worker', 'Admin']:
                    orders_today_handler.handle_today(message)
                else:
                    self.bot.send_message(message.chat.id, "У вас нет прав для просмотра сегодняшних записей.")
            elif message.text == 'История посещений':
                orders_today_handler.handle_history(message)
            elif message.text == 'Статистика':
                if role == 'Admin':
                    statistic_handler.handle(message)
                else:
                    self.bot.send_message(message.chat.id, "У вас нет прав для просмотра статистики.")
        finally:
            cur.close()
            conn.close()