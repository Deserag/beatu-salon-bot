import telebot

class Menu:
    def __init__(self, bot):
        self.bot = bot

    def show_menu(self, chat_id, role):
        if role == 'User':
            markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
            markup.add('Запись на прием', 'История посещений', 'Профиль')
            self.bot.send_message(chat_id, "Основное меню:", reply_markup=markup)
        elif role == 'Worker':
            markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
            markup.add('Запись на прием','Сегодняшние записи', 'Статистика', 'Профиль')
            self.bot.send_message(chat_id, "Меню работника:", reply_markup=markup)
        elif role == 'Admin':
            markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
            markup.add('Запись на прием','Сегодняшние записи', 'Статистика', 'Профиль', 'Управление пользователями')
            self.bot.send_message(chat_id, "Меню администратора:", reply_markup=markup)

    def handle_menu_item(self, message, order_handler):
        if message.text == 'Запись на прием':
            order_handler.handle(message)