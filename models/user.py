from dataclasses import dataclass                         # импорт декоратора класса, чтобы писать без __init__  и т.д.
from datetime import datetime                             # функциоанал для работы с датами и временем
from typing import Optional                               # Optional[Type]  # означает: Type или None

@dataclass                                                # @dataclass = меньше шаблонного кода для классов-данных
class User:
    id: Optional[int] = None                              #  может быть указанным типом или None
    user_id: Optional[int] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    created_at: Optional[datetime] = None

    @classmethod                                          # @classmethod = методы, которые работают с классом и создают экземпляры
    def from_db_row(cls, row: tuple):                     # получает класс как первый аргумент
        if not row:
            return None
        return cls(                                       # cоздает объект ТОГО ЖЕ класса
            id = row[0],    
            user_id = row[1],
            username = row[2],
            full_name = row[3],
            created_at = datetime.fromisoformat(row[4]) if row[4] else None
        )

@dataclass
class Booking:
    id: Optional[int] = None
    user_id: Optional[int] = None
    service_type: Optional[str] = None
    booking_date: Optional[datetime] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_db_row(cls, row: tuple):
        if not row:
            return None
        return cls(
            id=row[0],
            user_id=row[1],
            service_type=row[2],
            booking_date=datetime.fromisoformat(row[3]) if row[3] else None,
            created_at=datetime.fromisoformat(row[4]) if row[4] else None
        )