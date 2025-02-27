import telebot
from registration import StartHandler
from history import HistoryHandler
from menu import Menu
from order import OrderHandler
from config import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)
menu = Menu(bot)
order_handler = OrderHandler(bot)
start_handler = StartHandler(bot, menu)
history_handler = HistoryHandler(bot)

@bot.callback_query_handler(func=lambda call: call.data == "evaluate")
def handle_evaluation_callback(call):
    bot.send_message(call.message.chat.id, "Спасибо за оценку!")

@bot.message_handler(commands=['start'])
def start(message):
    start_handler.handle(message)

@bot.message_handler(func=lambda message: message.text == 'История посещений')
def history(message):
    history_handler.handle(message)

@bot.message_handler(func=lambda message: message.text == 'Запись на прием')
def order(message):
    order_handler.handle(message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('service_'))
def handle_service_choice(call):
    service_id = call.data.split('_')[1]
    order_handler.process_service(call.message.chat.id, service_id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('master_'))
def handle_master_choice(call):
    master_id = call.data.split('_')[1]
    order_handler.process_master(call.message.chat.id, master_id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'confirm_order')
def handle_confirm_order(call):
    order_handler.complete_order(call.message.chat.id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'cancel_order')
def handle_cancel_order(call):
    order_handler.cancel_order(call.message.chat.id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('time_'))
def handle_time_choice(call):
    time = call.data.split('_')[1]
    order_handler.process_time(call.message.chat.id, time)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'occupied')
def handle_occupied_time(call):
    bot.answer_callback_query(call.id, "Это время уже занято.")

bot.polling()