import sqlite3

from werkzeug.security import check_password_hash, generate_password_hash

from moviebot.database.db_manager import DatabaseManager


class UserDB:
    def __init__(self, users_db_path: str = "data/users.db") -> None:
        self.manager = DatabaseManager(users_db_path)

    def get_user_id(self, username: str) -> int:
        with self.manager as cursor:
            cursor.execute("SELECT id FROM users WHERE username=?", (username,))
            user_id = cursor.fetchone()

        return user_id[0] if user_id else None

    def setup_db(self) -> None:
        with self.manager as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                )
            """
            )
            cursor.connection.commit()

    def register_user(self, username: str, password: str) -> bool:
        hashed_password = generate_password_hash(password, method="sha256")

        with self.manager as cursor:
            try:
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hashed_password),
                )
                cursor.connection.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def verify_user(self, username: str, password: str) -> bool:
        with self.manager as cursor:
            cursor.execute(
                "SELECT password FROM users WHERE username=?", (username,)
            )
            stored_password = cursor.fetchone()

        if stored_password and check_password_hash(
            stored_password[0], password
        ):
            return True
        else:
            return False
