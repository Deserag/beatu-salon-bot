import telebot

class HistoryHandler:
    def __init__(self, bot):
        self.bot = bot

    def handle(self, message):
        chat_id = message.chat.id
        self.bot.send_message(chat_id, "История посещений:")
        self.send_evaluation_button(chat_id)

    def send_evaluation_button(self, chat_id):
        markup = telebot.types.InlineKeyboardMarkup()
        evaluation_button = telebot.types.InlineKeyboardButton("Оценить", callback_data="evaluate")
        markup.add(evaluation_button)
        self.bot.send_message(chat_id, "Оцените посещение:", reply_markup=markup)