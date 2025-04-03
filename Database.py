import sqlite3
from typing import Optional
import Entities


class Database:
    _instance = None

    def __new__(cls, db_name: str = 'user.db'):

        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.db_name = db_name
            cls._instance.connection = None
            cls._instance.cursor = None
            cls._instance.connect()  # Открываем соединение при перв
        return cls._instance

    def connect(self):
        self.connection = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                          (user_id INTEGER PRIMARY KEY, username TEXT, role TEXT)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS ads
                          (user_id INTEGER PRIMARY KEY, district TEXT, price REAL, address TEXT)''')


        self.connection.commit()


    def add_user(self, user: Entities.User) -> bool:
        """Добавляет пользователя в БД."""
        try:
            self.cursor.execute(
                "INSERT OR IGNORE INTO users (user_id, username, role) VALUES (?, ?, ?)",
                (user.id, user.name, user.role)
            )
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"DB Error: {e}")
            return False

    def get_user(self, user_id: int) -> Optional[Entities.User]:
        """Возвращает данные пользователя."""
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        output = self.cursor.fetchone()

        if output is not None:
            user = Entities.User(output[0], output[1], output[2])
            return user

        return None

    # For ads

    def add_ad(self, ad: Entities.Ad) -> bool:
        """Добавляет объявление в БД."""
        try:
            self.cursor.execute(
                "INSERT OR IGNORE INTO ads (user_id, district, price, address) VALUES (?, ?, ?, ?)",
                (ad.user_id, ad.district, ad.price, ad.address)
            )
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"DB Error: {e}")
            return False

    def get_ad(self, user_id: int) -> Optional[Entities.Ad]:
        """Возвращает данные пользователя."""
        self.cursor.execute("SELECT * FROM ads WHERE user_id = ?", (user_id,))
        output = self.cursor.fetchone()

        if output is not None:
            ad = Entities.Ad(output[0], output[1], output[2], output[3])
            return ad

        return None


    def delete_ad(self, user_id: int) -> bool:
        try:
            self.cursor.execute("DELETE FROM ads WHERE user_id = ?", (user_id,))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"DB Error: {e}")
            return False
