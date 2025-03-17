import telebot
from datetime import datetime, timedelta

class StatisticHandler:
    def __init__(self, bot):
        self.bot = bot
        self.prisma = None

    def handle(self, message):
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

        total_profit = 0
        today_masters = set()

        for record in today_records:
            total_profit += record.service.price
            today_masters.add(f"{record.worker.firstName} {record.worker.lastName}")

        message_text = f"Статистика за {today.strftime('%d.%m.%Y')}:\n\n"
        message_text += f"Прибыль за сегодня: {total_profit} руб.\n"
        message_text += f"Количество оказанных услуг: {len(today_records)}\n"
        message_text += f"Сегодня работают: {', '.join(today_masters)}"

        self.bot.send_message(chat_id, message_text)