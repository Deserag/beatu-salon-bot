import telebot
import json
from registration import StartHandler
from history import HistoryHandler
from config import BOT_TOKEN
bot = telebot.TeleBot(BOT_TOKEN)

@bot.callback_query_handler(func=lambda call: call.data == "evaluate")
def handle_evaluation_callback(call):
    bot.send_message(call.message.chat.id, "Спасибо за оценку!")

start_handler = StartHandler(bot)
history_handler = HistoryHandler(bot)

@bot.message_handler(commands=['start'])
def start(message):
    start_handler.handle(message)

@bot.message_handler(func=lambda message: message.text == 'История посещений')
def history(message):
    history_handler.handle(message)

bot.polling()