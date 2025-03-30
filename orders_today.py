import telebot
import psycopg2
from datetime import datetime, timedelta
from config import get_db_connection

class OrdersTodayHandler:
    def __init__(self, bot):
        self.bot = bot

    def handle_today(self, message):
        chat_id = message.chat.id
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT s.name, u.first_name, u.last_name, sr.date_time
                FROM service_records sr
                JOIN services s ON sr.service_id = s.id
                JOIN user u ON sr.worker_id = u.id
                WHERE sr.date_time >= %s AND sr.date_time < %s
                ORDER BY sr.date_time
            """, (today, tomorrow))
            
            records = cur.fetchall()
            
            if records:
                message_text = "Сегодняшние записи:\n\n"
                for record in records:
                    dt = record[3]
                    message_text += (
                        f"Услуга: {record[0]}\n"
                        f"Мастер: {record[1]} {record[2]}\n"
                        f"Дата: {dt.strftime('%d.%m.%Y')}\n"
                        f"Время: {dt.strftime('%H:%M')}\n\n"
                    )
                self.bot.send_message(chat_id, message_text)
            else:
                self.bot.send_message(chat_id, "На сегодня записей нет.")
                
        finally:
            cur.close()
            conn.close()

    def handle_history(self, message):
        chat_id = message.chat.id
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("SELECT id FROM clients WHERE telegram_id = %s", (str(chat_id),))
            client = cur.fetchone()
            
            if not client:
                self.bot.send_message(chat_id, "История посещений пуста.")
                return

            cur.execute("""
                SELECT s.name, u.first_name, u.last_name, sr.date_time
                FROM service_records sr
                JOIN services s ON sr.service_id = s.id
                JOIN user u ON sr.worker_id = u.id
                WHERE sr.client_id = %s
                ORDER BY sr.date_time DESC
            """, (client[0],))
            
            records = cur.fetchall()
            
            if records:
                message_text = "История посещений:\n\n"
                for record in records:
                    dt = record[3]
                    message_text += (
                        f"Услуга: {record[0]}\n"
                        f"Мастер: {record[1]} {record[2]}\n"
                        f"Дата: {dt.strftime('%d.%m.%Y')}\n"
                        f"Время: {dt.strftime('%H:%M')}\n\n"
                    )
                self.bot.send_message(chat_id, message_text)
            else:
                self.bot.send_message(chat_id, "История посещений пуста.")
                
        finally:
            cur.close()
            conn.close()