import telebot
from datetime import datetime, timedelta
from config import get_db_connection

class StatisticHandler:
    def __init__(self, bot):
        self.bot = bot

    def handle(self, message):
        chat_id = message.chat.id
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            # Получаем записи на сегодня с информацией об услугах и мастерах
            cur.execute("""
                SELECT s.price, u.first_name, u.last_name
                FROM service_records sr
                JOIN services s ON sr.service_id = s.id
                JOIN  u ON sr.worker_id = u.id
                WHERE sr.date_time >= %s AND sr.date_time < %s
            """, (today, tomorrow))
            
            records = cur.fetchall()
            
            total_profit = 0
            today_masters = set()

            for record in records:
                price, first_name, last_name = record
                total_profit += price
                today_masters.add(f"{first_name} {last_name}")

            # Формируем сообщение со статистикой
            message_text = f"Статистика за {today.strftime('%d.%m.%Y')}:\n\n"
            message_text += f"Общая выручка: {total_profit} руб.\n"
            message_text += f"Количество записей: {len(records)}\n"
            
            if today_masters:
                message_text += f"Работающие мастера:\n"
                message_text += "\n".join(f"• {master}" for master in sorted(today_masters))
            else:
                message_text += "Сегодня нет запланированных записей"

            # Получаем статистику по популярным услугам
            cur.execute("""
                SELECT s.name, COUNT(*) as count
                FROM service_records sr
                JOIN services s ON sr.service_id = s.id
                WHERE sr.date_time >= %s AND sr.date_time < %s
                GROUP BY s.name
                ORDER BY count DESC
                LIMIT 3
            """, (today, tomorrow))
            
            popular_services = cur.fetchall()
            
            if popular_services:
                message_text += "\n\nПопулярные услуги:\n"
                for service in popular_services:
                    message_text += f"• {service[0]} - {service[1]} записей\n"

            self.bot.send_message(chat_id, message_text)

        except Exception as e:
            self.bot.send_message(chat_id, f"Ошибка при получении статистики: {str(e)}")
        finally:
            cur.close()
            conn.close()