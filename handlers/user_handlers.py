from telegram import Update                     # Update - объект с данными о входящем сообщении
from telegram.ext import ContextTypes           # ContextTypes - для работы с контекстом бота (данные, чат и т.д.)
from models.user import User
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserHandlers:
    def __init__(self, db):                     # __init__ - конструктор, принимает объект базы данных
        self.db = db                            # # ← сюда передается DatabaseHandler когда БД в main инициализирцем, self.db = db - сохраняем БД в атрибут класса для использования во всех методах
        logger.info("UserHandlers инициализирован")


    # асинхронный обработчик команды /start
    # update - содержит информацию о сообщении ("что произошло" (сообщение, кто отправил))
    # context - "в какой обстановке произошло" (состояние бота), (контекст — это "окружение" или "состояние системы" в конкретный момент времени) бота
    async def start (self, update: Update, context: ContextTypes.DEFAULT_TYPE):     
        # Обработчик команды /start
        # user = update.effective_user - получаем данные пользователя
        user = update.effective_user
        logger.info(f"Команда /start от {user.full_name} (ID: {user.id})")

        try:
            # Создаем объект пользователя
            new_user = User(
                user_id=user.id,
                username=user.username,
                full_name=user.full_name,
                created_at=datetime.now()
            )           
            
            # Сохраняем в базу данных
            saved_user = self.db.add_user(new_user)
            logger.info(f"Пользователь {user.id} сохранен в БД")

            await update.message.reply_text(       # метод Telegram Bot API для ответа на сообщение в том же чате
                f"Привет, {user.full_name}! 👋\n"
                f"Я бот для записи на услуги.\n"
                f"Используйте команды:\n"
                f"/book - записаться\n"
                f"/my_bookings - мои записи"
            )
        
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            await update.message.reply_text("❌ Произошла ошибка при сохранении в БД")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Доступные команды:\n"
            "/start - начать работу\n"
            "/book - записаться на услугу\n"
            "/my_bookings - посмотерть мои записи\n"
            "/help - помощь\n"
        )

    async def book_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        logger.info(f"Команда /book от {user.full_name}")

        # Пока просто заглушка - в будущем здесь будет полноценная логика записи
        await update.message.reply_text(
            "📅 Запись на услугу\n\n"
            "Выберите услугу:\n"
            "1. 💇 Стрижка\n"
            "2. 💅 Маникюр\n"
            "3. ✂️ Стрижка + укладка\n\n"
            "⚡ Функционал записи в разработке...\n"
            "Скоро здесь можно будет выбрать дату и время!"
        )

    async def my_bookings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        logger.info(f"Команда /my_bookings от {user.full_name}")

        # Пока просто заглушка - в будущем здесь будет вывод записей из БД
        await update.message.reply_text(
            "📋 Ваши записи:\n\n"
            "Пока нет активных записей.\n\n"
            "⚡ Функционал просмотра записей в разработке...\n"
            "Скоро здесь будут отображаться все ваши бронирования!\n"
            ) 