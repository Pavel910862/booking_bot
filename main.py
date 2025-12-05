import os
import logging
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters   

from database.db_handler import DatabaseHandler
from handlers.user_handlers import UserHandlers
from handlers.booking_handlers import BookingHandlers, SERVICE, DATE, TIME, CONFIRM

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def error_handler(update: object, context):
    logging.error(f"Ошибка: {context.error}")

def main():
    token = "8222875427:AAHXTK6OTrJJ5Sm_OFZcxEa_A9qZE--PY4Q"

    try:
        # Создаем  Application
        application = Application.builder().token(token).build()

        # Инициализируем базу данных и обработчики
        db = DatabaseHandler("booking.db")
        user_handlers = UserHandlers(db)
        booking_handlers = BookingHandlers(db)

        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", user_handlers.start))
        application.add_handler(CommandHandler("help", user_handlers.help_command))
        application.add_handler(CommandHandler("my_bookings", booking_handlers.my_bookings_command))
        
        # Вместо простой команды /book создаем ConversationHandler для полноценного диалога
        booking_conv_handler = ConversationHandler(
            entry_points = [CommandHandler('book', booking_handlers.start_booking)],
            states = {
                SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, booking_handlers.choose_service)],
                DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, booking_handlers.choose_date)],
                TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND,booking_handlers.choose_time)],
                CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND,booking_handlers.confirm_booking)],
                },
                fallbacks=[CommandHandler('cancel', booking_handlers.cancel_booking)],
        )   
                
        application.add_handler(booking_conv_handler)

        application.add_error_handler(error_handler)

        print("Бот запускается...")
        print("📝 Доступные команды:")
        print("   /start - начать работу")
        print("   /book - записаться на услугу") 
        print("   /my_bookings - мои записи")
        print("   /help - помощь")

        # Запускаем бота в режиме polling (для разработки)
        application.run_polling()
    
    except Exception as e:
        print(f"❌ Ошибка при запуске: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == '__main__':
    main()