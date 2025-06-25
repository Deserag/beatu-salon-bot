import telebot
from datetime import datetime, timedelta
from config import get_db_connection, BOT_TOKEN

class NotificationSender:
    def __init__(self, bot):
        self.bot = bot

    def send_hourly_notifications(self):
        conn = get_db_connection()
        cur = conn.cursor()

        try:
            current_time = datetime.now()
            time_threshold_start = current_time + timedelta(hours=1)
            time_threshold_end = current_time + timedelta(hours=2)

            cur.execute("""
                SELECT
                    sr."dateTime",
                    s.name AS service_name,
                    u."telegramId",
                    u."firstName"
                FROM "serviceRecord" sr
                JOIN service s ON sr."serviceId" = s.id
                JOIN "user" u ON sr."userId" = u.id -- ИСПОЛЬЗУЕМ sr."userId" для связи с таблицей "user"
                WHERE sr."dateTime" >= %s AND sr."dateTime" < %s
            """, (time_threshold_start, time_threshold_end))

            upcoming_records = cur.fetchall()

            for record in upcoming_records:
                record_datetime, service_name, user_telegram_id, user_first_name = record
                if user_telegram_id: 
                    notification_message = (
                        f"Привет, {user_first_name}!\n\n"
                        f"Напоминаем, у вас скоро запись:\n"
                        f"Услуга: {service_name}\n"
                        f"Дата: {record_datetime.strftime('%d.%m.%Y')}\n"
                        f"Время: {record_datetime.strftime('%H:%M')}\n\n"
                        f"Будем рады вас видеть!"
                    )
                    self.bot.send_message(user_telegram_id, notification_message)
                    print(f"Отправлено уведомление для {user_telegram_id} о записи на {service_name} в {record_datetime}")
                else:
                    print(f"Пользователь с ID {record[2]} не имеет telegramId, уведомление не отправлено.")

        except Exception as e:
            print(f"Ошибка при отправке уведомлений: {e}")
        finally:
            cur.close()
            conn.close()

