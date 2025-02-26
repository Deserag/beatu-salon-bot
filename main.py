import telebot
import os
from dotenv import load_dotenv
import psycopg2
from registration import StartHandler
from config import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def connect_to_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None

start_handler = StartHandler(bot, connect_to_db)

@bot.callback_query_handler(func=lambda call: call.data == "evaluate")
def handle_evaluation_callback(call):
    bot.send_message(call.message.chat.id, "Спасибо за оценку!")

@bot.message_handler(commands=['start'])
def start(message):
    start_handler.handle(message)

if __name__ == '__main__':
    bot.polling()