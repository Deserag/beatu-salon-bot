import telebot
import json

ORDERS_DATA_FILE = 'orders.json'

def load_orders():
    try:
        with open(ORDERS_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_orders(orders):
    with open(ORDERS_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(orders, f, indent=4)

class HistoryHandler:
    def __init__(self, bot):
        self.bot = bot
        self.orders = load_orders()
        self.current_evaluation = {}

    def handle(self, message):
        chat_id = message.chat.id
        user_orders = []

        for order_id, order in self.orders.items():
            if order['chat_id'] == chat_id:
                user_orders.append((order_id, order))

        if user_orders:
            message_text = "История посещений:\n\n"
            for order_id, order in user_orders:
                try:
                    message_text += f"Услуга: {order['service']}\nМастер: {order['master']}\nДата: {order['date']}\nВремя: {order['time']}\n\n"
                except KeyError:
                    message_text += f"Услуга: {order['service']}\nМастер: {order['master']}\nВремя: {order['time']}\n\n"
            self.bot.send_message(chat_id, message_text)
            for order_id, order in user_orders:
                self.send_evaluation_button(chat_id, order_id, order['service'])
        else:
            self.bot.send_message(chat_id, "История посещений пуста.")

    def send_evaluation_button(self, chat_id, order_id, service_name):
        markup = telebot.types.InlineKeyboardMarkup()
        evaluation_button = telebot.types.InlineKeyboardButton(f"Оценить {service_name}", callback_data=f"evaluate_{order_id}")
        markup.add(evaluation_button)
        self.bot.send_message(chat_id, "Оцените посещение:", reply_markup=markup)

    def handle_evaluation_callback(self, call):
        order_id = call.data.split('_')[1]
        self.current_evaluation[call.message.chat.id] = {'order_id': order_id}
        self.send_rating_buttons(call.message.chat.id)

    def send_rating_buttons(self, chat_id):
        markup = telebot.types.InlineKeyboardMarkup()
        for rating in range(1, 6):
            markup.add(telebot.types.InlineKeyboardButton(str(rating), callback_data=f"rating_{rating}"))
        self.bot.send_message(chat_id, "Выберите оценку (1-5):", reply_markup=markup)

    def handle_rating_callback(self, call):
        rating = call.data.split('_')[1]
        self.current_evaluation[call.message.chat.id]['rating'] = rating
        self.bot.send_message(call.message.chat.id, "Введите комментарий (необязательно):")
        self.bot.register_next_step_handler(call.message, self.process_comment)

    def process_comment(self, message):
        chat_id = message.chat.id
        comment = message.text
        order_id = self.current_evaluation[chat_id]['order_id']
        rating = self.current_evaluation[chat_id]['rating']

        self.orders[order_id]['rating'] = rating
        self.orders[order_id]['comment'] = comment

        save_orders(self.orders)
        self.bot.send_message(chat_id, f"Спасибо за оценку ({rating}) и комментарий!")
        del self.current_evaluation[chat_id]