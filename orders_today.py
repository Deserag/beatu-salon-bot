import telebot
from datetime import datetime, timedelta

class OrdersTodayHandler:
    def __init__(self, bot):
        self.bot = bot
        self.prisma = None

    def handle_today(self, message):
        chat_id = message.chat.id
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)

        today_records = self.prisma.serviceRecord.find_many(
            where={
                'dateTime': {
                    'gte': datetime.combine(today, datetime.min.time()),
                    'lt': datetime.combine(tomorrow, datetime.min.time()),
                }
            },
            include={'service': True, 'worker': True}
        )

        if today_records:
            message_text = "Сегодняшние записи:\n\n"
            for record in today_records:
                message_text += f"Услуга: {record.service.name}\nМастер: {record.worker.firstName} {record.worker.lastName}\nДата: {record.dateTime.strftime('%d.%m.%Y')}\nВремя: {record.dateTime.strftime('%H:%M')}\n\n"
            self.bot.send_message(chat_id, message_text)
        else:
            self.bot.send_message(chat_id, "На сегодня записей нет.")

    def handle_history(self, message):
        chat_id = message.chat.id
        client = self.prisma.client.find_first(where={'telegramId': str(chat_id)})

        if not client:
            self.bot.send_message(chat_id, "История посещений пуста.")
            return

        user_records = self.prisma.serviceRecord.find_many(
            where={'clientId': client.id},
            include={'service': True, 'worker': True}
        )

        if user_records:
            message_text = "История посещений:\n\n"
            for record in user_records:
                message_text += f"Услуга: {record.service.name}\nМастер: {record.worker.firstName} {record.worker.lastName}\nДата: {record.dateTime.strftime('%d.%m.%Y')}\nВремя: {record.dateTime.strftime('%H:%M')}\n\n"
            self.bot.send_message(chat_id, message_text)
        else:
            self.bot.send_message(chat_id, "История посещений пуста.")