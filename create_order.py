import telebot
import re
import psycopg2
from datetime import datetime, timedelta
from config import get_db_connection

class OrderHandler:
    def __init__(self, bot):
        self.bot = bot
        self.current_order = {}

    def handle(self, message):
        chat_id = message.chat.id
        self.current_order[chat_id] = {}
        self.show_services(chat_id)

    def show_services(self, chat_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM services")
        services = cur.fetchall()
        cur.close()
        conn.close()
        
        markup = telebot.types.InlineKeyboardMarkup()
        for service in services:
            markup.add(telebot.types.InlineKeyboardButton(service[1], callback_data=f'service_{service[0]}'))
        self.bot.send_message(chat_id, "Выберите услугу:", reply_markup=markup)

    def process_service(self, chat_id, service_id):
        self.current_order[chat_id]['service_id'] = service_id
        self.show_masters(chat_id, service_id)

    def show_masters(self, chat_id, service_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT u.id, u.first_name, u.last_name 
            FROM user u
            JOIN worker_on_service wos ON wos.user_id = u.id
            WHERE wos.service_id = %s
        """, (service_id,))
        masters = cur.fetchall()
        cur.close()
        conn.close()
        
        markup = telebot.types.InlineKeyboardMarkup()
        for master in masters:
            markup.add(telebot.types.InlineKeyboardButton(
                f"{master[1]} {master[2]}", 
                callback_data=f'master_{master[0]}'
            ))
        self.bot.send_message(chat_id, "Выберите мастера:", reply_markup=markup)

    def process_master(self, chat_id, master_id):
        self.current_order[chat_id]['master_id'] = master_id
        self.bot.register_next_step_handler(
            self.bot.send_message(chat_id, "Введите дату в формате ДД.ММ.ГГГГ:"),
            self.process_date, chat_id
        )

    def process_date(self, message, chat_id):
        date_str = message.text
        if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', date_str):
            self.bot.send_message(chat_id, "Неверный формат даты. Введите дату в формате ДД.ММ.ГГГГ:")
            self.bot.register_next_step_handler(
                self.bot.send_message(chat_id, "Введите дату в формате ДД.ММ.ГГГГ:"),
                self.process_date, chat_id
            )
            return
        
        try:
            date = datetime.strptime(date_str, '%d.%m.%Y').date()
            self.current_order[chat_id]['date'] = date
            self.show_available_times(chat_id)
        except ValueError:
            self.bot.send_message(chat_id, "Неверная дата. Введите дату в формате ДД.ММ.ГГГГ:")
            self.bot.register_next_step_handler(
                self.bot.send_message(chat_id, "Введите дату в формате ДД.ММ.ГГГГ:"),
                self.process_date, chat_id
            )

    def show_available_times(self, chat_id):
        date = self.current_order[chat_id]['date']
        master_id = self.current_order[chat_id]['master_id']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT start_time FROM schedules 
            WHERE user_id = %s AND date = %s
        """, (master_id, date))
        occupied_times = [t[0].strftime('%H:%M') for t in cur.fetchall()]
        cur.close()
        conn.close()
        
        available_times = [f'{hour:02d}:{minute:02d}' 
                          for hour in range(9, 18) 
                          for minute in range(0, 60, 30)]
        
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
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT name FROM services WHERE id = %s", (order['service_id'],))
        service_name = cur.fetchone()[0]
        
        cur.execute("SELECT first_name, last_name FROM user WHERE id = %s", (order['master_id'],))
        master = cur.fetchone()
        master_name = f"{master[0]} {master[1]}"
        
        cur.close()
        conn.close()
        
        message = (
            f"Вы выбрали услугу: {service_name}\n"
            f"Мастер: {master_name}\n"
            f"Дата: {order['date'].strftime('%d.%m.%Y')}\n"
            f"Время: {order['time']}\n"
            "Подтвердить заказ?"
        )
        
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("Подтвердить", callback_data="confirm_order"))
        markup.add(telebot.types.InlineKeyboardButton("Отменить", callback_data="cancel_order"))
        self.bot.send_message(chat_id, message, reply_markup=markup)

    def complete_order(self, chat_id):
        order = self.current_order[chat_id]
        time_obj = datetime.strptime(order['time'], '%H:%M').time()
        order_datetime = datetime.combine(order['date'], time_obj)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            # Получаем клиента
            cur.execute("SELECT id FROM clients WHERE telegram_id = %s", (str(chat_id),))
            client_id = cur.fetchone()[0]
            
            # Находим свободный кабинет для мастера
            cur.execute("""
                SELECT c.id, c.office_id 
                FROM cabinets c
                JOIN user_on_cabinet uoc ON uoc.cabinet_id = c.id
                WHERE uoc.user_id = %s AND c.status = 'AVAILABLE'
                LIMIT 1
            """, (order['master_id'],))
            cabinet = cur.fetchone()
            
            if not cabinet:
                self.bot.send_message(chat_id, "К сожалению, нет доступных кабинетов для выбранного мастера.")
                return
            
            # Создаем запись о сервисе
            cur.execute("""
                INSERT INTO service_records (
                    client_id, worker_id, date_time, 
                    service_id, office_id, work_cabinet_id
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                client_id, order['master_id'], order_datetime,
                order['service_id'], cabinet[1], cabinet[0]
            ))
            
            # Добавляем в расписание
            end_time = order_datetime + timedelta(minutes=30)
            cur.execute("""
                INSERT INTO schedules (
                    date, start_time, end_time, 
                    user_id, cabinet_id
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                order['date'], order_datetime.time(), end_time.time(),
                order['master_id'], cabinet[0]
            ))
            
            conn.commit()
            self.bot.send_message(chat_id, "Заказ успешно оформлен!")
            
        except Exception as e:
            conn.rollback()
            self.bot.send_message(chat_id, f"Произошла ошибка: {str(e)}")
        finally:
            cur.close()
            conn.close()
        
        del self.current_order[chat_id]

    def cancel_order(self, chat_id):
        self.bot.send_message(chat_id, "Заказ отменен.")
        del self.current_order[chat_id]