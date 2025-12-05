from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
# ConversationHandler - для FSM (конечный автомат для состояния диалога)
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters     
from models.user import Booking
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)                # создает именованный логгер для текущего модуля

'''Пользователь: /book
    ↓
Бот: "Выберите услугу" → состояние SERVICE (0)
    ↓  
Пользователь: "💇 Стрижка"
    ↓
Бот: "На какую дату?" → состояние DATE (1)
    ↓
Пользователь: "20.11.2024"  
    ↓
Бот: "На какое время?" → состояние TIME (2)
    ↓
Пользователь: "14:30"
    ↓
Бот: "Подтвердите..." → состояние CONFIRM (3)'''

SERVICE, DATE, TIME, CONFIRM = range(4)             # Состояния для ConversationHandler


class BookingHandlers:
    def __init__(self, db):                         # Метод инициализции класса, вызывается при создании бота
        self.db = db                                # Сохраняем переданный объект базы данных для работы с БД, т.е сюда БД передается для подключения
        # c self. своё свойство для каждого объекта, без self. общий атрибут для всех объектов (свойство - логика, атирибут - костанта)
        self.available_services = ["💇 Стрижка", "Маникюр", "✂️ Стрижка + укладка"]
        self.working_hours = ["10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00"]


    # Асинхронный метод начала процесса бронирования
    async def start_booking(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user                # Получаем информацию о пользователе который отправил сообщение

        # Создаем клавиатуру с конпками услугами
        # Для каждой услуги создаем отдельную строку в клавиатуре
        keyboard = [[KeyboardButton(service)] for service in self.available_services]
        '''Создаем разметку клавиатуры с параметрами:
        one_time_keyboard=True - клавиатура скроется после выбора
        resize_keyboard=True - клавиатура автоматически подстроит размер'''
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True, input_field_placeholder="Выберите услугу...")
        
        await update.message.reply_text(
            "📅 Запись на услуги\n\n"
            "Выберите услугу:",
            reply_markup=reply_markup              # Прикрепляем созданную клавиатуру из 47 строки
        )
        
        return SERVICE                             # Возвращаем следующее состояние - выбор услуги
    
    # Асинхронный метод обработки выбора услуги
    async def choose_service(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        service = update.message.text              # Получаем текст сообщения (выбранную услугу)
        context.user_data['service'] = service     # Сохраняем её (выбранную услугу) во временные данные пользователя

        today = datetime.now().date()
        dates = []                                 # Создаем список доступных дат (сегодня + следующие 7 дней)
        for i in range(7):
            date = today + timedelta(days=i)       # Вычисляем дату путем добавления i дней к сегодняшней дате
            dates.append(date.strftime("%d.%m.%Y"))# Форматируем дату в строку и добавляем в список

        keyboard = [[KeyboardButton(date)] for date in dates] # Создаем клавиатуру с кнопкам и дат
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

        await update.message.reply_text(           # Отправляем сообщение с подтверждением выбора услуги и просьбой выбрать дату
            f"✅ Выбрана услуга {service}\n\n"
            "Теперь выберите дату:",
            reply_markup=reply_markup
        ) 
       
        return DATE                                # Возвращаем следующее состояние - выбор даты
    
    # Асинхронный метод выбора даты
    async def choose_date(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        date_str = update.message.text             # Получаем выбранную дату из сообщения
        context.user_data['date'] = date_str       # Сохраняем во временные данные пользователя

        keyboard = [[KeyboardButton(time)] for time in self.working_hours]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

        await update.message.reply_text(
            f"📅 Дата: {date_str}\n\n"
            "Выберите время:",
            reply_markup=reply_markup
        )

        return TIME

    # Асинхронный метод обработки выбора времени
    async def choose_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        time_str = update.message.text
        context.user_data['time'] = time_str

        # Извлекаем ранее сохраненные данные об услуге и дате
        service = context.user_data['service']
        date = context.user_data['date']

        keyboard = [[KeyboardButton("✅ Подтвердить"), KeyboardButton("❌ Отменить")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

        # Отправляем сообщения со сводкой бронирования для подтверждения
        await update.message.reply_text(            # update - 'то объект, который Telegram присылает боту при любом событии (сообщение, кнопка и тд)
            f"📋 Подтвердите запись:\n\n"
            f"📍 Услуга: {service}\n"
            f"📅 Дата: {date}\n"
            f"⏰ Время: {time_str}\n\n"
            f"Всё верно?",
            reply_markup=reply_markup
        )

        return CONFIRM
    
    # Асинхронный метод подтверждения бронирования
    async def confirm_booking(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user

        # СПЕРВА отправляем сообщение с удалением клавиатуры
        if update.message.text == '✅ Подтвердить':
            await update.message.reply_text(
                ".",
                reply_markup=ReplyKeyboardRemove()
        )
            # Извлекаем все данные о бронировании из временного хранилища
            service = context.user_data['service']
            date_str = context.user_data['date']
            time_str = context.user_data['time']

            booking_datetime = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")

            # Создаем новый объект броинирования с собранными данными
            new_booking = Booking(
                user_id=user.id,
                service_type=service,
                booking_date=booking_datetime,
                created_at=datetime.now()
            )

            saved_booking = self.db.add_booking(new_booking)

            await update.message.reply_text(
                f"🎉 Запись подтверждена!\n\n"
                f"📍 Услуга: {service}\n"
                f"📅 Дата: {date_str}\n"
                f"⏰ Время: {time_str}\n\n"
                f"Ждём вас! 🎯",
            )
        else:
            await update.message.reply_text(
            ".",
            reply_markup=ReplyKeyboardRemove()
        )
            # если пользователь нажал кнопку "Отменить", отправляем сообщение об отмене
            await update.message.reply_text(
                "❌ Запись отменена",
            )

        context.user_data.clear()
        return ConversationHandler.END                  # завершаем машину состояний
        
    # Асинхронный метод отмены бронирования
    async def cancel_booking(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "❌ Процесс бронирования отменен",
            reply_markup=None
        )

        context.user_data.clear()
        return ConversationHandler.END

    # Асинхронный метод проверки моих записей
    async def my_bookings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        
        try:
            bookings = self.db.get_user_bookings(user.id)

            if not bookings:
                await update.message.reply_text(
                "📋 У вас пока нет активных записей.\n\n"
                "Используйте /book чтобы создать первую запись! ✨"    
                )
                return
            
            message = "📋 Ваши записи:\n\n"

            for i, booking in enumerate(bookings, 1):
                date_str = booking.booking_date.strftime("%d.%m.%Y")
                time_str = booking.booking_date.strftime("%H:%M")

                message += f"🔸 **Запись #{i}**\n"
                message += f"   📍 Услуга: {booking.service_type}\n"
                message += f"   📅 Дата: {date_str}\n"
                message += f"   ⏰ Время: {time_str}\n"
                message += f"   🆔 ID: {booking.id}\n\n"

            await update.message.reply_text(message, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Ошибка при получении бронирований: {e}")
            await update.message.reply_text(
                "❌ Произошла ошибка при получении ваших записей.\n"
                "Попробуйте позже или обратитесь к администратору."
            )

