import sqlite3
from models.user import User, Booking
from datetime import datetime

class DatabaseHandler:
    def __init__(self, db_path: str):
        self.connection = sqlite3.connect(db_path, check_same_thread=False)  # check_same_thread=False - разрешает использование подключения из разных потоков (обычно не рекомендуется, но иногда необходимо)
        self._create_tables()           

    def _create_tables(self):
        # Создаем таблицы в базе данных (''' - для многочтрочного текста)
        # with — контекстный менеджер -  это страховка от "забыл закрыть ресурс". Используйте везде, где есть "получил → использовал → должен освободить".
        # здесь with управляет транзакциями, в частности применяет изменения
        # self.connection.execute - это метод для выполнения SQL-запросов в базе данных через соединение.
        with self.connection:
            self.connection.execute('''                                                                    
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    full_name TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            ''')
        self.connection.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                service_type TEXT NOT NULL,
                booking_date TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
                
    def add_user(self, user: User) -> User:
        # Добавляем пользователя в БД
        if not user.created_at:
            user.created_at = datetime.now()

        # указаетль на конкретные строки в БД, чтобы не загружать в память всю БД
        cursor = self.connection.execute('''
            INSERT OR IGNORE INTO users (user_id, username, full_name, created_at)
            VALUES(?, ?, ?, ?)''',
            (user.user_id, user.username, user.full_name, user.created_at.isoformat()))
        
        self.connection.commit()
        
        # Получаем ID новой запииси
        if cursor.lastrowid:                    # lastrowid - это атрибут курсора SQLite, который возвращает ID последней вставленной строки.
            user.id = cursor.lastrowid

        return user
    
    def add_booking(self, booking: Booking) -> Booking:
        if not booking.created_at:
            booking.created_at = datetime.now()

        cursor = self.connection.execute('''
            INSERT INTO bookings (user_id, service_type, booking_date, created_at)
            VALUES(?, ?, ?, ?)''',
            (booking.user_id, booking.service_type, booking.booking_date.isoformat(), booking.created_at.isoformat()))
        
        self.connection.commit()
        
        if cursor.lastrowid:                                # Если БД сгенерировала ID
            booking.id = cursor.lastrowid                   # Сохраняем его в объект

        return booking

    def get_user_bookings(self, user_id: int):
        # получаем все бронирования пользователя
        cursor = self.connection.execute(               # Отправляет запрос в базу данных - Ждет ответа - Создает курсор с результатами  
            'SELECT * FROM bookings WHERE user_id = ? ORDER BY booking_date DESC',
            (user_id,)
        )
        rows = cursor.fetchall()
        return [Booking.from_db_row(row) for row in rows] if rows else []

    def get_user_by_telegram_id(self, telegram_id: int):
        # получает пользователя по Telegram ID
        # выбрать все поля из таблицы user
        # где user_id равен переданному значению
        # ВАЖНО: запятая делает кортеж с одним элементом
        # connection.execute() возвращает курсор с результатами
        cursor = self.connection.execute(
            'SELECT * FROM users WHERE user_id = ?',
            (telegram_id,)
        )
        row = cursor.fetchone()                          # fetchone() — получить одну строку
        # from_db_row - метод в user.py - cоздает объект User из строки БД
        return User.from_db_row(row) if row else None    # Если пользователь найден → возвращает кортеж с данными, если не найден → возвращает None

    def close(self):
        self.connection.close()