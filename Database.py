import sqlite3
from typing import Optional, List
import Entities
from Entities import Ad


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
                          (user_id INTEGER PRIMARY KEY, 
                          district TEXT, price REAL, address TEXT)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS filters
                            (filter_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            district TEXT,
                            min_price INTEGER,
                            max_price INTEGER,
                            FOREIGN KEY (user_id) REFERENCES users(user_id));
                            ''')


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

    def delete_user(self, user_id: int) -> bool:
        try:
            self.cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"DB Error: {e}")
            return False

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

    def add_filter(self, filter: Entities.Filter) -> bool:
        """Добавляет объявление в БД."""
        try:
            for district in filter.districts:
                self.cursor.execute(
                    "INSERT INTO filters (user_id, district, min_price, max_price) VALUES (?, ?, ?, ?)",
                    (filter.user_id, district, filter.min_price, filter.max_price)
                )
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"DB Error: {e}")
            return False

    def get_filter(self, user_id: int) -> Optional[Entities.Filter]:
        try:
            self.cursor.execute("SELECT * FROM filters WHERE user_id = ?", (user_id,))
            output = self.cursor.fetchall()

            if output:
                districts = []
                for row in output:
                    districts.append(row[2])

                filter = Entities.Filter(output[0][1], districts, output[0][3], output[0][4])
                return filter
            else:
                return None

        except sqlite3.Error as e:
            print(f"DB Error: {e}")
            return False

    def delete_filter(self, user_id: int) -> bool:
        try:
            self.cursor.execute("DELETE FROM filters WHERE user_id = ?",
                                (user_id,))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"DB Error: {e}")
            return False

    def find_ads_by_filter(self, filter: Entities.Filter) -> list[Ad] | None:
        try:
            self.cursor.execute('''
            SELECT *
            FROM ads
            WHERE 
                price BETWEEN ? AND ? 
                AND district IN ({});
            '''.format(', '.join(['?']*len(filter.districts))),
                [filter.min_price, filter.max_price]+filter.districts
                                )
            out = self.cursor.fetchall()[:10]
            ads = [Entities.Ad(i[0], i[1], i[2], i[3]) for i in out]

            return ads
        except sqlite3.Error as e:
            print(f"DB Error: {e}")
            return None


