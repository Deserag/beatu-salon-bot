import telebot
import re
from datetime import datetime, timedelta

class OrderHandler:
    def __init__(self, bot):
        self.bot = bot
        self.prisma = None
        self.current_order = {}

    def handle(self, message):
        chat_id = message.chat.id
        self.current_order[chat_id] = {}
        self.show_services(chat_id)

    def show_services(self, chat_id):
        services = self.prisma.service.find_many()
        markup = telebot.types.InlineKeyboardMarkup()
        for service in services:
            markup.add(telebot.types.InlineKeyboardButton(service.name, callback_data=f'service_{service.id}'))
        self.bot.send_message(chat_id, "Выберите услугу:", reply_markup=markup)

    def process_service(self, chat_id, service_id):
        self.current_order[chat_id]['service_id'] = service_id
        self.show_masters(chat_id, service_id)

    def show_masters(self, chat_id, service_id):
        service = self.prisma.service.find_first(where={'id': service_id}, include={'workersOnService': True})
        markup = telebot.types.InlineKeyboardMarkup()
        for worker_service in service.workersOnService:
            master = self.prisma.user.find_first(where={'id': worker_service.userId})
            if master:
                markup.add(telebot.types.InlineKeyboardButton(f'{master.firstName} {master.lastName}', callback_data=f'master_{master.id}'))
        self.bot.send_message(chat_id, "Выберите мастера:", reply_markup=markup)

    def process_master(self, chat_id, master_id):
        self.current_order[chat_id]['master_id'] = master_id
        self.bot.register_next_step_handler(self.bot.send_message(chat_id, "Введите дату в формате ДД.ММ.ГГГГ:"), self.process_date, chat_id)

    def process_date(self, message, chat_id):
        date_str = message.text
        if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', date_str):
            self.bot.send_message(chat_id, "Неверный формат даты. Введите дату в формате ДД.ММ.ГГГГ:")
            self.bot.register_next_step_handler(self.bot.send_message(chat_id, "Введите дату в формате ДД.ММ.ГГГГ:"), self.process_date, chat_id)
            return
        try:
            date = datetime.strptime(date_str, '%d.%m.%Y').date()
            self.current_order[chat_id]['date'] = date
            self.show_available_times(chat_id, self.current_order[chat_id]['service_id'], self.current_order[chat_id]['master_id'])
        except ValueError:
            self.bot.send_message(chat_id, "Неверный формат даты. Введите дату в формате ДД.ММ.ГГГГ:")
            self.bot.register_next_step_handler(self.bot.send_message(chat_id, "Введите дату в формате ДД.ММ.ГГГГ:"), self.process_date, chat_id)

    def show_available_times(self, chat_id, service_id, master_id):
        date = self.current_order[chat_id]['date']
        master = self.prisma.user.find_first(where={'id': master_id})
        start_time = datetime.combine(date, datetime.min.time())
        end_time = start_time + timedelta(hours=24)
        schedules = self.prisma.schedule.find_many(
            where={
                'userId': master_id,
                'date': {'gte': start_time, 'lt': end_time}
            }
        )
        occupied_times = [schedule.startTime.strftime('%H:%M') for schedule in schedules]
        available_times = [f'{hour:02d}:{minute:02d}' for hour in range(9, 18) for minute in range(0, 60, 30)]
        markup = telebot.types.InlineKeyboardMarkup()
        for time in available_times:
            if time in occupied_times:
                button_text = f" {time} (занято)"
                callback_data = "occupied"
            else:
                button_text = f"🟢 {time}"
                callback_data = f"time_{time}"
            markup.add(telebot.types.InlineKeyboardButton(button_text, callback_data=callback_data))
        self.bot.send_message(chat_id, "Выберите время:", reply_markup=markup)

    def process_time(self, chat_id, time):
        self.current_order[chat_id]['time'] = time
        self.confirm_order(chat_id)

    def confirm_order(self, chat_id):
        order = self.current_order[chat_id]
        service = self.prisma.service.find_first(where={'id': order['service_id']})
        master = self.prisma.user.find_first(where={'id': order['master_id']})
        message = f"Вы выбрали услугу: {service.name}\nМастер: {master.firstName} {master.lastName}\nДата: {order['date'].strftime('%d.%m.%Y')}\nВремя: {order['time']}\nПодтвердить заказ?"
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("Подтвердить", callback_data="confirm_order"))
        markup.add(telebot.types.InlineKeyboardButton("Отменить", callback_data="cancel_order"))
        self.bot.send_message(chat_id, message, reply_markup=markup)

    def complete_order(self, chat_id):
        order = self.current_order[chat_id]
        service = self.prisma.service.find_first(where={'id': order['service_id']})
        master = self.prisma.user.find_first(where={'id': order['master_id']})
        time_obj = datetime.strptime(order['time'], '%H:%M').time()
        order_datetime = datetime.combine(order['date'], time_obj)
        client = self.prisma.client.find_first(where={'telegramId': str(chat_id)})

        # Выбор кабинета
        cabinet = self.prisma.cabinet.find_first(
            where={
                'status': 'AVAILABLE',
                'users': {'some': {'userId': master.id}}
            }
        )

        if not cabinet:
            self.bot.send_message(chat_id, "К сожалению, нет доступных кабинетов для выбранного мастера.")
            return

        self.prisma.serviceRecord.create({
            'data': {
                'clientId': client.id,
                'workerId': master.id,
                'dateTime': order_datetime,
                'serviceId': service.id,
                'officeId': cabinet.officeId,
                'workCabinetId': cabinet.id,
            }
        })
        self.prisma.schedule.create({
            'data': {
                'date': order['date'],
                'startTime': order_datetime,
                'endTime': order_datetime + timedelta(minutes=30),
                'userId': master.id,
                'cabinetId': cabinet.id,
            }
        })
        self.bot.send_message(chat_id, "Заказ успешно оформлен!")
        del self.current_order[chat_id]

    def cancel_order(self, chat_id):
        self.bot.send_message(chat_id, "Заказ отменен.")
        del self.current_order[chat_id]