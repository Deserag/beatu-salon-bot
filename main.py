import telebot
from registration import StartHandler
from history import HistoryHandler
from menu import Menu
from create_order import OrderHandler
from personal_account import ProfileHandler
from orders_today import OrdersTodayHandler
from config import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)
menu = Menu(bot)
order_handler = OrderHandler(bot)
profile_handler = ProfileHandler(bot)
orders_today_handler = OrdersTodayHandler(bot)
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
    orders_today_handler.handle_history(message)

@bot.message_handler(func=lambda message: message.text == 'Запись на прием')
def order(message):
    order_handler.handle(message)

@bot.message_handler(func=lambda message: message.text == 'Профиль')
def profile(message):
    profile_handler.handle(message)

@bot.message_handler(func=lambda message: message.text == 'Сегодняшние записи')
def today_orders(message):
    orders_today_handler.handle_today(message)

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

@bot.callback_query_handler(func=lambda call: call.data == 'edit_name')
def handle_edit_name(call):
    profile_handler.edit_name(call)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'edit_surname')
def handle_edit_surname(call):
    profile_handler.edit_surname(call)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'edit_secondname')
def handle_edit_secondname(call):
    profile_handler.edit_secondname(call)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'edit_birthdate')
def handle_edit_birthdate(call):
    profile_handler.edit_birthdate(call)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'edit_phone')
def handle_edit_phone(call):
    profile_handler.edit_phone(call)
    bot.answer_callback_query(call.id)

bot.polling()