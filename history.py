import telebot

class HistoryHandler:
    def __init__(self, bot):
        self.bot = bot
        self.prisma = None
        self.current_evaluation = {}

    def handle(self, message):
        chat_id = message.chat.id
        client = self.prisma.client.find_first(where={'telegramId': str(chat_id)})

        if not client:
            self.bot.send_message(chat_id, "История посещений пуста.")
            return

        service_records = self.prisma.serviceRecord.find_many(
            where={'clientId': client.id},
            include={'service': True, 'worker': True}
        )

        if service_records:
            message_text = "История посещений:\n\n"
            for record in service_records:
                message_text += f"Услуга: {record.service.name}\nМастер: {record.worker.firstName} {record.worker.lastName}\nДата: {record.dateTime.strftime('%d.%m.%Y')}\nВремя: {record.dateTime.strftime('%H:%M')}\n\n"
            self.bot.send_message(chat_id, message_text)

            for record in service_records:
                self.send_evaluation_button(chat_id, record.id, record.service.name)
        else:
            self.bot.send_message(chat_id, "История посещений пуста.")

    def send_evaluation_button(self, chat_id, record_id, service_name):
        markup = telebot.types.InlineKeyboardMarkup()
        evaluation_button = telebot.types.InlineKeyboardButton(f"Оценить {service_name}", callback_data=f"evaluate_{record_id}")
        markup.add(evaluation_button)
        self.bot.send_message(chat_id, "Оцените посещение:", reply_markup=markup)

    def handle_evaluation_callback(self, call):
        record_id = call.data.split('_')[1]
        self.current_evaluation[call.message.chat.id] = {'record_id': record_id}
        self.send_rating_buttons(call.message.chat.id)

    def send_rating_buttons(self, chat_id):
        markup = telebot.types.InlineKeyboardMarkup()
        for rating in range(1, 6):
            markup.add(telebot.types.InlineKeyboardButton(str(rating), callback_data=f"rating_{rating}"))
        self.bot.send_message(chat_id, "Выберите оценку (1-5):", reply_markup=markup)

    def handle_rating_callback(self, call):
        rating = int(call.data.split('_')[1])
        self.current_evaluation[call.message.chat.id]['rating'] = rating
        self.bot.send_message(call.message.chat.id, "Введите комментарий (необязательно):")
        self.bot.register_next_step_handler(call.message, self.process_comment)

    def process_comment(self, message):
        chat_id = message.chat.id
        comment = message.text
        record_id = self.current_evaluation[chat_id]['record_id']
        rating = self.current_evaluation[chat_id]['rating']

        self.prisma.review.create({
            'data': {
                'grade': rating,
                'comment': comment,
                'clientId': self.prisma.client.find_first(where={'telegramId': str(chat_id)}).id,
                'serviceId': self.prisma.serviceRecord.find_first(where={'id': record_id}).serviceId
            }
        })
        self.bot.send_message(chat_id, f"Спасибо за оценку ({rating}) и комментарий!")
        del self.current_evaluation[chat_id]